from trader import Trader
import numpy as np
from utils import draw_from_uniform


class Technical(Trader):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type
        """
        super().__init__(unique_id, model_reference)

        self.short_window = int(draw_from_uniform(model_reference.SHORT_WINDOW_MIN, model_reference.SHORT_WINDOW_MAX))
        self.long_window = int(draw_from_uniform(model_reference.LONG_WINDOW_MIN, model_reference.LONG_WINDOW_MAX))
        self.exit_window = int(draw_from_uniform(model_reference.EXIT_WINDOW_MIN, model_reference.EXIT_WINDOW_MAX))

        self.normalization_constant = model_reference.TECHNICAL_NORM_FACTOR

        # Short term moving average history.
        self.short_MA = []
        # Long term moving average history.
        self.long_MA = []

        # Difference in slope between the two moving averages.
        self.slope_difference = []

        self.current_price = 0.0

    def trade(self, t):
        """Describe trading behavior of technical trader"""

        # Get the current price.
        self.current_price = self.market_maker.get_current_price()

        # Get moving averages.
        self.short_MA.append(self._compute_moving_average(t, self.short_window))
        self.long_MA.append(self._compute_moving_average(t, self.long_window))

        # Get moving averages slope difference.
        self.slope_difference.append(self._compute_slope_difference(t))

        # Check if the position has been liquidated.
        if self.position[t-1] == 0:
            # Open a position (change its value to positive or negative).
            # Short term MA crosses long term MA from below. (price is going to increase)
            if self.short_MA[t-1] < self.long_MA[t-1] and self.short_MA[t] >= self.long_MA[t]:
                # Open a long position.
                self.position.append(self.normalization_constant * abs(self.slope_difference[t]))
            # Short term MA crosses long term MA from above. (price is going to decrease)
            elif self.short_MA[t-1] > self.long_MA[t-1] and self.short_MA[t] <= self.long_MA[t]:
                # Open a short position.
                self.position.append(-1 * self.normalization_constant * abs(self.slope_difference[t]))
            else:
                self.position.append(0)     # maintain the position at zero.

        elif self.position[t-1] > 0:
            # Liquidation condition. (current price is the lowest in the last "window" days)
            if self.current_price <= min(self._get_price_window(t, self.exit_window)):
                self.position.append(0)     # liquidate long position.
            else:
                # If the liquidation condition is not satisfied update with long position.
                self.position.append(self.normalization_constant * abs(self.slope_difference[t]))

        elif self.position[t-1] < 0:
            # Liquidation condition. (current price is the highest in the last "window" days)
            if self.current_price >= max(self._get_price_window(t, self.exit_window)):
                self.position.append(0)     # liquidate short position.
            else:
                # If the liquidation condition is not satisfied update with short position.
                self.position.append(-1 * self.normalization_constant * abs(self.slope_difference[t]))

        # Order > 0 : buy, Order = 0 : hold, Order < 0 : sell
        self.order.append(self.position[t] - self.position[t-1])

        self.market_maker.submit_order(self.order[t])

    def _compute_moving_average(self, t, window):
        """
        Returns the moving average of past prices in the given window.
        """
        return sum(self._get_price_window(t, window)) / window

    def _get_price_window(self, t, window):
        """
        Returns list of past prices for the given window.
        """
        if t >= (window - 1):
            return self.market_maker.get_prices(low_limit=(t - window + 1), high_limit=None)
        else:
            return []

    def _compute_slope_difference(self, t):
        """
        Returns the slope difference between
        the short and long term MAs in a given time.
        """
        return np.arctan(self.short_MA[t] - self.short_MA[t-1]) - np.arctan(self.long_MA[t] - self.long_MA[t-1])
