"""
Agent Registry Module

This module provides a registry and factory mechanism for creating agents
in the multi-agent system, supporting extensibility and centralized management.
"""

from typing import Dict, Any, Callable, Optional
from agents.base_agent import SimpleAgent
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Registry for managing agent creation functions and providing a factory interface.
    """
    
    def __init__(self) -> None:
        """Initialize the agent registry."""
        self._agents: Dict[str, Callable] = {}
    
    def register(self, name: str, factory_func: Callable) -> None:
        """
        Register an agent factory function.
        
        Args:
            name (str): Name of the agent type
            factory_func (Callable): Function that creates the agent
        """
        if name in self._agents:
            logger.warning(f"Overriding existing agent registration for '{name}'")
        self._agents[name] = factory_func
        logger.debug(f"Registered agent factory for '{name}'")
    
    def create_agent(
        self, 
        name: str, 
        llm_config: Dict[str, Any], 
        work_dir: str
    ) -> Optional[SimpleAgent]:
        """
        Create an agent by name using the registered factory function.
        
        Args:
            name (str): Name of the agent type to create
            llm_config (Dict[str, Any]): LLM configuration
            work_dir (str): Working directory path
            
        Returns:
            Optional[SimpleAgent]: Created agent instance or None if not found
        """
        if name not in self._agents:
            logger.error(f"No agent factory registered for '{name}'")
            return None
        
        try:
            agent = self._agents[name](llm_config, work_dir)
            logger.debug(f"Created agent '{name}': {agent.name}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent '{name}': {e}")
            return None
    
    def list_agents(self) -> list[str]:
        """
        Get a list of all registered agent types.
        
        Returns:
            list[str]: List of registered agent names
        """
        return list(self._agents.keys())
    
    def is_registered(self, name: str) -> bool:
        """
        Check if an agent type is registered.
        
        Args:
            name (str): Agent type name to check
            
        Returns:
            bool: True if registered, False otherwise
        """
        return name in self._agents


# Global registry instance
_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """
    Get the global agent registry instance.
    
    Returns:
        AgentRegistry: The global registry instance
    """
    return _registry


def register_agent(name: str, factory_func: Callable) -> None:
    """
    Register an agent factory function with the global registry.
    
    Args:
        name (str): Name of the agent type
        factory_func (Callable): Function that creates the agent
    """
    _registry.register(name, factory_func)


def create_agent(
    name: str, 
    llm_config: Dict[str, Any], 
    work_dir: str
) -> Optional[SimpleAgent]:
    """
    Create an agent using the global registry.
    
    Args:
        name (str): Name of the agent type to create
        llm_config (Dict[str, Any]): LLM configuration
        work_dir (str): Working directory path
        
    Returns:
        Optional[SimpleAgent]: Created agent instance or None if not found
    """
    return _registry.create_agent(name, llm_config, work_dir)


# Register default agents
def _register_default_agents() -> None:
    """Register all default agent types."""
    from agents.coder_agent import get_coder_agent
    from agents.reviewer_agent import get_reviewer_agent
    from agents.reviewer_agent2 import get_reviewer_agent2
    from agents.qa_agent import get_qa_agent
    from agents.user_agent import get_user_agent
    from agents.dumb_user_agent import get_dumb_user_agent
    
    register_agent("coder", get_coder_agent)
    register_agent("reviewer", get_reviewer_agent)
    register_agent("reviewer2", get_reviewer_agent2)
    register_agent("qa", get_qa_agent)
    register_agent("user", get_user_agent)
    register_agent("dumb_user", get_dumb_user_agent)


# Auto-register default agents when module is imported
_register_default_agents()