from mesa.batchrunner import FixedBatchRunner
from model import *
import multiprocessing
import time
import os

dir_data = os.path.join('.', 'Data')
experiment = 'Experiment1.1'
dir_exp = os.path.join(dir_data, experiment)
if not os.path.exists(dir_exp):
    os.makedirs(dir_exp)

def run_simulation(i):
    print("Iteration {} running...".format(i))
    batch = FixedBatchRunner(model_cls=HeterogeneityInArtificialMarket, max_steps=1530)
    model = HeterogeneityInArtificialMarket(
        initial_fundamentalist=100,
        initial_technical=100,
        initial_mimetic=100,
        initial_noise=100,
        network_type="small world",
        verbose=False
    )
    batch.run_model(model)
    df = model.datacollector.get_model_vars_dataframe()
    file_name = os.path.join(dir_exp, "batch_record_"+str(i)+".csv")
    df.to_csv(file_name, header=True, index=False)
    print("Iteration {} completed.".format(i))


if __name__ == '__main__':
    # Activate multiprocessing
    start_time = time.time()
    print("Start multiprocessing...")

    optimal_thread_count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(optimal_thread_count)

    iterations = 10
    pool.map(run_simulation, list(range(iterations)))

    pool.close()
    pool.join()

    print("Completed!")
    end_time = time.time()
    duration = end_time - start_time
    print("Processing time: {}".format(duration))

