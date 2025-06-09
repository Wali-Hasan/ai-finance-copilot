"""
Visualization module for creating financial charts and graphs.
"""
from typing import Dict, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

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
        try:
            fig = go.Figure()
            
            # Convert to numeric and sort by index
            y_values = pd.to_numeric(data, errors='coerce')
            
            # Format y-values to billions for better readability
            if np.max(np.abs(y_values)) > 1e9:
                y_values = y_values / 1e9
                y_suffix = "B"
            elif np.max(np.abs(y_values)) > 1e6:
                y_values = y_values / 1e6
                y_suffix = "M"
            else:
                y_suffix = ""
            
            # Create hover text
            hover_text = []
            for x, y in zip(data.index, y_values):
                hover_text.append(metric_name + ": " + str(round(y, 2)) + y_suffix + "<br>Date: " + str(x))
            
            # Create the trace
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=y_values,
                    mode='lines+markers',
                    name=metric_name,
                    line=dict(width=3),
                    hovertext=hover_text,
                    hoverinfo='text'
                )
            )
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title=metric_name + " (" + y_suffix + ")",
                template="plotly_white",
                showlegend=True,
                hovermode='closest',
                yaxis=dict(
                    tickformat=".2f",
                    title_standoff=25
                ),
                xaxis=dict(
                    tickangle=-45,
                    title_standoff=25
                ),
                margin=dict(t=50, l=50, r=50, b=50)
            )
            
            return fig
            
        except Exception as e:
            logger.error("Error in create_metric_trend: " + str(e))
            raise

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
        try:
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

            # Create hover text
            hover_text = []
            for k, v in processed_ratios.items():
                if abs(v) > 0.01:
                    hover_text.append(k + ": " + str(round(v, 2)) + "%")
                else:
                    hover_text.append(k + ": " + str(round(v, 4)))

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=list(processed_ratios.keys()),
                    y=list(processed_ratios.values()),
                    text=hover_text,
                    textposition='auto',
                    hoverinfo='text'
                )
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Ratio",
                yaxis_title="Value",
                template="plotly_white",
                showlegend=False,
                xaxis_tickangle=-45,
                yaxis=dict(tickformat=".2f")
            )
            
            return fig
            
        except Exception as e:
            logger.error("Error in create_ratio_comparison: " + str(e))
            raise

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
        try:
            # Convert any Series to scalar values and format names
            processed_rates = {}
            for k, v in growth_rates.items():
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
                    processed_rates[formatted_key] = v
                else:
                    processed_rates[formatted_key] = 0.0

            # Create hover text
            hover_text = []
            for k, v in processed_rates.items():
                hover_text.append(k + ": " + str(round(v, 1)) + "%")

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    y=list(processed_rates.keys()),
                    x=list(processed_rates.values()),
                    orientation='h',
                    text=hover_text,
                    textposition='auto',
                    hoverinfo='text'
                )
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Growth Rate (%)",
                yaxis_title="Metric",
                template="plotly_white",
                showlegend=False,
                height=400,
                xaxis=dict(tickformat=".1f")
            )
            
            # Add a vertical line at x=0 to show positive/negative growth
            fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="gray")
            
            return fig
            
        except Exception as e:
            logger.error("Error in create_growth_chart: " + str(e))
            raise

class Visualization:
    def __init__(self, output_dir: str = 'output'):
        """Initialize visualization with output directory."""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info("Created output directory: " + self.output_dir)

    def plot_metric(self, series: pd.Series, metric: str) -> go.Figure:
        """Create a line plot for a single metric."""
        try:
            # Convert index to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(series.index):
                series.index = pd.to_datetime(series.index)
            
            # Sort by date
            series = series.sort_index()
            
            # Create the plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=series.index,
                y=series.values,
                mode='lines+markers',
                name=metric
            ))
            
            # Update layout
            fig.update_layout(
                title=metric + " Over Time",
                xaxis_title="Date",
                yaxis_title="Value",
                showlegend=True
            )
            
            logger.info("Plotted " + metric + " data points: " + str(len(series)))
            return fig
            
        except Exception as e:
            logger.error("Error plotting " + metric + ": " + str(e))
            logger.error("Data: " + str(series))
            return None

    def create_trend_chart(self, trend_data: Dict[str, pd.Series], title: str) -> None:
        """Create a trend chart from multiple series."""
        try:
            fig = go.Figure()
            
            for metric, series in trend_data.items():
                # Convert values to billions for better readability
                values_in_billions = series / 1e9
                
                fig.add_trace(go.Scatter(
                    x=series.index,
                    y=values_in_billions,
                    mode='lines+markers',
                    name=metric
                ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Value (Billions USD)",
                showlegend=True,
                template="plotly_dark"
            )
            
            # Save the plot
            output_path = os.path.join(self.output_dir, title.lower().replace(' ', '_') + ".html")
            fig.write_html(output_path)
            
            logger.info("Successfully created trend chart: " + output_path)
            
        except Exception as e:
            logger.error("Error creating trend chart: " + str(e))
            logger.error("Trend data: " + str(trend_data))

    def create_growth_chart(self, growth_rates: Dict[str, float], title: str) -> go.Figure:
        """Create a horizontal bar chart for growth rates."""
        try:
            metrics = list(growth_rates.keys())
            values = list(growth_rates.values())
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=values,
                y=metrics,
                orientation='h',
                marker_color='rgb(55, 83, 109)'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Growth Rate (%)",
                yaxis_title="Metric",
                showlegend=False,
                template="plotly_dark"
            )
            
            return fig
            
        except Exception as e:
            logger.error("Error creating growth chart: " + str(e))
            return None

    def create_ratio_comparison(self, ratios: Dict[str, float], title: str) -> go.Figure:
        """Create a bar chart for ratio comparison."""
        try:
            metrics = list(ratios.keys())
            values = list(ratios.values())
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=metrics,
                y=values,
                marker_color='rgb(55, 83, 109)'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Ratio",
                yaxis_title="Value",
                showlegend=False,
                template="plotly_dark"
            )
            
            return fig
            
        except Exception as e:
            logger.error("Error creating ratio comparison: " + str(e))
            return None 