import subprocess
import json
import os

class ComplexityAnalyzer:
    def __init__(self, timeout=30):
        self.timeout = timeout

    def run_analysis(self, target_path):
        """Runs radon to get complexity (CC) and maintainability (MI) metrics."""
        try:
            import radon.complexity as cc
            import radon.metrics as mi
        except ImportError:
            return {"error": "Radon library is not installed. Please install radon to use complexity analysis."}
        
        target_path = os.path.abspath(target_path)
        
        try:
            # Use radon API instead of subprocess
            cc_results = cc.cc_visit(target_path)
            mi_results = mi.mi_visit(target_path, multi=True)
            
            return {
                "complexity": [block._asdict() for block in cc_results],
                "maintainability": mi_results
            }
        except Exception as e:
            return {"error": str(e)}