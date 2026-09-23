from queue import Empty, Queue

from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import NaivePortfolio
from strategy import BuyAndHoldStrategy

class Backtest:
    """
    Encapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self,
        csv_dir,
        symbol_list,
        start_date,
        initial_capital,
    ):
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.events = Queue()

        self.data_handler = HistoricCSVDataHandler(
            events=self.events,
            csv_dir=self.csv_dir,
            symbol_list=self.symbol_list,
        )

        self.strategy = BuyAndHoldStrategy(
            bars=self.data_handler,
            events=self.events,
        )

        self.portfolio = NaivePortfolio(
            bars=self.data_handler,
            events=self.events,
            start_date=self.start_date,
            initial_capital=self.initial_capital,
        )

        self.execution_handler = SimulatedExecutionHandler(
            events=self.events,
            bars=self.data_handler,
        )

    def _run_backtest(self):
        """
        Executes the event-driven backtest.
        """

        while True:
            if self.data_handler.continue_backtest:
                self.data_handler.update_bars()
            else:
                break

            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    if event is not None:
                        self._handle_event(event)

    def _handle_event(self, event):
        """
        Routes a single event to the correct component.
        """

        if event.type == "MARKET":
            self.strategy.calculate_signals(event)
            self.portfolio.update_timeindex(event)
            # portfolio.update_timeindex(event) will go here later

        elif event.type == "SIGNAL":
            self.portfolio.update_signal(event)

        elif event.type == "ORDER":
            self.execution_handler.execute_order(event)

        elif event.type == "FILL":
            self.portfolio.update_fill(event)

    def run(self):
        """
        Runs the backtest and prints a simple summary.
        """

        self._run_backtest()

        print("Backtest complete.")
        print(self.portfolio.current_positions)
        print(self.portfolio.current_holdings)

if __name__ == "__main__":
    backtest = Backtest(
        csv_dir="data",
        symbol_list=["AAPL"],
        start_date="2025-01-02",
        initial_capital=100000.0,
    )

    backtest.run()