import numpy as np
from trader import Trader
from utils import draw_from_normal, draw_from_uniform


class Noise(Trader):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type"""
        super().__init__(unique_id, model_reference)

        self.model_reference = model_reference

        self.herding_probability = self.model_reference.HERDING_PROBABILITY
        self.buy_probability = self.model_reference.BUY_PROBABILITY
        self.sell_probability = self.model_reference.SELL_PROBABILITY

        self.mu_order_size = self.model_reference.MU_ORDER_SIZE
        self.sigma_order_size = self.model_reference.SIGMA_ORDER_SIZE

        if not ((0.0 <= self.buy_probability <= 0.5) and (0.0 <= self.sell_probability <= 0.5)):
            print("error in Noise trader probabilities")
            # exit()

    def trade(self, t):
        # if t == 1:
        #     exit()
        if draw_from_uniform(0.0, 1.0) <= self.herding_probability:
            # participate in herding
            ntrader_id = self.unique_id

            if ntrader_id in self.model_reference.coordinated_ntrader_behaviour["buy"]:
                # buy
                order = draw_from_normal(mu=self.mu_order_size, sigma=self.sigma_order_size, lower=0.0)
            elif ntrader_id in self.model_reference.coordinated_ntrader_behaviour["sell"]:
                # sell
                order = draw_from_normal(mu=-self.mu_order_size, sigma=self.sigma_order_size, upper=0.0)
            elif ntrader_id in self.model_reference.coordinated_ntrader_behaviour["hold"]:
                # hold
                order = 0.0
            else:
                print("ntrader id not found in behaviour dictionary")
                order = 0.0
        else:
            # trade randomly
            random_float = draw_from_uniform(0.0, 1.0)

            if 0.0 <= random_float < self.buy_probability:
                # buy order
                order = draw_from_normal(mu=self.mu_order_size, sigma=self.sigma_order_size, lower=0.0)
            elif self.buy_probability <= random_float < (self.buy_probability + self.sell_probability):
                # sell order
                order = draw_from_normal(mu=-self.mu_order_size, sigma=self.sigma_order_size, upper=0.0)
            else:
                order = 0.0

        # print(order)

        if self.is_within_risk_tolerance():
            self.position.append(self.position[-1] + order)
            self.order.append(order)
            self.market_maker.submit_order(order)
        else:
            self.position.append(self.position[-1])
            self.order.append(0.0)

        self.update_agent_finances()
