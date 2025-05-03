from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RunContext
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    silero,
    anthropic,
    google
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from dataclasses import dataclass, field
from pydantic import Field

from typing import Annotated, Optional
import yaml
from livekit.agents.llm import function_tool
import logging
import os
import django
import requests
from datetime import datetime

prompt = """"You are a polite and professional salon assistant. Your main goal is to help users book appointments. Follow this flow:

1. Greet the user and ask: "Would you like to book an appointment?"

2. If the user says "yes" or expresses interest in booking:
   - Ask for their name.
   - Then ask for their preferred date and time.
   - Confirm their appointment with a friendly message.

3. If the user asks **anything salon-related** such as:
   - Discounts
   - Special offers
   - Services (e.g., haircut, facial, waxing, etc.)
   - Stylist availability
   - Or anything that is not directly about booking a time

   Capture their query set it using the save_query function and Simply respond: **""Let me check with my supervisor and get back to you.""** and end the conversation.
   Do not provide any salon-related information beyond that.

Stay helpful, friendly, and concise. Always redirect the conversation back to booking if it goes off-topic."""

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler("salon_agent.log", mode="a")  # 'a' for append mode
file_handler.setLevel(logging.INFO)

# Create formatter and set it for both handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
load_dotenv()


@dataclass
class CustomerInformation:
    customer_name: Optional[str] = None
    reservation_time: Optional[str] = None
    reservation_date: Optional[str] = None
    query: Optional[str] = None

    def summarize(self):
        data = {
            "customer_name": self.customer_name or "Not provided",
            "reservation_time": self.reservation_time or "Not provided",
            "reservation_date": self.reservation_date or "Not provided",
            "query": self.query or "Not provided",
        }
        return yaml.dump(data)


RunContext_T = RunContext[CustomerInformation]


@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context: RunContext_T,
) -> str:
    """Called when the user provides their name.
    Confirm the spelling with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_name = name
    logger.warning(f"User's name updated to: {name}")
    return f"The name is updated to {name}"


@function_tool()
async def book_appointment(
    name: Annotated[str, Field(description="The customer's name")],
    date: Annotated[str, Field(description="The date of the appointment")],
    time: Annotated[str, Field(description="The time of the appointment")],
    context: RunContext_T,
) -> str:
    """Called when the user books an appointment.
    Confirm the spelling the day and time with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_name = name
    userdata.reservation_time = time
    userdata.reservation_date = date
    today_date = datetime.now().strftime("%Y-%m-%d")

    logger.warning(f"Appointment booked for {name} on {date} at {time}")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/saloon/appointments/",
            json={
                "customer_name": name,
                "reservation_date": today_date,
                "reservation_time": "12:00",
            },
            timeout=5,
        )
        if response.status_code == 201:
            logger.info("Appointment saved via API.")
        else:
            logger.error(f"Failed to save appointment via API: {response.text}")
            return "Could not book your appointment due to a system error."
    except Exception as e:
        logger.error(f"API error: {e}")
        return "Could not book your appointment due to a system error."

    return f"The appointment is booked for {name} on {date} at {time}."


@function_tool()
async def save_query(
    query: Annotated[str, Field(description="The user's query")],
    context: RunContext_T,
) -> str:
    """Called when the user asks a question or has a query that is not related to booking an appointment."""
    name = context.userdata.customer_name or "Guest"
    context.userdata.query = query
    logger.warning(f"User's query: {query}")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/saloon/queries/",
            json={"customer_name": name, "query": query},
            timeout=5,
        )
        if response.status_code == 201:
            logger.info("Query saved to database.")
        else:
            logger.error(f"Query saving failed: {response.text}")
    except Exception as e:
        logger.error(f"Exception during query save: {e}")
    return "Let me check with my supervisor and get back to you."




class GreeterAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are an Salon Assistant working in Looks Salon. You are friendly and helpful"
                "your job is to ask the customer's name. Then set it . Don't ask any unessary questions apart name"
                "If the customer want to book an appointment. Set it up by calling the function"
            ),
            tools=[update_name, book_appointment , save_query],
        )

    async def on_enter(self):
        userdata: CustomerInformation = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        chat_ctx.add_message(
            role="system",
            content=prompt,
        )
        await self.update_chat_ctx(chat_ctx)

        return await self.session.generate_reply("Greetings! Would you like to book an appointment")


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    # session = AgentSession[CustomerInformation](
    #     stt=deepgram.STT(model="nova-3", language="multi"),
    #     llm=openai.LLM.with_ollama(
    #         model="llama3.2",
    #         base_url="http://localhost:11434/v1",
    #     ),
    #     tts=cartesia.TTS(),
    #     vad=silero.VAD.load(),
    #     turn_detection=MultilingualModel(),
    #     userdata=CustomerInformation(),
    # )


        
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.8,
            instructions="You are a helpful assistant",
        ),
        userdata=CustomerInformation(),
    )



    await session.start(
            room=ctx.room,
            agent=GreeterAssistant(),
            room_input_options=RoomInputOptions(),
            )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
