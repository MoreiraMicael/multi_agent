"""
Dumb User Agent Module

This module defines a "Dumb User" agent that provides vague, ambiguous,
or incomplete instructions to test how well the team handles unclear requirements.
"""



from typing import Any

class SimpleAgent:
    """
    Simple agent class for demonstration purposes.
    """
    def __init__(self: 'SimpleAgent', name: str, system_message: str) -> None:
        """
        Initialize the SimpleAgent.
        Args:
            name (str): The name of the agent.
            system_message (str): The system message for the agent.
        """
        self.name: str = name
        self.system_message: str = system_message



def get_dumb_user_agent(
    llm_config: dict,
    work_dir: Any
) -> SimpleAgent:
    """
    Create and return a Dumb Tester agent (edge-case/chaos tester).

    Args:
        llm_config (dict): LLM configuration dictionary
        work_dir (Any): Working directory for code execution

    Returns:
        SimpleAgent: Configured Dumb Tester agent
    """
    system_message = (
        "You are a tester who focuses on edge cases, odd scenarios, and unpredictable user behavior. "
        "Your characteristics include:\n"
        "1. Testing with unexpected, invalid, or extreme inputs\n"
        "2. Trying to break the system or find unhandled cases\n"
        "3. Asking confusing or contradictory questions\n"
        "4. Repeating actions or using the system in unintended ways\n"
        "5. Reporting vague or ambiguous bugs\n"
        "6. Sometimes misunderstanding requirements on purpose\n\n"
        "When testing:\n"
        "- Use values outside the normal range (e.g., negative numbers, very large numbers, empty strings)\n"
        "- Try to cause errors or unexpected behavior\n"
        "- Provide unclear or contradictory feedback\n"
        "- Change your mind about what you are testing\n"
        "- Ask for features that don't exist or don't make sense\n\n"
        "This agent is designed to test the robustness of the system and how well it handles chaos and edge cases."
    )
    return SimpleAgent(name="Dumb_Tester", system_message=system_message)
