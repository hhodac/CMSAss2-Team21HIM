import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

df = pd.read_csv("batch_record.csv", header=0)
df_position = df[['NetFundamentalPosition', 'NetTechnicalPosition']]
sns.lineplot(data=df_position)
plt.xlabel('Time step')
plt.ylabel('Position')
plt.title('Net position changing over time')
plt.show()
