# This is an adaption from: https://github.com/LCfP/Agent-Based-Stock-Market-Model
from mesa.batchrunner import FixedBatchRunner
from model import *
import multiprocessing
import time
import os

import pandas as pd
import numpy as np
import market

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

import statsmodels.api as sm 
import pylab as py 
import scipy.stats as stats

import json

def get_stylized_facts(show=True):
    stylized_facts = {}
    file_list = []
    dirname = os.path.dirname
    for file in os.listdir(dirname(dir)):
        if file.endswith(".csv"):
            file_list.append(os.path.join(dirname(dir), file))

    if len(file_list) == 0:
        return []

    df_list = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        _df_position = _df[["price", "order_all_sum"]]
        df_list.append(_df_position)

    n_rows, _ = df_list[0].shape
    df = pd.concat(df_list, axis=0)
    all_prices = df.price.to_numpy().reshape(len(file_list), n_rows)
    all_orders = df.order_all_sum.to_numpy().reshape(len(file_list), n_rows)
    all_returns = get_returns(all_prices)

    # Returns Autocorrelation
    returns_autocorr = get_returns_autocorrelation(all_returns, lags=35)
    returns_autocorr = pd.DataFrame(returns_autocorr)
    visualise_autocorrelations(returns_autocorr, "Returns Autocorrelation", show)

    avg_returns_autocorr = returns_autocorr.mean(axis=1)
    returns_autocorr_mean = np.mean(avg_returns_autocorr[1:])
    stylized_facts["Returns Autocorrelation mean"] = returns_autocorr_mean
    print("Returns Autocorrelation mean: ", returns_autocorr_mean)

    # Volatility clustering (Absolute returns autocorrelation)
    absolute_returns = [returns.abs() for returns in all_returns]
    absolute_returns_autocorr = get_returns_autocorrelation(absolute_returns, lags=35)
    absolute_returns_autocorr = pd.DataFrame(absolute_returns_autocorr)
    visualise_autocorrelations(absolute_returns_autocorr, "Absolute Returns Autocorrelation", show)

    avg_abs_returns_autocorr = absolute_returns_autocorr.mean(axis=1)
    abs_returns_autocorr_mean = np.mean(avg_abs_returns_autocorr[1:])
    stylized_facts["Absolute Returns Autocorrelation mean"] = abs_returns_autocorr_mean
    print("Returns Autocorrelation mean: ", abs_returns_autocorr_mean)

    # Long term memory for Return Autocorrelations
    hurst_returns_autocorr = get_hurst_exponent(all_returns, lag_1=2, lag_2=20)
    avg_hurst_returns_autocorr = np.mean(hurst_returns_autocorr)
    stylized_facts["Long term memory for Return Autocorrelations (hurst)"] = avg_hurst_returns_autocorr
    print('Long term memory for Return Autocorrelations (hurst):', avg_hurst_returns_autocorr)

    # Long term memory for Volatility clustering (Absolute returns autocorrelation)
    hurst_abs_returns_autocorr = get_hurst_exponent(absolute_returns, lag_1=2, lag_2=20)
    avg_hurst_abs_returns_autocorr = np.mean(hurst_abs_returns_autocorr)
    stylized_facts["Long term memory for Volatility clustering (hurst)"] = avg_hurst_abs_returns_autocorr
    print('Long term memory for Volatility clustering (hurst):', avg_hurst_abs_returns_autocorr)

    # Correlation between volume and volatility
    correlations = get_volume_volatility_correlation(all_orders, all_returns)
    avg_correlations = np.mean(correlations)
    stylized_facts["Average correlation between volume and volatility"] = avg_correlations
    print('Average correlation between volume and volatility:', avg_correlations)

    plt.figure(figsize=(10.0, 6.0))
    # fig.tight_layout(pad=3.0)
    # ax1.plot(range(len(correlations)), correlations, 'k-')
    plt.boxplot(correlations)
    # plt.xlabel("Iterations", fontsize=20)
    plt.ylabel("Correlation between volume and volatility", fontsize=20)
    plt.title("Correlation between volume and volatility", fontsize=25)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    # plt.ylim(-1, 1)
    plt.savefig(os.path.join(dir, "Correlation between volume and volatility.png"))
    if show:
        plt.show()

    # Fat tails - Kurtosis
    kurtosis = get_kurtosis(all_returns)
    avg_kurtosis = np.mean(kurtosis)
    stylized_facts["Fat Tails (Average Kurtoris)"] = avg_kurtosis
    print('Average Kurtoris:', avg_kurtosis)

    # Returns distribution histogram
    plt.figure(figsize=(10.0, 6.0))
    plt.hist(all_returns[0], bins="auto")
    plt.xlabel("Returns", fontsize=20)
    plt.ylabel("Frequency", fontsize=20)
    plt.title("Returns distribution histogram", fontsize=25)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    # plt.ylim(-1, 1)
    plt.savefig(os.path.join(dir, "Returns distribution histogram.png"))
    # if show:
    plt.show()


    # Returns QQ plot
    # sm.qqplot(all_returns[0], line ='45') 
    # py.show()
    stats.probplot(all_returns[0], dist="norm", plot=py)
    time.sleep(1)
    # if show:
    py.show()
    py.savefig(os.path.join(dir, "QQ plot.png"))
    time.sleep(1)

    return stylized_facts

def get_returns(all_prices):
    all_returns = []
    for prices in all_prices:
        all_returns.append(pd.Series(prices).pct_change())
    return all_returns

def get_returns_autocorrelation(all_returns, lags):
    returns_autocorr = {}
    for i, returns in enumerate(all_returns):
        returns_autocorr["iter_" + str(i)] = [returns[1:].autocorr(lag=lag) for lag in range(lags)]
    return returns_autocorr

def get_hurst_exponent(all_returns, lag_1, lag_2):
    """
    Calculates a measure of long memory with the hurst exponent.
    This is an adaption from:
    https://robotwealth.com/demystifying-the-hurst-exponent-part-1/
    """
    hurst_exponents = []
    for returns in all_returns:
        returns = list(returns)[1:]
        # print("Returns:", returns)
        # returns = returns.dropna() # Remove any missing values
        # print("Returns dropped:", returns)
        lags = range(lag_1, lag_2)
        std_differences = [np.sqrt(np.std(np.subtract(returns[lag:], returns[:-lag]))) for lag in lags]
        # print("std_differences: ", std_differences)
        m = np.polyfit(np.log(lags), np.log(std_differences), 1)
        # print("polyfit: ", m)
        hurst = m[0]*2.0
        # print("hurst: ", hurst)
        hurst_exponents.append(hurst)
    return hurst_exponents

def get_volume_volatility_correlation(volumes, returns):
    correlations = []
    window = 10
    for vol, ret in zip(volumes, returns):
        vol = pd.Series(abs(vol))
        roller_returns = ret.rolling(window)
        returns_volatility = roller_returns.std(ddof=0)
        correlations.append(returns_volatility.corr(vol))
    return correlations

def get_kurtosis(all_returns):
    kurtosis = []
    for returns in all_returns:
        series_returns = pd.Series(returns)
        kurtosis.append(series_returns.kurtosis())
    return kurtosis
    # if kurt > 4:
    #     return True, kurt
    # else:
    #     return False, np.inf

def visualise_autocorrelations(returns_autocorr, title, show=True):

    fig, ax1 = plt.subplots(1, 1, figsize=(10.0, 5.0))
    # fig.tight_layout(pad=3.0)
    ax1.plot(returns_autocorr.index, returns_autocorr.mean(axis=1), 'k-')
    ax1.fill_between(returns_autocorr.index, 
                 returns_autocorr.mean(axis=1) + returns_autocorr.std(axis=1), 
                 returns_autocorr.mean(axis=1) - returns_autocorr.std(axis=1), 
                 alpha=0.3, facecolor='black')
    plt.xlabel("Lags", fontsize=20)
    plt.ylabel(title, fontsize=20)
    plt.title(title + " vs. Lags", fontsize=25)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    plt.ylim(-1, 1)
    plt.savefig(os.path.join(dir, title+"vs Lags.png"))
    if show:
        plt.show()


if __name__ == '__main__':
    start_time = time.time()

    global dir
    dir = os.path.join(".", "Data", "Experiment2.1", "stylized_facts")

    for i in range(7, 9):
        dir = os.path.join(".", "Data", "Experiment2."+str(i), "stylized_facts")
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        # Get stylized facts
        stylized_facts = get_stylized_facts(show=False)

        # Save stylized facts into json file
        if len(stylized_facts) > 0:
            file_name = os.path.join(dir, "stylized_facts.json")
            with open(file_name, "w") as file:
                json.dump(stylized_facts, file, indent=4, sort_keys=True)

    print("Completed!")
    end_time = time.time()
    duration = end_time - start_time
    print("Processing time: {}".format(duration))