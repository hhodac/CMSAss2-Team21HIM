import numpy as np
from trader import Trader
from utils import draw_from_uniform


class Mimetic(Trader):
    """Represents heterogeneous type of traders in the artificial financial market model"""

    def __init__(self, unique_id, model_reference):
        """Generate a trader with specific type"""
        super().__init__(unique_id, model_reference)
        self.model_reference = model_reference

        self.neighbour_ids = self.model_reference.network.get_neighbors(node_id=self.unique_id, include_center=False)
        # self.ft_neighbour_ids = [id for id in self.neighbour_ids if (id in self.model_reference.ftrader_ids) or (id in self.model_reference.ttrader_ids)]

        self.neighbours = []
        self.neighbour_list = []

        self.weights = []
        self.softmax_weights = []

        self.current_time = 0

        self.evaluation_period = int(draw_from_uniform(model_reference.MIN_PERIOD, model_reference.MAX_PERIOD))

    def trade(self, t):
        """Describe trading behavior of fundamentalist trader"""
        self.current_time = t

        if self.current_time == 0:
            self._find_neighbours()
            self.order.append(0)
            self.position.append(0)
        else:
            time_quotient = self.current_time // self.evaluation_period
            time_remainder = self.current_time % self.evaluation_period

            if (time_quotient >= 1) and (time_remainder == 0):

                print("time_step: ", self.current_time)

                self._sort_neighbours()

                self._update_weights()

                chosen_order = self._choose_order()

                if self.is_within_risk_tolerance():
                    self.position.append(self.position[-1] + chosen_order)
                    self.order.append(chosen_order)
                    self.market_maker.submit_order(chosen_order)
                else:
                    self.position.append(self.position[-1])
                    self.order.append(0.0)
            else:
                self.order.append(0)
                self.position.append(0)

        self.update_agent_finances()

    def _find_neighbours(self):
        self.neighbours = [trader for trader in self.model_reference.all_traders if
                           (trader.unique_id in self.neighbour_ids)]
        self.weights = [1.0 for _ in self.neighbours]
        self.softmax_weights = np.exp(self.weights) / sum(np.exp(self.weights))

    def _sort_neighbours(self):
        self.neighbour_list = []

        for trader in self.neighbours:
            current_wealth = trader.net_wealth[-1]
            past_wealth = trader.net_wealth[-self.evaluation_period]
            net_wealth = current_wealth - past_wealth

            net_order = 0.0
            for i in range(self.evaluation_period + 1):
                net_order += trader.order[-i]

            self.neighbour_list.append((trader, net_wealth, net_order))

        # sort neighbours by net wealth
        self.neighbour_list = sorted(self.neighbour_list, key=lambda t: t[1], reverse=True)

    def _update_weights(self):
        best_trader = self.neighbour_list[0][0]
        best_trader_id = best_trader.unique_id
        best_trader_net_wealth = self.neighbour_list[0][1]
        best_trader_net_order = self.neighbour_list[0][2]

        print("best_id: {}, best_net_wealth: {}, best_net_order: {}".format(best_trader_id, best_trader_net_wealth,
                                                                            best_trader_net_order))

        best_trader_index = self.neighbours.index(best_trader)

        self.weights[best_trader_index] = self.weights[best_trader_index] + 1.0
        self.softmax_weights = np.exp(self.weights) / sum(np.exp(self.weights))

        print("weights: {}, probabilities: {}".format(self.weights, self.softmax_weights))

    def _choose_order(self):
        chosen_trader = np.random.choice(a=self.neighbours, size=1, replace=True, p=self.softmax_weights)[0]
        chosen_trader_id = chosen_trader.unique_id

        chosen_trader_order = [tr for tr in self.neighbour_list if tr[0].unique_id == chosen_trader_id][0][2]

        print("chosen_id: {}, chosen_trader: {}, chosen_order: {}".format(chosen_trader_id, chosen_trader, chosen_trader_order))

        return chosen_trader_order

