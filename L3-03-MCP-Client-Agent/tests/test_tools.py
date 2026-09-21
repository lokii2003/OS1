"""
=============================================================
SIMPLE TESTS
=============================================================
Purpose:
    Basic tests for the calculator and chat history modules.

Run:
    pytest tests/test_tools.py -v
=============================================================
"""

import sys
import os

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from servers.calculator_server import safe_calculate
from chat_history import generate_title


# -----------------------------------------------
# Calculator Tests
# -----------------------------------------------

class TestSafeCalculator:
    """Test the safe calculator (no eval!)."""

    def test_addition(self):
        assert safe_calculate("2 + 3") == 5.0

    def test_subtraction(self):
        assert safe_calculate("10 - 4") == 6.0

    def test_multiplication(self):
        assert safe_calculate("5 * 6") == 30.0

    def test_division(self):
        assert safe_calculate("20 / 4") == 5.0

    def test_complex_expression(self):
        assert safe_calculate("25 * 8 + 10") == 210.0

    def test_parentheses(self):
        assert safe_calculate("(2 + 3) * 4") == 20.0

    def test_nested_parentheses(self):
        assert safe_calculate("((2 + 3) * (4 - 1))") == 15.0

    def test_decimal_numbers(self):
        result = safe_calculate("3.5 * 2")
        assert result == 7.0

    def test_division_by_zero(self):
        try:
            safe_calculate("10 / 0")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Division by zero" in str(e)

    def test_empty_expression(self):
        try:
            safe_calculate("")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_operator_precedence(self):
        # Multiplication before addition
        assert safe_calculate("2 + 3 * 4") == 14.0

    def test_single_number(self):
        assert safe_calculate("42") == 42.0


# -----------------------------------------------
# Chat Title Generation Tests
# -----------------------------------------------

class TestTitleGeneration:
    """Test the simple title generator."""

    def test_question_prefix_removal(self):
        title = generate_title("What is the weather in Pune?")
        assert "weather" in title.lower()
        assert not title.lower().startswith("what is the")

    def test_punctuation_removal(self):
        title = generate_title("Calculate 25 * 8?")
        assert not title.endswith("?")

    def test_capitalization(self):
        title = generate_title("hello world")
        assert title[0].isupper()

    def test_truncation(self):
        long_message = "x" * 100
        title = generate_title(long_message)
        assert len(title) <= 53  # 50 + "..."

    def test_empty_message(self):
        title = generate_title("")
        assert title == "New Chat"

    def test_simple_message(self):
        title = generate_title("Calculate 25 * 8 + 10")
        assert "Calculate" in title or "calculate" in title.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
