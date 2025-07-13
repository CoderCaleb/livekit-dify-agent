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
        latest_query = next(
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
            api_url="http://localhost/v1/chat-messages",  # Replace with the actual endpoint
            payload=payload,
            headers=headers,
        )


class DifyLLMStream(llm.LLMStream):
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
        super().__init__(llm, chat_ctx=chat_ctx, fnc_ctx=fnc_ctx, conn_options=conn_options)
        self._api_url = api_url
        self._payload = payload
        self._headers = headers

    async def _run(self):
        print("Debug: Entering _run method.")
        print("Debug: Chat Context:", self.chat_ctx._metadata)
        if self.chat_ctx._metadata.get("user_id",None) == None:
            self._chat_ctx._metadata["user_id"] = self._payload["user"]
        if self._payload["query"] == None:    
            raise ValueError("No valid user query found in the chat context.")
        async with httpx.AsyncClient(timeout=self._conn_options.timeout) as client:  # Step 1
            print(f"Debug: Making request to {self._api_url} with payload: {self._payload}")
            async with client.stream("POST", self._api_url, json=self._payload, headers=self._headers, timeout=15) as response:  # Step 2
                print(f"Debug: Response received with status code: {response.status_code}")
                async for line in response.aiter_lines():  # Step 3
                    print(f"Debug: Received line: {line}")
                    if line.startswith("data:"):  # Step 4
                        event_data = line.lstrip("data:").strip()  # Step 5
                        print(f"Debug: Parsed event data: {event_data}")
                        parsed_event_data = json.loads(event_data)
                        if parsed_event_data["event"] == "message":
                            parsed_chunk = self._parse_chunk(event_data)
                            if parsed_chunk:
                                print(f"Debug: Parsed chunk: {parsed_chunk}")
                                self._event_ch.send_nowait(parsed_chunk)
                        elif parsed_event_data["event"] == "node_started":
                            self._chat_ctx._metadata["conversation_id"] = parsed_event_data["conversation_id"]

                            

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