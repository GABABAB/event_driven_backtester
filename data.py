import os
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from event import MarketEvent

class DataHandler(ABC):
    #Abstract base class for supplying market data
    @abstractmethod
    def get_latest_bar(self, symbol):
        #Return the latest bar for a symbol
        raise NotImplementedError
    
    @abstractmethod
    def get_latest_bars(self, symbol, number_of_bars=1):
        #Return the latest number of bars for a symbol
        raise NotImplementedError
    
    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        #Return datetime of latest bar
        raise NotImplementedError
    
    @abstractmethod
    def get_latest_bar_value(self, symbol, value_name):
        #Return one value from the latest bar.
        raise NotImplementedError
    
    @abstractmethod
    def get_latest_bars_values(
        self, 
        symbol,
        value_name,
        number_of_bars=1
        ):
        #Returns values from several recent bars
        raise NotImplementedError

    @abstractmethod
    def update_bars(self):
        #Move data handler forward by one bar
        raise NotImplementedError
    
class HistoricCSVDataHandler(DataHandler):
    #Reads historical price data from CSV files and supplies it to backtester one bar at a time
    def __init__(self, events, csv_dir, symbol_list):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}

        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        #Opens the csv files and prepares its data
        for symbol in self.symbol_list:
            csv_path = os.path.join(self.csv_dir, f"{symbol}.csv")

            self.symbol_data[symbol] = pd.read_csv(
                csv_path,
                header=0,
                index_col=0,
                parse_dates=True,
            )

            self.symbol_data[symbol] = self.symbol_data[symbol].iterrows()
            self.latest_symbol_data[symbol] = []

    def get_latest_bar(self, symbol):
        #Return the most latest bar 
        try:
            return self.latest_symbol_data[symbol][-1]
        except KeyError:
            raise KeyError(f"Symbol '{symbol}' is not available.")
        except IndexError:
            raise IndexError(f"No bars have been revealed yet for '{symbol}'")

    def get_latest_bars(self, symbol, number_of_bars=1):
        #Return most recent bars
        try:
            return self.latest_symbol_data[symbol][-number_of_bars:]
        except KeyError:
            raise KeyError(f"Symbol '{symbol}' is not available.")
        
    def get_latest_bar_datetime(self, symbol):
        #Return the datettime of most recent bar
        latest_bar = self.get_latest_bar(symbol)
        return latest_bar[0]
    
    def get_latest_bar_value(self, symbol, value_name):
        #Return one value from most recently revealed bar.
        latest_bar = self.get_latest_bar(symbol)
        return getattr(latest_bar[1], value_name)

    def get_latest_bars_values(self, symbol, value_name, number_of_bars=1):
        #Return one value from several recent bars
        bars = self.get_latest_bars(symbol, number_of_bars)

        return np.array(
            [getattr(bar[1], value_name) for bar in bars]
        )
    
    def update_bars(self):
        #Reveal one new bar for every symbol and create a MarketEvent.
        for symbol in self.symbol_list:
            try:
                bar = next(self.symbol_data[symbol])
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[symbol].append(bar)

        if self.continue_backtest:
            self.events.put(MarketEvent()) 

