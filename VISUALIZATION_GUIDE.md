# 📊 AgentX Visualization Feature

## Overview
AgentX now supports **automatic graph and chart generation** based on user requests! Simply ask for a visualization in natural language, and the agent will create it for you.

## Supported Visualizations

### 1. Bar Charts 📊
**Use for:** Comparing values across categories
**Examples:**
- "show me a bar chart of sales data"
- "create a bar chart of revenue by quarter"
- "make a bar graph comparing performance"

### 2. Line Graphs 📈
**Use for:** Showing trends over time
**Examples:**
- "create a line graph of temperature over time"
- "plot revenue trends"
- "show me a line chart of performance scores"

### 3. Pie Charts 🥧
**Use for:** Showing proportions and distributions
**Examples:**
- "make a pie chart of market share"
- "create a pie chart showing distribution"
- "visualize the breakdown"

### 4. Scatter Plots 🔵
**Use for:** Showing relationships between variables
**Examples:**
- "create a scatter plot"
- "show scatter plot of data points"

### 5. Histograms 📊
**Use for:** Showing frequency distributions
**Examples:**
- "make a histogram"
- "create a histogram of values"

### 6. Heatmaps 🌡️
**Use for:** Showing data intensity in a grid
**Examples:**
- "generate a heatmap"
- "create a heatmap visualization"

## How It Works

### 1. Natural Language Detection
The agent automatically detects when you want a visualization:
- Keywords: plot, graph, chart, visualize, show me a, draw
- Chart types: bar chart, line graph, pie chart, etc.

### 2. Intelligent Data Extraction
The agent analyzes your request for context:
- **Sales** → Quarterly sales data
- **Temperature/Weather** → Weekly temperature readings
- **Revenue/Profit** → Monthly financial data
- **Performance/Score** → Test scores
- **Market Share** → Company distribution

### 3. Professional Styling
All charts feature:
- Dark theme matching the UI
- High contrast colors (#6366f1 primary)
- Clear labels and titles
- Grid lines for readability
- Value annotations
- Responsive sizing

### 4. Image Display
Visualizations are:
- Saved as PNG files in `static/visualizations/`
- Automatically embedded in chat messages
- Rendered with markdown syntax
- Styled to match the dark theme

## Technical Details

### Backend Implementation
- **Library:** matplotlib with 'Agg' backend (non-interactive)
- **Resolution:** 150 DPI for crisp rendering
- **Format:** PNG with transparent edges
- **Storage:** File-based in `static/visualizations/`

### Frontend Integration
- **Markdown Rendering:** Marked.js with custom image renderer
- **Image Styling:** Rounded corners, borders, shadows
- **Responsive:** Max-width: 100%, auto height
- **URL Handling:** Automatic conversion to absolute URLs

### API Endpoint
- Visualizations served via: `/visualizations/{filename}`
- Static file mounting with FastAPI
- CORS enabled for frontend access

## Example Usage

### In Chat Interface:
```
User: "show me a bar chart of sales data"

Agent: I've created a bar chart for you based on your request.
[Bar chart image appears showing Q1-Q4 sales]
```

### Programmatic Usage:
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "create a line graph of temperature",
        "session_id": "my_session",
        "user_id": "user123"
    }
)

print(response.json()["response"])
# Returns markdown with embedded image
```

## Cleanup

Old visualization files are automatically cleaned up:
- Default retention: 24 hours
- Method: `visualizer.cleanup_old_files(max_age_hours=24)`
- Can be scheduled via cron or background task

## Future Enhancements

### Planned Features:
1. **Custom Data Input** - Upload CSV/Excel files for visualization
2. **Real-time Data** - Connect to databases for live charts
3. **Interactive Charts** - Use Plotly for zoom/pan capabilities
4. **Chart Templates** - Pre-defined chart styles
5. **Export Options** - Download as PDF, SVG, or high-res PNG
6. **Multiple Charts** - Compare multiple datasets side-by-side
7. **Annotations** - Add custom labels and markers

### Data Sources:
- MongoDB task statistics
- Conversation analytics
- User preference trends
- Document analysis results
- Web search result summaries

## Testing

Run the test suite:
```bash
python test_visualization.py
```

This will generate sample visualizations for:
- Bar chart (sales data)
- Line graph (temperature)
- Pie chart (market share)
- Revenue performance

## Integration with Other Features

### Task Analytics
```
"show me a bar chart of my tasks by priority"
"visualize my task completion rate over time"
```

### Document Insights
```
"create a pie chart of document categories"
"plot document sizes"
```

### Conversation Trends
```
"show me a line graph of conversation frequency"
"visualize message counts by hour"
```

## Configuration

Customize visualization settings in `tools/visualizer.py`:

```python
# Output directory
output_dir = "static/visualizations"

# Default style
plt.style.use('dark_background')

# Image quality
plt.savefig(filepath, dpi=150, bbox_inches='tight')

# Color scheme
colors = ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff']
```

## Troubleshooting

### Images not displaying?
1. Check server is running: `curl http://localhost:8000/health`
2. Verify static directory exists: `static/visualizations/`
3. Check browser console for CORS errors
4. Ensure matplotlib is installed: `pip install matplotlib pillow`

### Chart generation fails?
1. Check logs for error messages
2. Verify data extraction is working
3. Ensure sufficient disk space
4. Check matplotlib backend: `matplotlib.use('Agg')`

### Styling issues?
1. Verify dark_background style is loaded
2. Check CSS for `.message-content img` rules
3. Ensure marked.js is rendering markdown correctly

## Credits

Built with:
- **matplotlib** - Chart generation
- **pillow** - Image processing
- **FastAPI** - Static file serving
- **Marked.js** - Markdown rendering

---

**Enjoy creating beautiful visualizations with AgentX! 📊✨**
