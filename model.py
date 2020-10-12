import networkx as nx
from networkx.generators.random_graphs import watts_strogatz_graph
import random
import matplotlib.pyplot as plt

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid

from agents import Trader
from market import MarketMaker

def getMarketCurrentPrice(model):
    return model.marketMaker.getCurrentPrice()

def getMarketFundamentalPrice(model):
    return model.marketMaker.getFundamentalPrice()

class HeterogeneityInArtificialMarket(Model):
    """A model for simulating effect of heterogenious type of traders on an artificial market model"""

    height = 20
    width = 20

    initial_fundamentalist = 25
    initial_technical = 25
    initial_mimetic = 25
    initial_noise = 25
    initial_wealth = 100

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
        self.verbose = True

        # ID list of agent type
        self.ftrader_ids = []
        self.ttrader_ids = []
        self.mtrader_ids = []
        self.ntrader_ids = []

        # Initialize schedule to activate agent randomly
        self.schedule = RandomActivation(self)

        # Initialize GUI grid map
        self.grid = SingleGrid(self.width, self.height, torus=True)

        # Initialize market maker
        self.marketMaker = MarketMaker()

        # Initialize traders & networks
        self.generate_traders()
        self.mimetic_network = self.generate_mimetic_trader_networks()
        self.small_world = self.generate_small_world_networks()

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
            (x, y) = self.grid.find_empty()
            ftrader = Trader(id, (x, y), self, self.marketMaker, "FUNDAMENTALIST", self.initial_wealth)
            self.grid.place_agent(ftrader, (x, y))
            self.schedule.add(ftrader)
            self.ftrader_ids.append(id)

        # Create technical traders:
        for i in range(self.initial_technical):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            ttrader = Trader(id, (x, y), self, self.marketMaker, "TECHNICAL", self.initial_wealth)
            self.grid.place_agent(ttrader, (x, y))
            self.schedule.add(ttrader)
            self.ttrader_ids.append(id)

        # Create mimetic traders:
        for i in range(self.initial_mimetic):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            mtrader = Trader(id, (x, y), self, self.marketMaker, "MIMETIC", self.initial_wealth)
            self.grid.place_agent(mtrader, (x, y))
            self.schedule.add(mtrader)
            self.mtrader_ids.append(id)

        # Create noise traders:
        for i in range(self.initial_noise):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            ntrader = Trader(id, (x, y), self, self.marketMaker, "NOISE", self.initial_wealth)
            self.grid.place_agent(ntrader, (x, y))
            self.schedule.add(ntrader)
            self.ntrader_ids.append(id)

        pass

    def generate_small_world_networks(self):
        total_agents = sum([self.initial_fundamentalist,
                            self.initial_technical,
                            self.initial_mimetic,
                            self.initial_noise])
        small_world_network = watts_strogatz_graph(
            n=total_agents,
            k=5,                    # k nearest neighbours
            p=0.5,                  # probability of rewiring each edge
            seed=1234
        )

        # Debug = visualization
        # pos = nx.circular_layout(self.small_world)
        # plt.figure(figsize = (12, 12))
        # nx.draw_networkx(self.small_world, pos)
        # plt.show()
        return small_world_network

    def generate_mimetic_trader_networks(self):
        """Generate mimetic trader networks.
        Each mimetic trader is assigned in a network with 5 other agents,
        drawn from (fundamentalist & technical) traders.

        """
        mimetic_network = nx.Graph()

        # Generate graph and networks of mimetic traders
        mimetic_network.add_nodes_from([a.unique_id for a in self.schedule.agents])
        # Create list of agents for mimetic traders to follow
        l = self.ftrader_ids + self.ttrader_ids
        # Randomly assign 5 agents in the list to every mimetic trader
        for mimetic_id in self.mtrader_ids:
            random_pick_agent_ids = random.sample(l, 5)
            l_pairs = list([[mimetic_id, agent_id] for agent_id in random_pick_agent_ids])
            mimetic_network.add_edges_from(l_pairs)

        ##### Debug #####
        # nx.draw(self.mimetic_network, with_labels=True, font_weight='bold')
        # plt.show()
        # print(self.mimetic_network.number_of_edges())

        return mimetic_network


    def step(self):
        self.schedule.step()
        self.marketMaker.updatePrice()
        self.datacollector.collect(self)
        if self.verbose:
            print(
                [
                    self.schedule.time,
                    self.marketMaker.getCurrentPrice(),
                    self.marketMaker.getFundamentalPrice()
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