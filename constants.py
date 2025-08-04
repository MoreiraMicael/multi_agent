"""
Multi-Agent System Configuration Constants

This module contains all constants and configuration values used throughout
the multi-agent system, promoting maintainability and eliminating magic
numbers.
"""

from typing import Final

# Agent Names
AGENT_NAMES: Final = {
    "CODER": "Coder",
    "REVIEWER": "Reviewer",
    "REVIEWER2": "Reviewer2",
    "QA_SPECIALIST": "QA Specialist",
    "USER": "User",
    "DUMB_USER": "Dumb User",
    "TEST_RUNNER": "Test Runner",
    "IMPROVEMENT": "Improvement Agent",
}

# File Extensions and Patterns
PYTHON_FILE_EXTENSION: Final = ".py"
BACKUP_FILE_EXTENSION: Final = ".backup"
TEMP_FILE_EXTENSION: Final = ".tmp"

# Default Values
DEFAULT_ROUNDS: Final = 3
DEFAULT_MAX_CODER_ATTEMPTS: Final = 3
DEFAULT_FILE_NAME: Final = "multi_agent_generated_code.py"
DEFAULT_IMPROVEMENT_REPORT_NAME: Final = "improvement_report.log"
DEFAULT_TEST_MODE: Final = "script"

# Scoring System
SCORE_COMPLETE_CODE: Final = 100
SCORE_PASSING_TESTS: Final = 100

# Agent File Paths
AGENT_FILES: Final = [
    "coder_agent.py",
    "reviewer_agent.py",
    "reviewer_agent2.py",
    "qa_agent.py",
    "user_agent.py",
    "dumb_user_agent.py",
    "improvement_agent.py",
    "test_runner_agent.py",
]

# Error Messages
ERROR_MESSAGES: Final = {
    "AGENT_CREATION_FAILED": "Failed to create agent: {}",
    "FILE_READ_ERROR": "Could not read file {}: {}",
    "FILE_WRITE_ERROR": "Could not write to file {}: {}",
    "TEST_EXECUTION_FAILED": "Test execution failed: {}",
    "CODE_GENERATION_ERROR": "Error during code generation: {}",
    "FEEDBACK_ERROR": "Error during {} feedback: {}",
    "IMPROVEMENT_AGENT_ERROR": "Error running ImprovementAgent: {}",
}

# Validation Patterns
MAIN_BLOCK_PATTERN: Final = r"if __name__ ?== ?[\'\"]__main__[\'\"]:(.*)"
FUNCTION_CALL_PATTERN: Final = r"(\w+)\("
FUNCTION_DEF_PATTERN: Final = "def {}"

# Built-in Functions (should not trigger missing method warnings)
BUILTIN_FUNCTIONS: Final = {
    "print",
    "input",
    "len",
    "str",
    "int",
    "float",
    "bool",
    "list",
    "dict",
    "set",
    "tuple",
}
