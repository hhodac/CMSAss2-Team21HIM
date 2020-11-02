from mesa import Agent
from abc import abstractmethod


class Trader(Agent):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model):
        """
        Generate a trader.
        """
        super().__init__(unique_id, model)
        self.marketMaker = model.marketMaker
        self.position = []
        self.order = []

    def step(self):
        """Describe sequence of trader's behavior in the model to run their step function
        in correspondence to model.HeterogeneityInArtificialMarket.schedule.step()"""
        self.trade(self.model.schedule.time)
        return

    @abstractmethod
    def trade(self, t):
        pass


