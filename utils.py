from scipy.stats import truncnorm, uniform, pareto


def draw_from_uniform(lower, upper):
    """
    Given a lower, and upper bounds, generates and returns a real number from a uniform distribution.
    """
    try:
        if lower < upper:
            return uniform.rvs(loc=lower, scale=upper-lower, size=1)[0]
        else:
            raise Exception("Incorrect bounds in draw_from_uniform")
    except Exception as e:
        print(e)


def draw_from_normal(mu, sigma, lower=float('-inf'), upper=float('inf')):
    """
    Given a mean, std, lower, and upper bounds, generates and returns a real number from a normal distribution.
    """
    try:
        if lower < upper:
            return truncnorm.rvs(a=(lower - mu) / sigma, b=(upper - mu) / sigma, loc=mu, scale=sigma, size=1)[0]
        else:
            raise Exception("Incorrect bounds in draw_from_normal")
    except Exception as e:
        print(e)


def draw_from_pareto(a=1.5, xm=1.0, factor=1.0):
    """
    Given an a, lower bound on distribution, and multiplicative factor, returns a real number from pareto distribution.
    """
    try:
        if (a > 0.0) and (xm > 0.0) and (factor > 0.0):
            return factor * pareto.rvs(b=a, scale=xm, size=1)[0]
        else:
            raise Exception("Incorrect parameters in draw_from_pareto")
    except Exception as e:
        print(e)
