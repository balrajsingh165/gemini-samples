import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Import the environment loader utility
from env_loader import load_env_from_base, get_env_var

# Load environment variables from .env file
load_env_from_base()

# Get the Gemini API key from the environment variable
api_key = get_env_var("GEMINI_API_KEY", required=True)

# Create Gemini instance LLM class
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",  # or "gemini-2.0-flash"
    temperature=0.7,
    max_retries=2,
    google_api_key=api_key,
)


async def main():
    async with MultiServerMCPClient(
        {
            "airbnb": {
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
                "transport": "stdio",
            },
            # Add more or your own servers here, works with remote servers too via sse
            # "weather": {
            #     "url": "http://localhost:8000/sse",  # Ensure the weather server is running
            #     "transport": "sse",
            # },
        }
    ) as client:
        # Create ReAct Agent with MCP servers
        graph = create_react_agent(model, client.get_tools())

        # Initialize conversation history using simple tuples
        inputs = {"messages": []}

        print("Agent is ready. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting chat.")
                break

            # Append user message to history
            inputs["messages"].append(("user", user_input))

            # call our graph with streaming to see the steps
            async for state in graph.astream(inputs, stream_mode="values"):
                last_message = state["messages"][-1]
                last_message.pretty_print()

            # update the inputs with the agent's response
            inputs["messages"] == state["messages"]


if __name__ == "__main__":
    asyncio.run(main())
