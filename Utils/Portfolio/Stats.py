from numpy import sqrt
from pandas import Series
from sklearn.linear_model import LinearRegression


## Create function to calculate stock betas vs. given benchmark
def beta(x: Series, y: Series) -> float | None:
    """_summary_

    Parameters
    ----------
    x : Series
        X series
    y : Series
        Y series

    Returns
    -------
    _type_
        _description_
    """
    beta = (
        LinearRegression(fit_intercept=False)
        .fit(x.values.reshape(-1, 1), y.values.reshape(-1, 1))
        .coef_.item()
    )
    return beta


## Create function to calculate annualised volatility of stocks
def annualised_volatility(
    returns: Series, annual_trading_days: int = 252, drop_zero_returns: bool = True
) -> float | None:
    """_summary_

    Parameters
    ----------
    returns : Series
        series of returns
    annual_trading_days : int, optional
        number of assumed annual trading days, by default 252
    drop_zero_returns : bool, optional
        if True, returns data points witht the value 0 will be ignored, by default True
    """

    if drop_zero_returns:
        returns = returns.replace(0, None)
    annualised_volatility = returns.std() * sqrt(annual_trading_days)
    return annualised_volatility
