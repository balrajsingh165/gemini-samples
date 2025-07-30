"""
Gemini Browser Agent: Gemini 2.5 Flash can interact and control a web browser using browser_use.
"""

import os
import asyncio
import argparse
import logging  # Added for logging
from browser_use.llm import ChatGoogle
from browser_use import (
    Agent,
    BrowserSession,
)

# # --- Setup Logging ---
# # You can customize the logging level further if needed
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s"
# )
# logger = logging.getLogger("GeminiBrowserAgent")
# # # Silence noisy loggers if desired
# # logging.getLogger("browser_use").setLevel(logging.WARNING)
# # logging.getLogger("playwright").setLevel(logging.WARNING)
# # --- End Logging Setup ---


# ANSI color codes
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


async def setup_browser(headless: bool = False):
    """Initialize and configure the browser"""
    browser = BrowserSession(
        headless=headless,
        deterministic_rendering=headless,
        wait_for_network_idle_page_load_time=3.0,  # Increased wait time
        highlight_elements=True,  # Keep highlighting for headed mode debugging
        # save_recording_path="./recordings", # Keep recording if needed
        viewport_expansion=500,  # Include elements slightly outside the viewport
    )
    return browser


RECOVERY_PROMPT = """
IMPORTANT RULE: If an action fails multiple times consecutively (e.g., 3 times) or if the screenshot you receive is not changing after 3 attempts,
DO NOT simply repeat the exact same action. 
Instead use the `go_back` action and try navigating to the target differently. 
If that doesn't work, try a different search query on google.
"""
# --- End Failure Recovery Prompt ---


async def agent_loop(llm, browser_session, query, initial_url=None):
    """Run agent loop with optional initial URL."""
    # Set up initial actions if URL is provided
    initial_actions = None
    if initial_url:
        initial_actions = [
            {"open_tab": {"url": initial_url}},
        ]

    agent = Agent(
        task=query,
        message_context="The user name is Philipp and he lives in Nuremberg, Today is 2025-07-24.",
        llm=llm,
        browser_session=browser_session,
        use_vision=True,
        generate_gif=True,
        initial_actions=initial_actions,
        extend_system_message=RECOVERY_PROMPT,
        max_failures=3,
    )
    # Start Agent and browser, passing the logging hook
    result_history = await agent.run()

    return result_history.final_result() if result_history else "No result found"


async def main():
    # Disable telemetry
    os.environ["ANONYMIZED_TELEMETRY"] = "false"

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Run Gemini agent with browser interaction."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="The Gemini model to use for main tasks.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser in headless mode.",
    )
    args = parser.parse_args()

    # Import the environment loader utility
    from env_loader import load_env_from_base, get_env_var
    
    # Load environment variables from .env file
    load_env_from_base()
    
    gemini_api_key = get_env_var("GEMINI_API_KEY", required=True)

    llm = ChatGoogle(
        model=args.model,
        api_key=gemini_api_key,
        config={"automatic_function_calling": {"maximum_remote_calls": 100}},
    )
    browser = await setup_browser(headless=args.headless)

    print(f"{Colors.BOLD}{Colors.PURPLE}🤖 Gemini Browser Agent Ready{Colors.RESET}")
    print(f"{Colors.GRAY}Type 'exit' to quit{Colors.RESET}\n")

    while True:
        try:
            # Get user input and check for exit commands
            user_input = input(f"{Colors.BOLD}{Colors.BLUE}You: {Colors.RESET} ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print(f"\n{Colors.GRAY}Goodbye!{Colors.RESET}")
                break

            print(
                f"{Colors.BOLD}{Colors.GREEN}Gemini: {Colors.RESET}",
                end="",
                flush=True,
            )
            # Process the prompt and run agent loop
            result = await agent_loop(llm, browser, user_input)

            # Display the final result
            print(f"{Colors.GREEN}{result}{Colors.RESET}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")

    # Ensure browser is closed properly
    try:
        await browser.close()
        print("Browser closed successfully.")
    except Exception as e:
        print(f"\nError closing browser: {e}")


if __name__ == "__main__":
    # Ensure the event loop is managed correctly, especially for interactive mode
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting program.")
