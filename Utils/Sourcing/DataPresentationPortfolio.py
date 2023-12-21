from flask import Flask, render_template, request, send_file
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from ..Portfolio.Portfolio import PortfolioAnalysis  # adjusted
import mplfinance as mpf
import webbrowser

app = Flask(__name__)

# Modify this function to include additional portfolio information
def generate_candlestick_chart(portfolio_analysis: PortfolioAnalysis ):
    """Generates a candlestick chart and line chart for the given portfolio using Matplotlib and mplfinance.

    Args:
        A PortfolioAnalysis instance representing the portfolio data.

    Returns:
        Returns a BytesIO object containing the candlestick chart image, sector allocation DataFrame, country allocation DataFrame, and portfolio weight.
    """
    # Extract tickers and historical price data
    tickers = portfolio_analysis.portfolio_tickers

    # Create a figure and axis for the candlestick chart and line chart
    fig, (ax_candlestick, ax_line_chart) = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    # Loop through tickers and create a candlestick chart for each
    for ticker in tickers:
        # Filter data for the current ticker
        ticker_data = portfolio_analysis.constituent_returns[ticker]

        # Create a candlestick chart using mplfinance
        mpf.plot(ticker_data, type='candle', ax=ax_candlestick, title=f'Candlestick Chart - {ticker}')

    # Calculate portfolio cumulative returns
    portfolio_returns_cumulative = portfolio_analysis.get_portfolio_returns_cumulative()

    # Plot the cumulative returns of the entire portfolio
    ax_line_chart.plot(portfolio_returns_cumulative, label='Portfolio Cumulative Returns', color='blue')
    ax_line_chart.set_ylabel('Cumulative Returns')
    ax_line_chart.legend()

    # Save the figure to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    # Get some additional summary information about the portfolio using PortfolioAnalysis
    sector_allocation = portfolio_analysis.get_sector_allocation()
    country_allocation = portfolio_analysis.get_country_allocation()
    portfolio_weight = portfolio_analysis.portfolio_total_weight

    return image_stream, sector_allocation, country_allocation, portfolio_weight

@app.route('/', methods=['GET', 'POST'])
def display_portfolio_analysis():
    """Displays the portfolio analysis results on an HTML page, including the candlestick chart, sector allocation, country allocation, and portfolio weight.
Input: None (uses a predefined portfolio data or replace with actual portfolio data).

    Returns:
       Renders an HTML page with the portfolio analysis results.
    """
    portfolio_analysis = PortfolioAnalysis()  

    # Perform your analysis and generate the candlestick chart
    candlestick_chart, sector_allocation, country_allocation, portfolio_weight = generate_candlestick_chart(portfolio_analysis)

    # Generate an HTML page with the analysis results
    html_content = f
    """
        <html>
        <head>
            <title>Portfolio Analysis Results</title>
        </head>
        <body>
            <h1>Portfolio Analysis Results</h1>
            <div>
                <img src="data:image/png;base64,{candlestick_chart}" alt="Candlestick Chart">
            </div>
            <div>
                <h2>Sector Allocation</h2>
                {sector_allocation.to_html()}
            </div>
            <div>
                <h2>Country Allocation</h2>
                {country_allocation.to_html()}
            </div>
            <div>
                <h2>Portfolio Weight</h2>
                <p>{portfolio_weight}</p>
            </div>
        </body>
        </html>
    """

    # Convert the HTML content to Markup
    markup_content = Markup(html_content)

    # Return the rendered HTML page
    return markup_content
if __name__ == '__main__':
    # Open the default web browser automatically
    webbrowser.open('http://127.0.0.1:5000/')

    # Run the Flask application
    app.run(debug=True)
