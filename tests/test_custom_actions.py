"""Unit tests for custom_actions.py."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from custom_actions import _validate_text_input, ValidationError


def test_validate_text_normal():
    assert _validate_text_input("hello world") == "hello world"

def test_validate_text_strips():
    assert _validate_text_input("  hi  ") == "hi"

def test_validate_text_empty():
    with pytest.raises(ValidationError):
        _validate_text_input("")

def test_validate_text_too_long():
    with pytest.raises(ValidationError):
        _validate_text_input("x" * 501)

def test_validate_text_wrong_type():
    with pytest.raises(ValidationError):
        _validate_text_input(123)
