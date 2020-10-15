from trader import Trader
import utils
import model

class Fundamentalist(Trader):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, grid_pos, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, grid_pos, model, type, wealth)
        
        # Fundamental value perception variability (from uniform dist)
        self.fund_val_perception_var = 0 # model.get_fund_val_perception_var()
        # Fundamental value perception
        self.fund_val_perception = []
        # Maximum allowed difference between fundamental value perception and current price (from uniform dist)
        self.max_threshold = 5.0 # model.get_fund_max_threshold()
        # Minimum allowed difference between fundamental value perception and current price (from uniform dist)
        self.min_threshold = -5.0 # model.get_fund_min_threshold()                 

    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""

        # Get the current price
        self.price = self.marketMaker.getCurrentPrice()

        # Calculating the fundamental value perception.
        self.fund_val = self.marketMaker.getFundamentalValue()
        self.fund_val_perception.append(self.fund_val + self.fund_val_perception_var)

        # Check if the position has been liquidated.
        if self.position[t-1] == 0:
            if abs(self.fund_val_perception[t] - self.price) > self.max_threshold:
                self.position.append(self.fund_val_perception[t] - self.price)
            else:
                self.position.append(0)
        else:
            if abs(self.fund_val_perception[t] - self.price) < self.min_threshold:
                self.position.append(0)
            else:
                self.position.append(self.fund_val_perception[t] - self.price)

        self.order.append(self.position[t] - self.position[t-1])

        print(self.order[t])

        self.marketMaker.submitOrder(self.order[t])

        # How is the sell/buy process?