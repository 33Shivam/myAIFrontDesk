from livekit.agents import Agent
from tools import update_name, book_appointment, save_query
from prompts import prompt, instruction
from models import CustomerInformation

class GreeterAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=instruction,
            tools=[update_name, book_appointment, save_query],
        )

    async def on_enter(self):
        userdata: CustomerInformation = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(role="system", content=prompt)
        await self.update_chat_ctx(chat_ctx)
        return await self.session.generate_reply()