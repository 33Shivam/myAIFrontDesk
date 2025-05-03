from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins import google , cartesia, silero
# from config import logger
from models import CustomerInformation
from agent import GreeterAssistant
import webSocketConnection
import asyncio
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from api import fetch_knowledge_base


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()


    # Fetch the knowledge base
    knowledge_base = await fetch_knowledge_base()
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.8,
            instructions=f"""You are a helpful salon assistant. Answer based on this knowledge base:
            {knowledge_base}
            If the answer exists in the knowledge base, provide it. "
            If the query is not found in the knowledge base, respond politely and try to assist.""",
        ),
        tts=cartesia.TTS(),
        userdata=CustomerInformation(),
    )

    webSocketConnection.agent_session = session


    
    await asyncio.gather(
        session.start(
            room=ctx.room,
            agent=GreeterAssistant(),
            room_input_options=RoomInputOptions(),
        ),
        webSocketConnection.listen_for_answers() 
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
