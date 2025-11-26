"""
Quick test script for visualization feature
"""

import requests
import json

API_BASE = "http://localhost:8000"

# Test cases for different visualizations
test_cases = [
    "show me a bar chart of sales data",
    "create a line graph of temperature over time",
    "make a pie chart of market share",
    "plot revenue performance",
]

def test_visualization(message):
    print(f"\n{'='*60}")
    print(f"Testing: {message}")
    print('='*60)
    
    response = requests.post(
        f"{API_BASE}/chat",
        json={
            "message": message,
            "user_id": "test_user",
            "session_id": "viz_test_001"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse: {data['response']}\n")
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("Testing AgentX Visualization Capabilities")
    print("="*60)
    
    for test in test_cases:
        result = test_visualization(test)
        if not result:
            print("Test failed!")
            break
    
    print("\n" + "="*60)
    print("Testing complete! Check the frontend to view visualizations.")
    print("="*60)
