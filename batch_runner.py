from mesa.batchrunner import FixedBatchRunner
from model import *

simulation_batch = FixedBatchRunner(
    model_cls=HeterogeneityInArtificialMarket,
    model_reporters={
        "Price": get_market_price,
        "FundamentalValue": get_market_value,
        "Order": get_market_order,
        "NetFundamentalPosition": get_fundamental_position,
        "NetTechnicalPosition": get_technical_position
    },
    fixed_parameters={
        "initial_fundamentalist": 100,
        "initial_technical": 100,
        "initial_mimetic": 0,
        "initial_noise": 0,
        "network_type": "small world"
    },
    max_steps=1800
)

iterations = 10
for i in range(iterations):
    print("Step {}".format(i))
    model = HeterogeneityInArtificialMarket()
    simulation_batch.run_model(model)
    df = model.datacollector.get_model_vars_dataframe()
    file_name = "batch_record_"+str(i)+".csv"
    df.to_csv(file_name, header=True, index=False)
print("Completed!")
