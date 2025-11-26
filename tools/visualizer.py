"""
Visualization tool for generating graphs, charts, and images
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import io
import base64
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """Generate various types of visualizations based on user requests"""
    
    def __init__(self, output_dir: str = "static/visualizations"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('dark_background')
        
    def detect_visualization_request(self, user_input: str) -> Optional[str]:
        """Detect if user is requesting a visualization"""
        user_input_lower = user_input.lower()
        
        # Graph/Chart keywords
        if any(word in user_input_lower for word in [
            "plot", "graph", "chart", "visualize", "show me a",
            "bar chart", "line graph", "pie chart", "scatter plot",
            "histogram", "heatmap", "draw", "display"
        ]):
            # Determine chart type
            if "bar" in user_input_lower:
                return "bar_chart"
            elif "line" in user_input_lower:
                return "line_chart"
            elif "pie" in user_input_lower:
                return "pie_chart"
            elif "scatter" in user_input_lower:
                return "scatter_plot"
            elif "histogram" in user_input_lower:
                return "histogram"
            elif "heatmap" in user_input_lower:
                return "heatmap"
            else:
                # Default to line chart for generic requests
                return "line_chart"
        
        return None
    
    def generate_visualization(self, user_input: str, viz_type: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate visualization based on user request"""
        try:
            # Extract data from user input or use sample data
            if not data:
                data = self._extract_data_from_input(user_input, viz_type)
            
            # Generate the appropriate chart
            if viz_type == "bar_chart":
                filepath = self._create_bar_chart(data)
            elif viz_type == "line_chart":
                filepath = self._create_line_chart(data)
            elif viz_type == "pie_chart":
                filepath = self._create_pie_chart(data)
            elif viz_type == "scatter_plot":
                filepath = self._create_scatter_plot(data)
            elif viz_type == "histogram":
                filepath = self._create_histogram(data)
            elif viz_type == "heatmap":
                filepath = self._create_heatmap(data)
            else:
                filepath = self._create_line_chart(data)
            
            return {
                "success": True,
                "filepath": filepath,
                "visualization_type": viz_type,
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_data_from_input(self, user_input: str, viz_type: str) -> Dict[str, Any]:
        """Extract or generate sample data based on user input"""
        # For demonstration, generate sample data
        # In production, this would parse actual data from user input or use LLM to extract values
        
        user_input_lower = user_input.lower()
        
        # Try to detect topic/theme
        title = "Data Visualization"
        if "sales" in user_input_lower:
            title = "Sales Data"
            labels = ["Q1", "Q2", "Q3", "Q4"]
            values = [45000, 52000, 48000, 61000]
        elif "temperature" in user_input_lower or "weather" in user_input_lower:
            title = "Temperature Over Time"
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            values = [22, 24, 23, 25, 26, 24, 23]
        elif "revenue" in user_input_lower or "profit" in user_input_lower:
            title = "Monthly Revenue"
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            values = [85000, 90000, 88000, 95000, 102000, 98000]
        elif "population" in user_input_lower:
            title = "Population Growth"
            labels = ["2019", "2020", "2021", "2022", "2023"]
            values = [7.5, 7.6, 7.7, 7.8, 7.9]
        elif "market share" in user_input_lower:
            title = "Market Share Distribution"
            labels = ["Company A", "Company B", "Company C", "Company D", "Others"]
            values = [30, 25, 20, 15, 10]
        elif "performance" in user_input_lower or "score" in user_input_lower:
            title = "Performance Scores"
            labels = ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"]
            values = [85, 92, 88, 95, 90]
        else:
            # Generic sample data
            labels = ["Category A", "Category B", "Category C", "Category D", "Category E"]
            values = [23, 45, 56, 78, 32]
        
        return {
            "title": title,
            "labels": labels,
            "values": values,
            "xlabel": "Categories",
            "ylabel": "Values"
        }
    
    def _create_bar_chart(self, data: Dict[str, Any]) -> str:
        """Create a bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = data.get("labels", [])
        values = data.get("values", [])
        title = data.get("title", "Bar Chart")
        
        bars = ax.bar(labels, values, color='#6366f1', alpha=0.8, edgecolor='white', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=10, color='white')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get("xlabel", "Categories"), fontsize=12)
        ax.set_ylabel(data.get("ylabel", "Values"), fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _create_line_chart(self, data: Dict[str, Any]) -> str:
        """Create a line chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = data.get("labels", [])
        values = data.get("values", [])
        title = data.get("title", "Line Chart")
        
        ax.plot(labels, values, marker='o', linewidth=2.5, markersize=8, 
               color='#6366f1', markerfacecolor='#818cf8', markeredgecolor='white', 
               markeredgewidth=2)
        
        # Fill area under curve
        ax.fill_between(range(len(labels)), values, alpha=0.2, color='#6366f1')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get("xlabel", "Categories"), fontsize=12)
        ax.set_ylabel(data.get("ylabel", "Values"), fontsize=12)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _create_pie_chart(self, data: Dict[str, Any]) -> str:
        """Create a pie chart"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        labels = data.get("labels", [])
        values = data.get("values", [])
        title = data.get("title", "Pie Chart")
        
        colors = ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff']
        
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                          colors=colors, startangle=90,
                                          textprops={'fontsize': 11, 'color': 'white'},
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _create_scatter_plot(self, data: Dict[str, Any]) -> str:
        """Create a scatter plot"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate scatter data
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        # Create x, y coordinates
        x = np.arange(len(labels))
        y = values
        
        # Add some random scatter
        x_scatter = x + np.random.normal(0, 0.1, len(x))
        y_scatter = y + np.random.normal(0, max(y) * 0.05, len(y))
        
        ax.scatter(x_scatter, y_scatter, s=100, c='#6366f1', alpha=0.6, 
                  edgecolors='white', linewidth=2)
        
        ax.set_title(data.get("title", "Scatter Plot"), fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get("xlabel", "X Values"), fontsize=12)
        ax.set_ylabel(data.get("ylabel", "Y Values"), fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _create_histogram(self, data: Dict[str, Any]) -> str:
        """Create a histogram"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        values = data.get("values", [])
        # Generate more data points for histogram
        data_points = np.random.normal(np.mean(values), np.std(values) if len(values) > 1 else 10, 1000)
        
        ax.hist(data_points, bins=30, color='#6366f1', alpha=0.7, edgecolor='white', linewidth=1.2)
        
        ax.set_title(data.get("title", "Histogram"), fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(data.get("xlabel", "Values"), fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _create_heatmap(self, data: Dict[str, Any]) -> str:
        """Create a heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Generate sample heatmap data
        size = 10
        heatmap_data = np.random.rand(size, size) * 100
        
        im = ax.imshow(heatmap_data, cmap='RdYlBu_r', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Values', rotation=270, labelpad=20, fontsize=12)
        
        ax.set_title(data.get("title", "Heatmap"), fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        filepath = self._save_plot()
        plt.close()
        
        return filepath
    
    def _save_plot(self) -> str:
        """Save the current plot to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"viz_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor='#0f172a', edgecolor='none')
        
        logger.info(f"Saved visualization to {filepath}")
        return filename  # Return relative path for URL
    
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
