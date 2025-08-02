import pandas as pd
import numpy as np

class TradingStrategy:
    """
    Implements the trading logic based on MACD and HMA indicators.
    """
    def __init__(self, df_with_indicators: pd.DataFrame):
        """
        Initializes the strategy with a DataFrame that includes technical indicators.
        :param df_with_indicators: A pandas DataFrame containing price data, HMA, and MACD columns.
        """
        self.df = df_with_indicators
        # Dynamically find the correct MACD column names from pandas-ta
        try:
            self.macd_col = next(col for col in self.df.columns if col.startswith('MACD_'))
            self.macd_signal_col = next(col for col in self.df.columns if col.startswith('MACDs_'))
        except StopIteration:
            raise ValueError("MACD and MACD Signal columns not found in the DataFrame. Ensure indicators are added first.")

    def generate_signals(self):
        """
        Generates buy (1), sell (-1), and hold (0) signals.

        Long Signal Condition:
        1. Price crosses above HMA.
        2. MACD line crosses above its signal line.

        Short Signal Condition:
        1. Price crosses below HMA.
        2. MACD line crosses below its signal line.

        :return: A DataFrame with a 'signal' column.
        """
        # Initialize signal column with 0 (hold)
        self.df['signal'] = 0

        # --- Define Crossover Conditions ---

        # Price and HMA Crossover
        price_cross_above_hma = (self.df['close'].shift(1) <= self.df['hma'].shift(1)) & (self.df['close'] > self.df['hma'])
        price_cross_below_hma = (self.df['close'].shift(1) >= self.df['hma'].shift(1)) & (self.df['close'] < self.df['hma'])

        # MACD and Signal Line Crossover
        macd_cross_above_signal = (self.df[self.macd_col].shift(1) <= self.df[self.macd_signal_col].shift(1)) & \
                                  (self.df[self.macd_col] > self.df[self.macd_signal_col])
        macd_cross_below_signal = (self.df[self.macd_col].shift(1) >= self.df[self.macd_signal_col].shift(1)) & \
                                  (self.df[self.macd_col] < self.df[self.macd_signal_col])

        # --- Combine Conditions to Generate Signals ---

        # Generate Buy Signal (1)
        self.df.loc[price_cross_above_hma & macd_cross_above_signal, 'signal'] = 1

        # Generate Sell Signal (-1)
        self.df.loc[price_cross_below_hma & macd_cross_below_signal, 'signal'] = -1

        return self.df

if __name__ == '__main__':
    # This block is for demonstrating and testing the TradingStrategy.
    # It requires a DataFrame that has already been processed by TAHandler.

    # from data import DataHandler
    # from auth import Authenticator
    # from technical_analysis import TAHandler
    # import config

    # print("Testing TradingStrategy...")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     # Fetch data for INFY-EQ (token '1594')
    #     historical_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60, days_back=180)

    #     if not historical_data.empty:
    #         # Add technical indicators
    #         ta_handler = TAHandler(historical_data)
    #         df_with_indicators = ta_handler.add_indicators()

    #         # Initialize strategy and generate signals
    #         strategy = TradingStrategy(df_with_indicators)
    #         df_with_signals = strategy.generate_signals()

    #         print("\nDataFrame with trading signals:")
    #         # Display rows where a buy or sell signal is generated
    #         signal_rows = df_with_signals[df_with_signals['signal'] != 0]
    #         if not signal_rows.empty:
    #             print(signal_rows)
    #         else:
    #             print("No trading signals were generated in the given period.")
    #     else:
    #         print("Failed to fetch data, cannot test TradingStrategy.")
    # else:
    #     print("Login failed, cannot test TradingStrategy.")
    pass
