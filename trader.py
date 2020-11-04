from mesa import Agent
from abc import abstractmethod
from utils import draw_from_pareto, draw_from_normal


class Trader(Agent):

    def __init__(self, unique_id, model_reference):
        super().__init__(unique_id, model_reference)
        self.market_maker = model_reference.market_maker

        self.initial_cash = draw_from_pareto(a=model_reference.PARETO_ALPHA, xm=model_reference.PARETO_XM,
                                             factor=model_reference.BASE_WEALTH)

        self.risk_tolerance = draw_from_normal(mu=model_reference.MU_RISK_TOLERANCE,
                                               sigma=model_reference.SIGMA_RISK_TOLERANCE, lower=0.1, upper=0.9)

        self.position = [0]
        self.order = [0]

        self.portfolio = [0]
        self.cash = [self.initial_cash]
        self.net_wealth = [self.initial_cash]

    def get_position(self, t):
        return self.position[t]

    def get_order(self, t):
        return self.order[t]

    def get_portfolio(self, t):
        return self.portfolio[t]

    def get_cash(self, t):
        return self.cash[t]

    def get_net_wealth(self, t):
        return self.net_wealth[t]

    def step(self):
        self.trade(self.model.schedule.time)
        return

    def is_within_risk_tolerance(self):
        if abs(self.portfolio[-1]) < (self.risk_tolerance * self.net_wealth[-1]):
            return True
        else:
            return False

    def update_agent_finances(self):
        self._update_cash()
        self._update_portfolio()
        self._update_net_wealth()

    def _update_cash(self):
        delta_position = self.order[-1]
        self.cash.append(self.cash[-1] - delta_position * self.market_maker.get_current_price())

    def _update_portfolio(self):
        self.portfolio.append(self.position[-1] * self.market_maker.get_current_price())

    def _update_net_wealth(self):
        self.net_wealth.append(self.cash[-1] + self.portfolio[-1])

    @abstractmethod
    def trade(self, t):
        pass


