"""
Configuration Module

This module contains all configuration settings for the multi-agent system,
including model settings, workspace paths, and LLM configuration.
"""

import os
import json
from typing import Dict, Any


# Model Configuration
MODEL_NAME = "llama3:8b"
MODEL_TEMPERATURE = 0.2
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

# Workspace Configuration
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
        print(
            f"Warning: Could not load config file. Using default configuration. Error: {e}"
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

    Returns:
        str: Absolute path to the workspace
    """
    return os.path.abspath(WORKSPACE_PATH)


def ensure_workspace_exists() -> None:
    """
    Ensure the workspace directory exists, create it if it doesn't.
    """
    workspace_path = get_workspace_path()
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        print(f"Created workspace directory: {workspace_path}")


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
