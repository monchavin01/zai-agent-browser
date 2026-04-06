# Browser Agent

A secure browser automation tool powered by browser-use and ZhipuAI (Z.ai) for executing web tasks autonomously.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- A Z.ai API key (get one at https://open.bigmodel.cn/)

## Installation

1. Clone or navigate to the project directory:
   ```bash
   cd /path/to/zai-agent-browser
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   # .venv\Scripts\activate         # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your API key:
   ```
   ZAI_API_KEY=your-actual-api-key-here
   ```

3. (Optional) Customize other settings as needed.

## Usage

> Always activate the virtual environment before running:
> ```bash
> source .venv/bin/activate    # macOS/Linux
> # .venv\Scripts\activate     # Windows
> ```

**Run with a task argument:**
```bash
python browser_agent.py "Search for Python tutorials and open the first result"
```

**Run interactively:**
```bash
python browser_agent.py
# Then enter your task when prompted
```

**Watch Chrome interact in real-time (visible browser window):**
```bash
HEADLESS=false python browser_agent.py "Search for Python tutorials"
```
Or set it permanently in `.env`:
```
HEADLESS=false
```

**Deactivate when done:**
```bash
deactivate
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ZAI_API_KEY` | *required* | Your Z.ai API key from https://open.bigmodel.cn/ |
| `MODEL_NAME` | `glm-4.5-air` | LLM model to use. Options: `glm-4.5-air`, `glm-4.5`, `glm-4.6`, `glm-4.7`, `glm-5`, `glm-5-tbo`, `glm-5.1`, `glm-4v-flash`, `glm-4v` |
| `HEADLESS` | `true` | Browser mode: `true` = no window, `false` = visible browser |
| `ENABLE_VISION` | `false` | Enable screenshot mode (requires vision-capable model like `glm-4v-flash`) |
| `TEMPERATURE` | `0.1` | Creativity level: `0.0` = deterministic, `1.0` = creative |
| `MAX_ACTIONS_PER_STEP` | `10` | Max actions per agent step |
| `MAX_STEPS` | `20` | Max steps for agent execution |
| `ALLOWED_DOMAINS` | *empty* | Comma-separated list of allowed domains (empty = no restriction) |
| `MAX_VISITS_PER_DOMAIN` | `5` | Max times agent can visit the same domain (loop guard) |

## Custom Actions

Custom actions are defined in `custom_actions.py` and can be extended by adding new async functions. The available actions are:

- **`log_to_console`** - Log text to the browser console (with input validation)
- **`screenshot`** - Take a screenshot and save to `/tmp` (with path security)
- **`get_page_info`** - Get page title, URL, and viewport dimensions

### Adding a New Action

1. Create an async function that accepts a `page` parameter (Playwright page object)
2. Add input validation for any user-provided data
3. Return a dict with `success`, `action`, and optional `error` keys
4. Register it in the `CONTROLLER` mapping:

```python
async def my_custom_action(page, arg1: str) -> dict[str, Any]:
    # Your implementation here
    return {"success": True, "action": "my_custom_action"}

CONTROLLER = {
    "my_custom_action": my_custom_action,
    # ... existing actions
}
```

## Security Notes

- **Never commit `.env`** - The `.env` file is already listed in `.gitignore`, but double-check before pushing
- **API key rotation** - Rotate your Z.ai API key periodically and if you suspect it has been exposed
- **Input validation** - All custom actions include input validation to prevent injection attacks
- **Screenshot paths** - Screenshots are restricted to `/tmp` directory to prevent path traversal attacks

## Troubleshooting

| Error | Solution |
|-------|----------|
| `command not found: python3` | Install Python 3.10+ from https://python.org |
| venv not activated (wrong pip/python) | Run `source .venv/bin/activate` before any command |
| `Missing required environment variable: ZAI_API_KEY` | Ensure `.env` exists and `ZAI_API_KEY` is set |
| `ImportError: cannot import name 'ZhipuAI'` | Run `pip install -r requirements.txt` (now uses `langchain-openai`) |
| `No module named 'browser_use'` | Run `pip install -r requirements.txt` |
| `Executable not found` (Playwright) | Run `playwright install chromium` |
| `Error code: 400 / code 1210` | Vision mode is on but model doesn't support it. Set `ENABLE_VISION=false` or switch to `glm-4v-flash` |
| Task validation error | Ensure task is a non-empty string under 1000 characters |
| Screenshot path error | Screenshots must be saved to `/tmp` directory only |

## Project Structure

```
zai-agent-browser/
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
├── browser_agent.py      # Main entry point
├── custom_actions.py     # Custom browser actions
└── README.md             # This file
```
