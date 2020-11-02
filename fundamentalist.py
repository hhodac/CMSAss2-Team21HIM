from trader import Trader
from utils import draw_from_uniform


class Fundamentalist(Trader):
    """Represents one of the heterogeneous types of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type
        """
        super().__init__(unique_id, model_reference)

        self.perception_offset = draw_from_uniform(model_reference.VALUE_PERCEPTION_MIN,
                                                   model_reference.VALUE_PERCEPTION_MAX)
        self.entry_threshold = draw_from_uniform(model_reference.ENTRY_THRESHOLD_MIN,
                                                 model_reference.ENTRY_THRESHOLD_MAX)
        self.exit_threshold = draw_from_uniform(model_reference.EXIT_THRESHOLD_MIN,
                                                model_reference.EXIT_THRESHOLD_MAX)

        self.current_price = 0.0
        self.value_perception = 0.0

    def trade(self, t):
        """Describes trading behavior of fundamentalist trader"""
        # Get the current price
        self.current_price = self.market_maker.get_current_price()
        # Calculating the fundamental value perception.
        self.value_perception = self.market_maker.get_current_value() + self.perception_offset

        # Check if the position has been liquidated.
        if self.position[t-1] == 0:
            # Open a position (change its value to positive or negative).
            if abs(self.value_perception - self.current_price) > self.entry_threshold:
                self.position.append(self.value_perception - self.current_price)
            else:
                self.position.append(0)     # maintain the position at zero.
        else:
            # Liquidation condition.
            if abs(self.value_perception - self.current_price) < self.exit_threshold:
                self.position.append(0)     # liquidate the position.
            else:
                # If the liquidation condition is not satisfied update the position.
                self.position.append(self.value_perception - self.current_price)

        # Order > 0 : buy, Order = 0 : hold, Order < 0 : sell
        self.order.append(self.position[t] - self.position[t-1])

        self.market_maker.submit_order(self.order[t])
