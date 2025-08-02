import pandas as pd
import pandas_ta as ta
import numpy as np

class FeatureEngineer:
    """
    Creates features and target variables from OHLCV data for AI models.
    """
    def __init__(self, ohlcv_df: pd.DataFrame):
        """
        Initializes the FeatureEngineer with a DataFrame.
        :param ohlcv_df: A pandas DataFrame with 'open', 'high', 'low', 'close', 'volume' columns.
        """
        if not isinstance(ohlcv_df, pd.DataFrame) or ohlcv_df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")
        # Work on a copy to avoid modifying the original DataFrame
        self.df = ohlcv_df.copy()

    def add_features(self):
        """
        Adds a variety of technical and price-based features to the DataFrame.
        """
        print("Adding features: returns, MAs, volatility, RSI, MACD, HMA...")
        # Returns
        self.df['log_return'] = np.log(self.df['close'] / self.df['close'].shift(1))
        self.df['percent_return'] = self.df['close'].pct_change()

        # Moving Averages
        for length in [10, 20, 50]:
            self.df[f'sma_{length}'] = ta.sma(self.df['close'], length=length)
            self.df[f'ema_{length}'] = ta.ema(self.df['close'], length=length)

        # Volatility (rolling standard deviation of log returns)
        self.df['volatility'] = self.df['log_return'].rolling(window=20).std()

        # RSI
        self.df['rsi'] = ta.rsi(self.df['close'], length=14)

        # HMA and MACD
        self.df['hma'] = ta.hma(self.df['close'], length=20)
        macd = ta.macd(self.df['close'], fast=12, slow=26, signal=9)
        self.df = self.df.join(macd)

        # Drop rows with NaN values that were created by the indicators
        self.df.dropna(inplace=True)

        return self.df

    def add_targets(self, forward_candles=5, return_threshold=0.01):
        """
        Adds the target variables for the predictive models.
        :param forward_candles: How many periods to look ahead to determine the outcome.
        :param return_threshold: The percentage change required to define a buy or sell signal.
        """
        print(f"Adding targets: next price and signal based on {return_threshold*100}% return over {forward_candles} candles...")
        # Target for Regression: The closing price of the next candle
        self.df['next_price'] = self.df['close'].shift(-1)

        # Target for Classification: A buy (1), sell (-1), or hold (0) signal
        future_return = self.df['close'].shift(-forward_candles).pct_change(forward_candles)

        # Define signals based on the future return
        self.df['signal'] = 0
        self.df.loc[future_return > return_threshold, 'signal'] = 1
        self.df.loc[future_return < -return_threshold, 'signal'] = -1

        # Remove rows where we cannot calculate targets (the last few rows)
        self.df.dropna(inplace=True)

        return self.df

    def get_data(self):
        """
        Returns the processed DataFrame with features and targets.
        """
        return self.df

if __name__ == '__main__':
    # This block demonstrates how to use the FeatureEngineer.
    # It requires an active API session to fetch data.

    # from data import DataHandler
    # from auth import Authenticator

    # print("--- Testing FeatureEngineer ---")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     # Fetch some historical data for testing
    #     hist_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60, days_back=200)

    #     if not hist_data.empty:
    #         # 1. Initialize the FeatureEngineer
    #         feature_engineer = FeatureEngineer(hist_data)

    #         # 2. Add features
    #         df_with_features = feature_engineer.add_features()

    #         # 3. Add targets
    #         df_with_targets = feature_engineer.add_targets()

    #         print("\n--- DataFrame with Features and Targets ---")
    #         # Display the last few rows to see the results
    #         print(df_with_targets.tail())

    #         # You can inspect the columns to see all the added features
    #         print("\nColumns:", df_with_targets.columns)

    #         # Check the distribution of signals
    #         print("\nSignal Distribution:")
    #         print(df_with_targets['signal'].value_counts())

    # else:
    #     print("Login failed, cannot test FeatureEngineer.")
    pass
