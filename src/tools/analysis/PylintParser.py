import json

class PylintResult:
    """A container for parsed Pylint data."""
    def __init__(self, issues: list, score: float = 0.0) -> None:
        self.issues = issues
        self.score = score   
        
    def get_critical_issues(self):
        """Returns only Errors and Fatal issues."""
        return [i for i in self.issues if i['type'] in ['error', 'fatal']]

class PylintParser:
    def parse(self, raw_json):
        """Parses raw JSON string from PylintRunner into a PylintResult object."""
        try:
            if not raw_json or raw_json.strip() == "":
                return PylintResult([], 0.0)

            data = json.loads(raw_json)
            parsed_issues = []
            
            for item in data:
    
    
    
                    parsed_issues.append({

                    "line": item.get("line"),
                    "type": item.get("type"),     
                    
                    
                    "symbol": item.get("symbol"), 
                    "message": item.get("message"),
                    "module": item.get("module")})
            
            # Note: In JSON mode, Pylint doesn't always provide the X/10 score 
            # easily without extra flags. For now, we return the issues.
            return PylintResult(parsed_issues)
            
        except json.JSONDecodeError:
            print("Error: Could not decode Pylint JSON.")
            return PylintResult([], 0.0)