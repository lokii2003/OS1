"""
=============================================================
CALCULATOR MCP SERVER
=============================================================
Purpose:
    This is an MCP server that provides one tool:
    1. calculate — Safely evaluates arithmetic expressions

Why we need it:
    Demonstrates a second MCP server. The agent discovers tools
    from MULTIPLE servers and routes requests to the right one.

How it connects:
    MCP Client (mcp_client.py) connects to this server via stdio.
    When the user asks "Calculate 25 * 8 + 10", Gemini selects
    this tool, and the MCP client calls it.

Safety:
    We do NOT use eval(). Instead, we use a simple parser
    that only allows: numbers, +, -, *, /, and parentheses.

Run:
    python servers/calculator_server.py
=============================================================
"""

import re
from mcp.server.mcpserver import MCPServer  # MCP SDK v2 server class

# --- Create the MCP server instance ---
mcp = MCPServer("CalculatorServer")


# -----------------------------------------------
# SAFE EXPRESSION PARSER
# -----------------------------------------------
# This replaces eval() with a safe alternative.
# It only understands: numbers, +, -, *, /, ( )
#
# How it works:
# 1. Tokenize the expression into numbers and operators
# 2. Parse using recursive descent (respects operator precedence)
#    - parse_expression: handles + and -
#    - parse_term: handles * and /
#    - parse_factor: handles numbers and parentheses
# -----------------------------------------------

def safe_calculate(expression: str) -> float:
    """Safely evaluate an arithmetic expression without using eval()."""

    # Step 1: Tokenize — split expression into numbers and operators
    tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', expression)

    if not tokens:
        raise ValueError("Empty expression")

    # Position tracker for the parser
    pos = [0]  # Using a list so inner functions can modify it

    def peek():
        """Look at the current token without consuming it."""
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume():
        """Get the current token and move to the next one."""
        token = tokens[pos[0]]
        pos[0] += 1
        return token

    def parse_expression():
        """Handle + and - (lowest precedence)."""
        result = parse_term()

        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                result += right
            else:
                result -= right

        return result

    def parse_term():
        """Handle * and / (higher precedence than + -)."""
        result = parse_factor()

        while peek() in ('*', '/'):
            op = consume()
            right = parse_factor()
            if op == '*':
                result *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right

        return result

    def parse_factor():
        """Handle numbers and parentheses (highest precedence)."""
        token = peek()

        if token == '(':
            consume()  # eat '('
            result = parse_expression()
            if peek() != ')':
                raise ValueError("Missing closing parenthesis")
            consume()  # eat ')'
            return result

        if token is None:
            raise ValueError("Unexpected end of expression")

        # Must be a number
        consume()
        try:
            return float(token)
        except ValueError:
            raise ValueError(f"Invalid token: {token}")

    # Parse the full expression
    result = parse_expression()

    # Make sure we consumed all tokens
    if pos[0] < len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos[0]]}")

    return result


# -----------------------------------------------
# TOOL: calculate
# -----------------------------------------------
@mcp.tool()
def calculate(expression: str) -> str:
    """Performs safe arithmetic calculation. Supports +, -, *, /, parentheses, and decimal numbers. Example: '25 * 8 + 10'"""
    try:
        # Validate: only allow safe characters
        if not re.match(r'^[\d\s+\-*/().]+$', expression):
            return f"Error: Expression contains invalid characters. Only numbers and + - * / ( ) are allowed."

        result = safe_calculate(expression)

        # Format nicely: show as integer if there's no decimal part
        if result == int(result):
            result_str = str(int(result))
        else:
            result_str = f"{result:.6f}".rstrip('0').rstrip('.')

        return f"Expression: {expression}\nResult: {result_str}"

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: Could not calculate '{expression}'. {str(e)}"


# --- Run the server ---
if __name__ == "__main__":
    mcp.run()
