import os
from orchestrator import simulate_agent_conversation
from scenarios import scenarios

def test_scenario_1_end_to_end(tmp_path):
    # Use scenario 1 and override workspace to tmp_path
    scenario = scenarios["1"].copy()
    scenario["file_name"] = "test_generated_code.py"
    os.environ["WORKSPACE_PATH"] = str(tmp_path)
    result = simulate_agent_conversation(scenario)
    assert result is not None
    assert os.path.exists(result)
    with open(result, "r", encoding="utf-8") as f:
        code = f.read()
    assert "class NumberGuessingGame" in code
