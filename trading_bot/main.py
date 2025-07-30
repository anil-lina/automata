try:
    from .auth import Authenticator
    from .screener import Screener
    from .data import DataHandler
    from .technical_analysis import TAHandler
    from .strategy import TradingStrategy
    from .backtest import Backtester
    from . import config
except ImportError:
    # This allows the script to be run directly for testing,
    # assuming the other modules are in the same directory.
    from auth import Authenticator
    from screener import Screener
    from data import DataHandler
    from technical_analysis import TAHandler
    from strategy import TradingStrategy
    from backtest import Backtester
    import config

def run_backtest_for_stock(stock_symbol, api_session):
    """
    Runs the full backtesting pipeline for a single stock symbol.
    """
    print(f"\n{'='*20} Starting Backtest for {stock_symbol.upper()} {'='*20}")

    data_handler = DataHandler(api_session)

    # 1. Get token for the stock
    search_res = api_session.searchscrip('NSE', stock_symbol)
    if not (search_res and search_res.get('values')):
        print(f"Could not find token for {stock_symbol}. Skipping.")
        return
    stock_token = search_res['values'][0]['token']

    # 2. Fetch Historical Data (using 1H timeframe from config)
    print(f"Fetching {config.timeframes['1H']} min historical data...")
    hist_data = data_handler.get_historical_data(
        exchange='NSE',
        token=stock_token,
        interval=config.timeframes['1H'],
        days_back=365 # Fetch one year of data for backtesting
    )
    if hist_data.empty:
        print(f"Could not fetch historical data for {stock_symbol}. Skipping.")
        return

    # 3. Add Technical Indicators
    print("Calculating technical indicators...")
    ta_handler = TAHandler(hist_data)
    df_with_indicators = ta_handler.add_indicators()

    # 4. Generate Trading Signals
    print("Generating trading signals...")
    strategy = TradingStrategy(df_with_indicators)
    df_with_signals = strategy.generate_signals()

    signals_found = df_with_signals[df_with_signals['signal'] != 0]
    if signals_found.empty:
        print("No trading signals were generated for the given period. Skipping backtest.")
        return
    print(f"Found {len(signals_found)} signals.")

    # 5. Run the Backtest
    backtester = Backtester(df_with_signals)
    backtester.run()
    backtester.get_results()
    print(f"{'='*20} Backtest for {stock_symbol.upper()} Complete {'='*20}")

def main():
    """
    The main function to orchestrate the trading bot's operations.
    """
    print("--- Trading Bot Initializing ---")

    # Step 1: Authentication
    authenticator = Authenticator()
    api_session = authenticator.login()

    if not api_session:
        print("\n--- Bot shutting down due to authentication failure. ---")
        return

    # At this point, the user should have stocks in their config.py
    # For now, we will run the backtest on the list from the config,
    # simulating the output of a screener.

    if not config.stock_list:
        print("\nNo stocks found in the configuration (`stock_list`). Please add some and run again.")
        print("Example: config.stock_list = ['RELIANCE-EQ', 'TCS-EQ']")
    else:
        for stock_symbol in config.stock_list:
            run_backtest_for_stock(stock_symbol, api_session)

    print("\n--- Trading Bot run has finished. ---")


if __name__ == '__main__':
    # To run this script, you must have your credentials correctly
    # set up in the `config.py` file.
    main()
