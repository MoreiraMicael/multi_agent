"""
Reviewer Agent Module

This module defines the Reviewer agent responsible for reviewing code
written by the Coder agent and providing feedback and suggestions.
"""

from typing import Any
from .base_agent import SimpleAgent



def get_reviewer_agent(
    llm_config: dict,
    work_dir: Any
) -> SimpleAgent:
    """
    Create and return a Reviewer agent.

    Args:
        llm_config (dict): LLM configuration dictionary
        work_dir (Any): Working directory for code execution

    Returns:
        SimpleAgent: Configured Reviewer agent
    """
    system_message = (
        "You are a senior code reviewer with expertise in Python development. Your responsibilities include:\n"
        "1. Reviewing code for correctness, efficiency, and maintainability\n"
        "2. Checking adherence to Python best practices and PEP 8 standards\n"
        "3. Identifying potential bugs, security issues, and performance problems\n"
        "4. Suggesting improvements for code structure and design patterns\n"
        "5. Ensuring code is properly documented and tested\n"
        "6. Verifying that requirements are met accurately\n\n"
        "When reviewing code, focus on:\n"
        "- Code correctness and logic\n"
        "- Performance and efficiency\n"
        "- Security considerations\n"
        "- Maintainability and readability\n"
        "- Error handling and edge cases\n"
        "- Documentation quality\n"
        "- Test coverage and testability\n"
        "- Adherence to coding standards\n\n"
        "Provide constructive feedback with specific suggestions for improvement.\n"
        "If the code is good, acknowledge it and suggest any minor enhancements."
    )
    return SimpleAgent(name="Reviewer", system_message=system_message)
