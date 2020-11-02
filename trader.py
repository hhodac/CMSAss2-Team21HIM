from mesa import Agent
from abc import abstractmethod


class Trader(Agent):

    def __init__(self, unique_id, model_reference):
        super().__init__(unique_id, model_reference)
        self.market_maker = model_reference.market_maker
        self.position = [0]
        self.order = [0]

    def step(self):
        self.trade(self.model.schedule.time)
        return

    def get_order(self, t):
        return self.order[t]

    @abstractmethod
    def trade(self, t):
        pass


