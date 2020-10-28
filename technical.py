from trader import Trader
import utils
import model
import numpy as np

class Technical(Trader):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, model, type, wealth)

        # (from uniform distributions)
        self.short_window = 10
        self.long_window = 35
        self.exit_channel_window = 5

        # Short term moving average history.
        self.short_MA = []
        # Long term moving average history.
        self.long_MA = []

        # Difference in slope between the two moving averages.
        self.slope_diff = []

    def trade(self, t):
        """Describe trading behavior of technical trader"""

        # Get the current price.
        self.price = self.marketMaker.getCurrentPrice()

        # Get moving averages.
        self.short_MA.append(self.getMovingAverage(t, self.short_window))
        self.long_MA.append(self.getMovingAverage(t, self.long_window))

        # Get moving averages slope difference.
        self.slope_diff.append(self.getSlopeDifference(t))

        # Check if the position has been liquidated.
        if self.position[t-1] == 0:
            # Open a position (change its value to positive or negative).
            # Short term MA crosses long term MA from below. (price is going to increase)
            if self.short_MA[t-1] < self.long_MA[t-1] and self.short_MA[t] >= self.long_MA[t]:
                # Open a long position.
                self.position.append(model.TECH_NORM_FACTOR * abs(self.slope_diff[t]))
            # Short term MA crosses long term MA from above. (price is going to decrease)
            elif self.short_MA[t-1] > self.long_MA[t-1] and self.short_MA[t] <= self.long_MA[t]:
                # Open a short position.
                self.position.append(-1 * model.TECH_NORM_FACTOR * abs(self.slope_diff[t]))
            else:
                self.position.append(0)     # maintain the position in zero.

        elif self.position[t-1] > 0:
            # Liquidation condition. (current price is the lowest in the last "window" days)
            if self.price == min(self.getPrices(t, self.exit_channel_window)):
                self.position.append(0)     # liquidate long position.
            else:
                # If the liquidation condition is not satisfied update with long position.
                self.position.append(model.TECH_NORM_FACTOR * abs(self.slope_diff[t]))

        elif self.position[t-1] < 0:
            # Liquidation condition. (current price is the highest in the last "window" days)
            if self.price == max(self.getPrices(t, self.exit_channel_window)):
                self.position.append(0)     # liquidate short position.
            else:
                # If the liquidation condition is not satisfied update with short position.
                self.position.append(-1 * model.TECH_NORM_FACTOR * abs(self.slope_diff[t]))

        # Order > 0 : buy
        # Order = 0 : hold
        # Order < 0 : sell
        self.order.append(self.position[t] - self.position[t-1])

        self.marketMaker.submitOrder(self.order[t])


    def getPrices(self, t, window):
        """
        Returns list of past prices between the given window.
        """
        low_limit = t - window + 1      #summing one time step because it starts from t=0
        if low_limit < 0:
            low_limit = 0

        # Getting the prices from low_limit to high_limit inclusively
        return self.marketMaker.getPriceHistory(low_limit=low_limit, high_limit=t)


    def getMovingAverage(self, t, window):
        """
        Returns the moving average of past prices between the given window.
        """
        # Getting the prices
        prices = self.getPrices(t, window)

        return sum(prices)/window


    def getSlopeDifference(self, t):
        """
        Returns the slope difference between
        the short and long term MAs in a given time.
        """
        return np.arctan(self.short_MA[t] - self.short_MA[t-1]) \
               - np.arctan(self.long_MA[t] - self.long_MA[t-1])


