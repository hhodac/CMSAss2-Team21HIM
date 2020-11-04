from trader import Trader


class Mimetic(Trader):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type"""
        super().__init__(unique_id, model_reference)
        self.model_reference = model_reference

    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        if t == 0:
            self.order.append(0)
            self.position.append(0)
        else:
            neighbors_nodes = self.model_reference.network.get_neighbors(node_id=self.unique_id, include_center=False)
            chosen_successor = self.random.sample(self.model_reference.network.get_cell_list_contents(neighbors_nodes), 1)
            order = chosen_successor[0].get_order(t-1)

            if self.is_within_risk_tolerance():
                self.position.append(self.position[-1] + order)
                self.order.append(order)
                self.market_maker.submit_order(order)
            else:
                self.position.append(self.position[-1])
                self.order.append(0.0)

        self.update_agent_finances()
