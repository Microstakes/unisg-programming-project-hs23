# Install required packages first:
# pip install Flask pandas yfinance fredapi matplotlib

from flask import Flask, render_template, request
import pandas as pd
import yfinance as yf
from fredapi import Fred
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Function to fetch real-time stock data from Yahoo Finance
def fetch_stock_data(stock_name, start_date, end_date):
    df_stock_data = yf.download(stock_name, start=start_date, end=end_date)
    return df_stock_data

# Function to fetch macro-economic data from FRED API
def fetch_macro_data(series_ids, start_date, end_date):
    fred_api_key = 'your_fred_api_key'  # Replace with your FRED API key
    client = Fred(api_key=fred_api_key)
    
    temp_macro_data = {}
    for series_id in series_ids:
        try:
            data = client.get_series(
                series_id, observation_start=start_date, observation_end=end_date
            )
            temp_macro_data[series_id] = data
        except Exception as e:
            print(f"Error fetching data for {series_id}: {e}")
    
    df_macro_data = pd.DataFrame(temp_macro_data)
    if not temp_macro_data.empty:
        return df_macro_data

# Function to plot stock price trends and return base64-encoded image for HTML embedding
def plot_stock_trend(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'], label='Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Stock Price (USD)')
    plt.title('Stock Price Trend')
    plt.legend()
    plt.grid(True)
    #plt.show()
    
    return plt

    # Save the plot to a BytesIO object
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    
    # Encode the plot image to base64 for HTML embedding
    img_data = base64.b64encode(img_buf.read())#.decode('utf-8')
    
    return img_data

# Flask route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input
        stock_name = request.form['stock_name']
        second_stock_name = request.form['second_stock_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Fetch data from Yahoo Finance
        df_stock_data = fetch_stock_data(stock_name, start_date, end_date)

        # Fetch data for the second stock
        df_second_stock_data = fetch_stock_data(second_stock_name, start_date, end_date)

        # Fetch macro-economic data from FRED API
        df_macro_data = fetch_macro_data(['GDP', 'CPI'], start_date, end_date)

        # Combine DataFrames
        merged_data = pd.merge(df_stock_data, df_macro_data, left_index=True, right_index=True, how='inner')
        merged_second_stock_data = pd.merge(df_second_stock_data, df_macro_data, left_index=True, right_index=True, how='inner')

        # Plot stock trends
        stock_plot = plot_stock_trend(merged_data)
        second_stock_plot = plot_stock_trend(merged_second_stock_data)

        # Render HTML template with data and plots
        return render_template('result.html', 
                               data=merged_data.to_html(),
                               stock_plot=stock_plot,
                               second_stock_plot=second_stock_plot)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
