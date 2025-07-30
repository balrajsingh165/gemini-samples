# Google DeepMind Models Samples, Snippets and Guides

This repository contains personal tiny samples, snippets and guides showcasing cool experiments and implementations using Google DeepMind Gemini models.

```
├── examples/
│   └── gemini-with-openai-sdk.ipynb
├── guides/
│   └── function-calling.ipynb
├── scripts/
│   └── gemini-browser-use.py
├── javascript-examples/
│   └── gemini-native-image-out.js
├── LICENSE
└── README.md
```

## Guides:

- [Function Calling Guide](guides/function-calling.ipynb) - Comprehensive guide on implementing function calling
- [ReAct Agent](guides/langgraph-react-agent.ipynb) - Guide on building a ReAct agent with LangGraph and Gemini
- [Agentic Patterns](guides/agentic-pattern.ipynb) - Overview of agentic patterns and how to use them with Gemini
- [Gemini with Memory](guides/gemini-with-memory.ipynb) - Example how to integrate long-term memory into Gemini

## Examples

- [Gemini with OpenAI SDK](examples/gemini-with-openai-sdk.ipynb) - Use Gemini models with the OpenAI SDK
- [Gemini with Google Search](examples/gemini-google-search.ipynb) - Enable Google Search integration for up-to-date information
- [Structured Outputs](examples/gemini-structured-outputs.ipynb) - Generate structured JSON outputs using Pydantic
- [Meta Prompts](examples/gemini-meta-prompt-structured-outputs.ipynb) - Generate JSON schemas dynamically using meta prompts
- [Audio Transcription](examples/gemini-transcribe-with-timestamps.ipynb) - Transcribe audio with precise timestamps
- [Gemini MCP Example](examples/gemini-mcp-example.ipynb) - Example showcasing Model Context Protocol (MCP)
- [Gemini Analyze & Transcribe YouTube](examples/gemini-analyze-transcribe-youtube.ipynb) - Analyze and transcribe YouTube videos
- [Gemini Native Image Output](examples/gemini-native-image-out.ipynb) - Generate images directly with Gemini 2.0 Flash experimental model
- [Gemini File Editing](examples/gemini-file-editing.ipynb) - Example showcasing file editing capabilities
- [Gemini LangChain Integration](examples/gemini-langchain.ipynb) - Use Gemini models with LangChain
- [Gemini Code Executor Data Analysis](examples/gemini-code-executor-data-analysis.ipynb) - Example of data analysis using Gemini code execution
- [Gemini ADK MCP](examples/gemini-adk-mcp.ipynb) - Example using Gemini with ADK for MCP
- [Gemini PydanticAI Agent](examples/gemini-pydanticai-agent.ipynb) - Build agents using Gemini and PydanticAI
- [Gemini Context Caching](examples/gemini-context-caching.ipynb) - Example showcasing context caching and saving up to 75% on costs with Gemini
- [Gemini CrewAI](examples/gemini-crewai.ipynb) - Example showcasing CrewAI with Gemini 2.5 Pro Preview
- [Sequential Function Calling](examples/gemini-sequential-function-calling.ipynb) - Example showcasing sequential function calling with Gemini
- [Gemini Batch API](examples/gemini-batch-api.ipynb) - Example showcasing batch API with Gemini

## Scripts
- [Gemini Browser Use](scripts/gemini-browser-use.py) - Example script for using Gemini with browser interaction.
- [Gemini MCP Agent](scripts/gemini-mcp-agent.py) - A basic agent script demonstrating MCP.
- [Gemini MCP Pipedream](scripts/gemini-mcp-pipedream.py) - A basic agent script demonstrating MCP with Pipedream.
- [Gemini Veo3 Optimized Prompt](scripts/gemini-veo-meta.py) - A script using Gemini 2.5 to optimize prompts for Gemini Veo3.
- [Gemini Veo3 Vlogs](scripts/veo3-generate-viral-vlogs.py) - Automatic video generation with Gemini Veo3 combined multiple video clips.
- [Gemini Image Meta](scripts/gemini-image-meta.py) - Generate images with Gemini and Imagen.
- [Get Pipedream Token](scripts/get-pipedream-token.py) - Fetch OAuth access tokens for Pipedream MCP examples.
- [Environment Loader Test](scripts/test_env_loading.py) - Test script to verify environment variables are loaded correctly.

### JavaScript Examples

- [Gemini Native Image Output](javascript-examples/gemini-native-image-out.js) - Generate images directly with Gemini 2.0 Flash experimental model


### Gemma

- [Gemma with GenAI SDK](examples/gemma-with-genai-sdk.ipynb) - Use Gemma 3 27B It with Google's GenAI API
- [Gemma Function Calling](examples/gemma-function-calling.ipynb) - Implement function calling with Gemma 3 27B

## How to Use

1. **Clone the repository:**
    ```bash
    git clone https://github.com/philschmid/gemini-samples.git
    ```

2. **Set up environment variables:**
   Copy the sample environment file and configure your API keys:
   ```bash
   cp env.sample .env
   ```
   
       Edit `.env` and add your API keys:
    - **GEMINI_API_KEY** (Required): Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
    - **GOOGLE_API_KEY** (Required): Same as GEMINI_API_KEY, used in some LangChain examples
    - **PIPEDREAM_CLIENT_ID** (Optional): Get from [Pipedream API settings](https://pipedream.com/docs/rest-api/auth) for MCP examples
    - **PIPEDREAM_CLIENT_SECRET** (Optional): Get from [Pipedream API settings](https://pipedream.com/docs/rest-api/auth) for MCP examples
    - **PIPEDREAM_WORKSPACE_ID** (Optional): Your Pipedream workspace ID for reference

   **Note:** Never commit your actual `.env` file to version control!

3. **Explore the examples:** Browse the sample notebooks to find code related to different DeepMind models and experiments.

4. **Run and modify:** Experiment with the code, tweak parameters, and integrate the snippets into your own projects.

### API Key Usage Details

- **GEMINI_API_KEY**: Primary API key used throughout the project
  - Required for all Python examples in `/examples/`
  - Required for all guides in `/guides/`
  - Required for all scripts in `/scripts/`
  - Required for JavaScript examples in `/javascript-examples/`

- **GOOGLE_API_KEY**: Alternative name for the same Gemini API key
  - Used in some LangChain examples
  - Typically set to the same value as GEMINI_API_KEY

- **PIPEDREAM_CLIENT_ID, PIPEDREAM_CLIENT_SECRET, PIPEDREAM_WORKSPACE_ID**: Optional OAuth credentials for MCP (Model Context Protocol) examples
  - Used in `scripts/gemini-mcp-pipedream.py`
  - Use `scripts/get-pipedream-token.py` to fetch access tokens
  - Access tokens expire after 1 hour and need to be refreshed

**Important Notes:**
- Google Search integration is built into Gemini 2.0 Flash and doesn't require additional API keys
- For JavaScript examples, run with: `GEMINI_API_KEY=your_key npm run start`
- All Python examples automatically load environment variables from `.env`

### Pipedream OAuth Token Management

For Pipedream MCP examples, you'll need to use OAuth credentials instead of a simple API key:

1. **Set up OAuth credentials** in your `.env` file:
   ```
   PIPEDREAM_CLIENT_ID=your_client_id
   PIPEDREAM_CLIENT_SECRET=your_client_secret
   PIPEDREAM_WORKSPACE_ID=your_workspace_id
   ```

2. **Fetch access token** using the provided script:
   ```bash
   python scripts/get-pipedream-token.py
   ```

3. **Use the token** in your MCP examples (the script will show you how)

**Note:** Pipedream access tokens expire after 1 hour and need to be refreshed using the script.

## Contributing

Contributions are welcome! If you have additional examples or improvements, please feel free to open a pull request or create an issue.

## License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
