"""
Visualization module for creating financial charts and graphs.
"""
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class FinancialVisualizer:
    def create_metric_trend(self, 
                          data: pd.Series,
                          title: str,
                          metric_name: str) -> go.Figure:
        """
        Create a line chart showing the trend of a financial metric over time.
        
        Args:
            data: Time series data for the metric
            title: Chart title
            metric_name: Name of the metric being plotted
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data.values,
                mode='lines+markers',
                name=metric_name,
                line=dict(width=3)
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title=metric_name,
            template="plotly_white",
            showlegend=True,
            hovermode='x'
        )
        
        return fig

    def create_ratio_comparison(self, 
                              ratios: Dict[str, float],
                              title: str) -> go.Figure:
        """
        Create a bar chart comparing different financial ratios.
        
        Args:
            ratios: Dictionary of ratio names and values
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        # Convert any Series to scalar values and format names
        processed_ratios = {}
        for k, v in ratios.items():
            # Format the key name
            formatted_key = k.replace('_', ' ').title()
            
            # Process the value
            if isinstance(v, pd.Series):
                v = v.iloc[0] if not v.empty else 0.0
            try:
                v = float(v)
            except (ValueError, TypeError):
                v = 0.0
            
            if pd.notnull(v):
                processed_ratios[formatted_key] = v
            else:
                processed_ratios[formatted_key] = 0.0

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=list(processed_ratios.keys()),
                y=list(processed_ratios.values()),
                text=[f"{v:.2f}%" if abs(v) > 1 else f"{v:.2f}" for v in processed_ratios.values()],
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Ratio",
            yaxis_title="Value (%)",
            template="plotly_white",
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig

    def create_growth_chart(self, 
                          growth_rates: Dict[str, float],
                          title: str) -> go.Figure:
        """
        Create a horizontal bar chart showing growth rates.
        
        Args:
            growth_rates: Dictionary of growth metrics and their values
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        # Convert any Series to scalar values
        processed_rates = {}
        for k, v in growth_rates.items():
            if isinstance(v, pd.Series):
                v = v.iloc[0] if not v.empty else 0.0
            processed_rates[k] = float(v) if pd.notnull(v) else 0.0

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=list(processed_rates.keys()),
                x=list(processed_rates.values()),
                orientation='h',
                text=[f"{v:.1f}%" for v in processed_rates.values()],
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Growth Rate (%)",
            yaxis_title="Metric",
            template="plotly_white",
            showlegend=False,
            height=400
        )
        
        # Add a vertical line at x=0 to show positive/negative growth
        fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray")
        
        return fig 