from numpy import *
from pylab import plot, show

from hurst import compute_Hc, random_walk

# Method 1
# first, create an arbitrary time series, ts
ts = [0]
for i in range(1,100000):
    ts.append(ts[i-1]*1.0 + random.randn())
print("ts", array(ts))

# Method 2
# Use random_walk() function or generate a random walk series manually:
# series = random_walk(99999, cumprod=True)
random.seed(42)
random_changes = 1. + random.randn(99999) / 1000.
series = cumprod(random_changes)  # create a random walk from random changes
print("series", series)


# Method 1
# calculate standard deviation of differenced series using various lags
lags = range(2, 20)
tau = [sqrt(std(subtract(series[lag:], series[:-lag]))) for lag in lags]
# plot on log-log scale
# plot(log(lags), log(tau)); show()
# calculate Hurst as slope of log-log plot
m = polyfit(log(lags), log(tau), 1)
hurst = m[0]*2.0
print('hurst_1 = ',hurst)

# Method 2
# Evaluate Hurst equation
H, c, data = compute_Hc(series, kind='price', simplified=True)
print('hurst_2 = ',H)