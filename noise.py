from trader import Trader
import utils
import model

class Noise(Trader):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, model, type, wealth)


    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        order = utils.drawFromNormal(0,1)*1000
        self.order.append(order)
        self.marketMaker.submitOrder(order)

        