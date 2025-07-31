# pip install google-genai fastmcp
# requires Python 3.13+
import asyncio
import logging
import shutil
import sys
from datetime import datetime
from google import genai
from uuid import uuid4
from fastmcp import Client

# Import the environment loader utility
from env_loader import load_env_from_base, get_env_var

# Load environment variables from .env file
load_env_from_base()

# Suppress all logging including asyncio and other system logs
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("google").setLevel(logging.CRITICAL)
logging.getLogger("mcp").setLevel(logging.CRITICAL)
logging.getLogger("fastmcp").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("anyio").setLevel(logging.CRITICAL)

# Suppress warnings
import warnings

warnings.filterwarnings("ignore")


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


def get_terminal_width():
    """Get terminal width, default to 80 if unable to determine"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def print_banner():
    """Print professional startup banner with ASCII art - called only once"""
    print(
        f"""
{Colors.CYAN}{Colors.BOLD}
 ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗    ███╗   ███╗ ██████╗██████╗ 
██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║██║    ████╗ ████║██╔════╝██╔══██╗
██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║██║    ██╔████╔██║██║     ██████╔╝
██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║    ██╔████╔██║██║     ██╔═══╝ 
╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚████║██║    ██║ ╚═╝ ██║╚██████╗██║     
 ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╚═╝  ╚═══╝╚═╝    ╚═╝     ╚═╝ ╚═════╝╚═╝     
{Colors.RESET}
{Colors.GRAY}                    AI Assistant with Advanced Tool Integration{Colors.RESET}

{Colors.GRAY}{"═" * 80}{Colors.RESET}
{Colors.GRAY}⏰ Session Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}{Colors.RESET}
{Colors.GRAY}🆔 Session ID: {str(uuid4())[:8]}{Colors.RESET}
{Colors.GRAY}{"═" * 80}{Colors.RESET}
""",
        flush=True,
    )


def print_status(message, status="info"):
    """Print status message with appropriate icon and color"""
    if status == "success":
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}", flush=True)
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.RESET}", flush=True)
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}", flush=True)
    elif status == "loading":
        print(f"{Colors.BLUE}⏳ {message}{Colors.RESET}", flush=True)
    else:
        print(f"{Colors.GRAY}ℹ️  {message}{Colors.RESET}", flush=True)


def print_ai_response(text):
    """Print AI response with clean, simple formatting"""
    print(f"\n{Colors.GREEN}Assistant:{Colors.RESET}")
    print(f"{Colors.WHITE}{text}{Colors.RESET}\n")


def print_tools_loaded(available_tools):
    """Print simple tools loaded message"""
    if available_tools and hasattr(available_tools, "tools") and available_tools.tools:
        # Get unique categories
        categories = set()
        for tool in available_tools.tools:
            category = tool.name.split("_")[0] if "_" in tool.name else "general"
            categories.add(category.title())

        category_list = ", ".join(sorted(categories))
        print_status(f"Tools loaded: {category_list}", "success")
    else:
        print_status("No tools available", "warning")
        print_status("If tools fail to load, please restart the agent", "info")


def print_goodbye():
    """Print clean, professional goodbye message"""
    print(
        f"\n{Colors.CYAN}Session ended at {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}"
    )
    print(f"{Colors.GRAY}Thank you for using Gemini MCP Agent{Colors.RESET}")
    print(f"{Colors.GRAY}{'─' * 30}{Colors.RESET}\n")

    # Ensure terminal cursor is visible
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def print_retry_message():
    """Print friendly retry message with apology"""
    print(
        f"\n{Colors.YELLOW}I apologize for the inconvenience. Please try your request again.{Colors.RESET}"
    )
    print(
        f"{Colors.GRAY}If the issue persists, try rephrasing your request or restart the agent.{Colors.RESET}\n"
    )


class ProcessingAnimation:
    def __init__(self):
        self.running = False
        self.task = None

    async def _animate(self):
        """Simple analyzing animation with timeout"""
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        pattern_index = 0
        timeout_counter = 0
        max_timeout = 300  # 30 seconds (300 * 0.1)

        while self.running and timeout_counter < max_timeout:
            current_spinner = spinner[pattern_index % len(spinner)]
            sys.stdout.write(
                f"\r{Colors.YELLOW}{current_spinner} {Colors.CYAN}Analyzing...{Colors.RESET}   "
            )
            sys.stdout.flush()
            pattern_index += 1
            timeout_counter += 1

            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

        # If timeout reached, clear animation
        if timeout_counter >= max_timeout:
            self.stop()

    def start(self):
        """Start the processing animation"""
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self._animate())

    def stop(self):
        """Stop the processing animation and clear the line"""
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            # Clear the processing line
            sys.stdout.write("\r" + " " * 40 + "\r")
            sys.stdout.flush()


# Create Gemini instance LLM class
client = genai.Client()

# Build MCP servers configuration
mcp_servers_config = {
    "pipedream": {
        "transport": "http",
        "url": "https://remote.mcp.pipedream.net",
        "headers": {
            "Authorization": f"Bearer {get_env_var('PIPEDREAM_API_KEY', f'devtok_{uuid4()}')}",
            "x-pd-app-slug": "slack, google_sheets, notion, github, gmail, google_calendar",
        },
    }
}

# Add custom Heurist MCP server if URL is provided
heurist_mcp_url = get_env_var("HEURIST_MCP_URL", None)
if heurist_mcp_url:
    heurist_config = {
        "transport": "sse",
        "url": heurist_mcp_url,
        "headers": {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "User-Agent": "FastMCP/1.0",
        },
    }

    # Add authentication if provided
    heurist_api_key = get_env_var("HEURIST_API_KEY")
    if heurist_api_key:
        heurist_config["headers"]["Authorization"] = f"Bearer {heurist_api_key}"

    mcp_servers_config["heurist"] = heurist_config

mcp_client = Client({"mcpServers": mcp_servers_config})


async def run():
    print_banner()

    print_status("Initializing MCP client connection...", "loading")

    # Test MCP client connection first
    try:
        async with mcp_client:
            print_status("MCP Client connected successfully", "success")

            # List available tools
            try:
                tools = await mcp_client.session.list_tools()
                print_tools_loaded(tools)
            except Exception:
                print_status("Could not load tools", "warning")
                print_status("If tools fail to load, please restart the agent", "info")

            # Initialize Gemini with system configuration
            print_status("Configuring Gemini model...", "loading")

            config = genai.types.GenerateContentConfig(
                temperature=0,
                tools=[mcp_client.session],
                system_instruction=f"""
                    Very important:
                    - The user's timezone is {datetime.now().strftime("%Z")}.
                    - The current date is {datetime.now().strftime("%Y-%m-%d")}.
                    Any dates before this are in the past; any dates after this are in the future.

                    Language & Comprehension:
                    - When users refer to 'latest', 'most recent', or 'today's', do not assume your knowledge is current. Always validate using tools or external sources if needed.
                    - Speak in the language the user uses or explicitly requests.

                    Available MCP Servers:
                    - Pipedream: For Slack, Google Sheets, Notion, and GitHub integrations.
                    {"- Heurist: Custom MCP server for AI/ML tools and token price capabilities." if heurist_mcp_url else ""}

                    Tool Usage Guidelines:
                    - Select the appropriate tool based on the user's request.
                    - If a specific capability is missing in one tool but available in another (e.g., Heurist), prefer the one that supports the feature.
                    """,
            )

            chat = client.aio.chats.create(model="gemini-2.5-flash", config=config)
            print_status("Gemini model configured successfully", "success")

            # Start interactive session
            print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}", flush=True)
            print(
                f"{Colors.GREEN}{Colors.BOLD}🚀 SYSTEM READY - Start your conversation below{Colors.RESET}",
                flush=True,
            )
            print(
                f"{Colors.GRAY}💡 Type your message or 'exit' to quit{Colors.RESET}",
                flush=True,
            )
            print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n", flush=True)

            while True:
                try:
                    user_input = input(f"{Colors.BLUE}{Colors.BOLD}You: {Colors.RESET}")
                except (KeyboardInterrupt, EOFError):
                    print_goodbye()
                    break

                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print_goodbye()
                    break

                # Initialize processing animation
                processing = ProcessingAnimation()

                try:
                    # Start processing animation
                    processing.start()

                    # Send message and get response
                    response = await chat.send_message_stream(user_input)

                    # Keep processing animation running until we start getting response
                    full_response = ""
                    first_chunk = True

                    async for chunk in response:
                        if first_chunk:
                            # Stop processing animation and show generating message
                            processing.stop()
                            print(
                                f"{Colors.YELLOW}✨ Generating response...{Colors.RESET}",
                                flush=True,
                            )
                            first_chunk = False
                        full_response += chunk.text

                    # Print the response
                    print_ai_response(full_response)

                except Exception:
                    # Stop processing animation if there's an error
                    processing.stop()

                    # Print friendly retry message instead of error details
                    print_retry_message()

                    # Optional: Log the actual error for debugging (comment out in production)
                    # print(f"Debug: {str(e)}", file=sys.stderr)

    except Exception:
        print_status("Failed to connect to MCP servers", "error")

        # Try running without custom MCP servers
        if heurist_mcp_url:
            print_status(
                "Attempting connection without Heurist MCP server...", "loading"
            )
            fallback_config = {
                "mcpServers": {"pipedream": mcp_servers_config["pipedream"]}
            }
            fallback_client = Client(fallback_config)

            try:
                async with fallback_client:
                    print_status(
                        "Pipedream MCP connected successfully (fallback mode)",
                        "success",
                    )
                    print_status("Some functionality may be limited", "warning")

            except Exception:
                print_retry_message()
                print_status("Check your internet connection", "info")
                print_status("Verify PIPEDREAM_API_KEY in .env file", "info")
                print_status("Try using Claude Code instead: claude-code", "info")
                return


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        # Clean exit without showing error traceback
        pass
    except Exception:
        # Suppress any other exceptions during shutdown
        pass
