"""
Main entry point for the Multi-Agent Python Development System.
"""

import logging
import os

# Import orchestrator (using the refactored version)
from orchestrator_refactored import AgentOrchestrator
from scenarios import scenarios

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to run the multi-agent system."""
    print("=== Multi-Agent Python Development System ===")
    print()
    print("Available scenarios:")
    for key, scenario in scenarios.items():
        print(f"{key}. {scenario['description']}")
    print("\nSelect a scenario (1-5) or press Enter for scenario 1:")

    # Skip input if running in agent/automated mode
    automation_mode = os.environ.get("AGENT_AUTOMATION_MODE", "0")
    if automation_mode == "1":
        choice = "1"
        print("[Automation mode: Skipping input, using scenario 1]")
    else:
        choice = input().strip() or "1"

    if choice in scenarios:
        scenario = scenarios[choice]
        print(f"\nRunning scenario: {scenario['description']}")
        print()

        try:
            # Use the refactored orchestrator
            orchestrator = AgentOrchestrator()
            result = orchestrator.run_conversation(scenario)

            if result:
                print(f"\n✅ Success! Generated code saved to: {result}")
            else:
                print("\n❌ Failed to generate code.")

        except Exception as e:
            logger.error(f"Error during execution: {e}")
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice. Using default scenario 1.")
        scenario = scenarios["1"]
        orchestrator = AgentOrchestrator()
        result = orchestrator.run_conversation(scenario)
        if result:
            print(f"\n✅ Success! Generated code saved to: {result}")


if __name__ == "__main__":
    main()
