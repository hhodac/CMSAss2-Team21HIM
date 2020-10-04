from enum import Enum
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid, MultiGrid

from agents import Trader, MarketMaker

class Type(Enum):
    FUNDAMENTALIST = 0
    TECHNICAL = 1
    MIMETIC = 2
    NOISE = 3

def get_num_fundamentalist_traders(model):
    """ return number of fundamentalist traders"""
    traders = [trader for trader in model.schedule.agents if trader.type == Type.FUNDAMENTALIST]
    return len(traders)


def get_num_technical_traders(model):
    """return number of technical agents"""
    traders = [trader for trader in model.schedule.agents if trader.type == Type.TECHNICAL]
    return len(traders)


def get_num_mimetic_agents(model):
    """return number of mimetic traders"""
    traders = [trader for trader in model.schedule.agents if trader.type == Type.MIMETIC]
    return len(traders)


def get_num_noise_traders(model):
    """return number of noise traders"""
    traders = [trader for trader in model.schedule.agents if trader.type == Type.NOISE]
    return len(traders)


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

    verbose = False  # Print-monitoring

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


        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.height, self.width, torus=True)

        # Create fundamentalist traders:
        for i in range(self.initial_fundamentalist):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            ftrader = Trader(self.next_id(), (x, y), self, "FUNDAMENTALIST", self.initial_wealth)
            self.grid.place_agent(ftrader, (x, y))
            self.schedule.add(ftrader)

        # Create technical traders:
        for i in range(self.initial_technical):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            ttrader = Trader(self.next_id(), (x, y), self, "TECHNICAL", self.initial_wealth)
            self.grid.place_agent(ttrader, (x, y))
            self.schedule.add(ttrader)

        # Create mimetic traders:
        for i in range(self.initial_mimetic):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            mtrader = Trader(self.next_id(), (x, y), self, "MIMETIC", self.initial_wealth)
            self.grid.place_agent(mtrader, (x, y))
            self.schedule.add(mtrader)

        # Create noise traders:
        for i in range(self.initial_noise):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            ntrader = Trader(self.next_id(), (x, y), self, "NOISE", self.initial_wealth)
            self.grid.place_agent(ntrader, (x, y))
            self.schedule.add(ntrader)

        pass

    def step(self):
        self.schedule.step()
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