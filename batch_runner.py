from mesa.batchrunner import FixedBatchRunner
from model import *
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

simulation_batch = FixedBatchRunner(
    model_cls=HeterogeneityInArtificialMarket,
    model_reporters={
        "Price": get_market_price,
        "FundamentalValue": get_market_value,
        "Order": get_market_order,
        "NetFundamentalPosition": get_fundamental_position,
        "NetTechnicalPosition": get_technical_position
    },
    parameters_list={
        "initial_fundamentalist": 200,
        "initial_technical": 200,
        "initial_mimetic": 0,
        "initial_noise": 0,
        "simulation_period": 1,
        "network_type": "small world"
    },
    max_steps=10
)
model = HeterogeneityInArtificialMarket()
simulation_batch.run_model(model)

df = model.datacollector.get_model_vars_dataframe()
df.to_csv("batch_record.csv", header=True, index=False)
df_position = df[['NetFundamentalPosition', 'NetTechnicalPosition']]
sns.lineplot(data=df_position[1500:1750])
plt.xlabel('Time step')
plt.ylabel('Position')
plt.title('Net position changing over time')
plt.show()
