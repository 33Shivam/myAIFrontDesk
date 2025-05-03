import requests
from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents import RunContext

from config import logger
from models import CustomerInformation

RunContext_T = RunContext[CustomerInformation]

@function_tool()
async def update_name(
    name: Annotated[str, Field(description="The customer's name")],
    context: RunContext[CustomerInformation],
) -> str:
    """ Called when the user provides their name.
    # Confirm the spelling with the user before calling the function."""


    context.userdata.customer_name = name
    logger.info(f"User's name updated to: {name}")
    return f"The name is updated to {name}"

@function_tool()
async def book_appointment(
    name: Annotated[str, Field(description="The customer's name")],
    date: Annotated[str, Field(description="The date of the appointment")],
    time: Annotated[str, Field(description="The time of the appointment")],
    context: RunContext[CustomerInformation],
) -> str:
    """ Called when the user books an appointment.
     Confirm the spelling the day and time with the user before calling the function."""
    userdata = context.userdata
    userdata.customer_name = name
    userdata.reservation_date = date
    userdata.reservation_time = time

    try:
        response = requests.post(
            "http://127.0.0.1:8000/saloon/appointments/",
            json={
                "customer_name": name,
                "reservation_date": date,
                "reservation_time": time,
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
    context:RunContext[CustomerInformation],
) -> str:
    ''' Called when the user asks a question or has a query that is not related to booking an appointment.
'''

    name = context.userdata.customer_name or "Guest"
    context.userdata.query = query
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