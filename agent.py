import logging

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, silero
from DifyLLM import DifyLLM
import json

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load(
        min_silence_duration=0.7,
        prefix_padding_duration=0.5,
        padding_duration=0.3
    )

##When a user connects to a room, LiveKit server sends a request to an available worker (agent code). A worker accepts and starts a new process to handle the job. (the job is the entrypoint function)
async def entrypoint(ctx: JobContext):
    
    ## initial_ctx is a variable that contains _metadata and chat messages
    initial_ctx = llm.ChatContext()
    
    logger.info(f"connecting to room {ctx.room.name}")
    
    ## Connect user to room with audio only
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    print("initial_ctx:",participant.metadata)
    
    ##add access token and user_id as context for future use in Dify API calls
    initial_ctx._metadata["access_token"] = json.loads(participant.metadata).get("access_token", None) if participant.metadata else None
    initial_ctx._metadata["user_id"] = participant.identity

    logger.info(f"starting voice assistant for participant {participant.identity}")

    ##used my own DifyLLM class to support using the Dify API as the LLM
    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=DifyLLM(),        
        tts=deepgram.TTS(),
        chat_ctx=initial_ctx,
    )

    agent.start(ctx.room, participant)

    # The agent should be polite and greet the user when it joins :)
    await agent.say("Hello, how may i help you today?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
