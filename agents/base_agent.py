"""
Base Agent Module

This module defines the shared SimpleAgent class used by all agent modules
in the multi-agent system.
"""

from typing import Any


class SimpleAgent:
    """
    Simple agent class for demonstration purposes.
    
    This class serves as the base for all agents in the multi-agent system,
    providing a common interface with name and system message attributes.
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