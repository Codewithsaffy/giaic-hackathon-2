import asyncio
import os
import logging
import sys
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

api_key = os.getenv("CEREBRAS_API_KEY")
client = AsyncOpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")
model = OpenAIChatCompletionsModel(model="gpt-oss-120b", openai_client=client)

async def test():
    agent = Agent(name="Test", instructions="Just say hello", model=model)
    print("Running minimal agent...")
    result = await Runner.run(agent, "hi")
    print(f"Result: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(test())
