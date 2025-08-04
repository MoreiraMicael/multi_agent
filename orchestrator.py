import os
import logging
from config import get_llm_config, get_workspace_path, ensure_workspace_exists
from agents.coder_agent import get_coder_agent
from agents.reviewer_agent import get_reviewer_agent
from agents.reviewer_agent2 import get_reviewer_agent2
from agents.qa_agent import get_qa_agent
from agents.user_agent import get_user_agent
from agents.dumb_user_agent import get_dumb_user_agent
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def _create_agents(llm_config: Dict[str, Any], work_dir: str, use_dumb_user: bool) -> Dict[str, Any]:
    """
    Create all required agents for the conversation.
    
    Args:
        llm_config (Dict[str, Any]): LLM configuration
        work_dir (str): Working directory path
        use_dumb_user (bool): Whether to use dumb user agent or regular user
        
    Returns:
        Dict[str, Any]: Dictionary containing all created agents
    """
    coder = get_coder_agent(llm_config, work_dir)
    reviewer = get_reviewer_agent(llm_config, work_dir)
    reviewer2 = get_reviewer_agent2(llm_config, work_dir)
    qa_specialist = get_qa_agent(llm_config, work_dir)
    user = get_dumb_user_agent(llm_config, work_dir) if use_dumb_user else get_user_agent(llm_config, work_dir)
    
    from agents.test_runner_agent import TestRunnerAgent
    test_runner = TestRunnerAgent(work_dir)
    
    agents = {
        'coder': coder,
        'reviewer': reviewer,
        'reviewer2': reviewer2,
        'qa_specialist': qa_specialist,
        'user': user,
        'test_runner': test_runner
    }
    
    logger.info(f"✓ Created agents: {coder.name}, {reviewer.name}, {reviewer2.name}, {qa_specialist.name}, {user.name}, {test_runner.name}")
    return agents


def _load_existing_code(output_path: str) -> str:
    """
    Load existing code from file if it exists.
    
    Args:
        output_path (str): Path to the output file
        
    Returns:
        str: Existing code content or empty string
    """
    existing_code = ""
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_code = f.read()
            logger.info(f"📄 Loaded existing code from {output_path} as starting point.")
        except Exception as e:
            logger.error(f"Could not read existing file {output_path}: {e}")
    return existing_code


def _initialize_conversation_state(
    initial_prompt: str, existing_code: str
) -> Dict[str, Any]:
    """
    Initialize the conversation state dictionary.
    
    Args:
        initial_prompt (str): The initial prompt for the conversation
        existing_code (str): Any existing code to start with
        
    Returns:
        Dict[str, Any]: Initialized conversation state
    """
    return {
        "prompt": initial_prompt,
        "code": existing_code,
        "user_feedback": "",
        "reviewer_feedback": "",
        "reviewer2_feedback": "",
        "qa_feedback": ""
    }


def simulate_agent_conversation(
    scenario: Dict[str, Any], num_rounds: Optional[int] = None
) -> Optional[str]:
    """
    Simulate a multi-agent conversation to develop Python code.
    
    Args:
        scenario (Dict[str, Any]): Scenario configuration containing prompt,
                                  description, and other settings
        num_rounds (Optional[int]): Number of conversation rounds to execute.
                                   If None, uses scenario default or 3
    
    Returns:
        Optional[str]: Generated code if successful, None otherwise
    """
    from utils import call_ollama, extract_python_code_blocks, save_generated_code
    ensure_workspace_exists()
    llm_config = get_llm_config()
    work_dir = get_workspace_path()
    initial_prompt = scenario["prompt"]
    use_dumb_user = scenario.get("use_dumb_user", False)
    rounds = num_rounds if num_rounds is not None else scenario.get("num_rounds", 3)
    logger.info("Simulating multi-agent conversation...")
    logger.info(f"Scenario: {scenario.get('description', '')}")
    logger.info(f"Initial prompt: {initial_prompt}")
    logger.info("-" * 60)
    try:
        agents = _create_agents(llm_config, work_dir, use_dumb_user)
        
        # Determine test mode: 'script' or 'pytest' (default to 'script')
        test_mode = scenario.get('test_mode', 'script')

        # Load existing code if available
        file_name = scenario.get("file_name", "multi_agent_generated_code.py")
        output_path = os.path.join(work_dir, file_name)
        existing_code = _load_existing_code(output_path)
        
        # Initialize conversation state
        conversation_state = _initialize_conversation_state(initial_prompt, existing_code)
        
        # Extract agents for backward compatibility
        coder = agents['coder']
        reviewer = agents['reviewer']
        reviewer2 = agents['reviewer2']
        qa_specialist = agents['qa_specialist']
        user = agents['user']
        test_runner = agents['test_runner']

        import re
        def code_is_complete(code: str) -> bool:
            # Scenario-specific validation logic
            validation = scenario.get('validation')
            if validation == 'none':
                return True
            if validation and callable(validation):
                return validation(code)
            # Default: for Python, check for undefined method calls in __main__
            if scenario.get('language', 'python').lower() == 'python':
                main_block = re.search(r'if __name__ ?== ?[\'\"]__main__[\'\"]:(.*)', code, re.DOTALL)
                if main_block:
                    # Find all function calls in __main__
                    called = re.findall(r'(\w+)\(', main_block.group(1))
                    for func in called:
                        if func not in ['print', 'input'] and f'def {func}' not in code:
                            return False
            # For other languages or generic scenarios, just check code is not empty
            return bool(code.strip())


        import shutil
        import importlib.util
        import sys
        best_code = None
        best_code_valid = False
        best_code_score = -1
        import traceback
        # Scenario can provide a custom test function, else use default
        def run_python_tests_on_code(file_path: str) -> bool:
            custom_test = scenario.get('test_func')
            if custom_test and callable(custom_test):
                try:
                    return custom_test(file_path)
                except Exception as e:
                    logger.error(f"Custom test function failed: {e}")
                    logger.debug(traceback.format_exc())
                    return False
            try:
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                if module_name in sys.modules:
                    del sys.modules[module_name]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Default: pass if file loads without error
                return True
            except Exception as e:
                logger.error(f"Test failed: {e}")
                logger.debug(traceback.format_exc())
                return False

        def code_quality_score(code: str, file_path: str) -> int:
            # Score: +100 if code is complete, +100 if tests pass, +len(code)
            score = 0
            if code_is_complete(code):
                score += 100
            # Save code temporarily to test
            temp_path = file_path + ".tmp"
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(code)
                if run_python_tests_on_code(temp_path):
                    score += 100
            except Exception as e:
                logger.error(f"Error scoring code: {e}")
                logger.debug(traceback.format_exc())
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            score += len(code)
            return score


        for round_num in range(1, rounds + 1):
            logger.info(f"Conversation Round {round_num}")
            # User step: can provide feedback in later rounds
            if round_num == 1:
                user_message = conversation_state["prompt"]
            else:
                # Aggregate feedback more clearly
                feedbacks = []
                if conversation_state['reviewer_feedback']:
                    feedbacks.append(f"Reviewer: {conversation_state['reviewer_feedback']}")
                if conversation_state['reviewer2_feedback']:
                    feedbacks.append(f"Reviewer2: {conversation_state['reviewer2_feedback']}")
                if conversation_state['qa_feedback']:
                    feedbacks.append(f"QA: {conversation_state['qa_feedback']}")
                user_message = "Please address the following feedback:\n" + "\n".join(feedbacks)
            print(f"\n👤 {user.name}: {user_message}")
            conversation_state["user_feedback"] = user_message

            # Loop until code is complete
            code_complete = False
            code = conversation_state["code"]
            coder_attempts = 0
            while not code_complete and coder_attempts < 3:
                print(f"\n💻 {coder.name}: Generating code using Ollama... (attempt {coder_attempts+1})")
                coder_prompt = f"{coder.system_message}\n\nUser requirements:\n{user_message}\n\nPrevious feedback:\n" + "\n".join(feedbacks if round_num > 1 else []) + "\n\nWrite the Python code below:"
                try:
                    code_response = call_ollama(coder_prompt, system_message=coder.system_message)
                    code_blocks = extract_python_code_blocks(code_response)
                    code = code_blocks[-1] if code_blocks else code_response
                    code_complete = code_is_complete(code)
                    # Use code quality score
                    score = code_quality_score(code, output_path)
                    if code_complete and (not best_code_valid or score > best_code_score):
                        best_code = code
                        best_code_valid = True
                        best_code_score = score
                except Exception as e:
                    print(f"Error during code generation: {e}\n{traceback.format_exc()}")
                    code_complete = False
                if not code_complete:
                    print("\n⚠️  Detected missing methods or undefined calls. Asking coder to fix...")
                    user_message += "\n\n[The previous code was missing required methods or had undefined calls. Please fix all issues and provide a complete, executable class with all required methods implemented. Do not leave any method as a placeholder or with ... (rest of the methods).]"
                coder_attempts += 1
            conversation_state["code"] = code

            # Only save if code is valid and not worse than best so far
            backup_path = output_path + ".backup"
            if os.path.exists(output_path):
                shutil.copy2(output_path, backup_path)
            if best_code_valid:
                save_generated_code([best_code], output_path)
                tests_passed = True
                # Use both the built-in and TestRunnerAgent for validation
                if scenario.get('language', 'python').lower() == 'python':
                    tests_passed = run_python_tests_on_code(output_path)
                    test_runner_result = test_runner.run_tests(output_path, mode=test_mode)
                    print(f"\n🧪 {test_runner.name} result (mode: {test_mode}):")
                    print(f"Success: {test_runner_result['success']}")
                    if test_runner_result['stdout']:
                        print(f"Stdout:\n{test_runner_result['stdout']}")
                    if test_runner_result['stderr']:
                        print(f"Stderr:\n{test_runner_result['stderr']}")
                    tests_passed = tests_passed and test_runner_result['success']
                    # Feed test results into QA feedback for next round
                    if not test_runner_result['success']:
                        conversation_state['qa_feedback'] += f"\n[Automated test runner failed: {test_runner_result['stderr']}]"
                if not tests_passed:
                    print("\n❌ Tests failed. Restoring previous version.")
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, output_path)
                else:
                    print("\n✅ Code passed tests and was saved.")
            else:
                print("\n⚠️ No valid code generated. Keeping previous version.")

            # Reviewer 1 step: real LLM call
            try:
                reviewer_prompt = f"{reviewer.system_message}\n\nHere is the code to review:\n{code}\n\nPlease provide a review and suggestions."
                reviewer_feedback = call_ollama(reviewer_prompt, system_message=reviewer.system_message)
                print(f"\n🔍 {reviewer.name}: {reviewer_feedback}")
                conversation_state["reviewer_feedback"] = reviewer_feedback
            except Exception as e:
                print(f"Error during Reviewer feedback: {e}\n{traceback.format_exc()}")
                conversation_state["reviewer_feedback"] = "[Error: Reviewer feedback unavailable]"

            # Reviewer 2 step: real LLM call
            try:
                reviewer2_prompt = f"{reviewer2.system_message}\n\nStrict review of the following code:\n{code}\n\nPlease provide a strict review and suggestions."
                reviewer2_feedback = call_ollama(reviewer2_prompt, system_message=reviewer2.system_message)
                print(f"\n🔍 {reviewer2.name}: {reviewer2_feedback}")
                conversation_state["reviewer2_feedback"] = reviewer2_feedback
            except Exception as e:
                print(f"Error during Reviewer2 feedback: {e}\n{traceback.format_exc()}")
                conversation_state["reviewer2_feedback"] = "[Error: Reviewer2 feedback unavailable]"

            # QA step: real LLM call
            try:
                qa_prompt = f"{qa_specialist.system_message}\n\nPerform QA on the following code:\n{code}\n\nList any issues or confirm if it passes QA."
                qa_feedback = call_ollama(qa_prompt, system_message=qa_specialist.system_message)
                print(f"\n✅ {qa_specialist.name}: {qa_feedback}")
                conversation_state["qa_feedback"] = qa_feedback
            except Exception as e:
                print(f"Error during QA feedback: {e}\n{traceback.format_exc()}")
                conversation_state["qa_feedback"] = "[Error: QA feedback unavailable]"

            # Optionally, allow ImprovementAgent to participate in the main loop for continuous improvement
            if scenario.get("improvement_agent_in_loop"):
                try:
                    from agents.improvement_agent import ImprovementAgent
                    agent_files = [
                        os.path.join(os.path.dirname(__file__), "agents", "coder_agent.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "reviewer_agent.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "reviewer_agent2.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "qa_agent.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "user_agent.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "dumb_user_agent.py"),
                        os.path.join(os.path.dirname(__file__), "agents", "improvement_agent.py"),
                    ]
                    report_path = os.path.join(work_dir, f"improvement_report_round{round_num}.log")
                    improvement_agent = ImprovementAgent(agent_files, report_path)
                    print(f"\n🛠️  [Round {round_num}] Triggering ImprovementAgent to review agent class source files...")
                    improvement_agent.review_agents()
                except Exception as e:
                    print(f"Error running ImprovementAgent in loop: {e}\n{traceback.format_exc()}")

        # If scenario requests ImprovementAgent, trigger it
        if scenario.get("improvement_agent"):
            try:
                from agents.improvement_agent import ImprovementAgent
                agent_files = [
                    os.path.join(os.path.dirname(__file__), "agents", "coder_agent.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "reviewer_agent.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "reviewer_agent2.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "qa_agent.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "user_agent.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "dumb_user_agent.py"),
                    os.path.join(os.path.dirname(__file__), "agents", "improvement_agent.py"),
                ]
                file_name = scenario.get("file_name", "improvement_report.log")
                report_path = os.path.join(work_dir, file_name)
                improvement_agent = ImprovementAgent(agent_files, report_path)
                print("\n🛠️  Triggering ImprovementAgent to review agent class source files...")
                improvement_agent.review_agents()
            except Exception as e:
                logger.error(f"Error running ImprovementAgent: {e}")
        return output_path
    except Exception as e:
        logger.error(f"Error during simulation: {e}")
        raise
