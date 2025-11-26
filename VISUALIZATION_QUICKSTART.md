# 🎨 Quick Start: Visualization Examples

## Try These in the Chat!

### 📊 Sales & Revenue
```
"show me a bar chart of sales data"
"create a line graph of revenue performance"
"plot monthly revenue trends"
```

### 🌡️ Weather & Temperature
```
"create a line graph of temperature over time"
"show me weekly temperature data"
```

### 📈 Market & Performance
```
"make a pie chart of market share"
"visualize performance scores"
"create a bar chart comparing results"
```

### 🎯 Business Analytics
```
"show population growth over time"
"create a histogram of data distribution"
"generate a heatmap visualization"
```

## What Happens

1. **You ask:** "show me a bar chart of sales data"
2. **Agent detects:** Visualization request (bar chart)
3. **Agent generates:** Professional chart with sample data
4. **Agent displays:** Image embedded in chat message
5. **You see:** Beautiful dark-themed visualization!

## Sample Data Themes

The agent recognizes these keywords and generates appropriate sample data:

- **sales** → Quarterly sales (Q1-Q4)
- **temperature/weather** → Weekly readings (Mon-Sun)
- **revenue/profit** → Monthly financials (Jan-Jun)
- **performance/score** → Test scores (Test 1-5)
- **market share** → Company distribution
- **population** → Growth over years

## Tips

✅ **DO:**
- Use natural language: "show me", "create a", "make a"
- Specify chart type: "bar chart", "line graph", "pie chart"
- Add context: "sales", "temperature", "revenue"

❌ **DON'T:**
- Need exact data - agent generates smart samples
- Worry about formatting - agent handles styling
- Need special syntax - just ask naturally!

## Advanced Usage

### Want custom data?
You can upload CSV files directly in the chat!

**CSV Format:**
The agent is smart enough to understand most CSV structures, but for best results:
- **Header Row:** Include clear column names (e.g., "Month", "Revenue", "Category").
- **Data:** Ensure data is clean and consistent.

**Example CSV:**
```csv
Month,Revenue,Expenses
Jan,10000,5000
Feb,12000,5500
Mar,15000,6000
```

**How to use:**
1. Click the **Upload CSV** button (📊 icon) in the chat input.
2. Select your CSV file.
3. Ask a question like:
   - "Visualize this data"
   - "Show me a bar chart of Revenue vs Month"
   - "Analyze the trends in this file"

### Want to customize?
The visualizations automatically match:
- Your dark theme UI
- Professional color scheme
- Responsive sizing

## Example Session

```
User: hi
Agent: Hello! How can I help you today?

User: show me a bar chart of sales data
Agent: I've created a bar chart for you...
[Beautiful bar chart appears showing Q1-Q4 sales]

User: now show me a line graph of temperature
Agent: Here's the temperature line graph...
[Temperature trend chart appears]

User: create a pie chart of market share
Agent: I've generated the market share pie chart...
[Market distribution pie chart appears]
```

## View Generated Images

All visualizations are saved in:
```
E:\agentx\static\visualizations\
```

Images are named with timestamps:
```
viz_20251117_193259_186209.png
viz_20251117_193311_020958.png
```

## Test Script

Run automated tests:
```bash
python test_visualization.py
```

This creates multiple chart types automatically!

---

**Ready to create amazing visualizations? Just ask! 🚀**
