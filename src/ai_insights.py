"""
AI insights module using OpenAI's GPT models for financial analysis.
"""
from typing import Dict, Any
import os
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        """Initialize the OpenAI client."""
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_insight(self, 
                        question: str,
                        financial_data: Dict[str, pd.DataFrame],
                        metrics: Dict[str, Any]) -> str:
        """
        Generate AI insights based on financial data and metrics.
        
        Args:
            question: User's question about the financial data
            financial_data: Dict containing financial statements
            metrics: Dict containing calculated financial metrics
            
        Returns:
            str: AI-generated insight
        """
        # Prepare the context for the AI
        context = self._prepare_context(financial_data, metrics)
        
        # Create the prompt
        prompt = f"""As a financial analyst, analyze the following financial data and metrics:

{context}

Question: {question}

Provide a clear, concise analysis focusing specifically on the question asked."""

        # Get completion from OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior financial analyst providing insights based on company financial data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message['content']
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
                    context += f"- {metric.replace('_', ' ').title()}: {value:.2f}\n"
            else:
                context += f"- {values:.2f}\n"

        # Add recent financial statement data
        context += "\nRecent Financial Data:\n"
        for statement_name, df in financial_data.items():
            context += f"\n{statement_name.replace('_', ' ').title()} (Most Recent):\n"
            # Get the most recent period's data
            recent_data = df.iloc[0] if not df.empty else pd.Series()
            for item, value in recent_data.items():
                context += f"- {item}: {value:,.2f}\n"

        return context 