import logging
from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import os

logger = logging.getLogger(__name__)

class Visualization:
    def __init__(self):
        """Initialize visualization class and ensure output directory exists."""
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")

    def create_trend_chart(self, trend_data: Dict[str, pd.Series], title: str) -> None:
        """Create a line chart showing trends over time."""
        try:
            # Check if we have any non-empty data to plot
            valid_data = {k: v for k, v in trend_data.items() if not v.empty}
            if not valid_data:
                logger.warning("No valid data to plot")
                return

            plt.figure(figsize=(12, 6))
            
            for metric, series in valid_data.items():
                if not series.empty:
                    try:
                        # Convert values to billions for better readability
                        values = pd.to_numeric(series, errors='coerce') / 1e9
                        dates = series.index
                        
                        # Plot the data
                        plt.plot(dates, values, marker='o', label=metric)
                        logger.info(f"Plotted {metric} data points: {len(values)}")
                    except Exception as e:
                        logger.error(f"Error plotting {metric}: {str(e)}")
                        logger.error(f"Data: {series}")
                        continue
            
            plt.title(title)
            plt.xlabel('Year')
            plt.ylabel('Value (Billions USD)')
            plt.legend()
            plt.grid(True)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Format y-axis with simple decimal format
            def format_axis(x, _):
                return '{:.1f}B'.format(x)
            
            plt.gca().yaxis.set_major_formatter(FuncFormatter(format_axis))
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save the plot
            output_path = os.path.join(self.output_dir, f"{title.lower().replace(' ', '_')}.png")
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Successfully created trend chart: {output_path}")
        except Exception as e:
            logger.error(f"Error creating trend chart: {str(e)}")
            logger.error(f"Trend data: {trend_data}")
            raise 