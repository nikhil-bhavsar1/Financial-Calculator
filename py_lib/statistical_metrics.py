def sample_variance(values: list) -> float:
    """
    Sample Variance (s²)
    Formula: Σ(xi - x̄)² / (n - 1)
    Where: xi = each value
           x̄ = sample mean
           n = number of observations
    """
    n = len(values)
    mean = sum(values) / n
    return sum((x - mean) ** 2 for x in values) / (n - 1)


def population_variance(values: list) -> float:
    """
    Population Variance (σ²)
    Formula: Σ(xi - μ)² / N
    Where: μ = population mean
           N = population size
    """
    N = len(values)
    mean = sum(values) / N
    return sum((x - mean) ** 2 for x in values) / N


def portfolio_variance_two_assets(weight1: float, weight2: float, variance1: float, variance2: float, covariance: float) -> float:
    """
    Portfolio Variance (Two Assets)
    Formula: w₁²σ₁² + w₂²σ₂² + 2w₁w₂Cov(1,2)
    Where: w = weight of each asset
           σ² = variance of each asset
           Cov = covariance between assets
    """
    return (weight1 ** 2 * variance1) + (weight2 ** 2 * variance2) + (2 * weight1 * weight2 * covariance)


def sample_standard_deviation(values: list) -> float:
    """
    Sample Standard Deviation (s)
    Formula: √[Σ(xi - x̄)² / (n - 1)]
    """
    return sample_variance(values) ** 0.5


def population_standard_deviation(values: list) -> float:
    """
    Population Standard Deviation (σ)
    Formula: √[Σ(xi - μ)² / N]
    """
    return population_variance(values) ** 0.5


def returns_standard_deviation(returns: list) -> float:
    """
    Returns Standard Deviation (Volatility)
    Formula: √[Σ(Ri - R̄)² / (n - 1)]
    Where: Ri = return in period i
           R̄ = average return
    """
    return sample_variance(returns) ** 0.5


def sample_covariance(x_values: list, y_values: list) -> float:
    """
    Sample Covariance
    Formula: Cov(X,Y) = Σ[(xi - x̄)(yi - ȳ)] / (n - 1)
    """
    n = len(x_values)
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    return sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)) / (n - 1)


def population_covariance(x_values: list, y_values: list) -> float:
    """
    Population Covariance
    Formula: Cov(X,Y) = Σ[(xi - μx)(yi - μy)] / N
    """
    N = len(x_values)
    x_mean = sum(x_values) / N
    y_mean = sum(y_values) / N
    return sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(N)) / N


def correlation_coefficient(x_values: list, y_values: list) -> float:
    """
    Correlation Coefficient (Pearson's r)
    Formula: r = Cov(X,Y) / (σx × σy)
    Formula: r = Σ[(xi - x̄)(yi - ȳ)] / √[Σ(xi - x̄)² × Σ(yi - ȳ)²]
    Range: -1 to +1
    """
    cov = sample_covariance(x_values, y_values)
    x_std = sample_standard_deviation(x_values)
    y_std = sample_standard_deviation(y_values)
    return cov / (x_std * y_std)


def coefficient_of_variation(standard_deviation: float, mean: float) -> float:
    """
    Coefficient of Variation
    Formula: (Standard Deviation / Mean) × 100
    Formula: (σ / μ) × 100
    """
    return (standard_deviation / mean) * 100


def beta(covariance_investment_market: float, variance_market: float) -> float:
    """
    Beta
    Formula: β = Cov(Ri, Rm) / Var(Rm)
    Where: Ri = return of investment
           Rm = return of market
    """
    return covariance_investment_market / variance_market


def beta_alternative(correlation: float, standard_deviation_investment: float, standard_deviation_market: float) -> float:
    """
    Beta Alternative
    Formula: β = (Correlation × σi) / σm
    """
    return (correlation * standard_deviation_investment) / standard_deviation_market


def sharpe_ratio(portfolio_return: float, risk_free_rate: float, portfolio_standard_deviation: float) -> float:
    """
    Sharpe Ratio
    Formula: (Rp - Rf) / σp
    Where: Rp = portfolio return
           Rf = risk-free rate
           σp = standard deviation of portfolio
    """
    return (portfolio_return - risk_free_rate) / portfolio_standard_deviation


def treynor_ratio(portfolio_return: float, risk_free_rate: float, portfolio_beta: float) -> float:
    """
    Treynor Ratio
    Formula: (Rp - Rf) / βp
    Where: βp = portfolio beta
    """
    return (portfolio_return - risk_free_rate) / portfolio_beta


def information_ratio(portfolio_return: float, benchmark_return: float, tracking_error: float) -> float:
    """
    Information Ratio
    Formula: (Rp - Rb) / Tracking Error
    Where: Rb = benchmark return
           Tracking Error = standard deviation of (Rp - Rb)
    """
    return (portfolio_return - benchmark_return) / tracking_error


def sortino_ratio(portfolio_return: float, risk_free_rate: float, returns: list, minimum_acceptable_return: float) -> float:
    """
    Sortino Ratio
    Formula: (Rp - Rf) / Downside Deviation
    Where: Downside Deviation = √[Σ(min(Ri - MAR, 0))² / n]
           MAR = Minimum Acceptable Return
    """
    downside_squared = [min(r - minimum_acceptable_return, 0) ** 2 for r in returns]
    downside_deviation = (sum(downside_squared) / len(returns)) ** 0.5
    return (portfolio_return - risk_free_rate) / downside_deviation


def parametric_var(portfolio_value: float, z_score: float, standard_deviation: float, time_horizon: float) -> float:
    """
    Parametric VaR (Normal Distribution)
    Formula: VaR = Portfolio Value × z-score × σ × √t
    Where: z-score = confidence level (e.g., 1.65 for 95%, 2.33 for 99%)
           σ = standard deviation of returns
           t = time horizon
    """
    return portfolio_value * z_score * standard_deviation * (time_horizon ** 0.5)


def arithmetic_mean(values: list) -> float:
    """
    Arithmetic Mean
    Formula: x̄ = Σxi / n
    """
    return sum(values) / len(values)


def weighted_average(values: list, weights: list) -> float:
    """
    Weighted Average
    Formula: x̄w = Σ(wi × xi) / Σwi
    """
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def geometric_mean(returns: list) -> float:
    """
    Geometric Mean (for returns)
    Formula: [(1 + R₁) × (1 + R₂) × ... × (1 + Rn)]^(1/n) - 1
    """
    product = 1
    for r in returns:
        product *= (1 + r)
    return product ** (1 / len(returns)) - 1
