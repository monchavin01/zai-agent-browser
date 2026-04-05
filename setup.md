# Browser-use with Z.ai GLM Model Setup Guide

This guide explains how to configure and use the `browser-use` library with Z.ai's GLM (General Language Model) for browser automation tasks.

## Prerequisites

- Python 3.10 or higher
- Z.ai API key (obtain from [Z.ai platform](https://open.bigmodel.cn/))
- pip or conda package manager

## Installation

### 1. Install browser-use

```bash
pip install browser-use
```

### 2. Install additional dependencies

```bash
pip install aiohttp aiofiles
```

## Configuration

### 1. Set up your Z.ai API key

Export your API key as an environment variable:

```bash
export ZAI_API_KEY="your-api-key-here"
```

Or set it in your Python code:

```python
import os
os.environ["ZAI_API_KEY"] = "your-api-key-here"
```

### 2. Configure the GLM model

Z.ai offers several GLM models. The recommended model for browser automation is `glm-4-flash` or `glm-4-air`.

## Basic Usage Example

```python
import asyncio
import os
from browser_use import Agent, Controller
from langchain_core.messages import HumanMessage

# Set API key
os.environ["ZAI_API_KEY"] = "your-api-key-here"

# Configure the GLM model
from langchain_community.llms import ZhipuAI

llm = ZhipuAI(
    model="glm-4-flash",  # or "glm-4-air", "glm-4"
    temperature=0.1,
)

async def main():
    # Create a simple browser agent
    agent = Agent(
        task="Search for 'browser automation' on Google and find the first result",
        llm=llm,
    )

    # Run the agent
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Configuration

### Custom Controller with Actions

```python
from browser_use import Agent, Controller
from browser_use.controller.registry import Action
from langchain_community.llms import ZhipuAI

controller = Controller()

@controller.action("Custom action description")
async def custom_action(browser, text: str):
    """Your custom action logic here"""
    page = browser.get_current_page()
    await page.evaluate(f"console.log('{text}')")
    return "Action completed"

llm = ZhipuAI(model="glm-4-flash")

agent = Agent(
    task="Your task here",
    llm=llm,
    controller=controller,
)
```

### Model Parameters

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| `model` | GLM model variant | `glm-4-flash` (fast), `glm-4` (best) |
| `temperature` | Creativity/randomness | `0.1` (deterministic) |
| `max_tokens` | Maximum response tokens | `2000` |

```python
llm = ZhipuAI(
    model="glm-4",
    temperature=0.1,
    max_tokens=2000,
)
```

## Troubleshooting

### API Key Issues

- Ensure your API key is correctly set
- Check that your API key has not expired
- Verify you have sufficient quota

### Model Not Found

- Verify the model name is correct
- Check Z.ai documentation for available models
- Ensure your API key has access to the requested model

### Browser Automation Issues

- Make sure a compatible browser is installed
- Run with appropriate permissions
- Check for browser popup blockers

## Model Comparison

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `glm-4-flash` | Fastest | Good | Quick tasks, simple navigation |
| `glm-4-air` | Fast | Better | General browser automation |
| `glm-4` | Slower | Best | Complex tasks requiring reasoning |

## Resources

- [browser-use Documentation](https://github.com/browser-use/browser-use)
- [Z.ai API Documentation](https://open.bigmodel.cn/dev/api)
- [GLM Model Documentation](https://open.bigmodel.cn/)
