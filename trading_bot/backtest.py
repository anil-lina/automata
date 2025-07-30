import pandas as pd
import numpy as np

class Backtester:
    """
    Simulates a trading strategy on historical data and provides performance metrics.
    """
    def __init__(self, df_with_signals: pd.DataFrame, initial_capital=100000.0):
        """
        Initializes the Backtester.
        :param df_with_signals: A pandas DataFrame with price data and a 'signal' column.
        :param initial_capital: The starting capital for the simulation.
        """
        self.df = df_with_signals
        self.initial_capital = initial_capital
        self.trades = []
        self.position = 0  # 0: flat, 1: long, -1: short
        self.entry_price = 0.0

    def run(self):
        """
        Executes the backtest simulation.

        This is a simplified backtester that assumes:
        - We trade a fixed quantity (e.g., 1 unit) per signal.
        - It does not account for transaction costs, slippage, or commission.
        """
        print("\n--- Running Backtest ---")
        if 'signal' not in self.df.columns:
            raise ValueError("DataFrame must contain a 'signal' column.")

        for i in range(len(self.df)):
            signal = self.df['signal'].iloc[i]
            price = self.df['close'].iloc[i]
            date = self.df.index[i]

            # Close position if signal is opposite to current position
            if (signal == -1 and self.position == 1) or (signal == 1 and self.position == -1):
                self._close_position(date, price)

            # Open a new position if we are flat and there is a signal
            if self.position == 0:
                if signal == 1:
                    self._open_position(date, price, 'long')
                elif signal == -1:
                    self._open_position(date, price, 'short')

        # If a position is still open at the end of the data, close it
        if self.position != 0:
            self._close_position(self.df.index[-1], self.df['close'].iloc[-1])

        print("--- Backtest Complete ---")

    def _open_position(self, date, price, trade_type):
        self.position = 1 if trade_type == 'long' else -1
        self.entry_price = price
        self.entry_date = date
        print(f"{date} | OPEN {trade_type.upper()} at {price:.2f}")

    def _close_position(self, date, price):
        pnl = (price - self.entry_price) if self.position == 1 else (self.entry_price - price)

        self.trades.append({
            'entry_date': self.entry_date,
            'exit_date': date,
            'entry_price': self.entry_price,
            'exit_price': price,
            'pnl': pnl,
            'type': 'long' if self.position == 1 else 'short'
        })

        print(f"{date} | CLOSE at {price:.2f} | PnL: {pnl:.2f}")
        self.position = 0

    def get_results(self):
        """
        Calculates and prints the performance summary.
        """
        if not self.trades:
            print("\nNo trades were executed during the backtest.")
            return

        trades_df = pd.DataFrame(self.trades)
        total_pnl = trades_df['pnl'].sum()
        num_trades = len(trades_df)
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]
        win_rate = (len(wins) / num_trades) * 100 if num_trades > 0 else 0
        avg_win = wins['pnl'].mean() if not wins.empty else 0
        avg_loss = losses['pnl'].mean() if not losses.empty else 0
        profit_factor = abs(wins['pnl'].sum() / losses['pnl'].sum()) if losses['pnl'].sum() != 0 else np.inf

        print("\n--- Backtest Performance ---")
        print(f"Initial Capital: {self.initial_capital:.2f}")
        print(f"Total Net PnL: {total_pnl:.2f}")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Total Trades: {num_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Average Win: {avg_win:.2f}")
        print(f"Average Loss: {avg_loss:.2f}")
        print("----------------------------")

        return trades_df

if __name__ == '__main__':
    # This block is for demonstrating and testing the Backtester.
    # It requires a DataFrame that has been processed by the Strategy module.

    # from data import DataHandler
    # from auth import Authenticator
    # from technical_analysis import TAHandler
    # from strategy import TradingStrategy

    # print("Testing Backtester...")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     # Fetch data for INFY-EQ
    #     hist_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60, days_back=365)

    #     if not hist_data.empty:
    #         # Add indicators
    #         ta_handler = TAHandler(hist_data)
    #         df_with_indicators = ta_handler.add_indicators()

    #         # Generate signals
    #         strategy = TradingStrategy(df_with_indicators)
    #         df_with_signals = strategy.generate_signals()

    #         if df_with_signals[df_with_signals['signal'] != 0].empty:
    #             print("No signals were generated, so the backtest cannot run.")
    #         else:
    #             # Run the backtest
    #             backtester = Backtester(df_with_signals)
    #             backtester.run()
    #             backtester.get_results()
    # else:
    #     print("Login failed, cannot test Backtester.")
    pass
