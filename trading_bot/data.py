import pandas as pd
from datetime import datetime, timedelta

# To make this a module, I'll use a relative import.
try:
    from . import config
except ImportError:
    import config

class DataHandler:
    """
    Handles fetching historical data and option chains from the Shoonya API.
    """
    def __init__(self, api_session):
        """
        Initializes the DataHandler with an active API session.
        :param api_session: A logged-in ShoonyaApiPy object.
        """
        self.api = api_session

    def get_historical_data(self, exchange, token, interval, days_back=90):
        """
        Fetches historical candlestick data.
        :param exchange: The exchange of the instrument (e.g., 'NSE').
        :param token: The token of the instrument (e.g., '22').
        :param interval: The timeframe interval in minutes (e.g., 60 for 1H).
        :param days_back: The number of days of historical data to retrieve.
        :return: A pandas DataFrame with OHLCV data, indexed by time.
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        ret = self.api.get_time_price_series(
            exchange=exchange,
            token=token,
            starttime=start_time.timestamp(),
            endtime=end_time.timestamp(),
            interval=str(interval)
        )

        if ret:
            df = pd.DataFrame(ret)
            # Rename columns for clarity
            df.rename(columns={
                'time': 'timestamp',
                'into': 'open',
                'inth': 'high',
                'intl': 'low',
                'intc': 'close',
                'intv': 'volume'
            }, inplace=True)

            # Convert timestamp to datetime and set as index
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y %H:%M:%S')
            df.set_index('timestamp', inplace=True)

            # Convert OHLCV columns to numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.sort_index(inplace=True)
            return df
        else:
            print(f"Warning: Could not fetch historical data for {exchange}|{token}.")
            return pd.DataFrame()

    def get_option_chain(self, exchange, tradingsymbol, strikeprice, count=10):
        """
        Fetches the option chain for a given underlying symbol.
        :param exchange: The exchange of the options (e.g., 'NFO').
        :param tradingsymbol: The trading symbol of the underlying (e.g., 'NIFTY23DECFUT').
        :param strikeprice: The strike price to center the option chain around.
        :param count: The number of strikes to fetch on either side of the strikeprice.
        :return: A list of option contract details.
        """
        ret = self.api.get_option_chain(
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            strikeprice=strikeprice,
            count=count
        )

        if ret and ret.get('stat') == 'Ok':
            return ret.get('values', [])
        else:
            error_msg = ret.get('emsg') if ret else "Unknown error"
            print(f"Warning: Could not fetch option chain for {tradingsymbol}: {error_msg}")
            return []

if __name__ == '__main__':
    # This block is for demonstrating and testing the DataHandler.
    # It requires a valid API session to run.

    # from auth import Authenticator
    # print("Testing DataHandler...")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)

    #     # Example 1: Fetch historical data for INFY-EQ (token '1594' on NSE)
    #     print("\nFetching historical data for INFY-EQ...")
    #     historical_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60)
    #     if not historical_data.empty:
    #         print(historical_data.tail())
    #     else:
    #         print("Failed to fetch historical data.")

    #     # Example 2: Fetch option chain for NIFTY
    #     # Note: The 'tradingsymbol' for option chain needs to be a specific future or option symbol.
    #     print("\nFetching option chain for NIFTY...")
    #     # You would typically search for a current futures symbol first
    #     # e.g., nifty_fut_sym = api_session.searchscrip('NFO', 'NIFTY FUT')['values'][0]['tsym']
    #     # For this example, we'll use a placeholder symbol.
    #     option_chain_data = data_handler.get_option_chain(exchange='NFO', tradingsymbol='NIFTY24JANFUT', strikeprice=21500, count=2)
    #     if option_chain_data:
    #         print(f"Found {len(option_chain_data)} contracts in the option chain.")
    #         # Print details of the first few contracts
    #         for contract in option_chain_data[:3]:
    #             print(contract)
    #     else:
    #         print("Failed to fetch option chain.")
    # else:
    #     print("Could not test DataHandler because login failed.")
    pass
