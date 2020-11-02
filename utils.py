from scipy.stats import truncnorm, uniform


def draw_from_uniform(lower, upper):
    """
    Given a lower, and upper bounds, generates and returns a real number from a uniform distribution.
    """
    try:
        if lower < upper:
            return uniform.rvs(loc=lower, scale=upper-lower, size=1)[0]
        else:
            raise Exception("Incorrect bounds in drawFromUniform")    
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
            raise Exception("Incorrect bounds in drawFromNormal")    
    except Exception as e:
        print(e)
