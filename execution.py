from abc import ABC, abstractmethod

from event import FillEvent


class ExecutionHandler(ABC):
    """
    Abstract base class for handling order execution.
    """

    @abstractmethod
    def execute_order(self, event):
        """
        Execute an OrderEvent, producing a FillEvent.
        """
        raise NotImplementedError

class SimulatedExecutionHandler(ExecutionHandler):
    """
    Simulates order execution by immediately filling every
    order at its requested price, on a fictional exchange.
    """

    def __init__(self, events, bars):
        self.events = events
        self.bars = bars

    def execute_order(self, event):
        """
        Converts an OrderEvent into a FillEvent with no
        latency, slippage or fill ratio issues.
        """

        if event.type == "ORDER":
            fill_price = self.bars.get_latest_bar_value(
                event.symbol, "Close"
            )

            fill_cost = fill_price * event.quantity

            fill = FillEvent(
                timeindex=self.bars.get_latest_bar_datetime(event.symbol),
                symbol=event.symbol,
                exchange="ARCA",
                quantity=event.quantity,
                direction=event.direction,
                fill_cost=fill_cost,
            )

            self.events.put(fill)