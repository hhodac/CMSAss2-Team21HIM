import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

def get_experiment_info(file_path):
    file_path_split = file_path.split("/")
    experiment_number = file_path_split[-2]

    file_name_split = file_path_split[-1].split(".")
    idx = int(file_name_split[0].split("_")[-1])

    return experiment_number, idx

def plot_time_vs_mean_of_selected_columns(file_list, select_columns, title, xrange):
    df_list = []
    for file in file_list:
        _df = pd.read_csv(file, header=0)
        _n_rows, _ = _df.shape
        experiment_no, _ = get_experiment_info(file)

        for col in select_columns:
            _df_select = _df.loc[:,['step', col]]
            _df_select['type'] = experiment_no
            _df_select = _df_select.rename(columns={col: "data"})
            df_list.append(_df_select)

    df = pd.concat(df_list, axis=0, ignore_index=True)

    plt.figure(figsize=(15.0, 9.0))
    sns.lineplot(data=df, x="step", y="data", ci="sd", hue="type")
    plt.title(title, fontsize=25)
    plt.xlabel("Step", fontsize=20)
    plt.ylabel(select_columns[0], fontsize=20)
    plt.yticks(fontsize=16)
    plt.xticks(fontsize=16)
    plt.xlim(xrange[0], xrange[1])
    plt.legend(loc="best", fontsize=20)
    plt.savefig(os.path.join(dir, title+".png"))
    plt.show()

dir = os.path.join(".", "Data")

file_list = []
for root, dirs, files in os.walk(dir):
    for file in files:
        if file.endswith(".csv"):
            file_list.append(os.path.join(root, file))

# Time vs. average price of all experiments
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=['current_price'],
    title="Time vs. average price of all experiments",
    xrange=(1,1530)
)

# Time vs. average fundamental value of all experiments
plot_time_vs_mean_of_selected_columns(
    file_list=file_list,
    select_columns=['current_value'],
    title="Time vs. average fundamental value of all experiments",
    xrange=(1,1530)
)