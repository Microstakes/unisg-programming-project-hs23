import yfinance as yf
import DataPresentation
from datetime import date
from PIL import Image
import numpy as np 
import matplotlib.pyplot as plt

def main():
   stock_name = input("Enter the stock name: ")
   stockData = DataPresentation.fetch_stock_data(stock_name, date(2023,1,1), date(2023,12,31))
   chartPlot = DataPresentation.plot_stock_trend(stockData)
   chartPlot.show()

if __name__ == "__main__":
    main()