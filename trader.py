from mesa import Agent
from abc import abstractmethod


class Trader(Agent):

    def __init__(self, unique_id, model_reference):
        super().__init__(unique_id, model_reference)
        self.market_maker = model_reference.marketMaker
        self.position = []
        self.order = []

    def step(self):
        self.trade(self.model.schedule.time)
        return

    @abstractmethod
    def trade(self, t):
        pass


