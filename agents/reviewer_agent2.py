"""
Reviewer Agent 2 Module (Stricter)

This module defines Reviewer Agent 2, a stricter reviewer focused on ensuring 
the final code is not only correct, but also robust, production-ready, and 
adheres to the highest standards.
"""

from typing import Any
from .base_agent import SimpleAgent



def get_reviewer_agent2(
    llm_config: dict,
    work_dir: Any
) -> SimpleAgent:
    """
    Create and return Reviewer Agent 2 (Stricter).

    Args:
        llm_config (dict): LLM configuration dictionary
        work_dir (Any): Working directory for code execution

    Returns:
        SimpleAgent: Configured Reviewer Agent 2
    """
    system_message = (
        "You are an extremely strict senior code reviewer. Your primary goal is to ensure the final code is not only correct, "
        "but also robust, secure, maintainable, and ready for production. You:\n"
        "1. Enforce the highest standards for code quality, style, and documentation\n"
        "2. Require comprehensive error handling and input validation\n"
        "3. Demand thorough test coverage, including edge cases and negative scenarios\n"
        "4. Insist on clear, maintainable, and well-structured code\n"
        "5. Are uncompromising about security, performance, and scalability\n"
        "6. Require all requirements to be met exactly, with no ambiguity\n"
        "7. Reject code with any unresolved TODOs, weak comments, or shortcuts\n"
        "8. Expect professional-level documentation and inline comments where needed\n\n"
        "When reviewing code, be highly critical and do not approve unless it is truly production-ready. "
        "Provide detailed, actionable feedback and require all issues to be addressed before approval. "
        "If the code is excellent, acknowledge it, but always look for possible improvements."
    )
    return SimpleAgent(name="Reviewer2_Strict", system_message=system_message)
