from mesa.batchrunner import FixedBatchRunner
from model import *
import multiprocessing
import time

def fixed_batch_init():
    """
    Initializes and returns batch runner with fixed-parameters.
    """
    # Define fixed-parameters here
    params = {
        "initial_fundamentalist": 100,
        "initial_technical": 100,
        "initial_mimetic": 0,
        "initial_noise": 0,
        "network_type": "small world"
    }

    # Model reporter (similar to data collector from model.py)
    model_reporters = {
        "price": lambda m: m.get_market_parameters(param_name='price'),
        "value": lambda m: m.get_market_parameters(param_name='value')
        # "Order": get_market_order
        # "NetFundamentalPosition": get_fundamental_position,
        # "NetTechnicalPosition": get_technical_position
    }

    # Define number of maximum iterations
    MAX_ITERATIONS = 1530

    # Generate fixed batch runner object
    batch = FixedBatchRunner(
        model_cls=HeterogeneityInArtificialMarket,
        model_reporters=model_reporters,
        fixed_parameters=params,
        max_steps=MAX_ITERATIONS
    )
    return batch

def run_simulation(i):
    print("Iteration {} running...".format(i))
    simulation_batch = fixed_batch_init()
    model = HeterogeneityInArtificialMarket()
    simulation_batch.run_model(model)
    df = model.datacollector.get_model_vars_dataframe()
    file_name = "batch_record_"+str(i)+".csv"
    df.to_csv(file_name, header=True, index=False)
    print("Iteration {} completed.".format(i))

# Activate multiprocessing
start_time = time.time()
print("Start multiprocessing...")

optimal_thread_count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(optimal_thread_count)

iterations = 1
pool.map(run_simulation, list(range(iterations)))

pool.close()
pool.join()

print("Completed!")
end_time = time.time()
duration = end_time - start_time
print("Processing time: {}".format(duration))