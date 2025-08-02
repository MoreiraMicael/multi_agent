import textwrap

scenarios = {
    "1": {
        "prompt": textwrap.dedent(
            """
            Create a Python class called 'NumberGuessingGame' that implements a guess-a-number game between 0-9. The class should:
            - Generate a random number between 0-9 for the player to guess
            - Track the number of attempts
            - Provide feedback (too high, too low, correct)
            - Keep track of game statistics (games played, wins, average attempts)
            - Include proper error handling for invalid inputs
            - Have methods to start a new game and display statistics
            - Include comprehensive docstring and type hints
        """
        ),
        "use_dumb_user": False,
        "description": "Clear requirements with regular user",
        "file_name": "guess_game_logic.py",
    },
    "2": {
        "prompt": """I need some kind of calculator thing that does math stuff. Make it good and \
        follow best practices. It should be enterprise-ready and scalable.""",
        "use_dumb_user": True,
        "description": "Vague requirements with dumb user",
        "file_name": "calculator_logic.py",
    },
    "3": {
        "prompt": textwrap.dedent(
            """
            Build a file utility that can read different file formats and extract information.
            It should support JSON, CSV, and text files. Include error handling for file not found,
            invalid formats, and permission issues. Make it extensible for future file types.

            After the file utility is implemented, trigger the ImprovementAgent to review all agent class
            source files (e.g., Coder, Reviewer, QA, User, Dumb_User, LoggingAgent) and generate a
            comprehensive, human-readable report with suggestions for code quality, documentation,
            design, and prompt engineering. The report must be written to a log file named
            'improvement_report.log'.
            """
        ),
        "use_dumb_user": False,
        "description": "File utility with ImprovementAgent review/report",
        "improvement_agent": True,
        "file_name": "improvement_report.log",
    },
    "4": {
        "prompt": textwrap.dedent(
            """
            The team must design and implement a new agent called 'ImprovementAgent'.

            Requirements:
            - The ImprovementAgent should review the source code of all other agent classes in the project (e.g., Coder, Reviewer, QA, User, Dumb_User, LoggingAgent).
            - It should analyze and suggest improvements with a focus on:
              - Code quality (style, type hints, error handling, etc.)
              - Docstring and documentation
              - Architectural/design patterns
              - Prompt engineering (system messages and agent instructions)
            - The ImprovementAgent should passively generate a comprehensive, human-readable report.
            - The report must be written to a log file.
            - The ImprovementAgent must be modular and reusable for other projects.
            - Include comprehensive docstring, type hints, and robust error handling.
            - Provide an example of how to integrate the ImprovementAgent with the existing agent workflow.

            Additional Context:
            - The ImprovementAgent is not responsible for reviewing configurations, prompts, or workflow integration—only agent class code.
            - In the future, another agent will focus on other review areas.
            """
        ),
        "use_dumb_user": False,
        "description": "Agents collaborate to create a new ImprovementAgent",
    },
}
