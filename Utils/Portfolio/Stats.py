from sklearn.linear_model import LinearRegression


## Create function to calculate stock betas vs. given benchmark
def beta(x, y):
    beta = (
        LinearRegression(fit_intercept=False)
        .fit(x.values.reshape(-1, 1), y.values.reshape(-1, 1))
        .coef_.item()
    )
    return beta
