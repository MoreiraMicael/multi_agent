"""
Core Services Module

This module provides core services for the multi-agent system including
code validation, quality scoring, and test execution. These services are
decoupled from the orchestrator for better testability and reusability.
"""

import importlib.util
import logging
import os
import re
import shutil
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional

from constants import (
    BUILTIN_FUNCTIONS,
    ERROR_MESSAGES,
    FUNCTION_CALL_PATTERN,
    FUNCTION_DEF_PATTERN,
    MAIN_BLOCK_PATTERN,
    SCORE_COMPLETE_CODE,
    SCORE_PASSING_TESTS,
    TEMP_FILE_EXTENSION,
)

logger = logging.getLogger(__name__)


class CodeValidationService:
    """Service for validating code completeness and correctness."""

    @staticmethod
    def is_code_complete(code: str, scenario: Dict[str, Any]) -> bool:
        """
        Check if the code is complete according to scenario validation logic.

        Args:
            code (str): The code to validate
            scenario (Dict[str, Any]): Scenario configuration

        Returns:
            bool: True if code is complete, False otherwise
        """
        # Scenario-specific validation logic
        validation = scenario.get("validation")
        if validation == "none":
            return True
        if validation and callable(validation):
            return validation(code)

        # Default: for Python, check for undefined method calls in __main__
        if scenario.get("language", "python").lower() == "python":
            return CodeValidationService._validate_python_main_block(code)

        # For other languages/generic scenarios, check code is not empty
        return bool(code.strip())

    @staticmethod
    def _validate_python_main_block(code: str) -> bool:
        """
        Validate that all functions called in __main__ are defined.

        Args:
            code (str): Python code to validate

        Returns:
            bool: True if all called functions are defined
        """
        # If code is empty, it's not complete
        if not code.strip():
            return False

        main_block = re.search(MAIN_BLOCK_PATTERN, code, re.DOTALL)
        if main_block:
            # Find all function calls in __main__
            called = re.findall(FUNCTION_CALL_PATTERN, main_block.group(1))
            for func in called:
                if (
                    func not in BUILTIN_FUNCTIONS
                    and FUNCTION_DEF_PATTERN.format(func) not in code
                ):
                    logger.warning(f"Undefined function call: {func}")
                    return False
        return True


class TestExecutionService:
    """Service for executing tests on generated code."""

    @staticmethod
    def run_python_tests(file_path: str, scenario: Dict[str, Any]) -> bool:
        """
        Run Python tests on the given file.

        Args:
            file_path (str): Path to the Python file to test
            scenario (Dict[str, Any]): Scenario configuration

        Returns:
            bool: True if tests pass, False otherwise
        """
        custom_test = scenario.get("test_func")
        if custom_test and callable(custom_test):
            return TestExecutionService._run_custom_test(custom_test, file_path)

        return TestExecutionService._run_default_test(file_path)

    @staticmethod
    def _run_custom_test(test_func: Callable, file_path: str) -> bool:
        """Run custom test function provided by scenario."""
        try:
            return test_func(file_path)
        except Exception as e:
            logger.error(ERROR_MESSAGES["TEST_EXECUTION_FAILED"].format(e))
            logger.debug(traceback.format_exc())
            return False

    @staticmethod
    def _run_default_test(file_path: str) -> bool:
        """Run default test by attempting to load the module."""
        try:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception as e:
            logger.error(ERROR_MESSAGES["TEST_EXECUTION_FAILED"].format(e))
            logger.debug(traceback.format_exc())
            return False


class CodeQualityService:
    """Service for scoring code quality."""

    @staticmethod
    def calculate_quality_score(
        code: str, file_path: str, scenario: Dict[str, Any]
    ) -> int:
        """
        Calculate code quality score based on completeness and test results.

        Args:
            code (str): The code to score
            file_path (str): Path where code will be saved for testing
            scenario (Dict[str, Any]): Scenario configuration

        Returns:
            int: Quality score (higher is better)
        """
        score = 0

        # Score for code completeness
        if CodeValidationService.is_code_complete(code, scenario):
            score += SCORE_COMPLETE_CODE

        # Score for passing tests
        temp_path = file_path + TEMP_FILE_EXTENSION
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)
            if TestExecutionService.run_python_tests(temp_path, scenario):
                score += SCORE_PASSING_TESTS
        except Exception as e:
            logger.error(ERROR_MESSAGES["FILE_WRITE_ERROR"].format(temp_path, e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Base score based on code length (encourages more complete solutions)
        score += len(code)

        return score


class FileService:
    """Service for file operations."""

    @staticmethod
    def load_existing_code(file_path: str) -> str:
        """
        Load existing code from file if it exists.

        Args:
            file_path (str): Path to the file

        Returns:
            str: File content or empty string if file doesn't exist/error
        """
        if not os.path.exists(file_path):
            return ""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"📄 Loaded existing code from {file_path}")
            return content
        except Exception as e:
            logger.error(ERROR_MESSAGES["FILE_READ_ERROR"].format(file_path, e))
            return ""

    @staticmethod
    def backup_file(file_path: str) -> Optional[str]:
        """
        Create a backup of the file.

        Args:
            file_path (str): Path to the file to backup

        Returns:
            Optional[str]: Path to backup file or None if error
        """
        if not os.path.exists(file_path):
            return None

        backup_path = file_path + ".backup"
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logger.error(ERROR_MESSAGES["FILE_WRITE_ERROR"].format(backup_path, e))
            return None

    @staticmethod
    def restore_backup(backup_path: str, original_path: str) -> bool:
        """
        Restore file from backup.

        Args:
            backup_path (str): Path to backup file
            original_path (str): Path to restore to

        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(backup_path):
            return False

        try:
            shutil.copy2(backup_path, original_path)
            return True
        except Exception as e:
            logger.error(ERROR_MESSAGES["FILE_WRITE_ERROR"].format(original_path, e))
            return False


class AgentFileService:
    """Service for managing agent file paths."""

    @staticmethod
    def get_agent_file_paths(base_dir: Optional[str] = None) -> List[str]:
        """
        Get list of agent file paths.

        Args:
            base_dir (Optional[str]): Base directory for agent files.
                                    If None, uses current directory.

        Returns:
            List[str]: List of absolute paths to agent files
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), "agents")

        from constants import AGENT_FILES

        return [os.path.join(base_dir, filename) for filename in AGENT_FILES]
