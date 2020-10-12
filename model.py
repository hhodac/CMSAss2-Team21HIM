import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid

from trader import Trader
from fundamentalist import Fundamentalist
from technical import Technical
from mimetic import Mimetic
from noise import Noise

from market import MarketMaker
import utils

# Global variables
fund_val_perception_var_min = -8.0
fund_val_perception_var_max = 8.0
fund_max_threshold_min = 2.0
fund_max_threshold_max = 5.0
fund_min_threshold_min = -0.5
fund_min_threshold_max = 1

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

        # ID list of agent type
        self.ftrader_ids = []
        self.ttrader_ids = []
        self.mtrader_ids = []
        self.ntrader_ids = []

        # Initialize network
        self.G = nx.Graph()

        # Initialize schedule to activate agent randomly
        self.schedule = RandomActivation(self)

        # Initialize GUI grid map
        self.grid = SingleGrid(self.width, self.height, torus=True)

        # Initialize market maker
        self.marketMaker = MarketMaker()

        # Initialize traders & networks
        self.generate_traders()
        self.generate_mimetic_trader_networks()

        pass

    def generate_traders(self):
        """Generate all the traders and add them to schedule.
        Also generate a list of trader ids for mimetic trader's network generation.

        """
        # Create fundamentalist traders:
        for i in range(self.initial_fundamentalist):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            ftrader = Fundamentalist(id, (x, y), self, "FUNDAMENTALIST", self.initial_wealth)
            self.grid.place_agent(ftrader, (x, y))
            self.schedule.add(ftrader)
            self.ftrader_ids.append(id)

        # Create technical traders:
        for i in range(self.initial_technical):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            ttrader = Trader(id, (x, y), self, "TECHNICAL", self.initial_wealth)
            self.grid.place_agent(ttrader, (x, y))
            self.schedule.add(ttrader)
            self.ttrader_ids.append(id)

        # Create mimetic traders:
        for i in range(self.initial_mimetic):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            mtrader = Trader(id, (x, y), self, "MIMETIC", self.initial_wealth)
            self.grid.place_agent(mtrader, (x, y))
            self.schedule.add(mtrader)
            self.mtrader_ids.append(id)

        # Create noise traders:
        for i in range(self.initial_noise):
            id = self.next_id()
            (x, y) = self.grid.find_empty()
            ntrader = Trader(id, (x, y), self, "NOISE", self.initial_wealth)
            self.grid.place_agent(ntrader, (x, y))
            self.schedule.add(ntrader)
            self.ntrader_ids.append(id)

        pass

    def generate_mimetic_trader_networks(self):
        """Generate mimetic trader networks.
        Each mimetic trader is assigned in a network with 5 other agents,
        drawn from (fundamentalist & technical) traders.

        """
        # Generate graph and networks of mimetic traders
        self.G.add_nodes_from([a.unique_id for a in self.schedule.agents])
        # Create list of agents for mimetic traders to follow
        l = self.ftrader_ids + self.ttrader_ids
        # Randomly assign 5 agents in the list to every mimetic trader
        for mimetic_id in self.mtrader_ids:
            random_pick_agent_ids = random.sample(l, 5)
            l_pairs = list([[mimetic_id, agent_id] for agent_id in random_pick_agent_ids])
            self.G.add_edges_from(l_pairs)

        ##### Debug #####
        # nx.draw(self.G, with_labels=True, font_weight='bold')
        # plt.show()
        # print(self.G.number_of_edges())
        pass
    
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
        self.schedule.step()
        # self.marketMaker.update()
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

        total_time_lapse = 255 * year_lapse
        for i in range(total_time_lapse):
            self.step()