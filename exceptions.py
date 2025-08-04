"""
Exception Classes for Multi-Agent System

This module defines custom exception classes for better error handling
and debugging throughout the multi-agent system.
"""

from typing import Any, Optional


class MultiAgentException(Exception):
    """Base exception class for multi-agent system errors."""

    def __init__(self, message: str, details: Optional[Any] = None):
        """
        Initialize the exception.

        Args:
            message (str): Error message
            details (Optional[Any]): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details


class AgentCreationError(MultiAgentException):
    """Raised when agent creation fails."""

    pass


class CodeGenerationError(MultiAgentException):
    """Raised when code generation fails."""

    pass


class CodeValidationError(MultiAgentException):
    """Raised when code validation fails."""

    pass


class TestExecutionError(MultiAgentException):
    """Raised when test execution fails."""

    pass


class FileOperationError(MultiAgentException):
    """Raised when file operations fail."""

    pass


class ConfigurationError(MultiAgentException):
    """Raised when configuration is invalid."""

    pass


class AgentRegistryError(MultiAgentException):
    """Raised when agent registry operations fail."""

    pass


class FeedbackError(MultiAgentException):
    """Raised when collecting agent feedback fails."""

    pass
