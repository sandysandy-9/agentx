import requests
import json
import os

API_BASE = "http://localhost:8000"

def test_csv_visualization():
    print("Testing CSV Visualization...")
    
    # 1. Create a sample CSV
    csv_content = """Month,Sales,Profit
Jan,100,20
Feb,120,25
Mar,150,30
Apr,170,35
May,200,45"""
    
    print(f"Sample CSV Data:\n{csv_content}\n")
    
    # 2. Send visualization request with CSV data
    payload = {
        "message": "create a bar chart of Sales by Month",
        "csv_data": csv_content,
        "chart_type": "bar_chart",
        "analyze": True
    }
    
    try:
        response = requests.post(f"{API_BASE}/visualize", json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print("✅ Visualization generated successfully!")
            print(f"Filepath: {result.get('filepath')}")
            print(f"Type: {result.get('visualization_type')}")
            
            if result.get("insights"):
                print("\nInsights:")
                print(json.dumps(result['insights'], indent=2))
            else:
                print("\n⚠️ No insights generated.")
                
        else:
            print(f"❌ Visualization failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")

if __name__ == "__main__":
    test_csv_visualization()
