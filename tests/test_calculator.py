import pytest
from tools.calculator import CalculatorTool

def test_calculator_basic():
    calc = CalculatorTool()
    result = calc.execute("2 + 2")
    assert result["success"] == True
    assert result["result"] == 4

def test_calculator_complex():
    calc = CalculatorTool()
    result = calc.execute("pow(2, 3) + 5 * 2")
    assert result["success"] == True
    assert result["result"] == 18

def test_calculator_math_func():
    calc = CalculatorTool()
    result = calc.execute("sqrt(16)")
    assert result["success"] == True
    assert result["result"] == 4.0

def test_calculator_intent_stripping():
    calc = CalculatorTool()
    result = calc.execute("calculate 10 / 2")
    assert result["success"] == True
    assert result["result"] == 5.0

def test_calculator_error():
    calc = CalculatorTool()
    result = calc.execute("2 / 0")
    assert result["success"] == False
    assert "division by zero" in str(result["error"])
