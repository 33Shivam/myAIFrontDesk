from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RunContext
from livekit.plugins import openai, cartesia, deepgram, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from dataclasses import dataclass
from pydantic import Field
from typing import Annotated, Optional
import yaml
import logging
import requests
from datetime import datetime
import os

load_dotenv()

# ---------- CONFIG LOGGING ----------
logger = logging.getLogger("salon")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logging.StreamHandler().setFormatter(formatter)

# ---------- DATA MODEL ----------
@dataclass
class CustomerInformation:
    customer_name: Optional[str] = None
    reservation_time: Optional[str] = None
    reservation_date: Optional[str] = None
    query : Optional[str] = None


    def summarize(self) -> str:
        data = {
            "customer_name": self.customer_name or "Not provided",
            "reservation_time": self.reservation_time or "Not provided",
            "reservation_date": self.reservation_date or "Not provided",
            "query": self.query or "Not provided",
        }
        return yaml.dump(data)


RunContext_T = RunContext[CustomerInformation]

# ---------- INTENT HELPER ----------
def is_booking_intent(message: str) -> bool:
    booking_keywords = ["book", "appointment", "reserve", "schedule"]
    return any(keyword in message.lower() for keyword in booking_keywords)

# ---------- FUNCTION TOOLS ----------
from livekit.agents.llm import function_tool

@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context: RunContext_T,
) -> str:
    """Called when the user provides their name.
    Confirm the spelling with the user before calling the function."""
    context.userdata.customer_name = name
    logger.info(f"Name set to {name}")
    return f"Thanks, {name}! Would you like to book an appointment or ask something about our services?"

@function_tool()
async def book_appointment(
    name: Annotated[str, Field(description="Customer name")],
    date: Annotated[str, Field(description="Appointment date")],
    time: Annotated[str, Field(description="Appointment time")],
    context: RunContext_T,
) -> str: 
    """Called when the user wants to book an appointment.
    Confirm the with the user before calling the function."""
    context.userdata.customer_name = name
    context.userdata.reservation_date = date
    context.userdata.reservation_time = time

    try:
        res = requests.post(
            "http://127.0.0.1:8000/saloon/appointments/",
            json={
                "customer_name": name,
                "reservation_date": date,
                "reservation_time": time,
            },
            timeout=5,
        )
        if res.status_code == 201:
            logger.info("Appointment saved.")
            return f"Great! Your appointment is booked for {date} at {time}."
        else:
            logger.error(f"Failed booking: {res.text}")
            return "Could not book your appointment due to a system error."
    except Exception as e:
        logger.error(f"Exception during booking: {e}")
        return "Could not book your appointment due to a network error."


@function_tool()
async def save_query(
        self,
        query: Annotated[str, Field(description="The user's query")],
        context: RunContext_T,
    ) -> str:
        """Called when the user asks a question or has a query that is not related to booking an appointment."""
        name = context.userdata.customer_name or "Guest"
        context.userdata.query = query
        try:
            res = requests.post(
                "http://127.0.0.1:8000/saloon/queries/",
                json={"customer_name": name, "query": query},
                timeout=5,
            )
            if res.status_code == 201:
                logger.info("Query saved to database.")
            else:
                logger.error(f"Query saving failed: {res.text}")
        except Exception as e:
            logger.error(f"Exception during query save: {e}")
        return "Let me check with my supervisor and get back to you." 






# ---------- AGENTS ----------

class BaseAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Initial agent that greets user and routes to appropriate agents.",
            tools=[update_name],
        )
        self.name_set = False

    async def on_enter(self):
        return "Hi! Welcome to Looks Salon. May I have your name, please?"

    async def on_message(self, message: str):
        userdata = self.session.userdata

        if not self.name_set:
            # First message after greeting = name
            await update_name(name=message, context=self.session)
            self.name_set = True
            return "Nice to meet you! Would you like to book an appointment or ask about something else?"

        if is_booking_intent(message):
            await self.session.update_agent(AppointmentAgent())
            return await self.session.current_agent()
        else:
            await self.session.update_agent(QueryAgent())
            await self.session.current_agent().save_query(query=message, context=self.session)
            return await self.session.current_agent()
        

    @function_tool()
    async def to_appointment(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when the user wants to book an appointment.
        This function will transfer the user to the appointment agent."""
    



class AppointmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instructions="You are a appointment booking agent. Your Job is to ask the customer for the date and time of their appointment. Then save it to the database by calling the tool",
            tools=[book_appointment],
        )

    async def on_enter(self):
        return "Great! Please tell me the date and time you'd like to book your appointment."

class QueryAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Handle general salon queries politely." 
                         , tools=[save_query])

    
    async def on_enter(self):
        return "Let me check with my supervisor and get back to you."


# ---------- ENTRYPOINT ----------
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession[CustomerInformation](
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM.with_ollama(model="llama3.2", base_url="http://localhost:11434/v1"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        userdata=CustomerInformation(),
    )

    await session.start(
        room=ctx.room,
        agent=BaseAgent(),
        room_input_options=RoomInputOptions(),
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
