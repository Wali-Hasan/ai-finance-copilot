"""
AI insights module using OpenAI's GPT models for financial analysis.
"""
from typing import Dict, Any
import os
import openai
import pandas as pd
from dotenv import load_dotenv
import logging
import streamlit as st

load_dotenv()

logger = logging.getLogger(__name__)

class AIInsights:
    def __init__(self):
        """Initialize the AI insights generator."""
        self.analyst = AIAnalyst()

    def generate_insights(self, question: str, symbol: str, metrics: Dict[str, Any], 
                         income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> str:
        """Generate AI insights from financial data and metrics."""
        try:
            # Prepare financial data
            financial_data = {
                'income_statement': income_stmt,
                'balance_sheet': balance_sheet
            }
            
            # Generate insights using AIAnalyst
            insight = self.analyst.generate_insight(
                question=question,
                financial_data=financial_data,
                metrics=metrics
            )
            
            return insight
            
        except Exception as e:
            logger.error("Error generating insight: " + str(e))
            return "Error generating insights. Please try again."

class AIAnalyst:
    def __init__(self):
        """Initialize the OpenAI client."""
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_insight(self, 
                        question: str,
                        financial_data: Dict[str, pd.DataFrame],
                        metrics: Dict[str, Any]) -> str:
        """Generate AI insights based on financial data and metrics."""
        context = self._prepare_context(financial_data, metrics)
        
        prompt = f"""Analyze the following financial data and provide a clear answer to this question:

Question: "{question}"

Financial Context:
{context}

Format your response exactly like this:
1. Start with a one-sentence direct answer
2. Then provide 3-4 key points, each on a new line
3. Format each point as:
   * [Specific Metric]: [Value in $X.XX B/M format] - [Brief explanation of significance]

Example:
The company shows strong financial performance in three key areas:

* Profit Margin: 23.97% - Demonstrates excellent cost management and pricing power

* Revenue Growth: $391.04B (up 2.02%) - Indicates steady market expansion

* Operating Efficiency: $123.22B operating income - Shows strong core business operations"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a precise financial analyst.
Your responses must:
- Start with a clear, direct answer
- Use asterisk (*) bullet points
- Put each point on a new line
- Format numbers as $X.XX B/M
- Keep explanations brief but specific"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Very low temperature for consistent formatting
                max_tokens=400
            )
            
            # Clean up the response formatting
            response_text = response.choices[0].message['content']
            
            # Ensure proper formatting
            lines = response_text.split('\n')
            formatted_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('*'):
                    formatted_lines.extend(['', line])  # Add blank line before bullets
                else:
                    formatted_lines.append(line)
            
            return '\n'.join(formatted_lines).strip()
            
        except Exception as e:
            return f"Error generating insight: {str(e)}"

    def _prepare_context(self, 
                        financial_data: Dict[str, pd.DataFrame],
                        metrics: Dict[str, Any]) -> str:
        """Prepare financial data context for the AI prompt."""
        context = "Financial Metrics:\n"
        
        # Add calculated metrics
        for category, values in metrics.items():
            context += f"\n{category.replace('_', ' ').title()}:\n"
            if isinstance(values, dict):
                for metric, value in values.items():
                    if isinstance(value, (int, float)):
                        context += f"- {metric.replace('_', ' ').title()}: {value:.2f}\n"
                    else:
                        context += f"- {metric.replace('_', ' ').title()}: {value}\n"
            else:
                if isinstance(values, (int, float)):
                    context += f"- {values:.2f}\n"
                else:
                    context += f"- {values}\n"

        # Add recent financial statement data
        context += "\nRecent Financial Data:\n"
        for statement_name, df in financial_data.items():
            context += f"\n{statement_name.replace('_', ' ').title()} (Most Recent):\n"
            if not df.empty:
                # Get the most recent period's data
                recent_data = df.iloc[0]
                for item, value in recent_data.items():
                    if pd.notna(value):  # Check if value is not NaN
                        if isinstance(value, (int, float)):
                            context += f"- {item}: {value:,.2f}\n"
                        else:
                            context += f"- {item}: {value}\n"

        return context 