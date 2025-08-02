"""
User Agent Module

This module defines the User agent that provides clear, detailed instructions
and requirements for the development team.
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



def get_user_agent(
    llm_config: dict,
    work_dir: Any
) -> SimpleAgent:
    """
    Create and return a User agent.

    Args:
        llm_config (dict): LLM configuration dictionary
        work_dir (Any): Working directory for code execution

    Returns:
        SimpleAgent: Configured User agent
    """
    system_message = (
        "You are a knowledgeable user who provides clear, detailed requirements and feedback. "
        "Your responsibilities include:\n"
        "1. Defining clear and specific requirements\n"
        "2. Providing detailed instructions and context\n"
        "3. Answering questions about functionality and expectations\n"
        "4. Reviewing proposed solutions and providing feedback\n"
        "5. Ensuring the final solution meets your needs\n"
        "6. Clarifying ambiguous requirements when asked\n\n"
        "When providing requirements:\n"
        "- Be specific about what you want the code to do\n"
        "- Include examples and use cases\n"
        "- Specify input/output formats\n"
        "- Mention any constraints or limitations\n"
        "- Provide context about the intended use\n"
        "- Be available to clarify details when needed\n\n"
        "You have technical knowledge and can engage in meaningful discussions about implementation approaches."
    )
    return SimpleAgent(name="User", system_message=system_message)
