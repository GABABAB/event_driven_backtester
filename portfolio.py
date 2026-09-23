from abc import ABC, abstractmethod

from event import OrderEvent


class Portfolio(ABC):
    """
    Abstract base class for portfolio management.
    """

    @abstractmethod
    def update_signal(self, event):
        """
        Convert a trading signal into an order.
        """
        raise NotImplementedError

    @abstractmethod
    def update_fill(self, event):
        """
        Update positions and holdings after an order is filled.
        """
        raise NotImplementedError


class NaivePortfolio(Portfolio):
    """
    Simple portfolio using fixed-size orders.
    """

    def __init__(
        self,
        bars,
        events,
        start_date,
        initial_capital=100000.0,
    ):
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.current_positions = {
            symbol: 0
            for symbol in self.symbol_list
        }

        self.all_positions = [
            self.construct_all_positions()
        ]

        self.current_holdings = {
            symbol: 0.0
            for symbol in self.symbol_list
        }

        self.all_holdings = [
            self.construct_all_holdings()
        ]

        self.current_holdings["cash"] = initial_capital
        self.current_holdings["commission"] = 0.0
        self.current_holdings["total"] = initial_capital

    def generate_naive_order(self, signal):
        """
        Convert a signal into a fixed-size market order.
        """

        symbol = signal.symbol
        direction = signal.signal_type
        quantity = 100

        current_quantity = self.current_positions[symbol]

        if direction == "LONG" and current_quantity == 0:
            return OrderEvent(
                symbol=symbol,
                order_type="MKT",
                quantity=quantity,
                direction="BUY",
            )

        if direction == "EXIT" and current_quantity > 0:
            return OrderEvent(
                symbol=symbol,
                order_type="MKT",
                quantity=abs(current_quantity),
                direction="SELL",
            )

        return None

    def update_signal(self, event):
        """
        Convert a SignalEvent into an OrderEvent.
        """

        if event.type == "SIGNAL":
            order = self.generate_naive_order(event)

            if order is not None:
                self.events.put(order)

    def construct_all_positions(self):
        d = {
            symbol: 0
            for symbol in self.symbol_list
        }

        d["datetime"] = self.start_date

        return d

    def construct_all_holdings(self):
        d = {
            symbol: 0.0
            for symbol in self.symbol_list
        }

        d["datetime"] = self.start_date
        d["cash"] = self.initial_capital
        d["commission"] = 0.0
        d["total"] = self.initial_capital

        return d

    def update_positions_from_fill(self, fill):
        """
        Updates positions after a FillEvent.
        """

        fill_dir = 0

        if fill.direction == "BUY":
            fill_dir = 1

        if fill.direction == "SELL":
            fill_dir = -1

        self.current_positions[fill.symbol] += (
            fill_dir * fill.quantity
        )

    def update_holdings_from_fill(self, fill):
        """
        Updates cash, commission and holdings after a FillEvent.
        """

        fill_dir = 0

        if fill.direction == "BUY":
            fill_dir = 1

        if fill.direction == "SELL":
            fill_dir = -1

        fill_cost = fill_dir * fill.fill_cost

        self.current_holdings[fill.symbol] += fill_cost
        self.current_holdings["commission"] += fill.commission
        self.current_holdings["cash"] -= (fill_cost + fill.commission)
        self.current_holdings["total"] -= (fill_cost + fill.commission)

    def update_fill(self, event):
        """
        Updates positions and holdings after a FillEvent.
        """

        if event.type == "FILL":
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
