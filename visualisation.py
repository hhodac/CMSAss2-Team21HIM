import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

experiment = 'Experiment2.8'
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


def plot_time_vs_selected_features(file_list, select_columns, title, xrange, ylabel, normalize=False, calibration=False):
    df_list = []
    df_list_positions = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        if normalize:
            for col in select_columns:
                initial_value = _df.loc[:,col][0]
                if initial_value != 0:
                    _df[col] = _df[col].div(initial_value)
                else:
                    print('initial value is zero')

        for col in select_columns:
            _df_select = _df.loc[:,['step', col]]
            if col.find("ftrader")>=0:
                _df_select['type'] = "fundamentalist"
            elif col.find("ttrader")>=0:
                _df_select['type'] = "technical"
            elif col.find("mtrader")>=0:
                _df_select['type'] = "mimetic"
            elif col.find("ntrader")>=0:
                _df_select['type'] = "noise"
            elif col.find("all")>=0:
                _df_select['type'] = "all"
            else:
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
    plt.xlabel("step", fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
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
plot_time_vs_selected_features(
    file_list=file_list,
    select_columns=['price', 'value'],
    title="Average price and fundamental value of traders as a function of time",
    ylabel="price/value",
    xrange=(1,1530)
)

def generate_selected_columns(prefix, suffix):
    default_targets = ['ftrader', 'ttrader', 'mtrader', 'ntrader', 'all']
    generate_columns = []
    for target in default_targets:
        generate_columns.append("_".join([prefix, target, suffix]))
    return generate_columns

experiment_list = [# 'title', 'prefix', 'suffix'
    #Wealth
    ['Normalized total wealth', 'wealth', 'sum', True],
    ['Normalized median wealth', 'wealth', 'median', True],
    ['Normalized standard deviation of wealth', 'wealth', 'std', True],
    #Position
    ['Total position', 'position', 'sum', False],
    ['Median position', 'position', 'median', False],
    ['Standard deviation of position', 'position', 'std', False],
    #Portfolio
    ['Total portfolio', 'portfolio', 'sum', False],
    ['Median portfolio', 'portfolio', 'median', False],
    ['Standard deviation of portfolio', 'portfolio', 'std', False],
    #Cash
    ['Normalized total cash', 'cash', 'sum', True],
    ['Normalized median cash', 'cash', 'median', True],
    ['Normalized standard deviation of cash', 'cash', 'std', True],
    #Standard deviation
    ['Total order', 'order', 'sum', False],
    ['Median order', 'order', 'median', False],
    ['Standard deviation of order', 'order', 'std', False],
]

for title, prefix, suffix, normalize in experiment_list:
    plot_time_vs_selected_features(
        file_list=file_list,
        select_columns=generate_selected_columns(prefix, suffix),
        title=title+" of traders as a function of time",
        ylabel=title,
        normalize=normalize,
        xrange=(1,1530)
    )

# # Wealth vs. time for each trader type (and for all traders, in black)
# # Total
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_sum',
#         'wealth_ttrader_sum',
#         'wealth_mtrader_sum',
#         'wealth_ntrader_sum',
#         'wealth_all_sum'
#     ],
#     title="Time vs. total wealth of traders",
#     xrange=(1,1530)
# )
#
# # Median
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_median',
#         'wealth_ttrader_median',
#         'wealth_mtrader_median',
#         'wealth_ntrader_median',
#         'wealth_all_median'
#     ],
#     title="Time vs. median wealth of traders",
#     xrange=(1,1530)
# )
#
# # Standard deviation
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_std',
#         'wealth_ttrader_std',
#         'wealth_mtrader_std',
#         'wealth_ntrader_std',
#         'wealth_all_std'
#     ],
#     title="Time vs. standard deviation of wealth of traders",
#     xrange=(1,1530)
# )
#
# # Position vs. time for each trader type (and for all traders, in black)
# # Total
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'position_ftrader_sum',
#         'position_ttrader_sum',
#         'position_mtrader_sum',
#         'position_ntrader_sum',
#         'position_all_sum'
#     ],
#     title="Time vs. total position of traders",
#     xrange=(1,1530)
# )
#
# # Median
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_median',
#         'wealth_ttrader_median',
#         'wealth_mtrader_median',
#         'wealth_ntrader_median',
#         'wealth_all_median'
#     ],
#     title="Time vs. median wealth of traders",
#     xrange=(1,1530)
# )
#
# # Standard deviation
# plot_time_vs_mean_of_selected_columns(
#     file_list=file_list,
#     select_columns=[
#         'wealth_ftrader_std',
#         'wealth_ttrader_std',
#         'wealth_mtrader_std',
#         'wealth_ntrader_std',
#         'wealth_all_std'
#     ],
#     title="Time vs. standard deviation of wealth of traders",
#     xrange=(1,1530)
# )
