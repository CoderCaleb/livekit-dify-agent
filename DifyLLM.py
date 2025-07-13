from __future__ import annotations

import asyncio
from asyncio.log import logger
import datetime
import os
import json
from dataclasses import dataclass
import random
import string
from typing import Any, Literal, MutableSet, Union


import aiohttp
import httpx
from livekit.agents import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    llm,
)
from livekit.agents.llm import ToolChoice, _create_ai_function_info
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions

import openai
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta


class DifyLLM(llm.LLM):
    ## since chat method is @abstractmethod, we know that we need to and can modify this chat method
    async def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        fnc_ctx: llm.function_context.FunctionContext | None = None,
        temperature: float | None = None,
        n: int | None = None,
        parallel_tool_calls: bool | None = None,
        tool_choice: Union[ToolChoice, Literal["auto", "required", "none"]] | None = None
    ) -> "DifyLLMStream":
        print("Debug: Entered the chat method.")
        
        ##find latest message from user
        latest_query = next(
            ##this will not return a list, but rather a generator expression which is more performance friendly
            (msg.content for msg in reversed(chat_ctx.messages) if msg.role == "user"),
            None,
        )
        print("Debug: chat_ctx:",chat_ctx)
        print(f"Debug: Latest query found: {latest_query}")

        chat_context_data = chat_ctx.copy()
        # Prepare the payload for Dify API
        payload = {
            "query": latest_query,
            "conversation_id": chat_context_data._metadata.get("conversation_id", None),
            "response_mode": "streaming",  # Or "blocking", depending on your preference
            "user": chat_context_data._metadata["user_id"],
            "inputs": {"access_token":chat_context_data._metadata.get("access_token", None)},
        }

        print(f"Debug: Payload prepared: {payload}")

        headers = {
            'Authorization': f'Bearer {os.environ.get("DIFY_API_KEY")}',  # Use the API key directly in the header
            'Content-Type': 'application/json'
        }
        print(f"Debug: Headers prepared: {headers}")

        return DifyLLMStream(
            llm=self,
            chat_ctx=chat_ctx,
            fnc_ctx=fnc_ctx,
            conn_options=conn_options,
            api_url="http://localhost/v1/chat-messages",
            payload=payload,
            headers=headers,
        )


class DifyLLMStream(llm.LLMStream): ##in charge of making request to API and streaming the responses to user
    ##auto runs when object is initialised
    def __init__(
        self,
        llm: llm.LLM,
        *,
        chat_ctx: llm.ChatContext,
        fnc_ctx: llm.function_context.FunctionContext | None,
        conn_options: APIConnectOptions,
        api_url: str,
        payload: dict,
        headers: dict,
    ) -> None:
        print("Debug: Initializing DifyLLMStream.")
        ##super is to access parent method which is init in this case, without super, child init would be ran as it overrides parents init
        super().__init__(llm, chat_ctx=chat_ctx, fnc_ctx=fnc_ctx, conn_options=conn_options)
        self._api_url = api_url
        self._payload = payload
        self._headers = headers

    async def _run(self):
        print("Debug: Entering _run method.")
        print("Debug: Chat Context:", self.chat_ctx._metadata)
        ##set user_id in metadata
        if self.chat_ctx._metadata.get("user_id",None) == None: ##why do this when payload["user"] will be None if chat_ctx is none, will look into this
            self._chat_ctx._metadata["user_id"] = self._payload["user"]
        if self._payload["query"] == None:
            raise ValueError("No valid user query found in the chat context.")
        ##purpose of with is to ensure proper cleanup (closing HTTP connection etc) even if theres error.
        ##result of __aenter__ is assigned to the variable after "as", and __aexit is ran after block finishes
        async with httpx.AsyncClient(timeout=self._conn_options.timeout) as client:  # Step 1 (set up async HTTP client, so that start API request while doing other processes at the same time)
            print(f"Debug: Making request to {self._api_url} with payload: {self._payload}")
            async with client.stream("POST", self._api_url, json=self._payload, headers=self._headers, timeout=15) as response:  # Step 2 (send POST request for a stream of events)
                print(f"Debug: Response received with status code: {response.status_code}")
                ##Iterators are single-use, forward-only.
                ##Iterables (like lists) can give you new iterators anytime to restart looping.
                ##aiter_lines() is a async iterator
                async for line in response.aiter_lines():  # Step 3 (loop through aysnc iterator which will wait for new data while doing other processes)
                    print(f"Debug: Received line: {line}")
                    if line.startswith("data:"):  # Step 4
                        event_data = line.lstrip("data:").strip()  # Step 5 (remove data: at the start of the string)
                        print(f"Debug: Parsed event data: {event_data}")
                        parsed_event_data = json.loads(event_data)
                        if parsed_event_data["event"] == "message":
                            parsed_chunk = self._parse_chunk(event_data)
                            if parsed_chunk:
                                print(f"Debug: Parsed chunk: {parsed_chunk}")
                                self._event_ch.send_nowait(parsed_chunk) ##send message to user
                        elif parsed_event_data["event"] == "node_started":
                            self._chat_ctx._metadata["conversation_id"] = parsed_event_data["conversation_id"] ##set conversation_id generated by Dify to metadata

    def _parse_chunk(self, response: str) -> llm.ChatChunk | None:
        print(f"Debug: Parsing chunk from response: {response}")
        try:
            # Parse JSON chunk and map to `ChatChunk`
            response_data = json.loads(response)
            print(llm.ChoiceDelta(role="assistant", content=response_data["answer"], tool_calls=None))
            choices = [
                Choice(_request_id=response_data["message_id"], delta=ChoiceDelta(role="assistant", content=response_data["answer"], tool_calls=None), index=response_data["created_at"])
            ]

            return llm.ChatChunk(request_id=response_data["message_id"], choices=choices)
        except Exception:
            logger.warning("Failed to parse chunk", exc_info=True)
            return None

    
def generate_guest_uid():
    return 'guest-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))