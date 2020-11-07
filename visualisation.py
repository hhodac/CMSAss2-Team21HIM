import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

def get_file_index(file_path):
    chunks = file_path.split(".")
    idx = int(chunks[1].split("_")[-1])
    return idx

def get_normalisation_factor(max_all_position_ftrader, all_position_trader, trader):
    mean_all_position_trader = np.mean(all_position_trader, axis=0)
    # print("mean_all_position_" + trader + ":\n", mean_all_position_trader)

    max_all_position_trader = max(np.abs(mean_all_position_trader))
    print("max_all_position_" + trader + ":\n", max_all_position_trader)

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
    plt.legend(loc="best", fontsize=20)
    plt.savefig(os.path.join(dir, title+".png"))
    plt.show()

# dir = os.path.join(".", "Data", "Experiment5")
dir = "./"

file_list = []
for file in os.listdir(dir):
    if file.endswith(".csv"):
        file_list.append(os.path.join(dir, file))

# Time vs. average price and fundamental value
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=['current_price', 'current_value'],
    title="Time vs. average price and fundamental value",
    xrange=(1,1530)
)

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
    xrange=(1,1000),
    calibration=True
)

# # Time vs. average order of traders
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'order_ftrader_mean',
#         'order_ttrader_mean',
#         'order_mtrader_mean',
#         'order_ntrader_mean',
#     ],
#     title="Time vs. average order of traders",
#     xrange=(1,1530)
# )

# # Time vs. average porfolio of traders
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'portfolio_ftrader_mean',
#         'portfolio_ttrader_mean',
#         'portfolio_mtrader_mean',
#         'portfolio_ntrader_mean',
#     ],
#     title="Time vs. average porfolio of traders",
#     xrange=(1,1530)
# )

# # Time vs. average cash of traders
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'cash_ftrader_mean',
#         'cash_ttrader_mean',
#         'cash_mtrader_mean',
#         'cash_ntrader_mean',
#     ],
#     title="Time vs. average cash of traders",
#     xrange=(1,1530)
# )

# # Time vs. average wealth of traders
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_mean',
#         'wealth_ttrader_mean',
#         'wealth_mtrader_mean',
#         'wealth_ntrader_mean',
#     ],
#     title="Time vs. average wealth of traders",
#     xrange=(1,1530)
# )

##############
# # Plot sample fundamental position vs. technical position
# sns.lineplot(data=df_list[0].iloc[:,[1,2]])
# plt.xlabel("Step")
# plt.ylabel("Position")
# plt.title("Net Fundamental Position vs. Net Technical Position")
# plt.savefig(os.path.join(dir,"Position comparison sample 1.png"))
# plt.show()
# df_list = []
# for file in file_list:
#     _df = pd.read_csv(file, header=0)
#     _n_rows, _ = _df.shape
#     _df["iteration"] = np.full((_n_rows, 1), get_file_index(file))
#     _df_position = _df[['current_price', 'position_ftrader_mean', 'position_ttrader_mean']]
#     df_list.append(_df_position)
#
# # Plot sample fundamental position vs. technical position
# sns.lineplot(data=df_list[0].iloc[:,[1,2]])
# plt.xlabel("Step")
# plt.ylabel("Position")
# plt.title("Net Fundamental Position vs. Net Technical Position")
# plt.savefig(os.path.join(dir,"Position comparison sample 1.png"))
# plt.show()
#
# n_rows, _ = df_list[0].shape
# df = pd.concat(df_list, axis=0)
# price = df.current_price.to_numpy().reshape(len(file_list), n_rows)
# fpos = df.position_ftrader_mean.to_numpy().reshape(len(file_list), n_rows)
# tpos = df.position_ttrader_mean.to_numpy().reshape(len(file_list), n_rows)
#
# mean_price = np.mean(price, axis=0)
# mean_fpos = np.mean(fpos, axis=0)
# mean_tpos = np.mean(tpos, axis=0)
#
# data = {
#     'step': range(n_rows),
#     'current_price': mean_price,
#     'position_ftrader_mean': mean_fpos,
#     'position_ttrader_mean': mean_tpos
# }
#
# df_visualize = pd.DataFrame(data)
#
# fig, ax = plt.subplots(3, 1, figsize=(8,12))
# fig.tight_layout(pad=3.0)
# sns.lineplot(data=df_visualize, y="current_price", x="step", ax=ax[0])
# sns.lineplot(data=df_visualize, y="position_ftrader_mean", x="step", ax=ax[1])
# sns.lineplot(data=df_visualize, y="position_ttrader_mean", x="step", ax=ax[2])
# ax[0].set_title('Price')
# ax[1].set_title('Net Fundamental Position')
# ax[2].set_title('Net Technical Position')
# ax[0].set_xlabel('Step')
# ax[1].set_xlabel('Step')
# ax[2].set_xlabel('Step')
# ax[0].set_ylabel('Value')
# ax[1].set_ylabel('Position')
# ax[2].set_ylabel('Position')
# plt.savefig(os.path.join(dir,"Average of price and aggregate positions of fundamentalist and technical traders.png"))
# plt.show()
