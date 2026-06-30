from abc import ABC, abstractmethod

from event import SignalEvent


class Strategy(ABC):
    #Abstract base class for all trading strategies.
    

    @abstractmethod
    def calculate_signals(self, event):
        #Calculate trading signals from new market data.
        
        raise NotImplementedError


class BuyAndHoldStrategy(Strategy):
    #Generates one LONG signal for each symbol, then holds it.
    

    def __init__(self, bars, events):
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list

        self.bought = {
            symbol: False
            for symbol in self.symbol_list
        }

    def calculate_signals(self, event):
        #Generate one long signal for each symbol.
        
        if event.type == "MARKET":
            for symbol in self.symbol_list:
                if not self.bought[symbol]:
                    latest_datetime = (
                        self.bars.get_latest_bar_datetime(symbol)
                    )

                    signal = SignalEvent(
                        strategy_id=1,
                        symbol=symbol,
                        datetime=latest_datetime,
                        signal_type="LONG",
                        strength=1.0,
                    )

                    self.events.put(signal)
                    self.bought[symbol] = True

