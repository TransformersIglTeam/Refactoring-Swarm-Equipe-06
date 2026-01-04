import subprocess
import os 


class PylintRunner:
    def __init__(self,timeout = 30):
        self.timeout = timeout
    def run_analysis(self,target_path): # hada ydir path -> abs path bach nevitiw les problem t3 windows
        target_path = os.path.abspath(target_path)
        command = ["pylint",
        target_path,
        "--output-format=json",
        #"--rcfile=.pylintrc" m7bsh ymchi hada (lazmlou logic of either creating a file or already in repo)
        ]


        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {"stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Pylint execution timed out."}
        except Exception as e:
            return {"error": str(e)}
