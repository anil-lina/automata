import pandas as pd
import pandas_ta as ta

try:
    from . import config
except ImportError:
    import config

class TAHandler:
    """
    Handles the calculation of technical indicators on a given DataFrame.
    """
    def __init__(self, ohlcv_df: pd.DataFrame):
        """
        Initializes the TAHandler with a pandas DataFrame.
        :param ohlcv_df: A DataFrame with 'open', 'high', 'low', 'close', 'volume' columns.
        """
        if not isinstance(ohlcv_df, pd.DataFrame) or ohlcv_df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")
        self.df = ohlcv_df

    def add_indicators(self):
        """
        Calculates and adds all required technical indicators to the DataFrame.
        Reads parameters from the config file.
        """
        # Add HMA
        self.df['hma'] = ta.hma(self.df['close'], length=config.hma_period)

        # Add MACD
        macd = ta.macd(
            self.df['close'],
            fast=config.macd_fast,
            slow=config.macd_slow,
            signal=config.macd_signal
        )
        # pandas-ta returns a DataFrame with columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        # We will join this DataFrame with our main one.
        self.df = self.df.join(macd)

        # Clean up NaN values created by the indicators
        self.df.dropna(inplace=True)

        return self.df

if __name__ == '__main__':
    # This block is for demonstrating and testing the TAHandler.
    # It requires an active API session and a valid config.

    # from data import DataHandler
    # from auth import Authenticator

    # print("Testing TAHandler...")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     # Fetch some data for INFY-EQ (token '1594')
    #     historical_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60)

    #     if not historical_data.empty:
    #         print("\nOriginal Data:")
    #         print(historical_data.tail())

    #         # Initialize TAHandler and add indicators
    #         ta_handler = TAHandler(historical_data)
    #         df_with_indicators = ta_handler.add_indicators()

    #         print("\nData with Technical Indicators:")
    #         print(df_with_indicators.tail())
    #     else:
    #         print("Failed to fetch data, cannot test TAHandler.")
    # else:
    #     print("Login failed, cannot test TAHandler.")
    pass
