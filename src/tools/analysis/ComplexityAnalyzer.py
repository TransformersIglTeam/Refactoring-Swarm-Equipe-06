import subprocess
import json
import os

class ComplexityAnalyzer:
    def __init__(self, timeout=30):
        self.timeout = timeout

    def run_analysis(self, target_path):
        """Runs radon to get complexity (CC) and maintainability (MI) metrics."""
        target_path = os.path.abspath(target_path)
        
        
        cc_command = ["radon", "cc", target_path, "--json"]
        
        
        mi_command = ["radon", "mi", target_path, "--json"]

        try:
            

            cc_result = subprocess.run(cc_command, capture_output=True, text=True, timeout=self.timeout)
            

            mi_result = subprocess.run(mi_command, capture_output=True, text=True, timeout=self.timeout)

            # nreturniw a merged dictionary
            return {
                "complexity": json.loads(cc_result.stdout) if cc_result.stdout else {},
                "maintainability": json.loads(mi_result.stdout) if mi_result.stdout else {},
                "error": cc_result.stderr if cc_result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}