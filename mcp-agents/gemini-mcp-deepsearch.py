import asyncio
import logging
import shutil
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from google import genai
from uuid import uuid4
from fastmcp import Client
from dotenv import load_dotenv
import warnings

sys.path.append(str(Path(__file__).parent / "scripts"))


def load_env_from_base():
    """Load environment variables from .env file in the base directory"""
    current_dir = Path(__file__).parent
    env_file = current_dir / ".env"

    if env_file.exists():
        load_dotenv(env_file)
    else:
        parent_env = current_dir.parent / ".env"
        if parent_env.exists():
            load_dotenv(parent_env)


def get_env_var(key, default=None):
    """Get environment variable with optional default value"""
    return os.getenv(key, default)


load_env_from_base()

logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("google").setLevel(logging.CRITICAL)
logging.getLogger("mcp").setLevel(logging.CRITICAL)
logging.getLogger("fastmcp").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("anyio").setLevel(logging.CRITICAL)


warnings.filterwarnings("ignore")


class DetailedLogger:
    """Enhanced logging system for LLM and tool calls with live logging"""

    def __init__(self, base_dir=None):
        self.base_dir = Path.cwd()
        self.session_id = str(uuid4())[:8]
        self.session_start = datetime.now()
        self.log_dir = self.base_dir / ".log"
        self.log_dir.mkdir(exist_ok=True)
        script_name = Path(__file__).stem
        self.log_file = self.log_dir / f"{script_name}_execution.logs"
        self.log_file.write_text("", encoding="utf-8")
        self._initialize_log_file()
        self.call_counter = 0

    def _initialize_log_file(self):
        """Initialize log file with header and session info"""
        session_info = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "agent_type": "Crypto Research Agent",
            "heurist_enabled": bool(get_env_var("HEURIST_MCP_URL")),
            "execution_directory": str(self.base_dir),
        }

        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("=" * 100 + "\n")
            f.write("CRYPTO RESEARCH AGENT EXECUTION LOG\n")
            f.write("=" * 100 + "\n")
            f.write(f"Session Info: {json.dumps(session_info, indent=2)}\n")
            f.write("=" * 100 + "\n\n")

    def _get_call_id(self):
        """Generate unique call ID"""
        self.call_counter += 1
        return f"{self.session_id}-{self.call_counter:04d}"

    def _sanitize_for_log(self, data, max_length=10000):
        """Sanitize data for logging"""
        try:
            if isinstance(data, str):
                return data[:max_length] + "..." if len(data) > max_length else data
            elif isinstance(data, (dict, list)):
                json_str = json.dumps(data, indent=2, default=str)
                return (
                    json_str[:max_length] + "..."
                    if len(json_str) > max_length
                    else json_str
                )
            else:
                str_data = str(data)
                return (
                    str_data[:max_length] + "..."
                    if len(str_data) > max_length
                    else str_data
                )
        except Exception as e:
            return f"<Error serializing data: {str(e)}>"

    def _write_log(self, log_entry):
        """Write log entry immediately with flush"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            f.flush()

    def log_user_query(self, query):
        """Log user input query"""
        timestamp = datetime.now().isoformat()
        call_id = self._get_call_id()

        log_entry = f"""
            [{timestamp}] USER QUERY - Call ID: {call_id}
            {"─" * 80}
            Query: {self._sanitize_for_log(query)}
            {"─" * 80}

        """

        self._write_log(log_entry)
        return call_id

    def log_llm_request(self, call_id, model, config, message):
        """Log LLM request details"""
        timestamp = datetime.now().isoformat()

        config_info = {
            "temperature": getattr(config, "temperature", None),
            "system_instruction": getattr(config, "system_instruction", None)[:500]
            + "..."
            if getattr(config, "system_instruction", None)
            and len(getattr(config, "system_instruction", "")) > 500
            else getattr(config, "system_instruction", None),
            "tools_available": bool(getattr(config, "tools", None)),
        }

        log_entry = f"""
            [{timestamp}] LLM REQUEST - Call ID: {call_id}
            {"─" * 80}
            Model: {model}
            Config: {self._sanitize_for_log(config_info)}
            Message: {self._sanitize_for_log(message)}
            {"─" * 80}

            """

        self._write_log(log_entry)

    def log_llm_response(self, call_id, response_text, tool_calls_made):
        """Log LLM response details"""
        timestamp = datetime.now().isoformat()

        log_entry = f"""
            [{timestamp}] LLM RESPONSE - Call ID: {call_id}
            {"─" * 80}
            Tools Called: {", ".join(tool_calls_made) if tool_calls_made else "None"}
            Response Length: {len(response_text)} characters
            Response: {self._sanitize_for_log(response_text)}
            {"─" * 80}

            """

        self._write_log(log_entry)

    def log_tool_call(self, call_id, tool_name, tool_args=None, server_name=None):
        """Log tool call request"""
        timestamp = datetime.now().isoformat()
        tool_call_id = f"{call_id}-tool-{tool_name}"

        log_entry = f"""
            [{timestamp}] TOOL CALL REQUEST - Call ID: {call_id} - Tool Call ID: {tool_call_id}  
            {"─" * 80}
            Tool Name: {tool_name}
            Server: {server_name or "Unknown"}
            Arguments: {self._sanitize_for_log(tool_args) if tool_args else "None"}
            {"─" * 80}

            """

        self._write_log(log_entry)
        return tool_call_id

    def log_tool_response(self, tool_call_id, response, success=True, error=None):
        """Log tool call response"""
        timestamp = datetime.now().isoformat()

        status = "SUCCESS" if success else "ERROR"

        log_entry = f"""
            [{timestamp}] TOOL CALL RESPONSE - Tool Call ID: {tool_call_id} - Status: {status}
            {"─" * 80}
            """

        if success:
            log_entry += f"Response: {self._sanitize_for_log(response)}\n"
        else:
            log_entry += f"Error: {self._sanitize_for_log(error)}\n"
            if response:
                log_entry += f"Partial Response: {self._sanitize_for_log(response)}\n"

        log_entry += "─" * 80 + "\n\n"

        self._write_log(log_entry)

    def log_error(self, call_id, error, context=None):
        """Log general errors"""
        timestamp = datetime.now().isoformat()

        log_entry = f"""
            [{timestamp}] ERROR - Call ID: {call_id}
            {"─" * 80}
            Error: {self._sanitize_for_log(str(error))}
            Context: {self._sanitize_for_log(context) if context else "None"}
            {"─" * 80}

            """

        self._write_log(log_entry)

    def log_session_end(self):
        """Log session end details"""
        timestamp = datetime.now().isoformat()
        duration = datetime.now() - self.session_start

        log_entry = f"""
            [{timestamp}] SESSION END
            {"─" * 80}
            Session Duration: {str(duration)}
            Total Calls Made: {self.call_counter}
            Log File: {self.log_file.name}
            {"─" * 80}

            """

        self._write_log(log_entry)

    def get_log_summary(self):
        """Get summary of current session logs"""
        return {
            "session_id": self.session_id,
            "execution_directory": str(self.base_dir),
            "log_file": str(self.log_file),
            "total_calls": self.call_counter,
            "session_duration": str(datetime.now() - self.session_start),
        }


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
    except:  # noqa: E722
        return 80


def print_banner():
    """Print professional startup banner with ASCII art"""
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
            {Colors.GRAY}              AI Research Assistant with Crypto Analysis Capabilities{Colors.RESET}

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
    """Print tool count"""
    if available_tools and hasattr(available_tools, "tools") and available_tools.tools:
        total_tools = len(available_tools.tools)
        print_status(f"Tools loaded: {total_tools}", "success")
    else:
        print_status("No tools available", "warning")
        print_status("If tools fail to load, please restart the agent", "info")


def print_goodbye(logger=None):
    """Print clean, professional goodbye message"""
    print(
        f"\n{Colors.CYAN}Session ended at {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}"
    )
    print(f"{Colors.GRAY}Thank you for using Gemini MCP Research Agent{Colors.RESET}")

    if logger:
        logger.log_session_end()
        summary = logger.get_log_summary()
        print(f"{Colors.GRAY}📁 Log saved: {summary['log_file']}{Colors.RESET}")
        print(
            f"{Colors.GRAY}📊 Total calls made: {summary['total_calls']}{Colors.RESET}"
        )

    print(f"{Colors.GRAY}{'─' * 30}{Colors.RESET}\n")

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
        max_timeout = 300

        while self.running and timeout_counter < max_timeout:
            current_spinner = spinner[pattern_index % len(spinner)]
            sys.stdout.write(
                f"\r{Colors.YELLOW}{current_spinner} {Colors.CYAN}Conducting deep research...{Colors.RESET}   "
            )
            sys.stdout.flush()
            pattern_index += 1
            timeout_counter += 1

            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

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
            sys.stdout.write("\r" + " " * 50 + "\r")
            sys.stdout.flush()


async def test_mcp_connection(mcp_client, max_retries=3, logger=None):
    """Test MCP connection and retry if failed"""
    for attempt in range(max_retries):
        try:
            tools = await mcp_client.session.list_tools()
            if logger:
                logger.log_tool_call("SYSTEM", "list_tools", server_name="MCP")
                logger.log_tool_response(
                    "SYSTEM-tool-list_tools",
                    f"Found {len(tools.tools) if tools and hasattr(tools, 'tools') else 0} tools",
                    success=True,
                )
            return True, tools
        except Exception as e:
            error_msg = str(e)
            if logger:
                logger.log_error(
                    "SYSTEM", e, f"MCP connection attempt {attempt + 1}/{max_retries}"
                )

            if attempt < max_retries - 1:
                print_status(
                    f"MCP connection failed (attempt {attempt + 1}/{max_retries}): {error_msg}",
                    "warning",
                )
                print_status(f"Retrying in {2 * (attempt + 1)} seconds...", "loading")
                await asyncio.sleep(2 * (attempt + 1))
            else:
                print_status(
                    f"MCP connection failed after {max_retries} attempts", "error"
                )
                return False, None
    return False, None


client = genai.Client()


async def run():
    logger = DetailedLogger()

    print_banner()
    print_status("Initializing MCP client connection...", "loading")
    mcp_servers_config = {}
    heurist_mcp_url = get_env_var("HEURIST_MCP_URL", None)

    if not heurist_mcp_url:
        error_msg = (
            "HEURIST_MCP_URL not configured. Please set this environment variable."
        )
        print_status(error_msg, "error")
        print_status("Add HEURIST_MCP_URL to your .env file", "info")
        logger.log_error("SYSTEM", error_msg)
        return

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

    heurist_api_key = get_env_var("HEURIST_API_KEY")
    if heurist_api_key:
        heurist_config["headers"]["Authorization"] = f"Bearer {heurist_api_key}"

    mcp_servers_config["heurist"] = heurist_config

    mcp_client = Client({"mcpServers": mcp_servers_config})

    try:
        async with mcp_client:
            connection_success, tools = await test_mcp_connection(
                mcp_client, logger=logger
            )

            if not connection_success:
                error_msg = "Heurist MCP connection failed - cannot proceed without crypto tools"
                print_status(error_msg, "error")
                print_status("Check your HEURIST_MCP_URL and HEURIST_API_KEY", "info")
                logger.log_error("SYSTEM", error_msg)
                return

            print_status("MCP Client connected successfully", "success")
            print_tools_loaded(tools)

            print_status("Configuring Gemini research model...", "loading")

            config = genai.types.GenerateContentConfig(
                temperature=0.1,
                tools=[mcp_client.session],
                system_instruction="""
                    You are a crypto analyst. Do deep research about the user query. Use as many tool calls as possible to get a comprehensive and in-depth view. After you obtain new information, explore new areas based on the updated information to get a deeper understanding.

                    CRITICAL RESEARCH METHODOLOGY:
                    1. ALWAYS use multiple tools (minimum 5-10 tool calls per query)
                    2. After each tool response, identify new research angles and use additional tools
                    3. Cross-validate information across different tools and sources
                    4. Explore related topics, market trends, technical analysis, social sentiment
                    5. Look for contradictions or gaps in data and investigate further
                    6. Use price data, on-chain metrics, news, social sentiment, project information tools
                    7. Never stop at surface-level information - dig deeper with each response

                    COMPREHENSIVE RESEARCH APPROACH:
                    - Start with basic project/token information
                    - Get current price and market data
                    - Analyze on-chain metrics and activity
                    - Check social sentiment and trending data
                    - Look at recent news and developments
                    - Examine trading patterns and volume
                    - Research team, partnerships, roadmap
                    - Compare with similar projects
                    - Identify risks and opportunities

                    REPORTING REQUIREMENTS:
                    After extensive research, provide:
                    - Executive Summary with key findings
                    - Technical Analysis with price/chart data
                    - Fundamental Analysis with project details
                    - Market Analysis with trends and sentiment  
                    - Risk Assessment with potential issues
                    - Investment Recommendation with rationale

                    Remember: More tool calls = better research = more comprehensive analysis. Always aim for nested tool calls to provide truly deep insights.
                """,
            )

            chat = client.aio.chats.create(model="gemini-2.5-flash", config=config)
            print_status("Crypto research model configured successfully", "success")

            print(f"\n{Colors.CYAN}{'═' * 80}{Colors.RESET}", flush=True)
            print(
                f"{Colors.GREEN}{Colors.BOLD}🚀 CRYPTO RESEARCH AGENT READY{Colors.RESET}",
                flush=True,
            )
            print(
                f"{Colors.GRAY}💡 Ask for crypto analysis, market research, or technical reports{Colors.RESET}",
                flush=True,
            )
            print(
                f"{Colors.GRAY}📊 The agent will conduct deep, multi-source research automatically{Colors.RESET}",
                flush=True,
            )
            print(
                f"{Colors.GRAY}🔍 Type your query or 'exit' to quit{Colors.RESET}",
                flush=True,
            )
            print(f"{Colors.CYAN}{'═' * 80}{Colors.RESET}\n", flush=True)

            while True:
                try:
                    user_input = input(
                        f"{Colors.BLUE}{Colors.BOLD}Research Query: {Colors.RESET}"
                    )
                except (KeyboardInterrupt, EOFError):
                    print_goodbye(logger)
                    break

                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print_goodbye(logger)
                    break

                call_id = logger.log_user_query(user_input)

                processing = ProcessingAnimation()
                max_retries = 3
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        processing.start()

                        logger.log_llm_request(
                            call_id, "gemini-2.5-flash", config, user_input
                        )

                        response = await chat.send_message_stream(user_input)

                        full_response = ""
                        first_chunk = True
                        tool_calls_made = []
                        response_started = False

                        async for chunk in response:
                            if hasattr(chunk, "candidates") and chunk.candidates:
                                for candidate in chunk.candidates:
                                    if (
                                        hasattr(candidate, "content")
                                        and candidate.content
                                    ):
                                        if hasattr(candidate.content, "parts"):
                                            for part in candidate.content.parts:
                                                if (
                                                    hasattr(part, "function_call")
                                                    and part.function_call
                                                ):
                                                    tool_name = part.function_call.name
                                                    if tool_name not in tool_calls_made:
                                                        tool_calls_made.append(
                                                            tool_name
                                                        )
                                                        processing.stop()
                                                        print(
                                                            f"{Colors.GRAY}🔧 Calling tool #{len(tool_calls_made)}: {tool_name}...{Colors.RESET}",
                                                            flush=True,
                                                        )

                                                        tool_args = (
                                                            dict(
                                                                part.function_call.args
                                                            )
                                                            if hasattr(
                                                                part.function_call,
                                                                "args",
                                                            )
                                                            else None
                                                        )
                                                        tool_call_id = (
                                                            logger.log_tool_call(
                                                                call_id,
                                                                tool_name,
                                                                tool_args,
                                                            )
                                                        )

                                                        processing.start()

                            if (
                                hasattr(chunk, "text")
                                and chunk.text is not None
                                and chunk.text.strip()
                            ):
                                if not response_started:
                                    processing.stop()
                                    if tool_calls_made:
                                        print(
                                            f"{Colors.GRAY}✅ Tools used ({len(tool_calls_made)}): {', '.join(tool_calls_made)}{Colors.RESET}",
                                            flush=True,
                                        )
                                    print(
                                        f"{Colors.YELLOW}📝 Compiling comprehensive research report...{Colors.RESET}",
                                        flush=True,
                                    )
                                    response_started = True
                                full_response += chunk.text
                            elif hasattr(chunk, "text") and chunk.text is not None:
                                full_response += chunk.text

                        logger.log_llm_response(call_id, full_response, tool_calls_made)

                        if full_response and full_response.strip():
                            print_ai_response(full_response)
                            if tool_calls_made:
                                print(
                                    f"{Colors.GRAY}📊 Total tools called: {len(tool_calls_made)} - {', '.join(tool_calls_made)}{Colors.RESET}\n"
                                )
                            break
                        else:
                            processing.stop()
                            retry_count += 1
                            if retry_count < max_retries:
                                print(
                                    f"{Colors.YELLOW}⚠️  Empty response received. Retrying... ({retry_count}/{max_retries}){Colors.RESET}"
                                )
                                logger.log_error(
                                    call_id,
                                    "Empty response received",
                                    f"Retry {retry_count}/{max_retries}",
                                )
                                await asyncio.sleep(2)
                                continue
                            else:
                                error_msg = (
                                    "No response received after multiple attempts"
                                )
                                print_ai_response(f"{error_msg}. Please try again.")
                                logger.log_error(call_id, error_msg)
                                if tool_calls_made:
                                    print(
                                        f"{Colors.GRAY}Tools called: {', '.join(tool_calls_made)}{Colors.RESET}\n"
                                    )
                                break

                    except Exception as e:
                        processing.stop()
                        retry_count += 1

                        error_msg = str(e) if e else "Unknown error occurred"
                        logger.log_error(
                            call_id, e, f"Retry attempt {retry_count}/{max_retries}"
                        )

                        if retry_count < max_retries:
                            print(
                                f"{Colors.YELLOW}⚠️  Error occurred. Retrying... ({retry_count}/{max_retries}){Colors.RESET}"
                            )
                            print(
                                f"{Colors.GRAY}Error: {error_msg[:100]}...{Colors.RESET}"
                            )
                            if tool_calls_made:
                                print(
                                    f"{Colors.GRAY}Tools called before error: {', '.join(tool_calls_made)}{Colors.RESET}"
                                )
                            await asyncio.sleep(3)
                            continue
                        else:
                            print_retry_message()
                            print(
                                f"{Colors.GRAY}Final error: {error_msg}{Colors.RESET}",
                                file=sys.stderr,
                            )
                            logger.log_error(call_id, e, "Final retry attempt failed")
                            if tool_calls_made:
                                print(
                                    f"{Colors.GRAY}Tools called before final error: {', '.join(tool_calls_made)}{Colors.RESET}"
                                )
                            break

    except Exception as e:
        print_status("Failed to connect to Heurist MCP server", "error")
        print_status(
            "Check your HEURIST_MCP_URL and HEURIST_API_KEY configuration", "info"
        )
        logger.log_error("SYSTEM", e, "Heurist MCP connection")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
    except Exception:
        pass
