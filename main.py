"""
Main entry point for the Multi-Agent Python Development System.
"""

import os
import re
import textwrap
from typing import List, Optional, Dict, Any

# Import agent creation functions
from agents.coder_agent import get_coder_agent
from agents.reviewer_agent import get_reviewer_agent
from agents.reviewer_agent2 import get_reviewer_agent2
from agents.qa_agent import get_qa_agent
from agents.user_agent import get_user_agent
from agents.dumb_user_agent import get_dumb_user_agent
from agents.improvement_agent import ImprovementAgent  # New agent

# Import configuration
from config import (
    get_llm_config,
    get_workspace_path,
    ensure_workspace_exists,
    get_chat_config,
)

from orchestrator import simulate_agent_conversation
from scenarios import scenarios

def main():
    print("=== Multi-Agent Python Development System ===")
    print()
    print("Available scenarios:")
    for key, scenario in scenarios.items():
        print(f"{key}. {scenario['description']}")
    print("\nSelect a scenario (1-5) or press Enter for scenario 1:")
    # Skip input if running in agent/automated mode
    if os.environ.get("AGENT_AUTOMATION_MODE", "0") == "1":
        choice = "1"
        print("[Automation mode: Skipping input, using scenario 1]")
    else:
        choice = input().strip() or "1"
    if choice in scenarios:
        scenario = scenarios[choice]
        print(f"\nRunning scenario: {scenario['description']}")
        print()
        result = simulate_agent_conversation(scenario)
        if result:
            print(f"\n✅ Success! Generated code saved to: {result}")
        else:
            print("\n❌ Failed to generate code.")
    else:
        print("Invalid choice. Using default scenario 1.")

if __name__ == "__main__":
    main()
