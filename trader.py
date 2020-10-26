from mesa import Agent

class Trader(Agent):
    """Represents heterogenious type of traders in the artificial financial market model"""

    def __init__(self, unique_id, grid_pos, model, type, wealth, **kwargs):
        """Generate a trader with specific type

        :param type: FUNDAMENTALIST, TECHNICAL, MIMETIC, NOISE
        """
        super().__init__(unique_id, model)
        self.pos = grid_pos
        self.position = [0]                     # Position history.                                         
        self.type = type
        self.wealth = wealth
        self.marketMaker = model.marketMaker
        self.order = [0]                        # Order history.

    def getType(self):
        return self.type

    def getPos(self):
        return self.pos

    def getWealth(self):
        return self.wealth

    def getPosition(self, t):
        return self.position[t]

    def getOrder(self, t):
        return self.order[t]

    def trade(self, t):
        return None

    def step(self):
        """Describe sequence of trader's behavior in the model to run their step function
        in correspondence to model.HeterogeneityInArtificialMarket.schedule.step()"""
        self.trade(self.model.schedule.time)
        pass