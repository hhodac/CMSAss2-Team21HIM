import networkx as nx
from networkx.generators.random_graphs import watts_strogatz_graph
import random
import statistics
import numpy as np

from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

from fundamentalist import Fundamentalist
from technical import Technical
from mimetic import Mimetic
from noise import Noise

from market import MarketMaker
from utils import draw_from_uniform


class HeterogeneityInArtificialMarket(Model):
    """A model for simulating effect of heterogeneous type of traders on an artificial market model"""

    description = (
        "A model for simulating effect of heterogeneous type of traders on an artificial market model."
    )

    # Global variables
    # For market maker V_{t} = V_{t-1} + N(0, sigma) + TREND_MAGNITUDE
    TREND_SIZE = 0.2                                              # default for experiment1.x: 0.0
    TREND_START_TIME = 500                                        # default for experiment1.x: 100
    TREND_END_TIME = 600                                          # default for experiment1.x: 200
    LOG_PRICE_FORMATION = False

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

    TECHNICAL_NORM_FACTOR = 25
    # MIMETIC_NORM_FACTOR = 17.5
    # NOISE_NORM_FACTOR = 1200

    # For Technical Traders
    MIN_PERIOD = 5
    MAX_PERIOD = 14

    # For Noise Traders
    BUY_PROBABILITY = 0.25           # should be b/w 0.0 and 0.5     default experiment1.x: 0.25
    SELL_PROBABILITY = 0.25          # should be b/w 0.0 and 0.5     default experiment1.x: 0.25
    HERDING_PROBABILITY = 0.60       # should be b/w 0.0 and 1.0     default experiment1.x: 0.6
    MIN_CLUSTER_SIZE = 10                                          # default experiment1.x: 10
    MAX_CLUSTER_SIZE = 20                                          # default experiment1.x: 20
    MU_ORDER_SIZE = 1.0                                            # default experiment1.x: 1.0
    SIGMA_ORDER_SIZE = 0.5                                         # default experiment1.x: 0.5

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

    MU_RISK_TOLERANCE = 0.4                                       # default for experiment1.x: 0.5
    SIGMA_RISK_TOLERANCE = 0.2

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
                                        sigma_price=self.SIGMA_PRICE, liquidity=self.liquidity,
                                        trend_size=self.TREND_SIZE, trend_start=self.TREND_START_TIME,
                                        trend_end=self.TREND_END_TIME, log_price_formation=self.LOG_PRICE_FORMATION)

        # List of trader objects
        self.fundamental_traders = []
        self.technical_traders = []
        self.mimetic_traders = []
        self.noise_traders = []
        self.all_traders = []

        self.clustered_ntrader_ids = []
        self.coordinated_ntrader_behaviour = dict()

        # Initialize traders & networks
        if network_type == "customize":
            self.network, self.G = self.generate_trader_networks()
        elif network_type == "small world":
            self.network, self.G = self.generate_small_world_networks()
        self.generate_traders()

        # Data collector for chart visualization
        self.datacollector = DataCollector(
            model_reporters={
                "step": lambda m: m.schedule.time,
                "price": lambda m: m.get_market_parameters(param_name='price'),
                "value": lambda m: m.get_market_parameters(param_name='value'),

                "order_ftrader_sum": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='order', stats_type='sum'),
                "order_ttrader_sum": lambda m: m.get_agent_stats(trader_type='technical', param_name='order', stats_type='sum'),
                "order_mtrader_sum": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='order', stats_type='sum'),
                "order_ntrader_sum": lambda m: m.get_agent_stats(trader_type='noise', param_name='order', stats_type='sum'),
                "order_all_sum": lambda m: m.get_agent_stats(trader_type='all', param_name='order', stats_type='sum'),

                "order_ftrader_mean": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='order', stats_type='mean'),
                "order_ttrader_mean": lambda m: m.get_agent_stats(trader_type='technical', param_name='order', stats_type='mean'),
                "order_mtrader_mean": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='order', stats_type='mean'),
                "order_ntrader_mean": lambda m: m.get_agent_stats(trader_type='noise', param_name='order', stats_type='mean'),
                "order_all_mean": lambda m: m.get_agent_stats(trader_type='all', param_name='order', stats_type='mean'),

                "order_ftrader_median": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='order', stats_type='median'),
                "order_ttrader_median": lambda m: m.get_agent_stats(trader_type='technical', param_name='order', stats_type='median'),
                "order_mtrader_median": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='order', stats_type='median'),
                "order_ntrader_median": lambda m: m.get_agent_stats(trader_type='noise', param_name='order', stats_type='median'),
                "order_all_median": lambda m: m.get_agent_stats(trader_type='all', param_name='order', stats_type='median'),

                "order_ftrader_std": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='order', stats_type='std'),
                "order_ttrader_std": lambda m: m.get_agent_stats(trader_type='technical', param_name='order', stats_type='std'),
                "order_mtrader_std": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='order', stats_type='std'),
                "order_ntrader_std": lambda m: m.get_agent_stats(trader_type='noise', param_name='order', stats_type='std'),
                "order_all_std": lambda m: m.get_agent_stats(trader_type='all', param_name='order', stats_type='std'),


                "position_ftrader_sum": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='position', stats_type='sum'),
                "position_ttrader_sum": lambda m: m.get_agent_stats(trader_type='technical', param_name='position', stats_type='sum'),
                "position_mtrader_sum": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='position', stats_type='sum'),
                "position_ntrader_sum": lambda m: m.get_agent_stats(trader_type='noise', param_name='position', stats_type='sum'),
                "position_all_sum": lambda m: m.get_agent_stats(trader_type='all', param_name='position', stats_type='sum'),

                "position_ftrader_mean": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='position', stats_type='mean'),
                "position_ttrader_mean": lambda m: m.get_agent_stats(trader_type='technical', param_name='position', stats_type='mean'),
                "position_mtrader_mean": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='position', stats_type='mean'),
                "position_ntrader_mean": lambda m: m.get_agent_stats(trader_type='noise', param_name='position', stats_type='mean'),
                "position_all_mean": lambda m: m.get_agent_stats(trader_type='all', param_name='position', stats_type='mean'),

                "position_ftrader_median": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='position', stats_type='median'),
                "position_ttrader_median": lambda m: m.get_agent_stats(trader_type='technical', param_name='position', stats_type='median'),
                "position_mtrader_median": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='position', stats_type='median'),
                "position_ntrader_median": lambda m: m.get_agent_stats(trader_type='noise', param_name='position', stats_type='median'),
                "position_all_median": lambda m: m.get_agent_stats(trader_type='all', param_name='position', stats_type='median'),

                "position_ftrader_std": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='position', stats_type='std'),
                "position_ttrader_std": lambda m: m.get_agent_stats(trader_type='technical', param_name='position', stats_type='std'),
                "position_mtrader_std": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='position', stats_type='std'),
                "position_ntrader_std": lambda m: m.get_agent_stats(trader_type='noise', param_name='position', stats_type='std'),
                "position_all_std": lambda m: m.get_agent_stats(trader_type='all', param_name='position', stats_type='std'),


                "wealth_ftrader_sum": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='wealth', stats_type='sum'),
                "wealth_ttrader_sum": lambda m: m.get_agent_stats(trader_type='technical', param_name='wealth', stats_type='sum'),
                "wealth_mtrader_sum": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='wealth', stats_type='sum'),
                "wealth_ntrader_sum": lambda m: m.get_agent_stats(trader_type='noise', param_name='wealth', stats_type='sum'),
                "wealth_all_sum": lambda m: m.get_agent_stats(trader_type='all', param_name='wealth', stats_type='sum'),

                "wealth_ftrader_mean": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='wealth', stats_type='mean'),
                "wealth_ttrader_mean": lambda m: m.get_agent_stats(trader_type='technical', param_name='wealth', stats_type='mean'),
                "wealth_mtrader_mean": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='wealth', stats_type='mean'),
                "wealth_ntrader_mean": lambda m: m.get_agent_stats(trader_type='noise', param_name='wealth', stats_type='mean'),
                "wealth_all_mean": lambda m: m.get_agent_stats(trader_type='all', param_name='wealth', stats_type='mean'),

                "wealth_ftrader_median": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='wealth', stats_type='median'),
                "wealth_ttrader_median": lambda m: m.get_agent_stats(trader_type='technical', param_name='wealth', stats_type='median'),
                "wealth_mtrader_median": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='wealth', stats_type='median'),
                "wealth_ntrader_median": lambda m: m.get_agent_stats(trader_type='noise', param_name='wealth', stats_type='median'),
                "wealth_all_median": lambda m: m.get_agent_stats(trader_type='all', param_name='wealth', stats_type='median'),

                "wealth_ftrader_std": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='wealth', stats_type='std'),
                "wealth_ttrader_std": lambda m: m.get_agent_stats(trader_type='technical', param_name='wealth', stats_type='std'),
                "wealth_mtrader_std": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='wealth', stats_type='std'),
                "wealth_ntrader_std": lambda m: m.get_agent_stats(trader_type='noise', param_name='wealth', stats_type='std'),
                "wealth_all_std": lambda m: m.get_agent_stats(trader_type='all', param_name='wealth', stats_type='std'),


                "cash_ftrader_sum": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='cash', stats_type='sum'),
                "cash_ttrader_sum": lambda m: m.get_agent_stats(trader_type='technical', param_name='cash', stats_type='sum'),
                "cash_mtrader_sum": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='cash', stats_type='sum'),
                "cash_ntrader_sum": lambda m: m.get_agent_stats(trader_type='noise', param_name='cash', stats_type='sum'),
                "cash_all_sum": lambda m: m.get_agent_stats(trader_type='all', param_name='cash', stats_type='sum'),

                "cash_ftrader_mean": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='cash', stats_type='mean'),
                "cash_ttrader_mean": lambda m: m.get_agent_stats(trader_type='technical', param_name='cash', stats_type='mean'),
                "cash_mtrader_mean": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='cash', stats_type='mean'),
                "cash_ntrader_mean": lambda m: m.get_agent_stats(trader_type='noise', param_name='cash', stats_type='mean'),
                "cash_all_mean": lambda m: m.get_agent_stats(trader_type='all', param_name='cash', stats_type='mean'),

                "cash_ftrader_median": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='cash', stats_type='median'),
                "cash_ttrader_median": lambda m: m.get_agent_stats(trader_type='technical', param_name='cash', stats_type='median'),
                "cash_mtrader_median": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='cash', stats_type='median'),
                "cash_ntrader_median": lambda m: m.get_agent_stats(trader_type='noise', param_name='cash', stats_type='median'),
                "cash_all_median": lambda m: m.get_agent_stats(trader_type='all', param_name='cash', stats_type='median'),

                "cash_ftrader_std": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='cash', stats_type='std'),
                "cash_ttrader_std": lambda m: m.get_agent_stats(trader_type='technical', param_name='cash', stats_type='std'),
                "cash_mtrader_std": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='cash', stats_type='std'),
                "cash_ntrader_std": lambda m: m.get_agent_stats(trader_type='noise', param_name='cash', stats_type='std'),
                "cash_all_std": lambda m: m.get_agent_stats(trader_type='all', param_name='cash', stats_type='std'),


                "portfolio_ftrader_sum": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='portfolio', stats_type='sum'),
                "portfolio_ttrader_sum": lambda m: m.get_agent_stats(trader_type='technical', param_name='portfolio', stats_type='sum'),
                "portfolio_mtrader_sum": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='portfolio', stats_type='sum'),
                "portfolio_ntrader_sum": lambda m: m.get_agent_stats(trader_type='noise', param_name='portfolio', stats_type='sum'),
                "portfolio_all_sum": lambda m: m.get_agent_stats(trader_type='all', param_name='portfolio', stats_type='sum'),

                "portfolio_ftrader_mean": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='portfolio', stats_type='mean'),
                "portfolio_ttrader_mean": lambda m: m.get_agent_stats(trader_type='technical', param_name='portfolio', stats_type='mean'),
                "portfolio_mtrader_mean": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='portfolio', stats_type='mean'),
                "portfolio_ntrader_mean": lambda m: m.get_agent_stats(trader_type='noise', param_name='portfolio', stats_type='mean'),
                "portfolio_all_mean": lambda m: m.get_agent_stats(trader_type='all', param_name='portfolio', stats_type='mean'),

                "portfolio_ftrader_median": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='portfolio', stats_type='median'),
                "portfolio_ttrader_median": lambda m: m.get_agent_stats(trader_type='technical', param_name='portfolio', stats_type='median'),
                "portfolio_mtrader_median": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='portfolio', stats_type='median'),
                "portfolio_ntrader_median": lambda m: m.get_agent_stats(trader_type='noise', param_name='portfolio', stats_type='median'),
                "portfolio_all_median": lambda m: m.get_agent_stats(trader_type='all', param_name='portfolio', stats_type='median'),

                "portfolio_ftrader_std": lambda m: m.get_agent_stats(trader_type='fundamental', param_name='portfolio', stats_type='std'),
                "portfolio_ttrader_std": lambda m: m.get_agent_stats(trader_type='technical', param_name='portfolio', stats_type='std'),
                "portfolio_mtrader_std": lambda m: m.get_agent_stats(trader_type='mimetic', param_name='portfolio', stats_type='std'),
                "portfolio_ntrader_std": lambda m: m.get_agent_stats(trader_type='noise', param_name='portfolio', stats_type='std'),
                "portfolio_all_std": lambda m: m.get_agent_stats(trader_type='all', param_name='portfolio', stats_type='std')
            }
        )

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

        return NetworkGrid(network), network

    def create_ntrader_clusters(self):
        remaining_list = self.ntrader_ids.copy()

        self.clustered_ntrader_ids = []

        while len(remaining_list) >= 1:
            sample_size = int(draw_from_uniform(lower=self.MIN_CLUSTER_SIZE, upper=self.MAX_CLUSTER_SIZE))
            sample_list = np.random.choice(a=remaining_list, size=sample_size, replace=True)
            sample_list = list(set(sample_list))
            remaining_list = [id for id in remaining_list if id not in sample_list]

            self.clustered_ntrader_ids.append(sample_list)

    def coordinate_ntrader_clusters(self):
        self.coordinated_ntrader_behaviour = {"buy": [], "sell": [], "hold": []}

        for cluster in self.clustered_ntrader_ids:
            random_float = draw_from_uniform(0.0, 1.0)

            if 0.0 <= random_float < self.BUY_PROBABILITY:
                # set cluster to buy and add to behaviour dictionary
                self.coordinated_ntrader_behaviour["buy"] = self.coordinated_ntrader_behaviour["buy"] + cluster
            elif self.BUY_PROBABILITY <= random_float < (self.BUY_PROBABILITY + self.SELL_PROBABILITY):
                # set cluster to sell and add to behaviour dictionary
                self.coordinated_ntrader_behaviour["sell"] = self.coordinated_ntrader_behaviour["sell"] + cluster
            else:
                # set cluster to hold and add to behaviour dictionary
                self.coordinated_ntrader_behaviour["hold"] = self.coordinated_ntrader_behaviour["hold"] + cluster

    def step(self):
        self.create_ntrader_clusters()
        self.coordinate_ntrader_clusters()
        self.market_maker.update_price()
        self.schedule.step()

        self.datacollector.collect(self)
        if self.verbose:
            print("Step: {}, Value: {}, Price: {}, Orders: {}, F-sum-pos: {}, T-sum-pos: {}, F-median-wealth: {}, "
                  "T-median-wealth: {}".format(self.schedule.time, self.market_maker.get_current_value(),
                                        self.market_maker.get_current_price(), self.market_maker.get_current_order(),
                                        self.get_agent_stats(trader_type='fundamental',
                                                       param_name='position', stats_type='sum'),
                                        self.get_agent_stats(trader_type='technical',
                                                       param_name='position', stats_type='sum'),
                                        self.get_agent_stats(trader_type='fundamental',
                                                       param_name='wealth', stats_type='median'),
                                        self.get_agent_stats(trader_type='technical',
                                                       param_name='wealth', stats_type='median')))
        pass

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

        if len(all_parameters) > 0:
            if stats_type == 'max':
                return max(all_parameters)
            elif stats_type == 'min':
                return min(all_parameters)
            elif stats_type == 'sum':
                if (param_name == 'position') or (param_name == 'order'):
                    all_parameters = [abs(element) for element in all_parameters]
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
        else:
            return None

