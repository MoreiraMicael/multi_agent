"""
Coder Agent Module

This module defines the Coder agent responsible for writing Python code
based on requirements and instructions from other agents.
"""

from typing import Any
from .base_agent import SimpleAgent



def get_coder_agent(
    llm_config: dict,
    work_dir: Any
) -> SimpleAgent:
    """
    Create and return a Coder agent.

    Args:
        llm_config (dict): LLM configuration dictionary
        work_dir (Any): Working directory for code execution

    Returns:
        SimpleAgent: Configured Coder agent
    """
    system_message = (
        "You are an expert Python coder. Your responsibilities include:\n"
        "1. Writing clean, efficient, and well-documented Python code\n"
        "2. Following Python best practices (PEP 8, type hints, docstring)\n"
        "3. Creating modular and maintainable code\n"
        "4. Implementing requested features accurately\n"
        "5. Handling edge cases and error conditions\n"
        "6. Writing code that is testable and follows SOLID principles\n\n"
        "When writing code:\n"
        "- Use descriptive variable and function names\n"
        "- Include comprehensive docstring\n"
        "- Add type hints where appropriate\n"
        "- Handle exceptions gracefully\n"
        "- Write code that is easy to understand and maintain\n"
        "- Follow the DRY (Don't Repeat Yourself) principle\n\n"
        "Always execute your code to verify it works correctly before presenting the final solution."
    )
    return SimpleAgent(name="Coder", system_message=system_message)
