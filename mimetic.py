from trader import Trader
import utils
import model

class Mimetic(Trader):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, model, type, wealth)


    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        if t==0:
            self.order.append(0)
        else:
            neighbors_nodes = self.model.network.get_neighbors(node_id=self.unique_id, include_center=False)
            chosen_successor = self.random.sample(self.model.network.get_cell_list_contents(neighbors_nodes), 1)
            order = chosen_successor[0].getOrder(t-1)
            self.order.append(order)
            self.marketMaker.submitOrder(order)
            # pass