"""
Main Streamlit application for the AI Finance Copilot.
"""
import streamlit as st
import pandas as pd
import logging
from data_loader import FinancialDataLoader
from financial_analysis import FinancialAnalyzer
from ai_insights import AIAnalyst
from visualizations import FinancialVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="AI Finance Copilot", layout="wide")

def format_metric_value(value) -> str:
    """Format metric value for display, handling different types."""
    try:
        if isinstance(value, pd.Series):
            value = value.iloc[0] if not value.empty else 0.0
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
            if abs(value) > 1:
                return f"{value:.2f}%"
            return f"{value:.2f}"
        return str(value)
    except:
        return "N/A"

def main():
    st.title("AI Finance Copilot 📊")
    st.write("Upload financial data or enter a ticker symbol for AI-powered financial analysis.")

    # Initialize components
    data_loader = FinancialDataLoader()
    ai_analyst = AIAnalyst()
    visualizer = FinancialVisualizer()

    # Sidebar for data input
    st.sidebar.header("Data Input")
    input_method = st.sidebar.radio("Choose input method:", ["Ticker Symbol", "CSV Upload"])

    financial_data = None
    progress_container = st.empty()
    error_container = st.empty()

    if input_method == "Ticker Symbol":
        ticker = st.sidebar.text_input("Enter ticker symbol (e.g., AAPL):", "AAPL")
        if st.sidebar.button("Analyze"):
            progress_container.text("Step 1/4: Fetching financial data...")
            try:
                financial_data = data_loader.load_from_ticker(ticker)
                if not data_loader.validate_data(financial_data):
                    error_container.error("Invalid or incomplete data received from financial APIs")
                    return
                progress_container.text("Step 2/4: Data loaded successfully")
            except Exception as e:
                error_container.error(f"Error loading data: {str(e)}")
                return
    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")
        if uploaded_file is not None:
            progress_container.text("Step 1/4: Processing CSV file...")
            try:
                financial_data = data_loader.load_from_csv(uploaded_file)
                if not data_loader.validate_data(financial_data):
                    error_container.error("Invalid or incomplete data in CSV file")
                    return
                progress_container.text("Step 2/4: CSV data loaded successfully")
            except Exception as e:
                error_container.error(f"Error loading CSV: {str(e)}")
                return

    if financial_data and data_loader.validate_data(financial_data):
        try:
            # Initialize analyzer with the data
            progress_container.text("Step 3/4: Calculating financial metrics...")
            analyzer = FinancialAnalyzer(financial_data['income_statement'], 
                                       financial_data['balance_sheet'])

            # Calculate metrics
            metrics = {
                'growth_rates': analyzer.calculate_growth_rates(),
                'profitability': analyzer.calculate_profitability_ratios(),
                'liquidity': analyzer.calculate_liquidity_ratios()
            }
            
            progress_container.text("Step 4/4: Preparing visualizations...")

            # Create tabs for different analyses
            tab1, tab2, tab3 = st.tabs(["📈 Key Metrics", "📊 Visualizations", "🤖 AI Insights"])

            with tab1:
                st.header("Key Financial Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Growth Rates")
                    for metric, value in metrics['growth_rates'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            format_metric_value(value)
                        )
                
                with col2:
                    st.subheader("Profitability")
                    for metric, value in metrics['profitability'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            format_metric_value(value)
                        )
                
                with col3:
                    st.subheader("Liquidity")
                    for metric, value in metrics['liquidity'].items():
                        st.metric(
                            metric.replace('_', ' ').title(),
                            format_metric_value(value)
                        )

            with tab2:
                st.header("Financial Visualizations")
                
                # Get trend data
                trend_data = analyzer.get_trend_data()
                
                # Create and display charts
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        if not trend_data['Revenue'].empty:
                            revenue_fig = visualizer.create_metric_trend(
                                trend_data['Revenue'],
                                "Revenue Trend",
                                "Revenue"
                            )
                            st.plotly_chart(revenue_fig, use_container_width=True)
                        else:
                            st.warning("No revenue trend data available")
                    except Exception as e:
                        logger.error(f"Error creating revenue chart: {str(e)}")
                        st.warning("Could not create revenue trend chart")
                    
                    try:
                        if metrics['growth_rates']:
                            growth_fig = visualizer.create_growth_chart(
                                metrics['growth_rates'],
                                "Growth Rates"
                            )
                            st.plotly_chart(growth_fig, use_container_width=True)
                        else:
                            st.warning("No growth rate data available")
                    except Exception as e:
                        logger.error(f"Error creating growth chart: {str(e)}")
                        st.warning("Could not create growth rates chart")
                
                with col2:
                    try:
                        if metrics['profitability']:
                            profitability_fig = visualizer.create_ratio_comparison(
                                metrics['profitability'],
                                "Profitability Ratios"
                            )
                            st.plotly_chart(profitability_fig, use_container_width=True)
                        else:
                            st.warning("No profitability data available")
                    except Exception as e:
                        logger.error(f"Error creating profitability chart: {str(e)}")
                        st.warning("Could not create profitability ratios chart")
                    
                    try:
                        if metrics['liquidity']:
                            liquidity_fig = visualizer.create_ratio_comparison(
                                metrics['liquidity'],
                                "Liquidity Ratios"
                            )
                            st.plotly_chart(liquidity_fig, use_container_width=True)
                        else:
                            st.warning("No liquidity data available")
                    except Exception as e:
                        logger.error(f"Error creating liquidity chart: {str(e)}")
                        st.warning("Could not create liquidity ratios chart")

            with tab3:
                st.header("AI Financial Insights")
                
                # Predefined questions
                questions = [
                    "Summarize the company's financial health",
                    "What stands out about their profitability?",
                    "How is their growth trajectory?",
                    "Analyze their liquidity position",
                    "Custom question"
                ]
                
                selected_question = st.selectbox("Choose a question:", questions)
                
                if selected_question == "Custom question":
                    user_question = st.text_input("Enter your question:")
                    if user_question:
                        with st.spinner("Generating insight..."):
                            insight = ai_analyst.generate_insight(
                                user_question,
                                financial_data,
                                metrics
                            )
                            st.write(insight)
                elif selected_question:
                    with st.spinner("Generating insight..."):
                        insight = ai_analyst.generate_insight(
                            selected_question,
                            financial_data,
                            metrics
                        )
                        st.write(insight)
            
            # Clear the progress message
            progress_container.empty()
            
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            error_container.error(f"Error analyzing data: {str(e)}")
            return

if __name__ == "__main__":
    main() 