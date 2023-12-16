import os as os
from datetime import datetime

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from fredapi import Fred

load_dotenv(find_dotenv())
fred_api_key = os.environ.get("FRED_API_KEY")

client = Fred(api_key=fred_api_key)


def fetch_macro_data(
    series_ids: list, start_date: str, end_date: str | None = None
) -> pd.DataFrame | None:
    """Function to fetch macro-economic data from FRED through fredapi for various economic indicators

    Parameters
    ----------
    series_ids : list
        list of macro-economic series ids
    start_date : str
        First oberservation date as string in format 'YYYY-MM-DD'
    end_date : str | None, optional
        Last oberservation date as string in format 'YYYY-MM-DD', by default None (converted to today's date)

    Returns
    -------
    pd.DataFrame | None
        _description_
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
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
