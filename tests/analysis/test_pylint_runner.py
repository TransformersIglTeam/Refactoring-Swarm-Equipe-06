import sys
import os

# 1. Tell Python to look in the 'src' folder
sys.path.append(os.path.abspath("src"))

# 2. Import your class
from tools.analysis.PylintRunner import PylintRunner

def test_pylint():
    print("🚀 Starting Pylint Test...")
    
    # Initialize your runner
    runner = PylintRunner(timeout=10)
    
    # Run analysis on our dirty file
    report = runner.run_analysis("dirty_code.py")
    
    if "error" in report:
        print(f"❌ Test Failed: {report['error']}")
    else:
        print("✅ Test Successful! Raw Output:")
        print(report["stdout"]) # This should be a long JSON string

if __name__ == "__main__":
    test_pylint()