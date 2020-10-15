from utils import drawFromUniform, drawFromNormal

class MarketMaker():
    """
    Market maker sets the price at which agents can trade the asset
    based on demand for the asset during the previous time step
    """

    def __init__(self, initial_fundamental_value, sigma_fundamental_value, volatility):
        self.fundamental_value = initial_fundamental_value
        self.sigma_fundamental_value = sigma_fundamental_value
        self.volatility = volatility
        
        # self.current_price = self.fundamental_value
        self.current_price = self.fundamental_value * 0.90
        self.total_orders = 0
        
        self.sigma_price_formation = 0.4
        self.mu_fundamental_value = 0
        self.mu_price_formation = 0

    def getCurrentPrice(self):
        """
        Returns the current price of the asset.
        """
        return self.current_price

    def getFundamentalValue(self):
        """
        Returns the current fundamental value.
        """
        return self.fundamental_value

    def updatePrice(self):
        """
        Updates the current price based on the change in fundamental value 
        and the net demand/supply of the previous time step.
        """
        self._updateFundamentalValue()
        self._updateCurrentPrice()
        self.total_orders = 0
        return

    def submitOrder(self, order):
        """
        Receives an order from an agent and adds it to the total daily orders.
        """
        self.total_orders += order
        return

    def _updateFundamentalValue(self):
        """
        Updates the fundamental value of the asset via a random walk process.
        """
        try:
            self.fundamental_value = self.fundamental_value # self.fundamental_value + drawFromNormal(mu=self.mu_fundamental_value, sigma=self.sigma_fundamental_value)    
            if self.fundamental_value < 0:
                raise Exception("Fundamental value became negative")            
        except Exception as e:
            print(e)
        return

    def _updateCurrentPrice(self):
        """
        Updates the current price based on a combination of previous price, total orders, market liquidity, and noise term. 
        """
        try:
            self.current_price = self.current_price + self.total_orders/self.volatility # + drawFromNormal(mu=self.mu_price_formation, sigma=self.sigma_price_formation)    
            if self.current_price < 0:
                raise Exception("Current price became negative")            
        except Exception as e:
            print(e)
        return
