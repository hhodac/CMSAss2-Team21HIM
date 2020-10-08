from mesa import Agent

class Trader(Agent):
    """Represents heterogenious type of traders in the artificial market model"""

    grid = None
    x = None
    y = None

    def __init__(self, unique_id, pos, model, marketMaker, type, wealth):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.type = type
        self.wealth = wealth
        self.marketMaker = marketMaker
        pass

    def getType(self):
        return self.type

    def getPos(self):
        return self.pos

    def getWealth(self):
        return self.wealth

    def behaviorFundamentalist(self):
        """Describe trading behavior of fundamentalist trader"""

        self.prev_pos = self.pos
        self.V_F = self.V + self.v_F

        if (self.V_F - self.P) > self.t_F or (self.V_F - self.P) < -self.t_F:
            self.pos = self.V_F - self.P
        elif (self.V_F - self.P) < self.t_F or (self.V_F - self.P) > -self.t_F:
            self.pos = 0
        elif (self.V_F - self.P) > self.T_F or (self.V_F - self.P) < -self.T_F:
            self.pos = self.V_F - self.P

        self.order = self.pos - self.prev_pos # Use an array

        return self.order

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