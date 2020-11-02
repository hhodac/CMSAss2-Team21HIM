import inspect

from utils import draw_from_normal


class MarketMaker:
    """
    Market maker sets the price at which agents can trade the asset
    based on demand for the asset during the previous time step
    """

    def __init__(self, initial_value=100.0, mu_value=0.0, sigma_value=0.25,
                 mu_price=0.0, sigma_price=0.4, liquidity=400):

        self.value_history = [initial_value]
        # mean of the fundamental price noise term (mu = 0.0)
        self.mu_value = mu_value
        # standard deviation for random term in fundamental value formation (sigma_V = 0.25)
        self.sigma_value = sigma_value

        # Initial price (P_0 = 100)
        self.price_history = [self.value_history[0]]
        # mean of the fundamental price noise term (mu = 0.0)
        self.mu_price = mu_price
        # standard deviation for random term in price formation (sigma_P = 0.4)
        self.sigma_price = sigma_price

        # Market Liquidity (liquidity = 400 from paper)
        self.liquidity = liquidity

        # excess market orders for the current day
        self.net_order = 0
        self.net_fundamental_order = 0
        self.net_technical_order = 0
        self.net_mimetic_order = 0
        self.net_noise_order = 0

        # time series of net daily orders by trader type
        self.order_history = []
        self.fundamental_order_history = []
        self.technical_order_history = []
        self.mimetic_order_history = []
        self.noise_order_history = []

        # model parameter dictionary of the market maker
        self.market_maker_parameters = {
            "V_0": self.value_history[0], "mu_V": self.mu_value, "sigma_V": self.sigma_value,
            "P_0": self.price_history[0], "mu_P": self.mu_price, "sigma_P": self.sigma_price,
            "liquidity": self.liquidity
        }

    def get_prices(self, low_limit=0, high_limit=None):
        """
        Returns the price history of the asset.
        """
        return self.price_history[low_limit:high_limit].copy()

    def get_values(self, low_limit, high_limit):
        """
        Returns the value history of the asset.
        """
        return self.value_history[low_limit:high_limit].copy()

    def get_orders(self, low_limit, high_limit):
        """
        Returns the order history of the asset.
        """
        return self.order_history[low_limit:high_limit].copy()

    def get_fundamental_orders(self, low_limit, high_limit):
        """
        Returns the fundamental order history of the asset.
        """
        return self.fundamental_order_history[low_limit:high_limit].copy()

    def get_technical_orders(self, low_limit, high_limit):
        """
        Returns the technical order history of the asset.
        """
        return self.technical_order_history[low_limit:high_limit].copy()

    def get_mimetic_orders(self, low_limit, high_limit):
        """
        Returns the mimetic order history of the asset.
        """
        return self.mimetic_order_history[low_limit:high_limit].copy()

    def get_noise_orders(self, low_limit, high_limit):
        """
        Returns the noise order history of the asset.
        """
        return self.noise_order_history[low_limit:high_limit].copy()

    def get_market_parameters(self):
        """
        Returns a dictionary containing the market maker parameters.
        """
        return self.market_maker_parameters

    def get_current_price(self):
        """
        Returns the current price of the asset.
        """
        return self.price_history[-1]

    def get_current_value(self):
        """
        Returns the current fundamental value.
        """
        return self.value_history[-1]

    def get_current_order(self):
        """
        Returns the current fundamental value.
        """
        return self.order_history[-1]

    def submit_order(self, order):
        """
        Receives an order from an agent and adds it to the total daily orders, depending on the agent type.
        """
        try:
            stack = inspect.stack()
            calling_class_name = stack[1][0].f_locals["self"].__class__.__name__

            self.net_order += order

            if calling_class_name == "Fundamentalist":
                self.net_fundamental_order += order
            elif calling_class_name == "Technical":
                self.net_technical_order += order
            elif calling_class_name == "Mimetic":
                self.net_mimetic_order += order
            elif calling_class_name == "Noise":
                self.net_noise_order += order
            else:
                raise Exception("Incorrect calling class names in submitOrder")
        except Exception as e:
            print(e)
        return

    def update_price(self):
        """
        Updates the current price based on the change in fundamental value
        and the net demand/supply of the previous time step.
        """
        self._update_value()
        self._update_price()
        self._update_orders()
        return

    def _update_value(self):
        """
        Updates the fundamental value of the asset via a random walk process.
        """
        try:
            last_value = self.value_history[-1]
            current_value = last_value + draw_from_normal(mu=self.mu_value, sigma=self.sigma_value)

            if current_value < 0:
                raise Exception("Fundamental value became negative")

            self.value_history.append(current_value)
        except Exception as e:
            print(e)
        return

    def _update_price(self):
        """
        Updates the current price based on a combination of previous price, total orders, market liquidity, and noise term. 
        """
        try:
            last_price = self.price_history[-1]
            last_order = self.order_history[-1]
            current_price = last_price + last_order / self.liquidity + draw_from_normal(mu=self.mu_price,
                                                                                        sigma=self.sigma_price)

            if current_price < 0:
                raise Exception("Current price became negative")

            self.price_history.append(current_price)
        except Exception as e:
            print(e)
        return

    def _update_orders(self):
        """
        Updates the instance variables that store the agent-dependent order history.
        """
        try:
            total_order = self.net_fundamental_order + self.net_technical_order \
                          + self.net_mimetic_order + self.net_noise_order

            if abs(self.net_order - total_order) > 1.0e-6:
                print("Net order = {} | Total order = {}".format(self.net_order, total_order))
                raise Exception("Orders don't sum up correctly in _update_orders")

            self.order_history.append(self.net_order)
            self.fundamental_order_history.append(self.net_fundamental_order)
            self.technical_order_history.append(self.net_technical_order)
            self.mimetic_order_history.append(self.net_mimetic_order)
            self.noise_order_history.append(self.net_noise_order)

            self._reset_orders()
        except Exception as e:
            print(e)
        return

    def _reset_orders(self):
        """
        When called, resets all current orders.
        """
        self.net_order = 0
        self.net_fundamental_order = 0
        self.net_technical_order = 0
        self.net_mimetic_order = 0
        self.net_noise_order = 0
        return
