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
            network_type='customize',
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
        self.network_type = network_type

        # ID list of agent type
        self.ftrader_ids, self.ttrader_ids, self.mtrader_ids, self.ntrader_ids, = self.generate_traders_id()

        # Initialize schedule to activate agent randomly
        self.schedule = RandomActivation(self)

        # Initialize market maker
        self.marketMaker = MarketMaker(self.initial_fundamental_value, self.sigma_fundamental_value, self.volatility)

        # Initialize traders & networks
        if network_type == "customize":
            self.network, self.G = self.generate_trader_networks()
        elif network_type == "small world":
            self.network, self.G = self.generate_small_world_networks()
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

    def generate_traders_id(self):
        total_agents_id = list(range(self.volatility))
        random.shuffle(total_agents_id)
        ftrader_ids = [total_agents_id.pop() for _ in range(self.initial_fundamentalist)]
        ttrader_ids = [total_agents_id.pop() for _ in range(self.initial_technical)]
        mtrader_ids = [total_agents_id.pop() for _ in range(self.initial_mimetic)]
        ntrader_ids = [total_agents_id.pop() for _ in range(self.initial_noise)]
        return ftrader_ids, ttrader_ids, mtrader_ids, ntrader_ids

    def generate_traders(self):
        """Generate all the traders and add them to schedule.
        Also generate a list of trader ids for mimetic trader's network generation.

        """
        # Create fundamentalist traders:
        for id in self.ftrader_ids:
            ftrader = Fundamentalist(id, self, "FUNDAMENTALIST", self.initial_wealth)
            self.network.place_agent(ftrader, id)
            self.schedule.add(ftrader)

        # Create technical traders:
        for id in self.ttrader_ids:
            ttrader = Technical(id, self, "TECHNICAL", self.initial_wealth)
            self.network.place_agent(ttrader, id)
            self.schedule.add(ttrader)

        # Create mimetic traders:
        for id in self.mtrader_ids:
            mtrader = Mimetic(id, self, "MIMETIC", self.initial_wealth)
            self.network.place_agent(mtrader, id)
            self.schedule.add(mtrader)

        # Create noise traders:
        for id in self.ntrader_ids:
            ntrader = Noise(id, self, "NOISE", self.initial_wealth)
            self.network.place_agent(ntrader, id)
            self.schedule.add(ntrader)

        pass

    def generate_small_world_networks(self):
        small_world_network = watts_strogatz_graph(self.volatility, k=5, p=0.5)

        # Debug = visualization
        # pos = nx.circular_layout(small_world_network)
        # plt.figure(figsize = (12, 12))
        # nx.draw_networkx(small_world_network, pos)
        # plt.show()
        return NetworkGrid(small_world_network), small_world_network

    def generate_trader_networks(self):
        """Generate mimetic trader networks.
        Each mimetic trader is assigned in a network with 5 other agents,
        drawn from (fundamentalist & technical) traders.

        """
        total_agents = range(sum([self.initial_fundamentalist, self.initial_technical, self.initial_mimetic, self.initial_noise]))
        # nodes = list(total_agents)
        network = nx.Graph()

        # Generate graph and networks of mimetic traders
        network.add_nodes_from(total_agents)

        ### Mimetic trader network
        # Randomly assign 2 ftraders & 2 ttraders to every mimetic trader
        for mimetic_id in self.mtrader_ids:
            random_pick_agent_ids = random.sample(self.ftrader_ids,2) + random.sample(self.ttrader_ids,2)
            l_pairs = list([[mimetic_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ### Fundamentalist trader network
        # Randomly assign 2 ftraders & 2 ttraders to every ftraders
        for fundamentalist_id in self.ftrader_ids:
            random_pick_agent_ids = random.sample([id for id in self.ftrader_ids if id != fundamentalist_id],2) \
                                    + random.sample(self.ttrader_ids,2)
            l_pairs = list([[fundamentalist_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ### Technical trader network
        # Randomly assign 2 ftraders & 2 ttraders to every ttraders
        for technical_id in self.ttrader_ids:
            random_pick_agent_ids = random.sample([id for id in self.ttrader_ids if id != technical_id],2) \
                                    + random.sample(self.ftrader_ids,2)
            l_pairs = list([[technical_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ### Noise trader network
        # Randomly group 5 noise traders together
        for noise_id in self.ntrader_ids:
            pick_agent_ids = [id for id in self.ntrader_ids if id != noise_id]
            random_pick_agent_ids = random.sample(pick_agent_ids,4)
            l_pairs = list([[noise_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ##### Debug #####
        # pos = nx.circular_layout(network)
        # nx.draw(network, with_labels=True, font_weight='bold', pos=pos)
        # plt.show()
        # print(network.number_of_edges())
        return NetworkGrid(network), network

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

    def get_network(self):
        return self.network