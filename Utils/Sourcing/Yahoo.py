import os as os
from datetime import datetime

import pandas as pd
import yfinance as yf


def fetch_ohlc(
    tickers: list | str,
    start_date: str,
    end_date: str | None = None,
) -> pd.DataFrame | None:
    """Function to fetch daily OHLC data from Yahoo Finance through yfinance

    Parameters
    ----------
    tickers : list | str
        list of Yahoo tickers or Yahoo ticker as str
    start_date : str
        First observation date as string in format 'YYYY-MM-DD'
    end_date : str | None, optional
        Last observation date as string in format 'YYYY-MM-DD', by default None (converted to today's date)

    Returns
    -------
    pd.DataFrame | None
        DataFrame with Open, High, Low, Close, and Volume
    """
    if not end_date:
        end_date = pd.to_datetime("today")

    if type(tickers) == str:
        tickers = [tickers]

    ohlc_data = yf.download(
        tickers, start=start_date, end=end_date, auto_adjust=True, progress=False
    )

    ohlc_data.index = pd.to_datetime(ohlc_data.index)

    return ohlc_data[["Open", "High", "Low", "Close"]]


def fetch_returns(
    tickers: list | str,
    start_date: str,
    end_date: str | None = None,
) -> pd.DataFrame | None:
    """Function to fetch daily total returns data from Yahoo Finance through yfinance

    Parameters
    ----------
    tickers : list | str
        list of Yahoo tickers or Yahoo ticker as str
    start_date : str
        First oberservation date as string in format 'YYYY-MM-DD'
    end_date : str | None, optional
        Last oberservation date as string in format 'YYYY-MM-DD', by default None (converted to today's date)

    Returns
    -------
    pd.DataFrame | None
        df containing returns for all tickers
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if type(tickers) == str:
        tickers = [tickers]

    temp_download = yf.download(
        tickers, start=start_date, end=end_date, auto_adjust=True, progress=False
    )
    temp_close = temp_download.iloc[
        :, temp_download.columns.get_level_values(0) == "Close"
    ]
    if temp_close.columns.nlevels == 2:
        temp_close.columns = temp_close.columns.droplevel(0)
    else:
        temp_close.columns = tickers
    temp_close.index = pd.to_datetime(temp_close.index).strftime("%Y-%m-%d")

    returns = temp_close.ffill().pct_change().dropna(how="all")

    if not returns.empty:
        return returns


def fetch_company_info(ticker: str) -> dict:
    """Function to fetch company (or index) info from Yahoo Finance through yfinance

    Parameters
    ----------
    ticker : str
        ticker for which to fetch info

    Returns
    -------
    dict
        dict containing ticker, name, sector, market cap (usd), and country (if available)
    """
    yf_ticker = yf.Ticker(ticker)
    temp_info = yf_ticker.info
    info = {
        "ticker": ticker,
        "name": temp_info.get("longName"),
        "sector": temp_info.get("sector"),
        "market_cap_usd": temp_info.get("marketCap"),
        "country": temp_info.get("country"),
    }
    return info
