import networkx as nx
from networkx.generators.random_graphs import watts_strogatz_graph
import random
import statistics

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

from fundamentalist import Fundamentalist
from technical import Technical
from mimetic import Mimetic
from noise import Noise

from market import MarketMaker


class HeterogeneityInArtificialMarket(Model):
    """A model for simulating effect of heterogeneous type of traders on an artificial market model"""

    description = (
        "A model for simulating effect of heterogeneous type of traders on an artificial market model."
    )

    # Global variables
    # For Fundamentalist Traders
    VALUE_PERCEPTION_MIN = -8.0
    VALUE_PERCEPTION_MAX = 8.0

    ENTRY_THRESHOLD_MIN = 2.0
    ENTRY_THRESHOLD_MAX = 5.0

    EXIT_THRESHOLD_MIN = -0.5
    EXIT_THRESHOLD_MAX = 1.0

    # For Technical Traders
    SHORT_WINDOW_MIN = 5
    SHORT_WINDOW_MAX = 15

    LONG_WINDOW_MIN = 35
    LONG_WINDOW_MAX = 50

    EXIT_WINDOW_MIN = 5
    EXIT_WINDOW_MAX = 30

    TECHNICAL_NORM_FACTOR = 25.0

    # For Market Maker
    INITIAL_VALUE = 100.0
    MU_VALUE = 0.0
    SIGMA_VALUE = 0.25

    MU_PRICE = 0.0
    SIGMA_PRICE = 0.4

    # For all agents
    PARETO_ALPHA = 1.3
    PARETO_XM = 1.0
    BASE_WEALTH = 1000.0

    MU_RISK_TOLERANCE = 0.5
    SIGMA_RISK_TOLERANCE = 0.2

    VERBOSE = False

    def __init__(
            self,
            initial_fundamentalist=25,
            initial_technical=25,
            initial_mimetic=25,
            initial_noise=25,
            network_type='customize',
            verbose=True
    ):
        super().__init__()

        self.initial_fundamentalist = initial_fundamentalist
        self.initial_technical = initial_technical
        self.initial_mimetic = initial_mimetic
        self.initial_noise = initial_noise

        self.network_type = network_type
        self.verbose = verbose
        self.liquidity = sum([initial_fundamentalist, initial_technical, initial_mimetic, initial_noise])

        # ID list of agent type
        self.ftrader_ids, self.ttrader_ids, self.mtrader_ids, self.ntrader_ids, = self.generate_traders_id()

        # Initialize schedule to activate agent randomly
        self.schedule = RandomActivation(self)

        # Initialize market maker
        self.market_maker = MarketMaker(initial_value=self.INITIAL_VALUE, mu_value=self.MU_VALUE,
                                       sigma_value=self.SIGMA_VALUE, mu_price=self.MU_PRICE,
                                       sigma_price=self.SIGMA_PRICE, liquidity=self.liquidity)

        # List of trader objects
        self.fundamental_traders = []
        self.technical_traders = []
        self.mimetic_traders = []
        self.noise_traders = []
        self.all_traders = []

        # Initialize traders & networks
        if network_type == "customize":
            self.network, self.G = self.generate_trader_networks()
        elif network_type == "small world":
            self.network, self.G = self.generate_small_world_networks()
        self.generate_traders()

        # Data collector for chart visualization
        self.datacollector = DataCollector(
            model_reporters={
                # "Price": get_market_price,
                # "Price": self.get_market_parameters(param_name='price')
                # "FundamentalValue": get_market_value,
                # "Order": get_market_order,
                # "NetFundamentalPosition": get_fundamental_position,
                # "NetTechnicalPosition": get_technical_position
            }
        )
        # self.datacollector.collect(self)

        pass

    def generate_traders_id(self):
        total_agents_id = list(range(self.liquidity))
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
            ftrader = Fundamentalist(id, self)
            self.fundamental_traders.append(ftrader)
            self.network.place_agent(ftrader, id)
            self.schedule.add(ftrader)

        # Create technical traders:
        for id in self.ttrader_ids:
            ttrader = Technical(id, self)
            self.technical_traders.append(ttrader)
            self.network.place_agent(ttrader, id)
            self.schedule.add(ttrader)

        # Create mimetic traders:
        for id in self.mtrader_ids:
            mtrader = Mimetic(id, self)
            self.mimetic_traders.append(mtrader)
            self.network.place_agent(mtrader, id)
            self.schedule.add(mtrader)

        # Create noise traders:
        for id in self.ntrader_ids:
            ntrader = Noise(id, self)
            self.noise_traders.append(ntrader)
            self.network.place_agent(ntrader, id)
            self.schedule.add(ntrader)

        self.all_traders = self.fundamental_traders + self.technical_traders + self.mimetic_traders + self.noise_traders

        pass

    def generate_small_world_networks(self):
        small_world_network = watts_strogatz_graph(self.liquidity, k=5, p=0.5)

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

        # Mimetic trader network
        # Randomly assign 2 ftraders & 2 ttraders to every mimetic trader
        for mimetic_id in self.mtrader_ids:
            random_pick_agent_ids = random.sample(self.ftrader_ids,2) + random.sample(self.ttrader_ids, 2)
            l_pairs = list([[mimetic_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        # Fundamentalist trader network
        # Randomly assign 2 ftraders & 2 ttraders to every ftraders
        for fundamentalist_id in self.ftrader_ids:
            random_pick_agent_ids = random.sample([id for id in self.ftrader_ids if id != fundamentalist_id], 2) \
                                    + random.sample(self.ttrader_ids, 2)
            l_pairs = list([[fundamentalist_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        # Technical trader network
        # Randomly assign 2 ftraders & 2 ttraders to every ttraders
        for technical_id in self.ttrader_ids:
            random_pick_agent_ids = random.sample([id for id in self.ttrader_ids if id != technical_id], 2) \
                                    + random.sample(self.ftrader_ids, 2)
            l_pairs = list([[technical_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ### Noise trader network
        # Randomly group 5 noise traders together
        for noise_id in self.ntrader_ids:
            pick_agent_ids = [id for id in self.ntrader_ids if id != noise_id]
            random_pick_agent_ids = random.sample(pick_agent_ids, 4)
            l_pairs = list([[noise_id, agent_id] for agent_id in random_pick_agent_ids])
            network.add_edges_from(l_pairs)

        ##### Debug #####
        # pos = nx.circular_layout(network)
        # nx.draw(network, with_labels=True, font_weight='bold', pos=pos)
        # plt.show()
        # print(network.number_of_edges())
        return NetworkGrid(network), network

    def step(self):
        self.market_maker.update_price()
        self.schedule.step()

        self.datacollector.collect(self)
        if self.VERBOSE:
            print("Step: {}, Value: {}, Price: {}, Orders: {}, F-sum-pos: {}, T-sum-pos: {}, F-median-wealth: {}, "
                  "T-median-wealth: {}".format(self.schedule.time, self.market_maker.get_current_value(),
                                        self.market_maker.get_current_price(), self.market_maker.get_current_order(),
                                        self.get_stats(trader_type='fundamental',
                                                       param_name='position', stats_type='sum'),
                                        self.get_stats(trader_type='technical',
                                                       param_name='position', stats_type='sum'),
                                        self.get_stats(trader_type='fundamental',
                                                       param_name='wealth', stats_type='median'),
                                        self.get_stats(trader_type='technical',
                                                       param_name='wealth', stats_type='median')))
        pass

    # def run_model(self):
    #     """Assuming there are 255 trading days per year.
    #     Total simulation period = 255 * year_lapse.
    #     Each step represents a trading day.
    #
    #     :param year_lapse: simulation period
    #     :return:
    #     """
    #
    #     if self.VERBOSE:
    #         print("Initial number fundamentalist: ", self.initial_fundamentalist)
    #         print("Initial number technical: ", self.initial_technical)
    #         print("Initial number mimetic: ", self.initial_mimetic)
    #         print("Initial number noise: ", self.initial_noise)
    #         print("Current market price: :", self.market_maker.get_current_price())
    #
    #     total_time_lapse = 5 * self.simulation_period
    #     for i in range(total_time_lapse):
    #         self.step()

    def get_network(self):
        return self.network

    def get_market_parameters(self, param_name):
        if param_name == "price":
            return self.market_maker.get_current_price()
        elif param_name == "value":
            return self.market_maker.get_current_value()
        elif param_name == "order":
            return self.market_maker.get_current_order()
        else:
            print("Error, unknown param_name in get_market_parameter")
            exit()

    def get_agent_stats(self, trader_type, param_name, stats_type):
        trader_list = []
        if trader_type == "fundamental":
            trader_list = self.fundamental_traders
        elif trader_type == "technical":
            trader_list = self.technical_traders
        elif trader_type == "mimetic":
            trader_list = self.mimetic_traders
        elif trader_type == "noise":
            trader_list = self.noise_traders
        elif trader_type == "all":
            trader_list = self.all_traders
        else:
            print("Error, unknown agent type")
            exit()

        all_parameters = []
        for trader in trader_list:
            if param_name == 'position':
                all_parameters.append(trader.get_position(self.schedule.time))
            elif param_name == 'order':
                all_parameters.append(trader.get_order(self.schedule.time))
            elif param_name == 'portfolio':
                all_parameters.append(trader.get_portfolio(self.schedule.time))
            elif param_name == 'cash':
                all_parameters.append(trader.get_cash(self.schedule.time))
            elif param_name == 'wealth':
                all_parameters.append(trader.get_net_wealth(self.schedule.time))
            else:
                print("Error, unknown parameter type")
                exit()

        if stats_type == 'max':
            return max(all_parameters)
        elif stats_type == 'min':
            return min(all_parameters)
        elif stats_type == 'sum':
            return sum(all_parameters)
        elif stats_type == 'mean':
            return statistics.mean(all_parameters)
        elif stats_type == 'median':
            return statistics.median(all_parameters)
        elif stats_type == 'std':
            return statistics.stdev(all_parameters) / len(all_parameters)
        else:
            print("Error, unknown stats type")
            exit()

