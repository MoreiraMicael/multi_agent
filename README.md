# Multi-Agent Python Development System

A sophisticated multi-agent system built with AutoGen that demonstrates collaborative AI agents working together to develop Python code. The system includes specialized agents for coding, code review, quality assurance, and user interaction.

## 🚀 Features

- **Modular Agent Architecture**: Separate agent modules for different roles
- **Multiple Agent Types**: Coder, Reviewer, QA Specialist, User, and Dumb User agents
- **Agent Registry System**: Extensible factory pattern for adding new agent types
- **Configurable LLM Backend**: Works with Ollama and other OpenAI-compatible APIs
- **Environment Variable Support**: Customizable workspace paths via `MULTI_AGENT_WORKSPACE_PATH`
- **Automated Code Generation**: Extracts and saves generated Python code
- **Comprehensive Testing**: pytest-based test suite for all components
- **Logging Support**: Structured logging for debugging and monitoring
- **VS Code Integration**: Optimized for development in Visual Studio Code
- **Code Quality Tools**: Black formatting, Flake8 linting, and import sorting

## 📁 Project Structure

```
├── agents/                     # Agent module definitions
│   ├── base_agent.py          # Base SimpleAgent class
│   ├── registry.py            # Agent registry and factory system
│   ├── coder_agent.py         # Expert Python coder agent
│   ├── reviewer_agent.py      # Code review specialist agent
│   ├── qa_agent.py           # Quality assurance agent
│   ├── user_agent.py         # Clear requirements user agent
│   └── dumb_user_agent.py    # Vague requirements user agent
├── coding_workspace/          # Generated code output directory
├── tests/                     # Test suite
│   └── test_agents.py        # Agent creation and integration tests
├── .vscode/                   # VS Code configuration
│   ├── settings.json         # Editor settings and tool configuration
│   ├── launch.json           # Debug and run configurations
│   └── extensions.json       # Recommended extensions
├── main.py                    # Main orchestration script
├── config.py                  # Central configuration management
├── requirements.txt           # Python dependencies
├── OAI_CONFIG_LIST           # LLM configuration file
└── README.md                 # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Ollama running locally (or access to OpenAI API)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**:

   ```powershell
   git clone <repository-url>
   cd autogen-ollama-project
   ```

2. **Create and activate virtual environment**:

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Ollama** (if using Ollama):

   - Ensure Ollama is running: `ollama serve`
   - Pull the required model: `ollama pull llama3:8b`
   - The `OAI_CONFIG_LIST` file should already be configured for Ollama

5. **Open in VS Code**:
   ```powershell
   code .
   ```
   - Install recommended extensions when prompted
   - VS Code will automatically detect the Python interpreter in your virtual environment

## 🎯 Usage

### Running the Main Application

```powershell
python main.py
```

The application provides three scenarios:

1. **Clear Requirements (Regular User)**: Well-defined requirements with specific details
2. **Vague Requirements (Dumb User)**: Ambiguous requirements to test agent collaboration
3. **File Processing Utility**: Complex file handling scenario

### Example Scenarios

#### Scenario 1: Calculator Class

```
Create a Python class called 'Calculator' that can perform basic arithmetic operations...
```

#### Scenario 2: Vague Requirements

```
I need some kind of calculator thing that does math stuff. Make it good and follow best practices...
```

#### Scenario 3: File Utility

```
Build a file utility that can read different file formats and extract information...
```

### Generated Output

- Generated code is saved to `coding_workspace/multi_agent_generated_code.py`
- Chat history shows the collaboration process between agents
- Each agent contributes their expertise to the final solution

## 🧪 Testing

### Running All Tests

```powershell
pytest tests/ -v
```

### Running Specific Test Categories

```powershell
# Test agent creation
pytest tests/test_agents.py::TestAgentCreation -v

# Test configuration
pytest tests/test_agents.py::TestConfiguration -v

# Test system integration
pytest tests/test_agents.py::TestSystemIntegration -v
```

### Test Coverage

```powershell
pytest tests/ --cov=. --cov-report=html
```

## 🔧 Code Quality

### Formatting with Black

```powershell
black .
```

### Linting with Flake8

```powershell
flake8 .
```

### Import Sorting with isort

```powershell
isort .
```

### Run All Quality Checks

```powershell
black . && isort . && flake8 .
```

## ⚙️ Configuration

### LLM Configuration

Edit `OAI_CONFIG_LIST` to configure your LLM backend:

```json
[
  {
    "model": "llama3:8b",
    "base_url": "http://localhost:11434/v1",
    "api_key": "ollama",
    "price": [0, 0]
  }
]
```

### Application Configuration

Modify `config.py` to adjust:

- Model temperature
- Maximum conversation rounds
- Workspace paths
- Chat behavior

#### Environment Variables

The system supports the following environment variables for configuration:

- **`MULTI_AGENT_WORKSPACE_PATH`**: Override the default workspace directory path
  ```bash
  export MULTI_AGENT_WORKSPACE_PATH="/custom/workspace/path"
  ```

#### Agent Registry

The system includes an extensible agent registry that allows for easy addition of new agent types:

```python
from agents.registry import register_agent, create_agent

# Register a custom agent
def my_custom_agent(llm_config, work_dir):
    return SimpleAgent("CustomAgent", "Custom system message")

register_agent("custom", my_custom_agent)

# Create the agent
agent = create_agent("custom", llm_config, work_dir)
```

### VS Code Configuration

The `.vscode/` directory contains:

- **settings.json**: Python interpreter, formatting, linting, and testing configuration
- **launch.json**: Debug and run configurations for main script and tests
- **extensions.json**: Recommended extensions for optimal development experience

## 🤖 Agent Roles

### Coder Agent

- Expert Python developer
- Writes clean, efficient, well-documented code
- Follows Python best practices and PEP 8
- Implements requested features accurately

### Reviewer Agent

- Senior code reviewer
- Checks code correctness and quality
- Identifies bugs and security issues
- Suggests improvements and optimizations

### QA Specialist Agent

- Quality assurance expert
- Develops testing strategies
- Creates comprehensive test cases
- Validates requirements compliance

### User Agent

- Provides clear, detailed requirements
- Answers questions about functionality
- Reviews and approves solutions
- Gives constructive feedback

### Dumb User Agent

- Simulates real-world vague requirements
- Tests team's ability to handle ambiguity
- Provides incomplete or conflicting information
- Helps improve requirement clarification processes

## 🚀 Advanced Usage

### Custom Agent Development

1. Create a new agent file in `agents/`
2. Implement the `get_<agent_name>_agent(llm_config, work_dir)` function
3. Import and add to the agent list in `main.py`
4. Add tests in `tests/test_agents.py`

### Integration with Other LLMs

1. Update `OAI_CONFIG_LIST` with your API configuration
2. Modify `config.py` if needed for specific LLM requirements
3. Test with `pytest tests/test_agents.py`

### Extending Scenarios

Add new scenarios to the `scenarios` dictionary in `main.py`:

```python
"4": {
    "prompt": "Your custom prompt here...",
    "use_dumb_user": False,
    "description": "Your scenario description"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Issues**:

   - Ensure Ollama is running: `ollama serve`
   - Check if the model is available: `ollama list`
   - Verify the base_url in configuration

2. **Import Errors**:

   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`
   - Check PYTHONPATH in VS Code settings

3. **Test Failures**:
   - Run tests with more verbose output: `pytest -v -s`
   - Check agent configuration in test fixtures
   - Verify workspace permissions

### Debug Mode

Use VS Code's debug configurations:

1. Set breakpoints in your code
2. Press F5 or use "Run and Debug" panel
3. Select "Debug Main Script" or "Debug Tests"
4. Step through the execution

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

### Development Workflow

```powershell
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
black . && isort . && flake8 . && pytest

# Commit and push
git add .
git commit -m "Add your feature description"
git push origin feature/your-feature-name
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙋‍♂️ Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the test cases for examples
3. Check agent system messages for role clarification
4. Open an issue with detailed error information

## 🔗 Related Resources

- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Ollama Documentation](https://ollama.ai/docs)
- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [pytest Documentation](https://docs.pytest.org/)

---

**Happy Coding! 🎉**
