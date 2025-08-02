import pandas as pd
import pandas_ta as ta
import requests
import zipfile
import io
import os
from datetime import datetime, timedelta
import time

# To run as a script, we need to handle the imports carefully
try:
    from .auth import Authenticator
    from .data import DataHandler
    from . import config
except ImportError:
    from auth import Authenticator
    from data import DataHandler
    import config

def download_nse_stocks():
    """
    Downloads the master list of NSE symbols from the Shoonya API,
    unzips it, and returns a list of equity stock symbols and their tokens.
    """
    url = "https://api.shoonya.com/NSE_symbols.txt.zip"
    print(f"Downloading master stock list from {url}...")

    try:
        response = requests.get(url)
        response.raise_for_status()

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        # The file inside the zip is named 'NSE_symbols.txt'
        with zip_file.open('NSE_symbols.txt') as file:
            df = pd.read_csv(file)

        # Filter for equities ('EQ') on the NSE exchange
        equities = df[(df['Instrument'] == 'EQ') & (df['Exchange'] == 'NSE')]
        # We only need the trading symbol and the token for API calls
        return equities[['Symbol', 'Token']].to_dict('records')

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download the stock list. {e}")
    except Exception as e:
        print(f"Error: Failed to process the stock list file. {e}")

    return []

def check_crossover(df: pd.DataFrame):
    """
    Checks for a bullish or bearish crossover on the last data point.
    Returns 'Bullish', 'Bearish', or None.
    """
    if len(df) < 2:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    try:
        macd_col = next(col for col in df.columns if col.startswith('MACD_'))
        signal_col = next(col for col in df.columns if col.startswith('MACDs_'))
    except StopIteration:
        return None # Should not happen if indicators were added correctly

    # Bullish Crossover: Price crosses above HMA AND MACD crosses above its signal line
    is_bullish = (prev['close'] < prev['hma'] and last['close'] > last['hma']) and \
                 (prev[macd_col] < prev[signal_col] and last[macd_col] > last[signal_col])

    # Bearish Crossover: Price crosses below HMA AND MACD crosses below its signal line
    is_bearish = (prev['close'] > prev['hma'] and last['close'] < last['hma']) and \
                 (prev[macd_col] > prev[signal_col] and last[macd_col] < last[signal_col])

    if is_bullish:
        return 'Bullish'
    if is_bearish:
        return 'Bearish'

    return None

def run_scanner():
    """
    Main function to run the standalone stock scanner.
    """
    print("--- Initializing Standalone Stock Scanner ---")

    authenticator = Authenticator()
    api_session = authenticator.login()
    if not api_session:
        print("\n--- Scanner shutting down due to authentication failure. ---")
        return

    data_handler = DataHandler(api_session)

    # 1. Get the list of all NSE stocks
    all_stocks = download_nse_stocks()
    if not all_stocks:
        print("\nCould not retrieve stock list. Exiting.")
        return

    print(f"\nFound {len(all_stocks)} NSE stocks to scan. This will take some time...")

    bullish_stocks = []
    bearish_stocks = []

    # 2. Iterate through each stock and check for the crossover condition
    for i, stock in enumerate(all_stocks):
        symbol, token = stock['Symbol'], str(stock['Token'])

        # Adding a small delay to avoid overwhelming the API
        time.sleep(0.5)

        print(f"Scanning ({i+1}/{len(all_stocks)}): {symbol}")

        # Fetch 1-hour data for the last ~60 days to ensure enough data for indicators
        hist_data = data_handler.get_historical_data('NSE', token, interval=60, days_back=60)

        if hist_data.empty or len(hist_data) < 50: # Need ~50 periods for slow MACD
            continue

        # Add indicators
        hist_data['hma'] = ta.hma(hist_data['close'], length=config.hma_period)
        macd = ta.macd(hist_data['close'], fast=config.macd_fast, slow=config.macd_slow, signal=config.macd_signal)
        hist_data = hist_data.join(macd)
        hist_data.dropna(inplace=True)

        # Check for crossover on the most recent data
        crossover_type = check_crossover(hist_data)

        if crossover_type == 'Bullish':
            bullish_stocks.append(symbol)
            print(f"  => Found Bullish Crossover for {symbol}")
        elif crossover_type == 'Bearish':
            bearish_stocks.append(symbol)
            print(f"  => Found Bearish Crossover for {symbol}")

    # 3. Display the final results
    print("\n" + "="*30)
    print("--- Scanner Run Complete ---")
    print("="*30)

    if bullish_stocks:
        print("\nBullish Crossover Stocks:")
        for s in bullish_stocks:
            print(f"- {s}")
    else:
        print("\nNo stocks found with a bullish crossover.")

    if bearish_stocks:
        print("\nBearish Crossover Stocks:")
        for s in bearish_stocks:
            print(f"- {s}")
    else:
        print("\nNo stocks found with a bearish crossover.")

    print("\n" + "="*30)

if __name__ == '__main__':
    run_scanner()
