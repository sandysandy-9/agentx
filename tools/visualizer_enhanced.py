"""
Enhanced Visualization tool with Plotly, custom data, advanced charts, and AI analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import os
from datetime import datetime
import logging
import json
import re
from sklearn.linear_model import LinearRegression
from scipy import stats

logger = logging.getLogger(__name__)


class EnhancedVisualizer:
    """Generate interactive visualizations with Plotly and AI-powered insights"""
    
    def __init__(self, output_dir: str = "static/visualizations"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Dark theme colors matching UI
        self.colors = {
            'primary': '#6366f1',
            'secondary': '#818cf8',
            'accent': '#a5b4fc',
            'background': '#0f172a',
            'paper': '#1e293b',
            'text': '#f1f5f9'
        }
        
    def detect_visualization_request(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Detect visualization request and extract parameters"""
        user_input_lower = user_input.lower()
        
        request = {
            'type': None,
            'interactive': 'interactive' in user_input_lower or 'plotly' in user_input_lower,
            'analyze': 'analyze' in user_input_lower or 'insights' in user_input_lower or 'trends' in user_input_lower,
            'data': None
        }
        
        # Detect chart type
        if any(word in user_input_lower for word in ["bar chart", "bar graph", "bar"]):
            request['type'] = "bar_chart"
        elif any(word in user_input_lower for word in ["line graph", "line chart", "line", "trend"]):
            request['type'] = "line_chart"
        elif any(word in user_input_lower for word in ["pie chart", "pie"]):
            request['type'] = "pie_chart"
        elif any(word in user_input_lower for word in ["scatter plot", "scatter"]):
            request['type'] = "scatter_plot"
        elif any(word in user_input_lower for word in ["histogram", "distribution"]):
            request['type'] = "histogram"
        elif any(word in user_input_lower for word in ["heatmap", "heat map"]):
            request['type'] = "heatmap"
        elif any(word in user_input_lower for word in ["area chart", "area"]):
            request['type'] = "area_chart"
        elif any(word in user_input_lower for word in ["bubble chart", "bubble"]):
            request['type'] = "bubble_chart"
        elif any(word in user_input_lower for word in ["3d", "three dimensional"]):
            request['type'] = "3d_scatter"
        elif any(word in user_input_lower for word in ["box plot", "box chart"]):
            request['type'] = "box_plot"
        elif any(word in user_input_lower for word in ["violin plot", "violin"]):
            request['type'] = "violin_plot"
        elif any(word in user_input_lower for word in ["funnel", "conversion"]):
            request['type'] = "funnel_chart"
        elif any(word in user_input_lower for word in ["gauge", "meter", "speedometer"]):
            request['type'] = "gauge"
        elif any(word in user_input_lower for word in ["plot", "graph", "chart", "visualize", "analyze", "show"]):
            request['type'] = "bar_chart"  # Default
        else:
            return None
        
        # Try to extract inline data
        request['data'] = self._extract_inline_data(user_input)
        
        return request
    
    def _extract_inline_data(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extract data from user input if provided"""
        # Look for patterns like: [10, 20, 30] or {data: [values]}
        try:
            # Try to find JSON-like structure first
            json_match = re.search(r'(\{.*\})', user_input)
            if json_match:
                try:
                    # Replace single quotes with double quotes for valid JSON
                    json_str = json_match.group(1).replace("'", '"')
                    data = json.loads(json_str)
                    # Ensure it's a dictionary or list of dictionaries
                    if isinstance(data, (dict, list)):
                        return data
                except json.JSONDecodeError:
                    pass

            # Try to find list of numbers: [1, 2, 3]
            list_match = re.search(r'\[([\d\s,.-]+)\]', user_input)
            if list_match:
                values_str = list_match.group(1)
                if values_str.strip():
                    values = [float(x.strip()) for x in values_str.split(',') if x.strip()]
                    return {"Value": values, "Index": list(range(1, len(values) + 1))}
            
            # Try to find simple key-value pairs: "A: 10, B: 20"
            # This is a bit risky as it might match normal text, so we'll be strict
            kv_pattern = r'([A-Za-z0-9]+)\s*:\s*(\d+(?:\.\d+)?)'
            matches = re.findall(kv_pattern, user_input)
            if len(matches) >= 2:
                categories = [m[0] for m in matches]
                values = [float(m[1]) for m in matches]
                return {"Category": categories, "Value": values}
                
        except Exception as e:
            logger.warning(f"Error extracting inline data: {e}")
            
        return None
    
    def generate_visualization(self, user_input: str, request: Dict[str, Any], custom_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Generate visualization based on request"""
        try:
            # Get or generate data
            if custom_data is not None:
                data = custom_data
            elif request.get('data'):
                data = pd.DataFrame(request['data'])
            else:
                data = self._generate_sample_data(user_input, request['type'])
            
            # Generate insights if requested
            insights = None
            if request.get('analyze'):
                insights = self._analyze_data(data, request['type'])
            
            # Create visualization
            if request.get('interactive', True):
                filepath = self._create_plotly_chart(data, request['type'], user_input)
            else:
                # Fallback to matplotlib for static
                filepath = self._create_static_chart(data, request['type'], user_input)
            
            return {
                "success": True,
                "filepath": filepath,
                "visualization_type": request['type'],
                "interactive": request.get('interactive', True),
                "insights": insights,
                "data_summary": {
                    "rows": len(data),
                    "columns": list(data.columns) if hasattr(data, 'columns') else []
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_sample_data(self, user_input: str, chart_type: str) -> pd.DataFrame:
        """Generate smart sample data based on context"""
        user_input_lower = user_input.lower()
        
        # Detect topic/theme
        if "sales" in user_input_lower:
            return pd.DataFrame({
                'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
                'Sales': [45000, 52000, 48000, 61000],
                'Target': [50000, 50000, 50000, 55000]
            })
        elif "temperature" in user_input_lower or "weather" in user_input_lower:
            return pd.DataFrame({
                'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'Temperature': [22, 24, 23, 25, 26, 24, 23],
                'Humidity': [65, 70, 68, 72, 75, 71, 69]
            })
        elif "revenue" in user_input_lower or "profit" in user_input_lower:
            return pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [85000, 90000, 88000, 95000, 102000, 98000],
                'Expenses': [60000, 62000, 61000, 65000, 70000, 68000]
            })
        elif "population" in user_input_lower:
            return pd.DataFrame({
                'Year': ['2019', '2020', '2021', '2022', '2023'],
                'Population': [7.5, 7.6, 7.7, 7.8, 7.9]
            })
        elif "market share" in user_input_lower:
            return pd.DataFrame({
                'Company': ['Company A', 'Company B', 'Company C', 'Company D', 'Others'],
                'Share': [30, 25, 20, 15, 10]
            })
        elif "performance" in user_input_lower or "score" in user_input_lower:
            return pd.DataFrame({
                'Test': ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5'],
                'Score': [85, 92, 88, 95, 90]
            })
        else:
            # Generic sample data
            return pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Value': [23, 45, 56, 78, 32]
            })
    
    def _analyze_data(self, data: pd.DataFrame, chart_type: str) -> Dict[str, Any]:
        """AI-powered data analysis and insights"""
        insights = {
            'summary': {},
            'trends': [],
            'anomalies': [],
            'predictions': None
        }
        
        # Get numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return insights
        
        # Basic statistics
        for col in numeric_cols:
            values = data[col].dropna()
            insights['summary'][col] = {
                'mean': float(values.mean()),
                'median': float(values.median()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max()),
                'range': float(values.max() - values.min())
            }
            
            # Detect trend
            if len(values) > 2:
                x = np.arange(len(values)).reshape(-1, 1)
                y = values.values
                model = LinearRegression()
                model.fit(x, y)
                slope = model.coef_[0]
                
                if abs(slope) > values.std() * 0.1:
                    direction = "increasing" if slope > 0 else "decreasing"
                    insights['trends'].append({
                        'column': col,
                        'direction': direction,
                        'slope': float(slope),
                        'confidence': 'high' if abs(slope) > values.std() * 0.5 else 'medium'
                    })
            
            # Detect anomalies (values beyond 2 std devs)
            mean = values.mean()
            std = values.std()
            anomalies_idx = np.where(np.abs(values - mean) > 2 * std)[0]
            
            if len(anomalies_idx) > 0:
                for idx in anomalies_idx:
                    insights['anomalies'].append({
                        'column': col,
                        'index': int(idx),
                        'value': float(values.iloc[idx]),
                        'deviation': float((values.iloc[idx] - mean) / std)
                    })
        
        # Simple prediction (next 2 points using linear regression)
        if len(numeric_cols) > 0 and len(data) > 3:
            col = numeric_cols[0]
            values = data[col].dropna().values
            x = np.arange(len(values)).reshape(-1, 1)
            model = LinearRegression()
            model.fit(x, values)
            
            future_x = np.array([[len(values)], [len(values) + 1]])
            predictions = model.predict(future_x)
            
            insights['predictions'] = {
                'column': col,
                'next_values': [float(p) for p in predictions],
                'method': 'linear_regression'
            }
        
        return insights
    
    def _create_plotly_chart(self, data: pd.DataFrame, chart_type: str, user_input: str) -> str:
        """Create interactive Plotly chart"""
        
        # Extract title from user input or generate
        title = self._extract_title(user_input, chart_type)
        
        # Common layout
        layout = dict(
            template='plotly_dark',
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['paper'],
            font=dict(color=self.colors['text'], family='Inter, sans-serif'),
            title=dict(text=title, font=dict(size=20)),
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        fig = None
        
        if chart_type == "bar_chart":
            x_col = data.columns[0]
            y_col = data.columns[1] if len(data.columns) > 1 else data.columns[0]
            fig = go.Figure(data=[
                go.Bar(x=data[x_col], y=data[y_col], marker_color=self.colors['primary'])
            ])
            fig.update_layout(**layout)
            
        elif chart_type == "line_chart":
            x_col = data.columns[0]
            fig = go.Figure()
            for col in data.columns[1:]:
                fig.add_trace(go.Scatter(
                    x=data[x_col], y=data[col], mode='lines+markers',
                    name=col, line=dict(width=3)
                ))
            fig.update_layout(**layout)
            
        elif chart_type == "pie_chart":
            fig = go.Figure(data=[go.Pie(
                labels=data[data.columns[0]],
                values=data[data.columns[1]],
                hole=0.3,
                marker=dict(colors=[self.colors['primary'], self.colors['secondary'], 
                                   self.colors['accent'], '#c7d2fe', '#e0e7ff'])
            )])
            fig.update_layout(**layout)
            
        elif chart_type == "scatter_plot":
            x_col, y_col = data.columns[0], data.columns[1]
            fig = go.Figure(data=[go.Scatter(
                x=data[x_col], y=data[y_col], mode='markers',
                marker=dict(size=12, color=self.colors['primary'], opacity=0.7)
            )])
            fig.update_layout(**layout)
            
        elif chart_type == "area_chart":
            x_col = data.columns[0]
            fig = go.Figure()
            for col in data.columns[1:]:
                fig.add_trace(go.Scatter(
                    x=data[x_col], y=data[col], fill='tonexty',
                    mode='lines', name=col
                ))
            fig.update_layout(**layout)
            
        elif chart_type == "bubble_chart":
            if len(data.columns) >= 3:
                fig = go.Figure(data=[go.Scatter(
                    x=data[data.columns[0]], 
                    y=data[data.columns[1]],
                    mode='markers',
                    marker=dict(
                        size=data[data.columns[2]],
                        color=self.colors['primary'],
                        opacity=0.6,
                        sizemode='diameter',
                        sizeref=2. * max(data[data.columns[2]]) / (40. ** 2)
                    )
                )])
                fig.update_layout(**layout)
                
        elif chart_type == "3d_scatter":
            if len(data.columns) >= 3:
                fig = go.Figure(data=[go.Scatter3d(
                    x=data[data.columns[0]],
                    y=data[data.columns[1]],
                    z=data[data.columns[2]],
                    mode='markers',
                    marker=dict(size=8, color=self.colors['primary'], opacity=0.8)
                )])
                fig.update_layout(**layout)
                
        elif chart_type == "box_plot":
            fig = go.Figure()
            for col in data.select_dtypes(include=[np.number]).columns:
                fig.add_trace(go.Box(y=data[col], name=col))
            fig.update_layout(**layout)
            
        elif chart_type == "violin_plot":
            fig = go.Figure()
            for col in data.select_dtypes(include=[np.number]).columns:
                fig.add_trace(go.Violin(y=data[col], name=col, box_visible=True))
            fig.update_layout(**layout)
            
        elif chart_type == "funnel_chart":
            fig = go.Figure(go.Funnel(
                y=data[data.columns[0]],
                x=data[data.columns[1]],
                marker=dict(color=self.colors['primary'])
            ))
            fig.update_layout(**layout)
            
        elif chart_type == "gauge":
            value = data[data.columns[1]].iloc[0] if len(data) > 0 else 50
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.colors['primary']},
                    'steps': [
                        {'range': [0, 50], 'color': self.colors['paper']},
                        {'range': [50, 75], 'color': self.colors['accent']},
                        {'range': [75, 100], 'color': self.colors['secondary']}
                    ]
                }
            ))
            fig.update_layout(**layout)
        
        else:
            # Default to bar chart
            fig = go.Figure(data=[go.Bar(x=data[data.columns[0]], y=data[data.columns[1]])])
            fig.update_layout(**layout)
        
        # Save as HTML
        filepath = self._save_plotly_chart(fig)
        return filepath
    
    def _create_static_chart(self, data: pd.DataFrame, chart_type: str, user_input: str) -> str:
        """Fallback to matplotlib for static charts"""
        # Reuse old visualizer logic here
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.style.use('dark_background')
        
        if chart_type == "bar_chart":
            ax.bar(data[data.columns[0]], data[data.columns[1]], color=self.colors['primary'])
        elif chart_type == "line_chart":
            for col in data.columns[1:]:
                ax.plot(data[data.columns[0]], data[col], marker='o', linewidth=2.5)
        
        plt.tight_layout()
        filepath = self._save_static_plot()
        plt.close()
        
        return filepath
    
    def _extract_title(self, user_input: str, chart_type: str) -> str:
        """Extract or generate chart title"""
        # Simple extraction - can be enhanced
        if "sales" in user_input.lower():
            return "Sales Data"
        elif "temperature" in user_input.lower():
            return "Temperature Over Time"
        elif "revenue" in user_input.lower():
            return "Revenue Analysis"
        elif "market share" in user_input.lower():
            return "Market Share Distribution"
        else:
            return chart_type.replace('_', ' ').title()
    
    def _save_plotly_chart(self, fig) -> str:
        """Save Plotly chart as interactive HTML"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"viz_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        fig.write_html(filepath, config={'responsive': True})
        
        logger.info(f"Saved interactive visualization to {filepath}")
        return filename
    
    def _save_static_plot(self) -> str:
        """Save matplotlib plot as PNG"""
        import matplotlib.pyplot as plt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"viz_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor=self.colors['background'], edgecolor='none')
        
        logger.info(f"Saved static visualization to {filepath}")
        return filename
    
    def parse_csv_data(self, csv_content: str) -> pd.DataFrame:
        """Parse CSV data from string"""
        from io import StringIO
        return pd.read_csv(StringIO(csv_content))
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old visualization files"""
        try:
            now = datetime.now()
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_age.total_seconds() > max_age_hours * 3600:
                        os.remove(filepath)
                        logger.info(f"Removed old visualization: {filename}")
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
