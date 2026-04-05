"""
Browser Agent - Main entry point for browser automation tasks.
Loads configuration from environment variables and runs browser tasks securely.
"""

import asyncio
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from browser_use import Agent, BrowserConfig
from langchain_community.llms import ZhipuAI

# Load environment variables at module import
load_dotenv()


def _get_required_env(key: str) -> str:
    """Get a required environment variable or raise a clear error."""
    value = os.getenv(key)
    if not value:
        raise ValueError(
            f"Missing required environment variable: {key}. "
            f"Please set it in your .env file or environment."
        )
    return value


def _get_env_with_default(key: str, default: str) -> str:
    """Get an environment variable with a default value."""
    return os.getenv(key, default)


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get a boolean environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def _validate_task(task: str) -> str:
    """
    Validate the task input.

    Args:
        task: The task string to validate

    Returns:
        The validated and sanitized task string

    Raises:
        ValueError: If task is invalid
    """
    if not task:
        raise ValueError("Task cannot be empty")

    if not isinstance(task, str):
        raise ValueError(f"Task must be a string, got {type(task).__name__}")

    # Strip leading/trailing whitespace
    task = task.strip()

    if not task:
        raise ValueError("Task cannot be empty or whitespace only")

    if len(task) > 1000:
        raise ValueError(f"Task too long (max 1000 chars, got {len(task)})")

    return task


def _create_llm() -> ZhipuAI:
    """
    Create and configure the ZhipuAI LLM instance.

    Returns:
        Configured ZhipuAI instance

    Raises:
        ValueError: If required environment variables are missing
    """
    api_key = _get_required_env("ZAI_API_KEY")
    model_name = _get_env_with_default("MODEL_NAME", "glm-4-flash")
    temperature = float(_get_env_with_default("TEMPERATURE", "0.1"))
    max_tokens = int(_get_env_with_default("MAX_TOKENS", "2000"))

    return ZhipuAI(
        zhipuai_api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )


async def run_agent(task: str) -> None:
    """
    Run the browser agent with the given task.

    Args:
        task: The task description for the agent to execute

    Raises:
        ValueError: If task validation fails or env vars are missing
        Exception: For other runtime errors during agent execution
    """
    # Validate the task first
    validated_task = _validate_task(task)

    # Get configuration
    headless = _get_env_bool("HEADLESS", True)

    try:
        # Create LLM
        llm = _create_llm()

        # Create and run agent
        agent = Agent(
            task=validated_task,
            llm=llm,
            browser_config=BrowserConfig(headless=headless),
        )

        result = await agent.run()
        print(f"Task completed: {result}")

    except ValueError as e:
        # Re-raise validation errors with context
        raise ValueError(f"Configuration error: {e}") from e
    except Exception as e:
        # Wrap other exceptions with context
        raise RuntimeError(f"Agent execution failed: {e}") from e


def _get_task_from_args() -> Optional[str]:
    """Get task from command line arguments if provided."""
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return None


def _prompt_for_task() -> str:
    """Prompt the user for a task description."""
    try:
        return input("Enter task description: ")
    except (EOFError, KeyboardInterrupt):
        print("\nNo task provided. Exiting.")
        sys.exit(0)


async def main() -> None:
    """Main entry point."""
    # Try to get task from args, otherwise prompt
    task = _get_task_from_args()
    if not task:
        task = _prompt_for_task()

    try:
        await run_agent(task)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
