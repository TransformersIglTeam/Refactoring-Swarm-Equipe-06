class ComplexityParser:
    def parse(self, raw_data):
        """Simplifies Radon data for the AI Auditor."""
        summary = []
        
        for file_path, functions in raw_data.get("complexity", {}).items():
            
            for func in functions:
                
                
                if func.get("complexity", 0) > 5:  # complex shi
                    summary.append({
                        "type": "High Complexity",

                        "entity": func.get("name"),
                        "score": func.get("complexity"),
                        "rank": func.get("rank"), # ranking system mn A ll F
                        
                        "message": f"Function '{func.get('name')}' is getting hard to read."})
        
        
        for file_path, metrics in raw_data.get("maintainability", {}).items():
            mi_score = metrics.get("mi", 100)
            if mi_score < 50:
                summary.append({
                    "type": "Low Maintainability",
                    "score": round(mi_score, 2),

                    "message": "This file is very difficult to maintain."})
                
        return summary