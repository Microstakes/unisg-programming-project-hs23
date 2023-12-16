import os as os
from datetime import datetime

import pandas as pd
import yfinance as yf


def fetch_total_returns(tickers, start_date, end_date=None):
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    temp_download = yf.download(
        tickers, start=start_date, end=end_date, auto_adjust=True
    )
    temp_close = temp_download.iloc[
        :, temp_download.columns.get_level_values(0) == "Close"
    ]
    temp_close.columns = temp_close.columns.droplevel(0)
    temp_close.index = pd.to_datetime(temp_close.index).strftime("%Y-%m-%d")

    df_dividends = pd.DataFrame()
    for ticker in tickers:
        yf_ticker = yf.Ticker(ticker)
        temp_dividends = pd.DataFrame(yf_ticker.get_dividends())
        temp_dividends = temp_dividends.rename(columns={"Dividends": ticker})
        df_dividends = pd.concat([df_dividends, temp_dividends])

    df_dividends.index = pd.to_datetime(df_dividends.index).strftime("%Y-%m-%d")
    df_dividends = df_dividends[df_dividends.index >= min(temp_close.index)]

    total_returns = (
        temp_close.add(df_dividends, fill_value=0.0).pct_change().dropna(how="all")
    )

    return total_returns
