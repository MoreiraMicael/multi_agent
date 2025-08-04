"""
Refactored Orchestrator Module

This module provides a clean, modular orchestrator for multi-agent
conversations using dependency injection and service-oriented architecture.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from agents.registry import get_agent_registry
from config import ensure_workspace_exists, get_llm_config, get_workspace_path
from constants import (
    DEFAULT_FILE_NAME,
    DEFAULT_MAX_CODER_ATTEMPTS,
    DEFAULT_ROUNDS,
    DEFAULT_TEST_MODE,
    ERROR_MESSAGES,
)
from services import (
    AgentFileService,
    CodeQualityService,
    CodeValidationService,
    FileService,
    TestExecutionService,
)

logger = logging.getLogger(__name__)


class ConversationState:
    """Manages the state of the multi-agent conversation."""

    def __init__(self, initial_prompt: str, existing_code: str = ""):
        """
        Initialize conversation state.

        Args:
            initial_prompt (str): The initial prompt for the conversation
            existing_code (str): Any existing code to start with
        """
        self.prompt = initial_prompt
        self.code = existing_code
        self.user_feedback = ""
        self.reviewer_feedback = ""
        self.reviewer2_feedback = ""
        self.qa_feedback = ""

    def get_aggregated_feedback(self) -> List[str]:
        """Get list of all non-empty feedback."""
        feedbacks = []
        if self.reviewer_feedback:
            feedbacks.append(f"Reviewer: {self.reviewer_feedback}")
        if self.reviewer2_feedback:
            feedbacks.append(f"Reviewer2: {self.reviewer2_feedback}")
        if self.qa_feedback:
            feedbacks.append(f"QA: {self.qa_feedback}")
        return feedbacks


class AgentOrchestrator:
    """
    Orchestrates multi-agent conversations for code development.
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.agent_registry = get_agent_registry()
        self.code_validation_service = CodeValidationService()
        self.test_execution_service = TestExecutionService()
        self.code_quality_service = CodeQualityService()
        self.file_service = FileService()
        self.agent_file_service = AgentFileService()

    def run_conversation(
        self, scenario: Dict[str, Any], num_rounds: Optional[int] = None
    ) -> Optional[str]:
        """
        Run a multi-agent conversation to develop Python code.

        Args:
            scenario (Dict[str, Any]): Scenario configuration
            num_rounds (Optional[int]): Number of rounds to execute

        Returns:
            Optional[str]: Path to generated code file if successful
        """
        try:
            # Setup
            ensure_workspace_exists()
            llm_config = get_llm_config()
            work_dir = get_workspace_path()

            # Extract scenario parameters
            initial_prompt = scenario["prompt"]
            use_dumb_user = scenario.get("use_dumb_user", False)
            rounds = num_rounds or scenario.get("num_rounds", DEFAULT_ROUNDS)
            test_mode = scenario.get("test_mode", DEFAULT_TEST_MODE)
            file_name = scenario.get("file_name", DEFAULT_FILE_NAME)
            output_path = os.path.join(work_dir, file_name)

            logger.info("Starting multi-agent conversation...")
            logger.info(f"Scenario: {scenario.get('description', '')}")
            logger.info(f"Initial prompt: {initial_prompt}")
            logger.info("-" * 60)

            # Create agents
            agents = self._create_agents(llm_config, work_dir, use_dumb_user)

            # Initialize conversation state
            existing_code = self.file_service.load_existing_code(output_path)
            conversation_state = ConversationState(initial_prompt, existing_code)

            # Run conversation rounds
            self._run_conversation_rounds(
                scenario,
                rounds,
                agents,
                output_path,
                conversation_state,
                test_mode,
                work_dir,
            )

            # Run improvement agent if requested
            self._run_improvement_agent_if_requested(scenario, work_dir)

            return output_path

        except Exception as e:
            logger.error(ERROR_MESSAGES["CODE_GENERATION_ERROR"].format(e))
            raise

    def _create_agents(
        self, llm_config: Dict[str, Any], work_dir: str, use_dumb_user: bool
    ) -> Dict[str, Any]:
        """Create all required agents for the conversation."""
        user_type = "dumb_user" if use_dumb_user else "user"

        agent_types = ["coder", "reviewer", "reviewer2", "qa", user_type]
        agents = {}

        for agent_type in agent_types:
            agent = self.agent_registry.create_agent(agent_type, llm_config, work_dir)
            if agent is None:
                raise RuntimeError(
                    ERROR_MESSAGES["AGENT_CREATION_FAILED"].format(agent_type)
                )
            agents[agent_type] = agent

        # Create test runner (not in registry yet)
        from agents.test_runner_agent import TestRunnerAgent

        agents["test_runner"] = TestRunnerAgent(work_dir)

        agent_names = [agent.name for agent in agents.values()]
        logger.info(f"✓ Created agents: {', '.join(agent_names)}")

        return agents

    def _run_conversation_rounds(
        self,
        scenario: Dict[str, Any],
        rounds: int,
        agents: Dict[str, Any],
        output_path: str,
        conversation_state: ConversationState,
        test_mode: str,
        work_dir: str,
    ) -> None:
        """Run the main conversation rounds."""
        best_code = None
        best_code_valid = False
        best_code_score = -1

        for round_num in range(1, rounds + 1):
            logger.info(f"Conversation Round {round_num}")

            # Prepare user message
            user_message = self._prepare_user_message(round_num, conversation_state)
            user_agent = agents.get("user", agents.get("dumb_user"))
            logger.info(f"👤 {user_agent.name}: {user_message}")
            conversation_state.user_feedback = user_message

            # Generate code
            code = self._generate_code_with_retries(
                scenario,
                agents["coder"],
                user_message,
                conversation_state,
                output_path,
                round_num,
            )
            conversation_state.code = code

            # Track best code
            if code:
                score = self.code_quality_service.calculate_quality_score(
                    code, output_path, scenario
                )
                is_complete = self.code_validation_service.is_code_complete(
                    code, scenario
                )
                if is_complete and (not best_code_valid or score > best_code_score):
                    best_code = code
                    best_code_valid = True
                    best_code_score = score

            # Save and test code
            self._save_and_test_code(
                best_code,
                best_code_valid,
                output_path,
                scenario,
                test_mode,
                agents["test_runner"],
                conversation_state,
            )

            # Get feedback from reviewers
            self._collect_agent_feedback(agents, code, conversation_state)

            # Run improvement agent in loop if requested
            self._run_improvement_agent_in_loop_if_requested(
                scenario, round_num, work_dir
            )

    def _prepare_user_message(
        self, round_num: int, conversation_state: ConversationState
    ) -> str:
        """Prepare the user message for the current round."""
        if round_num == 1:
            return conversation_state.prompt

        feedbacks = conversation_state.get_aggregated_feedback()
        return "Please address the following feedback:\n" + "\n".join(feedbacks)

    def _generate_code_with_retries(
        self,
        scenario: Dict[str, Any],
        coder_agent: Any,
        user_message: str,
        conversation_state: ConversationState,
        output_path: str,
        round_num: int,
    ) -> str:
        """Generate code with retry logic for incomplete code."""
        code = conversation_state.code
        coder_attempts = 0

        while coder_attempts < DEFAULT_MAX_CODER_ATTEMPTS:
            logger.info(
                f"💻 {coder_agent.name}: Generating code using Ollama... "
                f"(attempt {coder_attempts + 1})"
            )

            # Prepare coder prompt
            feedbacks = (
                conversation_state.get_aggregated_feedback() if round_num > 1 else []
            )
            coder_prompt = (
                f"{coder_agent.system_message}\n\n"
                f"User requirements:\n{user_message}\n\n"
                f"Previous feedback:\n{chr(10).join(feedbacks)}\n\n"
                f"Write the Python code below:"
            )

            try:
                from utils import call_ollama, extract_python_code_blocks

                code_response = call_ollama(
                    coder_prompt, system_message=coder_agent.system_message
                )
                code_blocks = extract_python_code_blocks(code_response)
                code = code_blocks[-1] if code_blocks else code_response

                is_complete = self.code_validation_service.is_code_complete(
                    code, scenario
                )
                if is_complete:
                    break

                logger.warning(
                    "⚠️ Detected missing methods or undefined calls. "
                    "Asking coder to fix..."
                )
                user_message += (
                    "\n\n[The previous code was missing required methods "
                    "or had undefined calls. Please fix all issues and "
                    "provide a complete, executable class with all required "
                    "methods implemented. Do not leave any method as a "
                    "placeholder or with ... (rest of the methods).]"
                )

            except Exception as e:
                logger.error(ERROR_MESSAGES["CODE_GENERATION_ERROR"].format(e))

            coder_attempts += 1

        return code

    def _save_and_test_code(
        self,
        best_code: Optional[str],
        best_code_valid: bool,
        output_path: str,
        scenario: Dict[str, Any],
        test_mode: str,
        test_runner_agent: Any,
        conversation_state: ConversationState,
    ) -> None:
        """Save the best code and run tests."""
        # Create backup
        backup_path = self.file_service.backup_file(output_path)

        if best_code_valid and best_code:
            from utils import save_generated_code

            save_generated_code([best_code], output_path)

            # Run tests
            tests_passed = True
            if scenario.get("language", "python").lower() == "python":
                tests_passed = self.test_execution_service.run_python_tests(
                    output_path, scenario
                )

                # Also run TestRunnerAgent
                test_runner_result = test_runner_agent.run_tests(
                    output_path, mode=test_mode
                )
                logger.info(f"🧪 {test_runner_agent.name} result (mode: {test_mode}):")
                logger.info(f"Success: {test_runner_result['success']}")

                if test_runner_result["stdout"]:
                    logger.info(f"Stdout:\n{test_runner_result['stdout']}")
                if test_runner_result["stderr"]:
                    logger.info(f"Stderr:\n{test_runner_result['stderr']}")

                tests_passed = tests_passed and test_runner_result["success"]

                # Feed test results into QA feedback for next round
                if not test_runner_result["success"]:
                    conversation_state.qa_feedback += (
                        f"\n[Automated test runner failed: "
                        f"{test_runner_result['stderr']}]"
                    )

            if not tests_passed:
                logger.warning("❌ Tests failed. Restoring previous version.")
                if backup_path:
                    self.file_service.restore_backup(backup_path, output_path)
            else:
                logger.info("✅ Code passed tests and was saved.")
        else:
            logger.warning("⚠️ No valid code generated. Keeping previous version.")

    def _collect_agent_feedback(
        self, agents: Dict[str, Any], code: str, conversation_state: ConversationState
    ) -> None:
        """Collect feedback from all review agents."""
        # Reviewer 1
        try:
            from utils import call_ollama

            reviewer = agents["reviewer"]
            reviewer_prompt = (
                f"{reviewer.system_message}\n\n"
                f"Here is the code to review:\n{code}\n\n"
                f"Please provide a review and suggestions."
            )
            reviewer_feedback = call_ollama(
                reviewer_prompt, system_message=reviewer.system_message
            )
            logger.info(f"🔍 {reviewer.name}: {reviewer_feedback}")
            conversation_state.reviewer_feedback = reviewer_feedback
        except Exception as e:
            logger.error(ERROR_MESSAGES["FEEDBACK_ERROR"].format("Reviewer", e))
            conversation_state.reviewer_feedback = (
                "[Error: Reviewer feedback unavailable]"
            )

        # Reviewer 2
        try:
            from utils import call_ollama

            reviewer2 = agents["reviewer2"]
            reviewer2_prompt = (
                f"{reviewer2.system_message}\n\n"
                f"Strict review of the following code:\n{code}\n\n"
                f"Please provide a strict review and suggestions."
            )
            reviewer2_feedback = call_ollama(
                reviewer2_prompt, system_message=reviewer2.system_message
            )
            logger.info(f"🔍 {reviewer2.name}: {reviewer2_feedback}")
            conversation_state.reviewer2_feedback = reviewer2_feedback
        except Exception as e:
            logger.error(ERROR_MESSAGES["FEEDBACK_ERROR"].format("Reviewer2", e))
            conversation_state.reviewer2_feedback = (
                "[Error: Reviewer2 feedback unavailable]"
            )

        # QA Specialist
        try:
            from utils import call_ollama

            qa = agents["qa"]
            qa_prompt = (
                f"{qa.system_message}\n\n"
                f"Perform QA on the following code:\n{code}\n\n"
                f"List any issues or confirm if it passes QA."
            )
            qa_feedback = call_ollama(qa_prompt, system_message=qa.system_message)
            logger.info(f"✅ {qa.name}: {qa_feedback}")
            conversation_state.qa_feedback = qa_feedback
        except Exception as e:
            logger.error(ERROR_MESSAGES["FEEDBACK_ERROR"].format("QA", e))
            conversation_state.qa_feedback = "[Error: QA feedback unavailable]"

    def _run_improvement_agent_in_loop_if_requested(
        self, scenario: Dict[str, Any], round_num: int, work_dir: str
    ) -> None:
        """Run ImprovementAgent in loop if scenario requests it."""
        if not scenario.get("improvement_agent_in_loop"):
            return

        try:
            from agents.improvement_agent import ImprovementAgent

            agent_files = self.agent_file_service.get_agent_file_paths()
            report_path = os.path.join(
                work_dir, f"improvement_report_round{round_num}.log"
            )
            improvement_agent = ImprovementAgent(agent_files, report_path)
            logger.info(
                f"🛠️ [Round {round_num}] Triggering ImprovementAgent "
                f"to review agent class source files..."
            )
            improvement_agent.review_agents()
        except Exception as e:
            logger.error(ERROR_MESSAGES["IMPROVEMENT_AGENT_ERROR"].format(e))

    def _run_improvement_agent_if_requested(
        self, scenario: Dict[str, Any], work_dir: str
    ) -> None:
        """Run ImprovementAgent if scenario requests it."""
        if not scenario.get("improvement_agent"):
            return

        try:
            from agents.improvement_agent import ImprovementAgent

            agent_files = self.agent_file_service.get_agent_file_paths()
            file_name = scenario.get("file_name", "improvement_report.log")
            report_path = os.path.join(work_dir, file_name)
            improvement_agent = ImprovementAgent(agent_files, report_path)
            logger.info(
                "🛠️ Triggering ImprovementAgent to review " "agent class source files..."
            )
            improvement_agent.review_agents()
        except Exception as e:
            logger.error(ERROR_MESSAGES["IMPROVEMENT_AGENT_ERROR"].format(e))


# Legacy function for backward compatibility
def simulate_agent_conversation(
    scenario: Dict[str, Any], num_rounds: Optional[int] = None
) -> Optional[str]:
    """
    Legacy function for backward compatibility.

    Args:
        scenario (Dict[str, Any]): Scenario configuration
        num_rounds (Optional[int]): Number of rounds to execute

    Returns:
        Optional[str]: Path to generated code file if successful
    """
    orchestrator = AgentOrchestrator()
    return orchestrator.run_conversation(scenario, num_rounds)
