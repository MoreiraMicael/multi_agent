import os
import subprocess

class TestRunnerAgent:
    def __init__(self, work_dir):
        self.name = "TestRunnerAgent"
        self.work_dir = work_dir
        self.system_message = "You are a strict test runner. Your job is to execute the provided Python file and report any errors or test failures."

    def run_tests(self, file_path: str, mode: str = "script") -> dict:
        """
        Executes the Python file as a script or with pytest and captures output and errors.
        If the script appears to require input(), provide a sequence of mock inputs to avoid hanging.
        mode: 'script' (default) or 'pytest'
        Returns a dict with 'success', 'stdout', 'stderr', 'mode'.
        """
        result = {
            'success': False,
            'stdout': '',
            'stderr': '',
            'mode': mode
        }
        try:
            if mode == "pytest":
                cmd = ["pytest", file_path, "--maxfail=1", "--disable-warnings", "-q"]
                proc = subprocess.run(
                    cmd,
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Check if the file uses input()
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                if "input(" in code:
                    # Provide a sequence of mock inputs (e.g., guesses 0-9, then -1 to quit)
                    mock_inputs = "1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n-1\n"
                    proc = subprocess.run(
                        ["python", file_path],
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True,
                        input=mock_inputs,
                        timeout=30
                    )
                else:
                    proc = subprocess.run(
                        ["python", file_path],
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
            result['stdout'] = proc.stdout
            result['stderr'] = proc.stderr
            result['success'] = proc.returncode == 0
        except Exception as e:
            result['stderr'] = str(e)
            result['success'] = False
        return result
