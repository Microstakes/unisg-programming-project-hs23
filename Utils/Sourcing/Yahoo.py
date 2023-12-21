import os as os
from datetime import datetime

import pandas as pd
import yfinance as yf

def fetch_ohlc(
    tickers: list | str,
    start_date: str,
    end_date: str | None = None,
    include_dividends: bool = False,
) -> pd.DataFrame | None:
    """Function to fetch daily OHLCV data from Yahoo Finance through yfinance

    Parameters
    ----------
    tickers : list | str
        list of Yahoo tickers or Yahoo ticker as str
    start_date : str
        First observation date as string in format 'YYYY-MM-DD'
    end_date : str | None, optional
        Last observation date as string in format 'YYYY-MM-DD', by default None (converted to today's date)
    include_dividends: bool
        Decide whether to include dividends (total returns) or not (price returns)

    Returns
    -------
    pd.DataFrame | None
        DataFrame with Open, High, Low, Close, and Volume
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    if type(tickers) == str:
        tickers = [tickers]

    temp_download = yf.download(
        tickers, start=start_date, end=end_date, auto_adjust=True, progress=False
    )

    if include_dividends:
        df_dividends = pd.DataFrame()
        for ticker in tickers:
            yf_ticker = yf.Ticker(ticker)
            temp_dividends = pd.DataFrame(yf_ticker.get_dividends())
            temp_dividends = temp_dividends.rename(columns={"Dividends": ticker})
            df_dividends = pd.concat([df_dividends, temp_dividends])

        df_dividends.index = pd.to_datetime(df_dividends.index).strftime("%Y-%m-%d")
        df_dividends = df_dividends[df_dividends.index >= min(temp_download.index)]

        ohlc_data = temp_download.add(df_dividends, fill_value=0.0)
    else:
        ohlc_data = temp_download

    return ohlc_data

def fetch_returns(
    tickers: list | str,
    start_date: str,
    end_date: str | None = None,
    include_dividends: bool = False,
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
    include_dividends: bool
        Decide whether to include dividends (total returns) or not (price returns)

    Returns
    -------
    pd.DataFrame | None
        _description_
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

    if include_dividends:
        df_dividends = pd.DataFrame()
        for ticker in tickers:
            yf_ticker = yf.Ticker(ticker)
            temp_dividends = pd.DataFrame(yf_ticker.get_dividends())
            temp_dividends = temp_dividends.rename(columns={"Dividends": ticker})
            df_dividends = pd.concat([df_dividends, temp_dividends])

        df_dividends.index = pd.to_datetime(df_dividends.index).strftime("%Y-%m-%d")
        df_dividends = df_dividends[df_dividends.index >= min(temp_close.index)]

        returns = (
            temp_close.add(df_dividends, fill_value=0.0)
            .ffill()
            .pct_change()
            .dropna(how="all")
        )
    else:
        returns = temp_close.ffill().pct_change().dropna(how="all")
        
    ohlc_data = fetch_ohlc(tickers, start_date, end_date, include_dividends)
    
    if not ohlc_data.empty:
        returns = ohlc_data['Close'].pct_change().dropna(how="all")

    if not returns.empty:
        return returns


def fetch_company_info(ticker):
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


def fetch_relative_returns(
    assets: list | str,
    benchmark: str,
    start_date: str,
    end_date: str | None = None,
    include_dividends: bool = False,
) -> pd.DataFrame | None:
    """Function to fetch daily relative returns data from Yahoo Finance through yfinance

    Parameters
    ----------
    assets : list | str
        list of Yahoo tickers or Yahoo ticker as str
    benchmark: str
        Yahoo ticker as str
    start_date : str
        First oberservation date as string in format 'YYYY-MM-DD'
    end_date : str | None, optional
        Last oberservation date as string in format 'YYYY-MM-DD', by default None (converted to today's date)
    include_dividends: bool
        Decide whether to include dividends (total returns) or not (price returns)

    Returns
    -------
    pd.DataFrame | None
        _description_
    """
    asset_returns = fetch_returns(assets, start_date, end_date, include_dividends)
    benchmark_returns = fetch_returns(
        benchmark, start_date, end_date, include_dividends
    )
    relative_returns = (1 + asset_returns).div(
        (1 + benchmark_returns[benchmark]), axis=0
    ) - 1

    if not relative_returns.empty:
        return relative_returns
