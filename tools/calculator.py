import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CalculatorTool:
    """
    A tool for performing mathematical calculations.
    Uses a safe subset of Python's math library.
    """
    
    def __init__(self):
        self.allowed_names = {
            k: v for k, v in math.__dict__.items() 
            if not k.startswith("__")
        }
        self.allowed_names.update({
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
        })

    def execute(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        """
        try:
            # Clean up the expression
            # Remove "calculate" or "what is" if present
            clean_expr = expression.lower()
            for prefix in ["calculate", "what is", "solve"]:
                if clean_expr.startswith(prefix):
                    clean_expr = clean_expr[len(prefix):]
            
            clean_expr = clean_expr.strip(" ?=")
            
            # Evaluate
            result = eval(clean_expr, {"__builtins__": {}}, self.allowed_names)
            
            return {
                "success": True,
                "result": result,
                "expression": clean_expr
            }
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
