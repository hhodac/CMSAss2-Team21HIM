class MarketMaker():
    """Market maker sets the price at which agents can trade the asset
    based on demand for the asset during the previous time step"""

    def __init__(self, initial_price=100):
        # Market price
        self.initial_price = initial_price
        self.current_price = initial_price
        pass

    def getCurrentPrice(self):
        return self.current_price

    def getFundamentalPrice(self):
        return

    def updatePrice(self):
        pass

    def _updateCurrentPrice(self):
        pass

    def _updateFundamentalPrice(self):
        pass

    def submitOrder(self):
        pass

    def _priceFormation(self):
        pass