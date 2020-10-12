from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import CanvasGrid

from trader import Trader
from market import MarketMaker
from model import HeterogeneityInArtificialMarket

grid_rows = 50
grid_cols = 50
cell_size = 10
canvas_width = grid_rows * cell_size
canvas_height = grid_cols * cell_size

TRADER_COLOR = {
    "FUNDAMENTALIST": "#0000FF",    # Blue
    "TECHNICAL": "#00FF00",         # Green
    "MIMETIC": "#FFFF00",           # Yellow
    "NOISE": "#454545",             # Gray
}

def trader_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Trader:
        portrayal = {"Shape": "circle",
                     "r": 1,
                     "Filled": "true",
                     "x": agent.getPos()[0],
                     "y": agent.getPos()[1],
                     "Color": TRADER_COLOR[agent.getType()],
                     "Layer": 0}

    elif type(agent) is MarketMaker:
        pass

    return portrayal


# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "initial_fundamentalist": UserSettableParameter(
        "slider", "fundamentalist_traders", 25, 1, 100, description="Number of Fundamentalist Traders"
    ),
    "initial_technical": UserSettableParameter(
        "slider", "technical_traders", 25, 1, 100, description="Number of Technical Traders"
    ),
    "initial_mimetic": UserSettableParameter(
        "slider", "mimetic_traders", 25, 1, 100, description="Number of Mimetic Traders"
    ),
    "initial_noise": UserSettableParameter(
        "slider", "noise_traders", 25, 1, 100, description="Number of Noise Traders"
    ),
    "initial_wealth": UserSettableParameter(
        "slider", "wealth", 100, 100, 1000, description="Initial wealth of each Trader"
    ),
}

canvas_element = CanvasGrid(
    trader_portrayal, grid_rows, grid_cols, canvas_width, canvas_height
)

chart_element = ChartModule(
    [
        {"Label": "Fundamentalist", "Color": TRADER_COLOR["FUNDAMENTALIST"]},
        {"Label": "Technical", "Color": TRADER_COLOR["TECHNICAL"]},
        {"Label": "Mimetic", "Color": TRADER_COLOR["MIMETIC"]},
        {"Label": "Noise", "Color": TRADER_COLOR["NOISE"]},
    ]
)

# create instance of Mesa ModularServer
server = ModularServer(
    model_cls=HeterogeneityInArtificialMarket,
    visualization_elements=[canvas_element],
    name="Artificial Market",
    model_params=model_params,
)

server.port = 8521