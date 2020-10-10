from mesa import Agent

class Trader(Agent):
    """Represents heterogenious type of traders in the artificial market model"""

    grid = None
    x = None
    y = None

    def __init__(self, id, pos, model, marketMaker, type, wealth, eta, fund_val, fund_val_perception_var, fund_val_perception, max_threshold, min_threshold, price):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(id, model)
        self.pos = pos
        self.type = type
        self.wealth = wealth
        self.marketMaker = marketMaker

        # Parameters for fundamental traders (implement a dictionary): self.fund_params = dict()
        # Agent constant values
        # self.eta (from normal dist)
        # self.fund_val_perception_var (get from uniform dist)
        # self.max_threshold (from uniform dist)
        # self.min_threshold (from uniform dist)
        self.eta = eta
        self.fund_val = fund_val                                # Fundamental value
        self.fund_val_perception_var = fund_val_perception_var  # Fundamental value perception variability
        self.fund_val_perception = fund_val_perception          # Fundamental value perception
        self.max_threshold = max_threshold                      # Maximum allowed difference between fundamental value perception and current price
        self.min_threshold = min_threshold                      # Minimum allowed difference between fundamental value perception and current price
        self.price = price                                      # Current price: self.price[t] = self.marketMaker.getprice()                                
        pass

    def getType(self):
        return self.type

    def getPos(self):
        return self.pos

    def getWealth(self):
        return self.wealth

    def behaviorFundamentalist(self, t):
        """Describe trading behavior of fundamentalist trader"""

        self.fund_val[t] = self.fund_val[t-1] + self.eta
        self.fund_val_perception[t] = self.fund_val[t] + self.fund_val_perception_var

        # Check if the position has been liquidated.
        if self.pos[t-1] == 0:
            if abs(self.fund_val_perception[t] - self.price) > self.max_threshold:
                self.pos[t] = self.fund_val[t] - self.price
            else:
                self.pos[t] = 0
        else:
            if abs(self.fund_val_perception[t] - self.price) < self.min_threshold:
                self.pos[t] = 0
            else:
                self.pos[t] = self.fund_val_perception[t] - self.price

        self.order = self.pos[t] - self.pos[t-1]

        # self.marketMaker.submitorder(self.order)

        # How is the sell/buy process?
        

    def behaviorTechnical(self):
        """Describe trading behavior of technical trader"""
        pass

    def behaviorMimetic(self):
        """Describe trading behavior of mimetic trader"""
        pass

    def behaviorNoise(self):
        """Describe trading behavior of noise trader"""
        pass


    def step(self):
        """Describe sequence of trader's behavior in the model to run their step function
        in correspondence to model.HeterogeneityInArtificialMarket.schedule.step()"""
        pass