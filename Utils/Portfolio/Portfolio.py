import os as os
from datetime import datetime

import numpy as np
import openpyxl as oxl
import pandas as pd

from ..Sourcing.Yahoo import fetch_company_info, fetch_returns
from .Formatting import write_df_to_xlsx_table
from .Stats import annualised_volatility, beta


class PortfolioAnalysis:
    def __init__(self, portfolio: pd.DataFrame, params={}):
        print(f"{datetime.now()} - initialising class PortfolioAnalysis")
        self.df_portfolio = portfolio
        self.start_date = params.get("start_date", None)
        self.end_date = params.get("end_date", None)
        self.benchmark = params.get("benchmark", None)
        self.include_dividends = params.get("include_dividends", False)

        self.portfolio_tickers = self.df_portfolio.index.unique().tolist()
        self.portfolio_total_weight = sum(self.df_portfolio["weight"])
        self.path_input = params.get("path_input", False)
        self.path_output = params.get("path_output", False)

        assert (
            round(self.portfolio_total_weight, 2) == 1
        ), f"Total portfolio weight is equal to {self.portfolio_total_weight}. Make sure it is set to 1"
        assert self.start_date, "start_date missing in params"
        assert self.benchmark, "benchmark missing in params"
        assert self.path_input, "input path missing in params"
        assert self.path_output, "output path missing in params"

        if not self.end_date:
            self.end_date = datetime.now().strftime("%Y-%m-%d")

        self.date_range = pd.date_range(
            start=self.start_date, end=self.end_date, freq="B"
        ).strftime("%Y-%m-%d")

        self.template_xlsx = os.path.join(self.path_input, "template.xlsx")

        print(f"{datetime.now()} - fetching portfolio data")

        self.constituent_returns = self.get_constituent_returns_daily()
        self.benchmark_returns = self.get_benchmark_returns_daily()
        self.constituents_info = self.get_constituents_info()

    def get_constituents_info(self):
        temp_constituents_info = pd.DataFrame(
            [fetch_company_info(ticker) for ticker in self.portfolio_tickers]
        )
        temp_constituents_info["weight"] = temp_constituents_info["ticker"].map(
            self.df_portfolio["weight"]
        )
        constituents_info = temp_constituents_info.set_index("ticker")
        return constituents_info

    def get_constituent_returns_daily(self):
        constituent_returns = fetch_returns(
            self.portfolio_tickers,
            self.start_date,
            self.end_date,
            self.include_dividends,
        ).reindex(self.date_range, fill_value=0)
        return constituent_returns

    def get_portfolio_returns_daily(self):
        temp_returns = self.constituent_returns
        temp_weights = temp_returns.columns.map(self.df_portfolio["weight"])
        portfolio_returns = temp_returns.mul(temp_weights).sum(axis=1)
        return portfolio_returns

    def get_portfolio_returns_cumulative(self):
        portfolio_returns_daily = self.get_portfolio_returns_daily().reindex(
            self.date_range, fill_value=0
        )
        portfolio_returns_cumulative = np.cumprod(1 + portfolio_returns_daily) - 1
        return portfolio_returns_cumulative

    def get_benchmark_returns_daily(self):
        benchmark_returns = fetch_returns(
            self.benchmark, self.start_date, self.end_date, self.include_dividends
        ).reindex(self.date_range, fill_value=0)[self.benchmark]
        return benchmark_returns

    def get_return_overview_daily(self):
        portfolio_returns_daily = self.get_portfolio_returns_daily()
        benchmark_returns_daily = self.get_benchmark_returns_daily()
        return_overview_daily = pd.DataFrame(
            portfolio_returns_daily.rename("portfolio_return")
        ).join(pd.DataFrame(benchmark_returns_daily.rename("benchmark_return")))
        return return_overview_daily

    def get_return_overview_cumulative(self):
        return_overview_daily = self.get_return_overview_daily()
        return_overview_cumulative = np.cumprod(1 + return_overview_daily) - 1
        return return_overview_cumulative

    def get_relative_returns_daily(self):
        temp_return_overview = self.get_return_overview_daily()
        relative_returns = (
            (1 + temp_return_overview["portfolio_return"]).div(
                (1 + temp_return_overview["benchmark_return"]), axis=0
            )
            - 1
        ).rename("relative_return")
        return relative_returns

    def get_sector_allocation(self):
        temp_info = self.constituents_info
        sector_allocation = (
            temp_info.groupby("sector")["weight"].sum().sort_values(ascending=False)
        )
        return sector_allocation

    def get_country_allocation(self):
        temp_info = self.constituents_info
        country_allocation = (
            temp_info.groupby("country")["weight"].sum().sort_values(ascending=False)
        )
        return country_allocation

    def get_constituents_stats(self):
        constituent_returns = self.constituent_returns
        bm_returns = self.benchmark_returns
        temp_volatility = pd.DataFrame(
            constituent_returns.apply(
                lambda stock_returns: annualised_volatility(stock_returns)
            ).rename("volatility_annualised")
        )
        temp_betas = pd.DataFrame(
            constituent_returns.apply(
                lambda stock_returns: beta(bm_returns, stock_returns)
            ).rename("beta")
        )
        temp_total_returns = pd.DataFrame(
            (np.cumprod(1 + constituent_returns) - 1).iloc[-1].rename("total_return")
        )
        temp_relative_returns = pd.DataFrame(
            (
                np.cumprod(1 + constituent_returns)
                .iloc[-1]
                .div((np.cumprod(1 + bm_returns).iloc[-1]), axis=0)
                - 1
            ).rename("relative_return")
        )
        constituent_stats = pd.concat(
            [
                self.df_portfolio,
                temp_total_returns,
                temp_relative_returns,
                temp_volatility,
                temp_betas,
            ],
            axis=1,
        )
        return constituent_stats

    def create_xlsx_output(self, output_name: str = "portfolio_overview"):
        info = self.constituents_info
        stats = self.get_constituents_stats()
        return_overview = self.get_return_overview_cumulative()
        constituent_returns = self.constituent_returns

        wb = oxl.load_workbook(self.template_xlsx)

        write_df_to_xlsx_table(wb, "constituent_info", info)
        write_df_to_xlsx_table(wb, "constituent_stats", stats)
        write_df_to_xlsx_table(
            wb, "return_overview", return_overview, base_formatting="0.00%;-0.00%"
        )
        write_df_to_xlsx_table(
            wb,
            "constituent_returns",
            constituent_returns,
            base_formatting="0.00%;-0.00%",
        )
        del wb["Sheet1"]
        file_path = os.path.join(self.path_output, f"{output_name}.xlsx")
        wb.save(file_path)
        print(f"{datetime.now()} - Portfolio output saved here: {file_path}")
