from trader import Trader
import utils
import model

class Noise(Trader):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, grid_pos, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, grid_pos, model, type, wealth)


    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        return None