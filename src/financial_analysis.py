"""
Financial analysis module for calculating key metrics and ratios.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from visualizations import Visualization

# Configure logging
logger = logging.getLogger(__name__)

class FinancialAnalysis:
    def __init__(self, income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame):
        """
        Initialize the analyzer with financial statements.
        
        Args:
            income_statement: Income statement DataFrame
            balance_sheet: Balance sheet DataFrame
        """
        self.income_stmt = income_stmt
        self.balance_sheet = balance_sheet
        self.visualizer = Visualization()

    def calculate_growth_rates(self) -> Dict[str, float]:
        """Calculate year-over-year growth rates for key metrics."""
        metrics = {
            'revenue_growth': self._get_growth_rate('Revenue'),
            'net_income_growth': self._get_growth_rate('Net Income'),
            'asset_growth': self._get_growth_rate('Total Assets', is_balance_sheet=True)
        }
        return metrics

    def _get_growth_rate(self, metric: str, is_balance_sheet: bool = False) -> float:
        """Helper method to calculate growth rate for a specific metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            
            # Map common variations of metric names
            metric_variations = {
                'Revenue': ['revenue', 'totalRevenue'],
                'Net Income': ['netIncome'],
                'Total Assets': ['totalAssets']
            }
            
            # Get the exact column name
            col_name = metric_variations.get(metric, [metric.lower()])[0]
            
            if col_name not in df.columns:
                logger.warning("Column " + col_name + " not found. Available columns: " + str(df.columns.tolist()))
                return 0.0
            
            # Get values for the last two periods and convert to numeric
            values = pd.to_numeric(df[col_name], errors='coerce')
            
            # Calculate year-over-year growth using the most recent full year data
            if len(values) >= 2:
                current = values.iloc[0]  # Most recent year
                previous = values.iloc[1]  # Previous year
                
                if previous != 0:
                    growth_rate = ((current - previous) / abs(previous)) * 100
                    logger.info("Growth rate for " + metric + ": " + str(round(growth_rate, 2)) + 
                              "% (Current: " + str(current) + ", Previous: " + str(previous) + ")")
                    return growth_rate
            
            return 0.0
            
        except Exception as e:
            logger.error("Error calculating growth rate for " + metric + ": " + str(e))
            return 0.0

    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """Calculate profitability ratios."""
        try:
            # Get latest values
            revenue = self._get_latest_value('Revenue')
            net_income = self._get_latest_value('Net Income')
            total_assets = self._get_latest_value('Total Assets', True)
            total_equity = self._get_latest_value('Total Equity', True)

            # Calculate ratios
            profit_margin = (net_income / revenue * 100) if revenue != 0 else 0
            roa = (net_income / total_assets * 100) if total_assets != 0 else 0
            roe = (net_income / total_equity * 100) if total_equity != 0 else 0

            logger.info("Profitability ratios - Revenue: " + str(revenue) + ", Net Income: " + str(net_income))
            logger.info("Profitability ratios - Total Assets: " + str(total_assets) + ", Total Equity: " + str(total_equity))
            logger.info("Profitability ratios - Margin: " + str(round(profit_margin, 2)) + "%, ROA: " + str(round(roa, 2)) + "%, ROE: " + str(round(roe, 2)) + "%")

            return {
                'Profit Margin': round(profit_margin, 2),
                'Return On Assets': round(roa, 2),
                'Return On Equity': round(roe, 2)
            }
        except Exception as e:
            logger.error("Error calculating profitability ratios: " + str(e))
            return {'Profit Margin': 0, 'Return On Assets': 0, 'Return On Equity': 0}

    def calculate_liquidity_ratios(self) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        try:
            # Get latest values
            current_assets = self._get_latest_value('Total Current Assets', True)
            current_liabilities = self._get_latest_value('Total Current Liabilities', True)
            total_liabilities = self._get_latest_value('Total Liabilities', True)
            total_equity = self._get_latest_value('Total Equity', True)

            # Calculate ratios
            current_ratio = current_assets / current_liabilities if current_liabilities != 0 else 0
            debt_to_equity = total_liabilities / total_equity if total_equity != 0 else 0

            logger.info("Liquidity ratios - Current Assets: " + str(current_assets) + ", Current Liabilities: " + str(current_liabilities))
            logger.info("Liquidity ratios - Total Liabilities: " + str(total_liabilities) + ", Total Equity: " + str(total_equity))
            logger.info("Liquidity ratios - Current Ratio: " + str(round(current_ratio, 2)) + ", D/E: " + str(round(debt_to_equity, 2)))

            return {
                'Current Ratio': round(current_ratio, 2),
                'Debt To Equity': round(debt_to_equity, 2)
            }
        except Exception as e:
            logger.error("Error calculating liquidity ratios: " + str(e))
            return {'Current Ratio': 0, 'Debt To Equity': 0}

    def _get_latest_value(self, metric: str, is_balance_sheet: bool = False) -> float:
        """Helper method to get latest value for a specific metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            
            # Map common variations of metric names
            metric_variations = {
                'Revenue': ['revenue', 'totalRevenue'],
                'Net Income': ['netIncome', 'netIncome'],
                'Total Assets': ['totalAssets'],
                'Total Equity': ['totalEquity', 'totalStockholdersEquity'],
                'Total Current Assets': ['totalCurrentAssets'],
                'Total Current Liabilities': ['totalCurrentLiabilities'],
                'Total Liabilities': ['totalLiabilities']
            }
            
            # Try each variation of the column name
            col_name = None
            for variation in metric_variations.get(metric, [metric.lower()]):
                if variation in df.columns:
                    col_name = variation
                    break
            
            if col_name is None:
                logger.warning("Column " + metric + " not found. Available columns: " + str(df.columns.tolist()))
                return 0.0
            
            # Get the latest value and convert to numeric
            value = pd.to_numeric(df[col_name].iloc[0], errors='coerce')
            if pd.isna(value):
                logger.warning("Could not convert " + metric + " value to numeric")
                return 0.0
                
            logger.info("Got latest value for " + metric + ": " + str(value))
            return float(value)
            
        except Exception as e:
            logger.error("Error getting latest value for " + metric + ": " + str(e))
            return 0.0

    def get_trend_data(self, metrics: List[str]) -> Dict[str, pd.Series]:
        """Get trend data for specified metrics."""
        trend_data = {}
        
        for metric in metrics:
            try:
                # Determine if metric is from balance sheet
                is_balance_sheet = metric in ['Total Assets', 'Total Equity']
                df = self.balance_sheet if is_balance_sheet else self.income_stmt
                
                # Map common variations of metric names
                metric_variations = {
                    'Revenue': ['revenue', 'totalRevenue'],
                    'Net Income': ['netIncome'],
                    'Total Assets': ['totalAssets'],
                    'Total Equity': ['totalEquity', 'totalStockholdersEquity']
                }
                
                # Try each variation of the column name
                col_name = None
                for variation in metric_variations.get(metric, [metric.lower()]):
                    if variation in df.columns:
                        col_name = variation
                        break
                
                if col_name:
                    series = pd.to_numeric(df[col_name], errors='coerce')
                    if not series.empty and not series.isna().all():
                        trend_data[metric] = series
                        logger.info("Successfully got trend data for " + metric)
                    else:
                        logger.warning("No valid numeric data for " + metric)
                else:
                    logger.warning("Column " + metric + " not found. Available columns: " + str(df.columns.tolist()))
                    
            except Exception as e:
                logger.error("Error getting trend data for " + metric + ": " + str(e))
                
        logger.info("Got trend data for metrics: " + str(list(trend_data.keys())))
        return trend_data

    def analyze(self, symbol: str) -> Dict[str, Dict[str, float]]:
        """Perform financial analysis and create visualizations."""
        try:
            logger.info("Starting analysis for " + symbol)
            
            # Calculate metrics
            profitability_ratios = self.calculate_profitability_ratios()
            liquidity_ratios = self.calculate_liquidity_ratios()
            growth_rates = {
                'Revenue Growth': self._get_growth_rate('Revenue'),
                'Net Income Growth': self._get_growth_rate('Net Income'),
                'Asset Growth': self._get_growth_rate('Total Assets', True)
            }
            
            # Get trend data for visualization
            metrics = ['Revenue']
            trend_data = self.get_trend_data(metrics)
            
            # Create visualizations
            for metric, series in trend_data.items():
                if series.empty:
                    logger.warning("Empty data series for " + metric)
                    continue
                logger.info("Data for " + metric + ": " + str(series.tolist()))
            
            self.visualizer.create_trend_chart(trend_data, symbol + " Revenue Trend")
            
            logger.info("Analysis completed for " + symbol)
            return {
                'Growth Rates': growth_rates,
                'Profitability': profitability_ratios,
                'Liquidity': liquidity_ratios
            }
            
        except Exception as e:
            logger.error("Error in analysis: " + str(e))
            return {
                'Growth Rates': {},
                'Profitability': {},
                'Liquidity': {}
            } 