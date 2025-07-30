# pip install google-genai mcp
# requires Python 3.13+
import asyncio
from google import genai
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Import the environment loader utility
from env_loader import load_env_from_base, get_env_var

# Load environment variables from .env file
load_env_from_base()

# Get the Gemini API key from the environment variable
api_key = get_env_var("GEMINI_API_KEY", required=True)

# Create Gemini instance LLM class
client = genai.Client(api_key=api_key)

remote_url = "https://mcp.deepwiki.com/mcp"


async def run():
    async with streamablehttp_client(remote_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Initialize conversation history using simple tuples
            config = genai.types.GenerateContentConfig(
                temperature=0,
                tools=[session],
            )
            print("Agent is ready. Type 'exit' to quit.")
            chat = client.aio.chats.create(
                model="gemini-2.5-flash-preview-05-20", config=config
            )
            while True:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    print("Exiting chat.")
                    break

                # Append user message to history
                response = await chat.send_message(user_input)
                if len(response.automatic_function_calling_history) > 0:
                    if (
                        response.automatic_function_calling_history[0].parts[0].text
                        == user_input
                    ):
                        response.automatic_function_calling_history.pop(0)
                    for call in response.automatic_function_calling_history:
                        if call.parts[0].function_call:
                            print(f"MCP call: {call.parts[0].function_call}")
                        elif call.parts[0].function_response:
                            print(
                                f"MCP response: {call.parts[0].function_response.response["result"].content[0].text}"
                            )
                print(f"Assistant: {response.text}")


if __name__ == "__main__":
    asyncio.run(run())
