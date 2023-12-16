import os as os
from datetime import datetime

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from fredapi import Fred

load_dotenv(find_dotenv())
fred_api_key = os.environ.get("FRED_API_KEY")

client = Fred(api_key=fred_api_key)


def fetch_macro_data(series_ids, start_date, end_date=None):
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
    return df_macro_data
