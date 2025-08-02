"""
Configuration Module

This module contains all configuration settings for the multi-agent system,
including model settings, workspace paths, and LLM configuration.
"""

import os
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Model Configuration
MODEL_NAME = "llama3:8b"
MODEL_TEMPERATURE = 0.2
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# Workspace Configuration
# Can be overridden with MULTI_AGENT_WORKSPACE_PATH environment variable
WORKSPACE_PATH = os.path.join(os.path.dirname(__file__), "coding_workspace")
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "OAI_CONFIG_LIST")

# Chat Configuration
MAX_ROUND = 10
SPEAKER_SELECTION_METHOD = "auto"


def get_llm_config() -> Dict[str, Any]:
    """
    Get the LLM configuration dictionary for AutoGen agents.

    Returns:
        dict: LLM configuration with model settings
    """
    try:
        # Try to load from OAI_CONFIG_LIST file if it exists
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r") as f:
                config_list = json.load(f)

            llm_config = {
                "config_list": config_list,
                "temperature": MODEL_TEMPERATURE,
                "cache_seed": 42,  # For reproducible results
                "timeout": 120,
            }
        else:
            # Fallback to default configuration
            llm_config = {
                "config_list": [
                    {
                        "model": MODEL_NAME,
                        "base_url": BASE_URL,
                        "api_key": API_KEY,
                        "price": [0, 0],
                    }
                ],
                "temperature": MODEL_TEMPERATURE,
                "cache_seed": 42,
                "timeout": 120,
            }

    except Exception as e:
        logger.warning(
            f"Could not load config file. Using default configuration. Error: {e}"
        )
        # Fallback configuration
        llm_config = {
            "config_list": [
                {
                    "model": MODEL_NAME,
                    "base_url": BASE_URL,
                    "api_key": API_KEY,
                    "price": [0, 0],
                }
            ],
            "temperature": MODEL_TEMPERATURE,
            "cache_seed": 42,
            "timeout": 120,
        }

    return llm_config


def get_workspace_path() -> str:
    """
    Get the absolute path to the coding workspace directory.
    
    Can be overridden by setting the MULTI_AGENT_WORKSPACE_PATH environment variable.

    Returns:
        str: Absolute path to the workspace
    """
    workspace_path = os.environ.get('MULTI_AGENT_WORKSPACE_PATH', WORKSPACE_PATH)
    return os.path.abspath(workspace_path)


def ensure_workspace_exists() -> None:
    """
    Ensure the workspace directory exists, create it if it doesn't.
    """
    workspace_path = get_workspace_path()
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        logger.info(f"Created workspace directory: {workspace_path}")


def get_chat_config() -> Dict[str, Any]:
    """
    Get configuration for the group chat.

    Returns:
        dict: Chat configuration parameters
    """
    return {
        "max_round": MAX_ROUND,
        "speaker_selection_method": SPEAKER_SELECTION_METHOD,
    }
