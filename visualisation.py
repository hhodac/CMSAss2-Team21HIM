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

file_list = []
for file in os.listdir():
    if file.endswith(".csv"):
        file_list.append(os.path.join(".", file))

df_list = []
for file in file_list:
    _df = pd.read_csv(file, header=0)
    _df_position = _df[['Price', 'NetFundamentalPosition', 'NetTechnicalPosition']]
    df_list.append(_df_position)

# Plot sample fundamental position vs. technical position
sns.lineplot(data=df_list[0].iloc[1500:1750,[1,2]])
plt.xlabel("Step")
plt.ylabel("Position")
plt.title("Net Fundamental Position vs. Net Technical Position")
plt.savefig("Position comparison sample 1.png")
plt.show()

n_rows, _ = df_list[0].shape
df = pd.concat(df_list, axis=0)
price = df.Price.to_numpy().reshape(n_rows,len(file_list))
fpos = df.NetFundamentalPosition.to_numpy().reshape(n_rows,len(file_list))
tpos = df.NetTechnicalPosition.to_numpy().reshape(n_rows,len(file_list))

mean_price = np.mean(price, axis=1)
mean_fpos = np.mean(fpos, axis=1)
mean_tpos = np.mean(tpos, axis=1)

data = {
    'Step': range(n_rows),
    'Price': mean_price,
    'NetFundamentalPosition': mean_fpos,
    'NetTechnicalPosition': mean_tpos
}

df_visualize = pd.DataFrame(data)

fig, ax = plt.subplots(3, 1, figsize=(8,12))
fig.tight_layout(pad=3.0)
sns.lineplot(data=df_visualize[1500:1750], y="Price", x="Step", ax=ax[0])
sns.lineplot(data=df_visualize[1500:1750], y="NetFundamentalPosition", x="Step", ax=ax[1])
sns.lineplot(data=df_visualize[1500:1750], y="NetTechnicalPosition", x="Step", ax=ax[2])
ax[0].set_title('Price')
ax[1].set_title('Net Fundamental Position')
ax[2].set_title('Net Technical Position')
ax[0].set_xlabel('Step')
ax[1].set_xlabel('Step')
ax[2].set_xlabel('Step')
ax[0].set_ylabel('Value')
ax[1].set_ylabel('Position')
ax[2].set_ylabel('Position')
plt.savefig("Average of price and aggregate positions of fundamentalist and technical traders.png")
plt.show()
