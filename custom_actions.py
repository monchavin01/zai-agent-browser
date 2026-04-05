"""
Custom Actions - Secure, validated actions for browser automation.
All actions include input validation and error handling.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


# Constants for security
_MAX_TEXT_LENGTH = 500
_ALLOWED_SCREENSHOT_DIR = "/tmp"


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def _validate_text_input(text: Any, max_length: int = _MAX_TEXT_LENGTH) -> str:
    """
    Validate text input.

    Args:
        text: The input to validate
        max_length: Maximum allowed length

    Returns:
        The validated and sanitized string

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(text, str):
        raise ValidationError(f"Input must be a string, got {type(text).__name__}")

    # Strip leading/trailing whitespace
    text = text.strip()

    if not text:
        raise ValidationError("Input cannot be empty or whitespace only")

    if len(text) > max_length:
        raise ValidationError(
            f"Input too long (max {max_length} chars, got {len(text)})"
        )

    return text


def _validate_screenshot_path(path: Any) -> Path:
    """
    Validate screenshot path is within allowed directory.

    Args:
        path: The path to validate

    Returns:
        The validated Path object

    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(path, (str, Path)):
        raise ValidationError(f"Path must be a string or Path, got {type(path).__name__}")

    path_obj = Path(path).resolve()

    # Ensure the path is within the allowed directory
    try:
        allowed_dir = Path(_ALLOWED_SCREENSHOT_DIR).resolve()
        path_obj.relative_to(allowed_dir)
    except ValueError:
        raise ValidationError(
            f"Screenshot path must be within {_ALLOWED_SCREENSHOT_DIR}, got {path}"
        )

    # Ensure parent directory exists or can be created
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    return path_obj


async def log_to_console(page, text: Any) -> dict[str, Any]:
    """
    Safely log text to the browser console.
    Uses json.dumps to prevent JavaScript injection.

    Args:
        page: The Playwright page object
        text: The text to log (will be validated)

    Returns:
        Result dict with success/error info
    """
    try:
        # Validate input
        validated_text = _validate_text_input(text)

        # Use json.dumps to safely escape the text for JavaScript
        # This prevents injection attacks vs using f-strings
        js_text = json.dumps(validated_text)

        # Execute safely - the text is passed as a JSON-encoded string literal
        result = await page.evaluate(f"console.log({js_text})")

        return {
            "success": True,
            "action": "log_to_console",
            "text_length": len(validated_text),
        }

    except ValidationError as e:
        return {
            "success": False,
            "action": "log_to_console",
            "error": f"Validation error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "action": "log_to_console",
            "error": f"Execution error: {e}",
        }


async def take_screenshot(
    page,
    filename: Optional[Any] = None,
    full_page: bool = False
) -> dict[str, Any]:
    """
    Take a screenshot and save it to a secure local path.

    Args:
        page: The Playwright page object
        filename: Optional custom filename (must be just a filename, no path)
        full_page: Whether to capture the full page

    Returns:
        Result dict with success/error info and file path
    """
    try:
        # Validate filename if provided
        if filename is None:
            # Generate safe default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        else:
            filename = _validate_text_input(filename, max_length=100)

            # Ensure it's just a filename, not a path
            if "/" in filename or "\\" in filename:
                raise ValidationError("Filename must not contain path separators")

        # Build the full path within the allowed directory
        file_path = _validate_screenshot_path(f"{_ALLOWED_SCREENSHOT_DIR}/{filename}")

        # Take the screenshot
        await page.screenshot(path=str(file_path), full_page=full_page)

        return {
            "success": True,
            "action": "screenshot",
            "path": str(file_path),
            "full_page": full_page,
        }

    except ValidationError as e:
        return {
            "success": False,
            "action": "screenshot",
            "error": f"Validation error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "action": "screenshot",
            "error": f"Execution error: {e}",
        }


async def get_page_info(page) -> dict[str, Any]:
    """
    Get safe information about the current page.
    Returns only non-sensitive metadata.

    Args:
        page: The Playwright page object

    Returns:
        Result dict with page information
    """
    try:
        info = await page.evaluate("""() => ({
            title: document.title,
            url: window.location.href,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight
        })""")

        return {
            "success": True,
            "action": "get_page_info",
            "info": info,
        }

    except Exception as e:
        return {
            "success": False,
            "action": "get_page_info",
            "error": f"Execution error: {e}",
        }


# Controller mapping for action registration
CONTROLLER = {
    "log_to_console": log_to_console,
    "screenshot": take_screenshot,
    "get_page_info": get_page_info,
}


async def execute_action(page, action_name: str, *args, **kwargs) -> dict[str, Any]:
    """
    Execute a custom action by name.

    Args:
        page: The Playwright page object
        action_name: Name of the action to execute
        *args: Positional arguments to pass to the action
        **kwargs: Keyword arguments to pass to the action

    Returns:
        Result dict from the action execution
    """
    action_func = CONTROLLER.get(action_name)

    if action_func is None:
        return {
            "success": False,
            "action": action_name,
            "error": f"Unknown action: {action_name}",
        }

    return await action_func(page, *args, **kwargs)
