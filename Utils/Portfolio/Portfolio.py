from datetime import datetime
from os import path

from numpy import cumprod
from openpyxl import load_workbook
from pandas import DataFrame, Series, concat, date_range

from ..Sourcing.Yahoo import fetch_company_info, fetch_returns
from .Formatting import line_plot, write_df_to_xlsx_table
from .Stats import annualised_volatility, beta


class PortfolioAnalysis:
    def __init__(self, portfolio: DataFrame, params={}):
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

        self.date_range = date_range(
            start=self.start_date, end=self.end_date, freq="B"
        ).strftime("%Y-%m-%d")

        self.template_xlsx = path.join(self.path_input, "template.xlsx")

        print(f"{datetime.now()} - fetching portfolio data")

        self.constituent_returns = self.get_constituent_returns_daily()
        self.benchmark_returns = self.get_benchmark_returns_daily()
        self.constituents_info = self.get_constituents_info()
        self.benchmark_info = fetch_company_info(self.benchmark)

    def get_constituents_info(self) -> DataFrame | None:
        """Function to get a df containing basic info for all constituents within the portfolio

        Returns
        -------
        _type_
            _description_
        """
        temp_constituents_info = DataFrame(
            [fetch_company_info(ticker) for ticker in self.portfolio_tickers]
        )
        temp_constituents_info["weight"] = temp_constituents_info["ticker"].map(
            self.df_portfolio["weight"]
        )
        constituents_info = temp_constituents_info.set_index("ticker")
        return constituents_info

    def get_constituent_returns_daily(self) -> DataFrame | None:
        """Function to get a df containing daily returns for all constituents within the portfolio

        Returns
        -------
        DataFrame | None
            _description_
        """
        constituent_returns = fetch_returns(
            self.portfolio_tickers,
            self.start_date,
            self.end_date,
            self.include_dividends,
        ).reindex(self.date_range, fill_value=0)
        return constituent_returns

    def get_portfolio_returns_daily(self):
        """Function to get a series containing daily portfolio returns

        Returns
        -------
        _type_
            _description_
        """
        temp_returns = self.constituent_returns
        temp_weights = temp_returns.columns.map(self.df_portfolio["weight"])
        portfolio_returns = temp_returns.mul(temp_weights).sum(axis=1)
        return portfolio_returns

    def get_portfolio_returns_cumulative(self) -> Series | None:
        """Function to get a series containing cumulative portfolio returns

        Returns
        -------
        Series | None
            _description_
        """
        portfolio_returns_daily = self.get_portfolio_returns_daily().reindex(
            self.date_range, fill_value=0
        )
        portfolio_returns_cumulative = cumprod(1 + portfolio_returns_daily) - 1
        return portfolio_returns_cumulative

    def get_benchmark_returns_daily(self) -> Series | None:
        """Function to get a series containing daily benchmark returns

        Returns
        -------
        Series | None
            _description_
        """
        benchmark_returns = fetch_returns(
            self.benchmark, self.start_date, self.end_date, self.include_dividends
        ).reindex(self.date_range, fill_value=0)[self.benchmark]
        return benchmark_returns

    def get_return_overview_daily(self) -> DataFrame | None:
        """Function to get a df containing daily portfolio and benchmark returns

        Returns
        -------
        DataFrame | None
            _description_
        """
        portfolio_returns_daily = self.get_portfolio_returns_daily()
        benchmark_returns_daily = self.get_benchmark_returns_daily()
        return_overview_daily = DataFrame(
            portfolio_returns_daily.rename("portfolio_return")
        ).join(DataFrame(benchmark_returns_daily.rename("benchmark_return")))
        return return_overview_daily

    def get_return_overview_cumulative(self) -> DataFrame | None:
        """Function to get a df containing cumulative portfolio and benchmark returns

        Returns
        -------
        DataFrame | None
            _description_
        """
        return_overview_daily = self.get_return_overview_daily()
        return_overview_cumulative = cumprod(1 + return_overview_daily) - 1
        return return_overview_cumulative

    def get_relative_returns_daily(self) -> Series | None:
        """Function to get a series containing daily relative returns

        Returns
        -------
        Series | None
            _description_
        """
        temp_return_overview = self.get_return_overview_daily()
        relative_returns = (
            (1 + temp_return_overview["portfolio_return"]).div(
                (1 + temp_return_overview["benchmark_return"]), axis=0
            )
            - 1
        ).rename("relative_return")
        return relative_returns

    def get_sector_allocation(self) -> DataFrame | None:
        """Function to get a df containing the sector allocation of the portfolio

        Returns
        -------
        DataFrame | None
            _description_
        """
        temp_info = self.constituents_info
        sector_allocation = (
            temp_info.groupby("sector")["weight"].sum().sort_values(ascending=False)
        )
        return sector_allocation

    def get_country_allocation(self) -> DataFrame | None:
        """Function to get a df containing the country allocation of the portfolio

        Returns
        -------
        DataFrame | None
            _description_
        """
        temp_info = self.constituents_info
        country_allocation = (
            temp_info.groupby("country")["weight"].sum().sort_values(ascending=False)
        )
        return country_allocation

    def get_constituents_stats(self) -> DataFrame | None:
        """Function to get a df containing various stats for all constituents within the portfolio

        Returns
        -------
        DataFrame | None
            _description_
        """
        constituent_returns = self.constituent_returns
        bm_returns = self.benchmark_returns
        temp_volatility = DataFrame(
            constituent_returns.apply(
                lambda stock_returns: annualised_volatility(stock_returns)
            ).rename("volatility_annualised")
        )
        temp_betas = DataFrame(
            constituent_returns.apply(
                lambda stock_returns: beta(bm_returns, stock_returns)
            ).rename("beta")
        )
        temp_total_returns = DataFrame(
            (cumprod(1 + constituent_returns) - 1).iloc[-1].rename("total_return")
        )
        temp_relative_returns = DataFrame(
            (
                cumprod(1 + constituent_returns)
                .iloc[-1]
                .div((cumprod(1 + bm_returns).iloc[-1]), axis=0)
                - 1
            ).rename("relative_return")
        )
        constituent_stats = concat(
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

    def create_xlsx_output(self, output_name: str = "portfolio_overview") -> None:
        """Function to create an xlsx output containing the most important information about the portfolio

        Parameters
        ----------
        output_name : str, optional
            _description_, by default "portfolio_overview"
        """
        info = self.constituents_info
        stats = self.get_constituents_stats()
        return_overview = self.get_return_overview_cumulative()
        constituent_returns = self.constituent_returns

        wb = load_workbook(self.template_xlsx)

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
        file_path = path.join(self.path_output, f"{output_name}.xlsx")
        wb.save(file_path)
        print(f"{datetime.now()} - Portfolio output saved here: {file_path}")

    def plot_returns_daily(self, include_benchmark: bool = True):
        constituent_returns = self.constituent_returns
        constituents_info = self.constituents_info

        if include_benchmark:
            benchmark_returns = self.benchmark_returns
            benchmark_name = self.benchmark_info["name"]
            benchmark_returns.rename(benchmark_name)

        for ticker in constituent_returns.columns:
            ticker_returns = constituent_returns[ticker]
            ticker_name = constituents_info.at[ticker, "name"]
            ticker_returns = ticker_returns.rename(ticker_name)

            if include_benchmark:
                returns = [ticker_returns, benchmark_returns]
            else:
                returns = ticker_returns

            line_plot(returns, title="Daily returns")

    def plot_returns_cumulative(self, include_benchmark: bool = True):
        constituent_returns = cumprod(1 + self.constituent_returns) - 1
        constituents_info = self.constituents_info

        if include_benchmark:
            benchmark_returns = cumprod(1 + self.benchmark_returns) - 1
            benchmark_name = self.benchmark_info["name"]
            benchmark_returns.rename(benchmark_name)

        for ticker in constituent_returns.columns:
            ticker_returns = constituent_returns[ticker]
            ticker_name = constituents_info.at[ticker, "name"]
            ticker_returns = ticker_returns.rename(ticker_name)

            if include_benchmark:
                returns = [ticker_returns, benchmark_returns]
            else:
                returns = ticker_returns

            line_plot(returns, title="Cumulative returns")
