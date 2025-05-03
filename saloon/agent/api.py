import aiohttp
import asyncio
from config import logger

async def fetch_knowledge_base():
    url = "http://127.0.0.1:8000/saloon/knowledge-base/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"Knowledge base fetched successfully: {data}")
                return {item["query"]: item["answer"] for item in data}
            else:
                logger.error(f"Failed to fetch knowledge base: {resp.status}")
                return {}
