# AI Finance Copilot

An AI-powered financial analysis tool that provides insights into company financials using data from Yahoo Finance/Alpha Vantage and OpenAI's GPT models.

## Features

- Load financial data from CSV files or fetch by ticker symbol
- Automated financial ratio analysis
- Interactive charts and visualizations
- AI-powered financial insights and analysis
- User-friendly Streamlit interface

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   FMP_API_KEY=your_key_here
   ```
4. Run the app:
   ```bash
   streamlit run src/app.py
   ```

## Project Structure

- `src/`
  - `app.py` - Main Streamlit application
  - `data_loader.py` - Data loading and API integration
  - `financial_analysis.py` - Financial calculations and ratios
  - `ai_insights.py` - OpenAI integration for insights
  - `visualizations.py` - Chart generation functions

## Usage

1. Launch the app using `streamlit run src/app.py`
2. Either:
   - Upload a CSV file with financial data
   - Enter a ticker symbol (e.g., AAPL, MSFT)
3. View automated analysis and ask questions about the company's financials 