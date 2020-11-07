import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

experiment = 'Experiment1.1'
dir = os.path.join('.', 'Data', experiment)
if not os.path.exists(dir):
    os.makedirs(dir)

def get_file_index(file_path):
    chunks = file_path.split(".")
    idx = int(chunks[1].split("_")[-1])
    return idx

def get_normalisation_factor(max_all_position_ftrader, all_position_trader, trader):
    mean_all_position_trader = np.mean(all_position_trader, axis=0)
    # print("mean_all_position_" + trader + ":\n", mean_all_position_trader)

    max_all_position_trader = max(np.abs(mean_all_position_trader))
    print("max_all_position_" + trader + ":\n", max_all_position_trader)

    if max_all_position_trader == 0:
        ratio = None
    else:
        ratio = max_all_position_ftrader/max_all_position_trader
    print("ratio_" + trader + ":\n", ratio)

    return ratio


def do_calibration(file_list, df_list_positions):
    df_positions = pd.concat(df_list_positions, axis=0, ignore_index=True)
    n_rows, _ = df_list_positions[0].shape

    # Fundamentalists positions
    all_position_ftrader = df_positions.position_ftrader_mean.to_numpy().reshape(len(file_list), n_rows)
    mean_all_position_ftrader = np.mean(all_position_ftrader, axis=0)
    # print("mean_all_position_ftrader:\n", mean_all_position_ftrader)
    max_all_position_ftrader = max(mean_all_position_ftrader)
    print("max_all_position_ftrader:\n", max_all_position_ftrader)

    # Technicals positions
    all_position_ttrader = df_positions.position_ttrader_mean.to_numpy().reshape(len(file_list), n_rows)
    get_normalisation_factor(max_all_position_ftrader, all_position_ttrader, "technical")

    # Mimetics positions
    all_position_mtrader = df_positions.position_mtrader_mean.to_numpy().reshape(len(file_list), n_rows)
    get_normalisation_factor(max_all_position_ftrader, all_position_mtrader, "mimetic")

    # Noise positions
    all_position_ntrader = df_positions.position_ntrader_mean.to_numpy().reshape(len(file_list), n_rows)
    get_normalisation_factor(max_all_position_ftrader, all_position_ntrader, "noise")


def plot_time_vs_mean_of_selected_columns(file_list, select_columns, title, xrange, calibration=False):
    df_list = []
    df_list_positions = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        _n_rows, _ = _df.shape

        for col in select_columns:
            _df_select = _df.loc[:,['step', col]]
            _df_select['type'] = col
            _df_select = _df_select.rename(columns={col: "data"})
            df_list.append(_df_select)

        if calibration:
            _df_position = _df[["position_ftrader_mean", "position_ttrader_mean", "position_mtrader_mean", "position_ntrader_mean"]]
            df_list_positions.append(_df_position)

    df = pd.concat(df_list, axis=0, ignore_index=True)

    if calibration:
        do_calibration(file_list, df_list_positions)

    plt.figure(figsize=(15.0, 9.0))
    sns.lineplot(data=df, x="step", y="data", ci="sd", hue="type")
    plt.title(title, fontsize=25)
    plt.xlabel("Step", fontsize=20)
    plt.ylabel("Position", fontsize=20)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    plt.xlim(xrange[0], xrange[1])
    plt.legend(loc="best", fontsize=20, labels=['fundamentalist','technical','mimetic','noise'])
    plt.savefig(os.path.join(dir, title+".png"))
    plt.show()

def plot_time_vs_price_value(file_list, xrange):
    title = "Time vs. average price and fundamental value"
    df_list = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        _n_rows, _ = _df.shape

        for col in ['current_price', 'current_value']:
            _df_select = _df.loc[:,['step', col]]
            if col.find("price")>=0:
                _df_select['type'] = "Price"
            elif col.find("value")>=0:
                _df_select['type'] = "Value"
            _df_select = _df_select.rename(columns={col: "data"})
            df_list.append(_df_select)

    df = pd.concat(df_list, axis=0, ignore_index=True)

    plt.figure(figsize=(15.0, 9.0))
    sns.lineplot(data=df, x="step", y="data", ci="sd", hue="type")
    plt.title(title, fontsize=25)
    plt.xlabel("Step", fontsize=20)
    plt.ylabel("Position", fontsize=20)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    plt.xlim(xrange[0], xrange[1])
    plt.legend(loc="best", fontsize=20)
    plt.savefig(os.path.join(dir, title+".png"))
    plt.show()

file_list = []
for file in os.listdir(dir):
    if file.endswith(".csv"):
        file_list.append(os.path.join(dir, file))

# Time vs. average price and fundamental value
plot_time_vs_price_value(file_list=file_list, xrange=(1,1530))

# Time vs. average net position of traders
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=[
        'position_ftrader_mean',
        'position_ttrader_mean',
        'position_mtrader_mean',
        'position_ntrader_mean',
    ],
    title="Time vs. average net position of traders",
    xrange=(1,1530),
    calibration=True
)

# Time vs. average order of traders
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=[
        'order_ftrader_mean',
        'order_ttrader_mean',
        'order_mtrader_mean',
        'order_ntrader_mean',
    ],
    title="Time vs. average order of traders",
    xrange=(1,1530)
)

# Time vs. average porfolio of traders
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=[
        'portfolio_ftrader_mean',
        'portfolio_ttrader_mean',
        'portfolio_mtrader_mean',
        'portfolio_ntrader_mean',
    ],
    title="Time vs. average porfolio of traders",
    xrange=(1,1530)
)

# Time vs. average cash of traders
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=[
        'cash_ftrader_mean',
        'cash_ttrader_mean',
        'cash_mtrader_mean',
        'cash_ntrader_mean',
    ],
    title="Time vs. average cash of traders",
    xrange=(1,1530)
)

# Time vs. average wealth of traders
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=[
        'wealth_ftrader_mean',
        'wealth_ttrader_mean',
        'wealth_mtrader_mean',
        'wealth_ntrader_mean',
    ],
    title="Time vs. average wealth of traders",
    xrange=(1,1530)
)

