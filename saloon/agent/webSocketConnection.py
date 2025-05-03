# ws_listener.py
import asyncio
import websockets
import json
from livekit.agents import AgentSession
from models import CustomerInformation
from config import logger

agent_session: AgentSession[CustomerInformation] = None  # will be set in entrypoint

async def listen_for_answers():
    uri = "ws://localhost:8000/ws/queries/"
    logger.info("Connecting to Django WebSocket...")

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected. Listening for admin answers...")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data.get("type") == "ANSWER_ADDED":
                        logger.info("got answer")

                        customer = data["data"]["customer_name"]
                        answer = data["data"]["answer"]
                        query = data["data"]["query"]

                        if agent_session:
                            logger.info(f"Sending answer to {customer}: {answer}")
                            await agent_session.say(
                                f"{customer}, the answer to your query '{query}' is: {answer}"
                            )
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await asyncio.sleep(5)
