"""
Comprehensive Test Suite for Refactored Multi-Agent System

This module contains pytest-based tests for the refactored services,
orchestrator, and other components to ensure quality and reliability.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from exceptions import AgentCreationError, CodeGenerationError, MultiAgentException
from orchestrator_refactored import AgentOrchestrator, ConversationState

# Import the modules we're testing
from services import (
    AgentFileService,
    CodeQualityService,
    CodeValidationService,
    FileService,
    TestExecutionService,
)


class TestCodeValidationService:
    """Test cases for CodeValidationService."""

    def test_is_code_complete_with_validation_none(self):
        """Test validation with 'none' setting."""
        scenario = {"validation": "none"}
        code = "incomplete code"
        assert CodeValidationService.is_code_complete(code, scenario) is True

    def test_is_code_complete_with_custom_validation(self):
        """Test validation with custom function."""

        def custom_validator(code):
            return "class" in code

        scenario = {"validation": custom_validator}

        valid_code = "class MyClass: pass"
        invalid_code = "def function(): pass"

        assert CodeValidationService.is_code_complete(valid_code, scenario) is True
        assert CodeValidationService.is_code_complete(invalid_code, scenario) is False

    def test_is_code_complete_python_main_block(self):
        """Test Python main block validation."""
        scenario = {"language": "python"}

        # Complete code with defined function
        complete_code = """
def hello():
    print("Hello")

if __name__ == "__main__":
    hello()
"""
        assert CodeValidationService.is_code_complete(complete_code, scenario) is True

        # Incomplete code with undefined function
        incomplete_code = """
if __name__ == "__main__":
    undefined_function()
"""
        assert (
            CodeValidationService.is_code_complete(incomplete_code, scenario) is False
        )

        # Code with builtin functions (should be valid)
        builtin_code = """
if __name__ == "__main__":
    print("Hello")
    len([1, 2, 3])
"""
        assert CodeValidationService.is_code_complete(builtin_code, scenario) is True

    def test_is_code_complete_empty_code(self):
        """Test empty code validation."""
        scenario = {}
        assert CodeValidationService.is_code_complete("", scenario) is False
        assert CodeValidationService.is_code_complete("   ", scenario) is False
        assert CodeValidationService.is_code_complete("# comment", scenario) is True


class TestTestExecutionService:
    """Test cases for TestExecutionService."""

    def test_run_python_tests_with_custom_test_func(self):
        """Test running tests with custom test function."""

        def mock_test_func(file_path):
            return True

        scenario = {"test_func": mock_test_func}
        result = TestExecutionService.run_python_tests("dummy_path", scenario)
        assert result is True

    def test_run_python_tests_custom_func_exception(self):
        """Test custom test function raising exception."""

        def failing_test_func(file_path):
            raise ValueError("Test failed")

        scenario = {"test_func": failing_test_func}
        result = TestExecutionService.run_python_tests("dummy_path", scenario)
        assert result is False

    @patch("services.importlib.util.spec_from_file_location")
    def test_run_python_tests_default_success(self, mock_spec):
        """Test default test execution success."""
        mock_spec.return_value = MagicMock()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('Hello World')")
            temp_path = f.name

        try:
            result = TestExecutionService.run_python_tests(temp_path, {})
            # Should attempt to load the module
            mock_spec.assert_called_once()
        finally:
            try:
                os.unlink(temp_path)
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors on Windows


class TestCodeQualityService:
    """Test cases for CodeQualityService."""

    @patch.object(CodeValidationService, "is_code_complete")
    @patch.object(TestExecutionService, "run_python_tests")
    def test_calculate_quality_score(self, mock_tests, mock_validation):
        """Test quality score calculation."""
        mock_validation.return_value = True
        mock_tests.return_value = True

        code = "def hello(): pass"
        scenario = {}

        with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
            score = CodeQualityService.calculate_quality_score(
                code, temp_file.name, scenario
            )

        # Score should be: 100 (complete) + 100 (tests pass) + len(code)
        expected_score = 100 + 100 + len(code)
        assert score == expected_score

    @patch.object(CodeValidationService, "is_code_complete")
    @patch.object(TestExecutionService, "run_python_tests")
    def test_calculate_quality_score_incomplete_code(self, mock_tests, mock_validation):
        """Test quality score for incomplete code."""
        mock_validation.return_value = False
        mock_tests.return_value = False

        code = "incomplete code"
        scenario = {}

        with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
            score = CodeQualityService.calculate_quality_score(
                code, temp_file.name, scenario
            )

        # Score should be: 0 (incomplete) + 0 (tests fail) + len(code)
        expected_score = len(code)
        assert score == expected_score


class TestFileService:
    """Test cases for FileService."""

    def test_load_existing_code_file_exists(self):
        """Test loading existing code when file exists."""
        test_content = "def test(): pass"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write(test_content)
            temp_path = f.name

        try:
            content = FileService.load_existing_code(temp_path)
            assert content == test_content
        finally:
            try:
                os.unlink(temp_path)
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors on Windows

    def test_load_existing_code_file_not_exists(self):
        """Test loading code when file doesn't exist."""
        content = FileService.load_existing_code("nonexistent_file.py")
        assert content == ""

    def test_backup_and_restore_file(self):
        """Test file backup and restore operations."""
        test_content = "original content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(test_content)
            temp_path = f.name

        try:
            # Create backup
            backup_path = FileService.backup_file(temp_path)
            assert backup_path is not None
            assert os.path.exists(backup_path)

            # Modify original
            with open(temp_path, "w") as modified_f:
                modified_f.write("modified content")

            # Restore from backup
            success = FileService.restore_backup(backup_path, temp_path)
            assert success is True

            # Verify content restored
            with open(temp_path, "r") as restored_f:
                restored_content = restored_f.read()

            assert restored_content == test_content

        finally:
            # Clean up
            for path in [temp_path, backup_path]:
                try:
                    if path and os.path.exists(path):
                        os.unlink(path)
                except (PermissionError, FileNotFoundError, NameError):
                    pass  # Ignore cleanup errors


class TestAgentFileService:
    """Test cases for AgentFileService."""

    def test_get_agent_file_paths_default(self):
        """Test getting agent file paths with default base directory."""
        paths = AgentFileService.get_agent_file_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert all(path.endswith(".py") for path in paths)

    def test_get_agent_file_paths_custom_dir(self):
        """Test getting agent file paths with custom base directory."""
        custom_dir = "/custom/path"
        paths = AgentFileService.get_agent_file_paths(custom_dir)
        assert all(path.startswith(custom_dir) for path in paths)


class TestConversationState:
    """Test cases for ConversationState."""

    def test_initialization(self):
        """Test conversation state initialization."""
        prompt = "Test prompt"
        code = "test code"
        state = ConversationState(prompt, code)

        assert state.prompt == prompt
        assert state.code == code
        assert state.user_feedback == ""
        assert state.reviewer_feedback == ""
        assert state.reviewer2_feedback == ""
        assert state.qa_feedback == ""

    def test_get_aggregated_feedback_empty(self):
        """Test aggregated feedback when no feedback is set."""
        state = ConversationState("prompt")
        feedbacks = state.get_aggregated_feedback()
        assert feedbacks == []

    def test_get_aggregated_feedback_with_content(self):
        """Test aggregated feedback with actual feedback."""
        state = ConversationState("prompt")
        state.reviewer_feedback = "Review feedback"
        state.qa_feedback = "QA feedback"

        feedbacks = state.get_aggregated_feedback()
        assert len(feedbacks) == 2
        assert "Reviewer: Review feedback" in feedbacks
        assert "QA: QA feedback" in feedbacks


class TestAgentOrchestrator:
    """Test cases for AgentOrchestrator."""

    @pytest.fixture
    def mock_scenario(self):
        """Fixture providing a mock scenario."""
        return {
            "prompt": "Create a simple calculator",
            "description": "Test scenario",
            "use_dumb_user": False,
            "num_rounds": 2,
            "file_name": "test_output.py",
        }

    @pytest.fixture
    def orchestrator(self):
        """Fixture providing an orchestrator instance."""
        return AgentOrchestrator()

    @patch("orchestrator_refactored.ensure_workspace_exists")
    @patch("orchestrator_refactored.get_llm_config")
    @patch("orchestrator_refactored.get_workspace_path")
    def test_orchestrator_initialization(
        self, mock_workspace, mock_config, mock_ensure, orchestrator
    ):
        """Test orchestrator initialization."""
        assert orchestrator.agent_registry is not None
        assert orchestrator.code_validation_service is not None
        assert orchestrator.test_execution_service is not None
        assert orchestrator.code_quality_service is not None
        assert orchestrator.file_service is not None
        assert orchestrator.agent_file_service is not None

    @patch("orchestrator_refactored.ensure_workspace_exists")
    @patch("orchestrator_refactored.get_llm_config")
    @patch("orchestrator_refactored.get_workspace_path")
    @patch.object(AgentOrchestrator, "_create_agents")
    @patch.object(FileService, "load_existing_code")
    def test_run_conversation_basic_flow(
        self,
        mock_load_code,
        mock_create_agents,
        mock_workspace,
        mock_config,
        mock_ensure,
        orchestrator,
        mock_scenario,
    ):
        """Test basic conversation flow."""
        # Setup mocks
        mock_workspace.return_value = "/tmp/workspace"
        mock_config.return_value = {"model": "test"}
        mock_load_code.return_value = ""
        mock_create_agents.return_value = {
            "coder": MagicMock(name="Coder"),
            "reviewer": MagicMock(name="Reviewer"),
            "reviewer2": MagicMock(name="Reviewer2"),
            "qa": MagicMock(name="QA"),
            "user": MagicMock(name="User"),
            "test_runner": MagicMock(name="TestRunner"),
        }

        # Mock the conversation rounds method to avoid complex setup
        with patch.object(orchestrator, "_run_conversation_rounds"):
            with patch.object(orchestrator, "_run_improvement_agent_if_requested"):
                result = orchestrator.run_conversation(mock_scenario)

        assert result is not None
        assert result.endswith("test_output.py")

    def test_prepare_user_message_first_round(self, orchestrator):
        """Test user message preparation for first round."""
        state = ConversationState("Initial prompt")
        message = orchestrator._prepare_user_message(1, state)
        assert message == "Initial prompt"

    def test_prepare_user_message_subsequent_round(self, orchestrator):
        """Test user message preparation for subsequent rounds."""
        state = ConversationState("Initial prompt")
        state.reviewer_feedback = "Needs improvement"
        state.qa_feedback = "Add tests"

        message = orchestrator._prepare_user_message(2, state)
        assert "Please address the following feedback:" in message
        assert "Reviewer: Needs improvement" in message
        assert "QA: Add tests" in message


class TestCustomExceptions:
    """Test cases for custom exception classes."""

    def test_multi_agent_exception_basic(self):
        """Test basic MultiAgentException."""
        message = "Test error"
        exception = MultiAgentException(message)
        assert str(exception) == message
        assert exception.message == message
        assert exception.details is None

    def test_multi_agent_exception_with_details(self):
        """Test MultiAgentException with details."""
        message = "Test error"
        details = {"error_code": 500, "context": "test"}
        exception = MultiAgentException(message, details)
        assert exception.details == details

    def test_specific_exception_inheritance(self):
        """Test that specific exceptions inherit from base."""
        assert issubclass(AgentCreationError, MultiAgentException)
        assert issubclass(CodeGenerationError, MultiAgentException)


# Integration tests
class TestIntegration:
    """Integration tests for the refactored system."""

    @patch("services.importlib.util.spec_from_file_location")
    def test_code_validation_and_quality_integration(self, mock_spec):
        """Test integration between validation and quality services."""
        mock_spec.return_value = MagicMock()

        # Valid Python code
        code = """
def add(a, b):
    return a + b

if __name__ == "__main__":
    result = add(2, 3)
    print(result)
"""
        scenario = {"language": "python"}

        # Test validation
        is_complete = CodeValidationService.is_code_complete(code, scenario)
        assert is_complete is True

        # Test quality scoring
        with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
            score = CodeQualityService.calculate_quality_score(
                code, temp_file.name, scenario
            )
            # Should get points for completeness + length
            assert score >= len(code) + 100  # 100 for completeness


if __name__ == "__main__":
    pytest.main([__file__])
