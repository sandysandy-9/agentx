from tools.calculator import CalculatorTool
import sys

try:
    calc = CalculatorTool()
    print("Calculator initialized")
    
    res = calc.execute("2 + 2")
    print(f"2 + 2 = {res}")
    
    res = calc.execute("sqrt(16)")
    print(f"sqrt(16) = {res}")
    
    print("Debug finished successfully")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
