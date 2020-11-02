from trader import Trader
from utils import draw_from_normal


class Noise(Trader):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type"""
        super().__init__(unique_id, model_reference)

    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        order = draw_from_normal(mu=0.0, sigma=1.0)
        self.order.append(order)
        self.market_maker.submitOrder(order)
