from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule


from fundamentalist import Fundamentalist
from technical import Technical
from mimetic import Mimetic
from noise import Noise



from model import HeterogeneityInArtificialMarket

TRADER_COLOR = {
    "FUNDAMENTALIST": "#0000FF",    # Blue
    "TECHNICAL": "#00FF00",         # Green
    "MIMETIC": "#FFFF00",           # Yellow
    "NOISE": "#454545",             # Gray
}

def get_agent_type(agent):
    if isinstance(agent, Fundamentalist):
        return "FUNDAMENTALIST"
    elif isinstance(agent, Technical):
        return "TECHNICAL"
    elif isinstance(agent, Mimetic):
        return "MIMETIC"
    elif isinstance(agent, Noise):
        return "NOISE"

def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return TRADER_COLOR[get_agent_type(agent)]

    portrayal = dict()
    nodes = list()
    for (_, agents) in G.nodes.data("agent"):
        node = dict()
        node["size"] = 6
        node["color"] = node_color(agents[0])
        node["tooltip"]= "id: {}<br>type: {}".format(
            agents[0].unique_id, get_agent_type(agents[0]))
        nodes.append(node)
    portrayal["nodes"] = nodes

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": "#e8e8e8",
            "width": 3,
        }
        for (source, target) in G.edges
    ]

    return portrayal


# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "initial_fundamentalist": UserSettableParameter(
        "slider", "fundamentalist_traders", 25, 0, 1000, description="Number of Fundamentalist Traders"
    ),
    "initial_technical": UserSettableParameter(
        "slider", "technical_traders", 25, 0, 1000, description="Number of Technical Traders"
    ),
    "initial_mimetic": UserSettableParameter(
        "slider", "mimetic_traders", 25, 0, 1000, description="Number of Mimetic Traders"
    ),
    "initial_noise": UserSettableParameter(
        "slider", "noise_traders", 25, 0, 1000, description="Number of Noise Traders"
    ),
    "network_type": UserSettableParameter(
        "choice", "network_type", value="customize", choices=["customize", "small world"]
    ),
}

network = NetworkModule(network_portrayal, 500, 500, library="d3")

chart_element = ChartModule(
    [
        {"Label": "current_price", "Color": '#FF0000'},
        {"Label": "current_value", "Color": '#00FF00'},
        # {"Label": "net_orders", "Color": '#0000FF'},
    ]
)

# create instance of Mesa ModularServer
server = ModularServer(
    model_cls=HeterogeneityInArtificialMarket,
    visualization_elements=[network, chart_element],
    name="Artificial Market",
    model_params=model_params,
)

server.port = 8521