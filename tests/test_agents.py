"""
Test Suite for Multi-Agent System

This module contains pytest-based tests for all agents in the multi-agent system
to ensure they can be created and configured properly.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agent creation functions
from agents.coder_agent import get_coder_agent
from agents.reviewer_agent import get_reviewer_agent
from agents.qa_agent import get_qa_agent
from agents.user_agent import get_user_agent
from agents.dumb_user_agent import get_dumb_user_agent
from agents.base_agent import SimpleAgent

# Import configuration functions
from config import get_llm_config, get_workspace_path, ensure_workspace_exists


@pytest.fixture
def mock_llm_config():
    """Fixture providing a mock LLM configuration for testing."""
    return {
        "config_list": [
            {
                "model": "test-model",
                "base_url": "http://localhost:11434/v1",
                "api_key": "test-key",
                "price": [0, 0],
            }
        ],
        "temperature": 0.7,
        "cache_seed": 42,
        "timeout": 120,
    }


@pytest.fixture
def temp_work_dir():
    """Fixture providing a temporary work directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestAgentRegistry:
    """Test class for agent registry functionality."""

    def test_agent_registry_creation(self):
        """Test that agent registry can be created and used."""
        from agents.registry import AgentRegistry
        
        registry = AgentRegistry()
        assert registry.list_agents() == []
        
    def test_agent_registration_and_creation(self, mock_llm_config, temp_work_dir):
        """Test registering and creating agents through registry."""
        from agents.registry import AgentRegistry, get_agent_registry
        from agents.coder_agent import get_coder_agent
        
        registry = AgentRegistry()
        registry.register("test_coder", get_coder_agent)
        
        agent = registry.create_agent("test_coder", mock_llm_config, temp_work_dir)
        assert agent is not None
        assert agent.name == "Coder"
        
    def test_global_registry_has_default_agents(self):
        """Test that global registry has default agents registered."""
        from agents.registry import get_agent_registry
        
        registry = get_agent_registry()
        agents = registry.list_agents()
        
        expected_agents = ["coder", "reviewer", "reviewer2", "qa", "user", "dumb_user"]
        for agent_name in expected_agents:
            assert agent_name in agents

    def test_global_registry_can_create_agents(self, mock_llm_config, temp_work_dir):
        """Test that global registry can create default agents."""
        from agents.registry import create_agent
        
        agent = create_agent("coder", mock_llm_config, temp_work_dir)
        assert agent is not None
        assert agent.name == "Coder"


class TestEnvironmentVariables:
    """Test class for environment variable functionality."""

    def test_workspace_path_environment_override(self):
        """Test that MULTI_AGENT_WORKSPACE_PATH can override workspace path."""
        import os
        import tempfile
        from config import get_workspace_path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable
            original_value = os.environ.get('MULTI_AGENT_WORKSPACE_PATH')
            os.environ['MULTI_AGENT_WORKSPACE_PATH'] = temp_dir
            
            try:
                workspace_path = get_workspace_path()
                assert workspace_path == os.path.abspath(temp_dir)
            finally:
                # Restore original environment
                if original_value is not None:
                    os.environ['MULTI_AGENT_WORKSPACE_PATH'] = original_value
                else:
                    os.environ.pop('MULTI_AGENT_WORKSPACE_PATH', None)


class TestBaseAgent:
    """Test class for the base SimpleAgent class."""

    def test_simple_agent_creation(self):
        """Test that SimpleAgent can be created with name and system message."""
        agent = SimpleAgent("TestAgent", "Test system message")
        
        assert agent.name == "TestAgent"
        assert agent.system_message == "Test system message"
        
    def test_simple_agent_import(self):
        """Test that SimpleAgent can be imported from base_agent module."""
        from agents.base_agent import SimpleAgent as ImportedAgent
        
        agent = ImportedAgent("ImportTest", "Import test message")
        assert agent.name == "ImportTest"
        assert agent.system_message == "Import test message"


class TestAgentCreation:
    """Test class for agent creation functions."""

    def test_get_coder_agent(self, mock_llm_config, temp_work_dir):
        """Test that the coder agent can be created successfully."""
        agent = get_coder_agent(mock_llm_config, temp_work_dir)

        assert agent is not None
        assert agent.name == "Coder"
        assert "expert Python coder" in agent.system_message

    def test_get_reviewer_agent(self, mock_llm_config, temp_work_dir):
        """Test that the reviewer agent can be created successfully."""
        agent = get_reviewer_agent(mock_llm_config, temp_work_dir)

        assert agent is not None
        assert agent.name == "Reviewer"
        assert "code reviewer" in agent.system_message

    def test_get_qa_agent(self, mock_llm_config, temp_work_dir):
        """Test that the QA agent can be created successfully."""
        agent = get_qa_agent(mock_llm_config, temp_work_dir)

        assert agent is not None
        assert agent.name == "QA_Specialist"
        assert "Quality Assurance" in agent.system_message

    def test_get_user_agent(self, mock_llm_config, temp_work_dir):
        """Test that the user agent can be created successfully."""
        agent = get_user_agent(mock_llm_config, temp_work_dir)

        assert agent is not None
        assert agent.name == "User"
        assert "knowledgeable user" in agent.system_message

    def test_get_dumb_user_agent(self, mock_llm_config, temp_work_dir):
        """Test that the dumb user agent can be created successfully."""
        agent = get_dumb_user_agent(mock_llm_config, temp_work_dir)

        assert agent is not None
        assert agent.name == "Dumb_User"
        assert "vague or ambiguous" in agent.system_message


class TestConfiguration:
    """Test class for configuration functions."""

    def test_get_llm_config_structure(self):
        """Test that get_llm_config returns a properly structured configuration."""
        config = get_llm_config()

        assert isinstance(config, dict)
        assert "config_list" in config
        assert "temperature" in config
        assert "cache_seed" in config
        assert "timeout" in config

        assert isinstance(config["config_list"], list)
        assert len(config["config_list"]) > 0

        # Check first config item structure
        first_config = config["config_list"][0]
        assert "model" in first_config
        assert "base_url" in first_config
        assert "api_key" in first_config

    def test_get_workspace_path(self):
        """Test that get_workspace_path returns a valid path."""
        workspace_path = get_workspace_path()

        assert isinstance(workspace_path, str)
        assert len(workspace_path) > 0
        assert os.path.isabs(workspace_path)  # Should be absolute path

    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_ensure_workspace_exists_creates_directory(
        self, mock_exists, mock_makedirs
    ):
        """Test that ensure_workspace_exists creates directory when it doesn't exist."""
        mock_exists.return_value = False

        ensure_workspace_exists()

        mock_makedirs.assert_called_once()

    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_ensure_workspace_exists_skips_existing_directory(
        self, mock_exists, mock_makedirs
    ):
        """Test that ensure_workspace_exists doesn't create directory when it exists."""
        mock_exists.return_value = True

        ensure_workspace_exists()

        mock_makedirs.assert_not_called()


class TestSystemIntegration:
    """Test class for system integration scenarios."""

    def test_all_agents_can_be_created_together(self, mock_llm_config, temp_work_dir):
        """Test that all agents can be created together without conflicts."""
        agents = []

        # Create all agents
        agents.append(get_coder_agent(mock_llm_config, temp_work_dir))
        agents.append(get_reviewer_agent(mock_llm_config, temp_work_dir))
        agents.append(get_qa_agent(mock_llm_config, temp_work_dir))
        agents.append(get_user_agent(mock_llm_config, temp_work_dir))
        agents.append(get_dumb_user_agent(mock_llm_config, temp_work_dir))

        # Verify all agents were created
        assert len(agents) == 5
        assert all(agent is not None for agent in agents)

        # Verify unique names
        names = [agent.name for agent in agents]
        assert len(set(names)) == len(names)  # All names should be unique

    def test_agent_system_messages_are_different(self, mock_llm_config, temp_work_dir):
        """Test that each agent has a unique system message."""
        agents = [
            get_coder_agent(mock_llm_config, temp_work_dir),
            get_reviewer_agent(mock_llm_config, temp_work_dir),
            get_qa_agent(mock_llm_config, temp_work_dir),
            get_user_agent(mock_llm_config, temp_work_dir),
            get_dumb_user_agent(mock_llm_config, temp_work_dir),
        ]

        system_messages = [agent.system_message for agent in agents]

        # Check that all system messages are different
        assert len(set(system_messages)) == len(system_messages)

        # Check that each message contains role-specific keywords
        assert any("coder" in msg.lower() for msg in system_messages)
        assert any("reviewer" in msg.lower() for msg in system_messages)
        assert any("quality assurance" in msg.lower() for msg in system_messages)
        assert any("user" in msg.lower() for msg in system_messages)
        assert any("vague" in msg.lower() for msg in system_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
