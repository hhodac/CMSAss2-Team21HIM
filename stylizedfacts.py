# From https://github.com/LCfP/Agent-Based-Stock-Market-Model
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


def run_simulation(i):
    print("Iteration {} running...".format(i))
    batch = FixedBatchRunner(model_cls=HeterogeneityInArtificialMarket, max_steps=10)
    model = HeterogeneityInArtificialMarket(
        initial_fundamentalist=50,
        initial_technical=50,
        initial_mimetic=50,
        initial_noise=50,
        network_type="small world",
        verbose=False
    )
    batch.run_model(model)
    df = model.datacollector.get_model_vars_dataframe()
    file_name = "batch_record_"+str(i)+".csv"
    df.to_csv(file_name, header=True, index=False)
    print("Iteration {} completed.".format(i))


def get_stylized_facts():
    file_list = []
    for file in os.listdir():
        if file.endswith(".csv"):
            file_list.append(os.path.join(".", file))

    df_list = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        _df_position = _df[["current_price"]]
        df_list.append(_df_position)

    n_rows, _ = df_list[0].shape
    # print("Current price:\n", df_list[0]["current_price"])
    df = pd.concat(df_list, axis=0)
    # print("Concatenated:\n", df)
    all_prices = df.current_price.to_numpy().reshape(len(file_list), n_rows)
    # print("Prices:\n", all_prices)

    all_returns = get_returns(all_prices)
    # print("Returns:\n", all_returns)

    # Returns Autocorrelation
    returns_autocorr = get_returns_autocorrelation(all_returns, lags=35)
    # print("Returns Autocorr:\n", returns_autocorr)

    # Volatility clustering (Absolute returns autocorrelation)
    absolute_returns = [returns.abs() for returns in all_returns]
    absolute_returns_autocorr = get_returns_autocorrelation(absolute_returns, lags=35)
    # print("Abosolute Returns Autocorr:\n", absolute_returns_autocorr)

    # # Long term memory for Return Autocorrelations
    # hurst_return_autocorr = get_hurst_exponent(returns_autocorr, lag_1=2, lag_2=20)
    # # Long term memory for Volatility clustering (Absolute returns autocorrelation)
    # hurst_abs_return_autocorr = get_hurst_exponent(absolute_returns_autocorr, lag_1=2, lag_2=20)

    return returns_autocorr, absolute_returns_autocorr

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

def get_hurst_exponent(returns, lag_1, lag_2):
    """
    Calculates a measure of long memory with the hurst exponent.
    This is an adaption from:
    https://robotwealth.com/demystifying-the-hurst-exponent-part-1/
    """
    returns = returns.dropna() # Remove any missing values from the price series
    lags = range(lag_1, lag_2)
    std_differences = [np.sqrt(np.std(np.subtract(returns[lag:], returns[:-lag]))) for lag in lags]
    m = np.polyfit(np.log(lags), np.log(std_differences), 1)
    hurst = m[0]*2.0
    return hurst

def visualise_stylized_facts(returns_autocorr, title):
    returns_autocorr = pd.DataFrame(returns_autocorr)
    # print("Returns Autocorr df:\n", returns_autocorr)
    # print("Indexes\n", returns_autocorr.index)

    avg_returns_autocorr = returns_autocorr.mean(axis=1)
    # print("avg_returns_autocorr: \n", avg_returns_autocorr)

    returns_autocorr_mean = np.mean(avg_returns_autocorr[1:])
    print("returns_autocorr_mean: \n", returns_autocorr_mean)

    fig, ax1 = plt.subplots(1, 1)
    fig.tight_layout(pad=3.0)
    ax1.plot(returns_autocorr.index, returns_autocorr.mean(axis=1), 'k-')
    ax1.fill_between(returns_autocorr.index, 
                 returns_autocorr.mean(axis=1) + returns_autocorr.std(axis=1), 
                 returns_autocorr.mean(axis=1) - returns_autocorr.std(axis=1), 
                 alpha=0.3, facecolor='black')
    ax1.set_ylabel('Autocorrelation', fontsize='20')
    ax1.set_xlabel('Lags', fontsize='20')
    plt.ylim(-1, 1)
    dir = os.path.join(".", "Data", "Experiment1")
    plt.savefig(os.path.join(dir, title+".png"))
    plt.show()


if __name__ == '__main__':
    # Activate multiprocessing
    start_time = time.time()
    
    print("Start multiprocessing...")

    optimal_thread_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(optimal_thread_count)

    iterations = 2
    pool.map(run_simulation, list(range(iterations)))

    pool.close()
    pool.join()

    # run_simulation(4)
    # run_simulation(3)

    returns_autocorr, absolute_returns_autocorr = get_stylized_facts()

    print("Completed!")
    end_time = time.time()
    duration = end_time - start_time
    print("Processing time: {}".format(duration))

    visualise_stylized_facts(returns_autocorr, "returns_autocorr")
    visualise_stylized_facts(absolute_returns_autocorr, "absolute_returns_autocorr")