"""
Main Streamlit application for the AI Finance Copilot.
"""
import streamlit as st
import pandas as pd
import logging
import os
from typing import Dict, Any
from data_loader import DataLoader
from financial_analysis import FinancialAnalysis
from ai_insights import AIInsights
from visualizations import Visualization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Finance Copilot", layout="wide")

def format_metric_value(value: float) -> str:
    """Format metric value for display."""
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        else:
            return f"{value:.2f}%"
    return str(value)

class FinanceApp:
    def __init__(self):
        """Initialize the finance application."""
        self.data_loader = DataLoader()
        self.insights_generator = AIInsights()

    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Analyze a stock given its ticker symbol."""
        try:
            logger.info("Starting analysis for " + str(symbol))
            
            # Load financial data
            income_stmt, balance_sheet = self.data_loader.get_financial_data(symbol)
            
            if income_stmt is None or balance_sheet is None:
                logger.error("Failed to load financial data for " + str(symbol))
                return {
                    'error': "Failed to load financial data. Please check the ticker symbol and try again."
                }

            # Perform financial analysis
            analyzer = FinancialAnalysis(income_stmt, balance_sheet)
            analysis_results = analyzer.analyze(symbol)
            
            # Combine results
            results = {
                'symbol': symbol,
                'metrics': analysis_results,
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet
            }
            
            logger.info("Analysis completed successfully for " + str(symbol))
            return results
            
        except Exception as e:
            logger.error("Error in analysis: " + str(e))
            return {
                'error': "An error occurred during analysis: " + str(e)
            }

    def process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process financial data from a CSV file."""
        try:
            logger.info("Processing CSV file: " + str(file_path))
            income_stmt, balance_sheet = self.data_loader.load_from_csv(file_path)
            
            if income_stmt is None or balance_sheet is None:
                return {
                    'error': "Failed to load data from CSV file."
                }
            
            # Extract symbol from filename or use generic name
            symbol = os.path.splitext(os.path.basename(file_path))[0].upper()
            
            # Perform analysis
            analyzer = FinancialAnalysis(income_stmt, balance_sheet)
            analysis_results = analyzer.analyze(symbol)
            
            return {
                'symbol': symbol,
                'metrics': analysis_results,
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet
            }
            
        except Exception as e:
            logger.error("Error processing CSV: " + str(e))
            return {
                'error': "Failed to process CSV file: " + str(e)
            }

def main():
    st.title("AI Finance Copilot 📊")
    st.write("Upload financial data or enter a ticker symbol for AI-powered financial analysis.")

    # Initialize session state for data persistence
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = None
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False

    # Initialize components
    app = FinanceApp()
    visualizer = Visualization()

    # Sidebar for data input
    st.sidebar.header("Data Input")
    input_method = st.sidebar.radio("Choose input method:", ["Ticker Symbol", "CSV Upload"])

    # Add a reset button in the sidebar at the top
    if st.session_state.analysis_done:
        if st.sidebar.button("Reset Analysis"):
            st.session_state.financial_data = None
            st.session_state.analysis_done = False
            st.session_state.current_insight = ""  # Clear the current insight
            st.session_state.last_question = ""    # Clear the last question
            st.experimental_rerun()

    progress_container = st.empty()
    error_container = st.empty()

    # Only show input fields if analysis hasn't been done
    if not st.session_state.analysis_done:
        if input_method == "Ticker Symbol":
            ticker = st.sidebar.text_input("Enter ticker symbol (e.g., AAPL):", "AAPL")
            if st.sidebar.button("Analyze"):
                progress_container.text("Step 1/4: Fetching financial data...")
                try:
                    st.session_state.financial_data = app.analyze_stock(ticker)
                    if 'error' in st.session_state.financial_data:
                        error_container.error(st.session_state.financial_data['error'])
                        return
                    progress_container.text("Step 2/4: Data loaded successfully")
                    st.session_state.analysis_done = True
                except Exception as e:
                    error_container.error("Error loading data: " + str(e))
                    return
        else:
            uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")
            if uploaded_file is not None:
                progress_container.text("Step 1/4: Processing CSV file...")
                try:
                    # Save the uploaded file temporarily
                    with open("temp_upload.csv", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Process the saved file
                    st.session_state.financial_data = app.process_csv("temp_upload.csv")
                    
                    # Clean up the temporary file
                    if os.path.exists("temp_upload.csv"):
                        os.remove("temp_upload.csv")
                    
                    if 'error' in st.session_state.financial_data:
                        error_container.error(st.session_state.financial_data['error'])
                        return
                    progress_container.text("Step 2/4: CSV data loaded successfully")
                    st.session_state.analysis_done = True
                except Exception as e:
                    error_container.error("Error loading CSV: " + str(e))
                    # Clean up on error
                    if os.path.exists("temp_upload.csv"):
                        os.remove("temp_upload.csv")
                    return

    if st.session_state.financial_data and 'metrics' in st.session_state.financial_data:
        try:
            # Get metrics
            progress_container.text("Step 3/4: Calculating financial metrics...")
            metrics = st.session_state.financial_data['metrics']
            
            progress_container.text("Step 4/4: Preparing visualizations...")

            # Create tabs for different analyses
            tab1, tab2, tab3 = st.tabs(["📈 Key Metrics", "📊 Visualizations", "🤖 AI Insights"])

            with tab1:
                st.header("Key Financial Metrics")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.subheader("Growth Rates")
                    for metric, value in metrics['Growth Rates'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            str(round(value, 2)) + "%"
                        )

                with col2:
                    st.subheader("Profitability")
                    for metric, value in metrics['Profitability'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            str(round(value, 2)) + "%"
                        )

                with col3:
                    st.subheader("Liquidity")
                    for metric, value in metrics['Liquidity'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            str(round(value, 2))
                        )

            with tab2:
                st.header("Financial Visualizations")
                col1, col2 = st.columns(2)

                with col1:
                    # Revenue Trend Chart
                    try:
                        revenue_data = st.session_state.financial_data['income_stmt']['revenue'] if 'revenue' in st.session_state.financial_data['income_stmt'].columns else st.session_state.financial_data['income_stmt']['totalRevenue']
                        if not revenue_data.empty:
                            revenue_fig = visualizer.plot_metric(revenue_data, "Revenue")
                            if revenue_fig:
                                st.plotly_chart(revenue_fig, use_container_width=True)
                        else:
                            st.warning("No revenue data available")
                    except Exception as e:
                        logger.error("Error creating revenue chart: " + str(e))
                        st.warning("Could not create revenue trend chart")

                    # Growth Rates Chart
                    try:
                        if metrics['Growth Rates']:
                            growth_fig = visualizer.create_growth_chart(
                                metrics['Growth Rates'],
                                "Growth Rates"
                            )
                            if growth_fig:
                                st.plotly_chart(growth_fig, use_container_width=True)
                    except Exception as e:
                        st.error("Error creating growth chart: " + str(e))

                with col2:
                    # Profitability Chart
                    try:
                        if metrics['Profitability']:
                            profitability_fig = visualizer.create_ratio_comparison(
                                metrics['Profitability'],
                                "Profitability Ratios"
                            )
                            if profitability_fig:
                                st.plotly_chart(profitability_fig, use_container_width=True)
                    except Exception as e:
                        st.error("Error creating profitability chart: " + str(e))

                    # Liquidity Chart
                    try:
                        if metrics['Liquidity']:
                            liquidity_fig = visualizer.create_ratio_comparison(
                                metrics['Liquidity'],
                                "Liquidity Ratios"
                            )
                            if liquidity_fig:
                                st.plotly_chart(liquidity_fig, use_container_width=True)
                    except Exception as e:
                        st.error("Error creating liquidity chart: " + str(e))

            with tab3:
                st.header("AI Financial Insights")
                st.write("Ask questions about the financial data or select from common questions:")

                # Initialize insights state if not exists
                if 'current_insight' not in st.session_state:
                    st.session_state.current_insight = ""
                if 'last_question' not in st.session_state:
                    st.session_state.last_question = ""

                # Common questions
                questions = [
                    "What are the key strengths in this company's financials?",
                    "What are the potential red flags or concerns?",
                    "How does the growth trajectory look?",
                    "Is the company financially healthy?",
                    "What's the company's efficiency in using its assets?",
                    "How does their profitability compare to industry standards?",
                    "Analyze their debt management strategy",
                    "What are the main revenue drivers?"
                ]

                # Create two columns for questions
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    user_question = st.text_input("Ask a question:", key="custom_question")
                with col2:
                    selected_question = st.selectbox(
                        "Or choose a common question:", 
                        [""] + questions,
                        key="common_questions"
                    )

                # Create a container for the insight
                insight_container = st.empty()

                # Function to generate and display insight
                def generate_and_display_insight(question):
                    if question:
                        with st.spinner("Generating insight..."):
                            # Set the last question before generating insight
                            st.session_state.last_question = question
                            
                            insight = app.insights_generator.generate_insights(
                                question=question,  # Pass the question explicitly
                                symbol=st.session_state.financial_data['symbol'],
                                metrics=st.session_state.financial_data['metrics'],
                                income_stmt=st.session_state.financial_data['income_stmt'],
                                balance_sheet=st.session_state.financial_data['balance_sheet']
                            )
                            st.session_state.current_insight = insight
                    
                    if st.session_state.current_insight:
                        # Format the insight for markdown display
                        formatted_insight = st.session_state.current_insight.replace('•', '*')  # Replace bullets with markdown asterisks
                        formatted_insight = formatted_insight.replace('\n*', '\n\n*')  # Add extra newline for markdown list
                        insight_container.markdown(formatted_insight)

                # Handle user input
                if user_question:
                    if user_question != st.session_state.last_question:
                        st.session_state.current_insight = ""  # Clear previous answer
                        generate_and_display_insight(user_question)
                elif selected_question:
                    if selected_question != st.session_state.last_question:
                        st.session_state.current_insight = ""  # Clear previous answer
                        generate_and_display_insight(selected_question)
                elif st.session_state.current_insight:  # Show previous insight if exists
                    insight_container.write(st.session_state.current_insight)

                # Add a clear button
                if st.session_state.current_insight:
                    if st.button("Clear Answer"):
                        st.session_state.current_insight = ""
                        st.session_state.last_question = ""
                        insight_container.empty()
                        st.experimental_rerun()

            # Clear the progress message
            progress_container.empty()

        except Exception as e:
            error_container.error("Error analyzing data: " + str(e))
            logger.error("Analysis error: " + str(e))

if __name__ == "__main__":
    main() 