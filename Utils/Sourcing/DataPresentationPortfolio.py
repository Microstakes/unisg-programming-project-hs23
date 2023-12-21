from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from Portfolio import PortfolioAnalysis  # adjusted
import mplfinance as mpf
import webbrowser

app = Flask(__name__)

# Modify this function to include additional portfolio information
def generate_candlestick_chart(df, tickers_column):
    # Extract tickers and historical price data
    tickers = df[tickers_column].unique()

    # Create a figure and axis for the candlestick chart and line chart
    fig, (ax_candlestick, ax_line_chart) = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

    # Loop through tickers and create a candlestick chart for each
    for ticker in tickers:
        # Filter data for the current ticker
        ticker_data = df[df[tickers_column] == ticker]

        # Create a candlestick chart using mplfinance
        mpf.plot(ticker_data, type='candle', ax=ax_candlestick, title=f'Candlestick Chart - {ticker}')

    # Calculate portfolio cumulative returns
    portfolio_analysis = PortfolioAnalysis(df)  # adjusted correctly?
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
    portfolio_weight = portfolio_analysis.portfolio_total_weight  # correct names?
    another_metric_value = portfolio_analysis.get_another_metric()  # correct names?

    return image_stream, sector_allocation, country_allocation, portfolio_weight, another_metric_value

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']

        # Read the Excel file into a Pandas DataFrame
        df = pd.read_excel(file)

        # Get the tickers column name from the form
        tickers_column = request.form['tickers_column']

        # Perform your analysis and generate the candlestick chart
        candlestick_chart, sector_allocation, country_allocation, portfolio_weight, another_metric_value = generate_candlestick_chart(df, tickers_column)

        # Render the results in an HTML page
        return render_template('results.html', candlestick_chart=candlestick_chart,
                               sector_allocation=sector_allocation, country_allocation=country_allocation,
                               portfolio_weight=portfolio_weight, another_metric_value=another_metric_value)

    return render_template('upload.html')

if __name__ == '__main__':
    # Open the default web browser automatically
    webbrowser.open('http://127.0.0.1:5000/')

    # Run the Flask application
    app.run(debug=True)
