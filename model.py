import networkx as nx
from networkx.generators.random_graphs import watts_strogatz_graph
import random
import matplotlib.pyplot as plt

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

from fundamentalist import Fundamentalist
from technical import Technical
from mimetic import Mimetic
from noise import Noise

from market import MarketMaker
import utils

# Global variables
# For Fundamentalist Traders
fund_val_perception_var_min = -8.0
fund_val_perception_var_max = 8.0
fund_max_threshold_min = 2.0
fund_max_threshold_max = 5.0
fund_min_threshold_min = -0.5
fund_min_threshold_max = 1
# For Technical Traders
TECH_NORM_FACTOR = 25

def getMarketCurrentPrice(model):
    return model.marketMaker.getCurrentPrice()

def getMarketFundamentalPrice(model):
    return model.marketMaker.getFundamentalValue()

class HeterogeneityInArtificialMarket(Model):
    """A model for simulating effect of heterogenious type of traders on an artificial market model"""

    description = (
        "A model for simulating effect of heterogeneous type of traders on an artificial market model."
    )

    verbose = True  # Print-monitoring

    def __init__(
            self,
            height=50,
            width=50,
            initial_fundamentalist=25,
            initial_technical=25,
            initial_mimetic=25,
            initial_noise=25,
            initial_wealth=100,
            initial_fundamental_value=100, 
            sigma_fundamental_value=0.25, 
            volatility=400,
            **kwargs
    ):
        super().__init__()
        self.height = height
        self.width = width
        self.initial_fundamentalist = initial_fundamentalist
        self.initial_technical = initial_technical
        self.initial_mimetic = initial_mimetic
        self.initial_noise = initial_noise
        self.initial_wealth = initial_wealth
        self.initial_fundamental_value = initial_fundamental_value
        self.sigma_fundamental_value = sigma_fundamental_value
        self.volatility = sum([initial_fundamentalist,initial_technical,initial_mimetic,initial_noise])
        self.verbose = True

        # ID list of agent type
        self.ftrader_ids = list(range(1, initial_fundamentalist+1))
        self.ttrader_ids = list(range(self.ftrader_ids[-1]+1, self.ftrader_ids[-1]+initial_technical+1))
        self.mtrader_ids = list(range(self.ttrader_ids[-1]+1, self.ttrader_ids[-1]+initial_mimetic+1))
        self.ntrader_ids = list(range(self.mtrader_ids[-1]+1, self.mtrader_ids[-1]+initial_noise+1))

        # Initialize schedule to activate agent randomly
        self.schedule = RandomActivation(self)

        # Initialize market maker
        self.marketMaker = MarketMaker(self.initial_fundamental_value, self.sigma_fundamental_value, self.volatility)

        # Initialize traders & networks
        self.mimetic_network, self.G = self.generate_mimetic_trader_networks()
        _, _ = self.generate_small_world_networks()
        self.generate_traders()

        # Data collector for chart visualization
        self.datacollector = DataCollector(
            model_reporters={
                "Price": getMarketCurrentPrice,
                "FundamentalPrice": getMarketFundamentalPrice,
            }
        )
        # self.datacollector.collect(self)

        pass

    def generate_traders(self):
        """Generate all the traders and add them to schedule.
        Also generate a list of trader ids for mimetic trader's network generation.

        """
        # Create fundamentalist traders:
        for i in range(self.initial_fundamentalist):
            id = self.next_id()
            ftrader = Fundamentalist(id, self, "FUNDAMENTALIST", self.initial_wealth)
            self.mimetic_network.place_agent(ftrader, id)
            self.schedule.add(ftrader)

        # Create technical traders:
        for i in range(self.initial_technical):
            id = self.next_id()
            ttrader = Technical(id, self, "TECHNICAL", self.initial_wealth)
            self.mimetic_network.place_agent(ttrader, id)
            self.schedule.add(ttrader)

        # Create mimetic traders:
        for i in range(self.initial_mimetic):
            id = self.next_id()
            mtrader = Mimetic(id, self, "MIMETIC", self.initial_wealth)
            self.mimetic_network.place_agent(mtrader, id)
            self.schedule.add(mtrader)

        # Create noise traders:
        for i in range(self.initial_noise):
            id = self.next_id()
            ntrader = Noise(id, self, "NOISE", self.initial_wealth)
            self.mimetic_network.place_agent(ntrader, id)
            self.schedule.add(ntrader)

        pass

    def generate_small_world_networks(self):
        small_world_network = nx.Graph()
        nodes = list(range(1, sum([self.initial_fundamentalist, self.initial_technical, self.initial_mimetic, self.initial_noise])+1))
        nodes = random.sample(nodes, len(nodes))
        # connect each node to k/2 neighbors
        small_world_network.add_nodes_from(nodes)
        k = 5
        p = 0.5
        for j in range(1, k // 2+1):
            targets = nodes[j:] + nodes[0:j] # first j nodes are now last in list
            small_world_network.add_edges_from(zip(nodes,targets))
        # rewire edges from each node
        # loop over all nodes in order (label) and neighbors in order (distance)
        # no self loops or multiple edges allowed
        for j in range(1, k // 2+1): # outer loop is neighbors
            targets = nodes[j:] + nodes[0:j] # first j nodes are now last in list
            # inner loop in node order
            for u,v in zip(nodes,targets):
                if random.random() < p:
                    w = random.choice(nodes)
                    # Enforce no self-loops or multiple edges
                    while w == u or small_world_network.has_edge(u, w):
                        w = random.choice(nodes)
                        if small_world_network.degree(u) >= len(nodes)-1:
                            break # skip this rewiring
                    else:
                        small_world_network.remove_edge(u,v)
                        small_world_network.add_edge(u,w)
        # Debug = visualization
        # pos = nx.circular_layout(small_world_network)
        # plt.figure(figsize = (12, 12))
        # nx.draw_networkx(small_world_network, pos)
        # plt.show()
        # print("generated small world completed")
        return NetworkGrid(small_world_network), small_world_network

    def generate_mimetic_trader_networks(self):
        """Generate mimetic trader networks.
        Each mimetic trader is assigned in a network with 5 other agents,
        drawn from (fundamentalist & technical) traders.

        """
        total_agents = range(1, sum([self.initial_fundamentalist, self.initial_technical, self.initial_mimetic, self.initial_noise])+1)
        # nodes = list(total_agents)
        mimetic_network = nx.Graph()

        # Generate graph and networks of mimetic traders
        mimetic_network.add_nodes_from(total_agents)

        # Create list of agents for mimetic traders to follow
        l = self.ftrader_ids + self.ttrader_ids + self.ntrader_ids

        # Randomly assign 5 agents in the list to every mimetic trader
        for mimetic_id in self.mtrader_ids:
            random_pick_agent_ids = random.sample(l, 5)
            l_pairs = list([[mimetic_id, agent_id] for agent_id in random_pick_agent_ids])
            mimetic_network.add_edges_from(l_pairs)

        ##### Debug #####
        # pos = nx.circular_layout(mimetic_network)
        # nx.draw(mimetic_network, with_labels=True, font_weight='bold', pos=pos)
        # plt.show()
        # print(mimetic_network.number_of_edges())

        return NetworkGrid(mimetic_network), mimetic_network

    # Get the fundamental value perception variability from an uniform distribution.
    def get_fund_val_perception_var(self):
        return utils.drawFromNormal(fund_val_perception_var_min, fund_val_perception_var_max)

    # Get the maximum threshold for fundamentalist traders from an uniform distribution.
    def get_fund_max_threshold(self):
        return utils.drawFromNormal(fund_max_threshold_min, fund_max_threshold_max)

    # Get the minimum threshold for fundamentalist traders from an uniform distribution.
    def get_fund_min_threshold(self):
        return utils.drawFromNormal(fund_min_threshold_min, fund_min_threshold_max)

    def step(self):
        self.marketMaker.updatePrice()
        self.schedule.step()

        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.marketMaker.getCurrentPrice(),
                    self.marketMaker.getFundamentalValue()
                ]
            )
        pass

    def run_model(self, year_lapse=5):
        """Assuming there are 255 trading days per year.
        Total simulation period = 255 * year_lapse.
        Each step represents a trading day.

        :param year_lapse: simulation period
        :return:
        """

        if self.verbose:
            print("Initial number fundamentalist: ", self.initial_fundamentalist)
            print("Initial number technical: ", self.initial_technical)
            print("Initial number mimetic: ", self.initial_mimetic)
            print("Initial number noise: ", self.initial_noise)
            print("Current market price: :", self.marketMaker.getCurrentPrice())

        total_time_lapse = 255 * year_lapse
        for i in range(total_time_lapse):
            self.step()

    def get_mimetic_network(self):
        return self.mimetic_network

    def get_small_world(self):
        return self.small_world