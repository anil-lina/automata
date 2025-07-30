import pandas as pd
from datetime import datetime, timedelta

try:
    from . import config
    from .data import DataHandler
except ImportError:
    import config
    from data import DataHandler

class Screener:
    """
    Scans and filters stocks and options based on user-defined criteria.
    """
    def __init__(self, api_session):
        """
        Initializes the Screener.
        :param api_session: A logged-in ShoonyaApiPy object.
        """
        self.api = api_session
        self.data_handler = DataHandler(self.api)
        self.stock_list = config.stock_list
        self.screener_config = config.screener_config

    def _get_stock_movement_pct(self, exchange, token):
        """
        Calculates the stock's percentage price change over the last trading day.
        """
        # Fetch daily data for the last 5 days to ensure we can find the last two trading days
        daily_data = self.data_handler.get_historical_data(exchange=exchange, token=token, interval=1440, days_back=5)

        if daily_data is not None and len(daily_data) >= 2:
            last_close = daily_data['close'].iloc[-1]
            prev_close = daily_data['close'].iloc[-2]
            if prev_close > 0:
                movement_pct = ((last_close - prev_close) / prev_close) * 100
                return movement_pct
        return 0.0

    def screen_stocks(self):
        """
        Scans through the stock list and applies screening criteria.
        :return: A list of option contracts that meet the criteria.
        """
        promising_options = []

        if not self.stock_list:
            print("Stock list is empty. Please add stock symbols to config.py.")
            return promising_options

        for stock_symbol in self.stock_list:
            print(f"\n--- Screening {stock_symbol} ---")

            # 1. Find the stock's token
            search_res = self.api.searchscrip('NSE', stock_symbol)
            if not (search_res and search_res.get('values')):
                print(f"Could not find token for {stock_symbol}. Skipping.")
                continue
            stock_info = search_res['values'][0]
            stock_token = stock_info['token']

            # 2. Check stock price movement
            movement = self._get_stock_movement_pct('NSE', stock_token)
            if abs(movement) < self.screener_config['min_stock_movement_pct']:
                print(f"Stock movement of {movement:.2f}% is below the {self.screener_config['min_stock_movement_pct']}% threshold. Skipping.")
                continue
            print(f"Stock movement: {movement:.2f}% (meets criteria)")

            # 3. Get current price to find ATM strike for option chain
            quote = self.api.get_quotes('NSE', stock_token)
            try:
                spot_price = float(quote['lp'])
            except (TypeError, ValueError):
                print(f"Could not get a valid spot price for {stock_symbol}. Skipping.")
                continue

            # 4. Find a near-month futures contract to fetch the option chain
            base_symbol = stock_info['tsym'].split('-')[0]
            future_search_res = self.api.searchscrip('NFO', f"{base_symbol} FUT")
            if not (future_search_res and future_search_res.get('values')):
                print(f"Could not find a futures contract for {base_symbol} to get option chain. Skipping.")
                continue
            future_symbol = future_search_res['values'][0]['tsym']

            # 5. Fetch the option chain
            option_chain = self.data_handler.get_option_chain('NFO', future_symbol, spot_price, count=15)
            if not option_chain:
                print(f"Could not get option chain for {stock_symbol}. Skipping.")
                continue

            # 6. Screen individual options
            for option in option_chain:
                option_quote = self.api.get_quotes(option['exch'], option['token'])
                try:
                    volume = int(option_quote['v'])
                except (TypeError, ValueError):
                    continue

                if volume >= self.screener_config['min_option_volume']:
                    # Note: Filtering by Option Greeks is a complex feature.
                    # The `get_option_greek` API requires inputs like volatility and interest rate,
                    # which are not easily determined. This implementation focuses on stock
                    # movement and option volume as per the initial straightforward requirements.
                    print(f"  => Found promising option: {option['tsym']} (Volume: {volume})")
                    promising_options.append(option)

        return promising_options

if __name__ == '__main__':
    # This block is for demonstrating and testing the Screener.
    # It requires a valid API session and a populated stock_list in config.

    # from auth import Authenticator

    # # Add some stocks to your config.py for testing, e.g.:
    # # config.stock_list = ['RELIANCE-EQ', 'TCS-EQ', 'HDFCBANK-EQ']

    # print("Testing Screener...")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     screener = Screener(api_session)
    #     screened_options = screener.screen_stocks()

    #     if screened_options:
    #         print("\n--- Final Screener Results ---")
    #         for option in screened_options:
    #             print(option)
    #     else:
    #         print("\nNo options met the screening criteria.")
    # else:
    #     print("Login failed, cannot test Screener.")
    pass
