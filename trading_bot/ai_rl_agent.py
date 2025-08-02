import pandas as pd
import os
import argparse

# To run as a script, we need to handle the imports carefully
try:
    from .ai_rl_environment import TradingEnv
    from .data import DataHandler
    from .auth import Authenticator
    from .ai_feature_engineering import FeatureEngineer
except ImportError:
    from ai_rl_environment import TradingEnv
    from data import DataHandler
    from auth import Authenticator
    from ai_feature_engineering import FeatureEngineer

# Import stable-baselines3
try:
    from stable_baselines3 import PPO
except ImportError:
    print("stable-baselines3 is not installed. Please install it with: pip install stable-baselines3[extra]")
    exit()


def train_rl_agent(stock_symbol: str, total_timesteps=25000):
    """
    The main function to train the RL agent.
    :param stock_symbol: The stock symbol to train the agent on (e.g., 'RELIANCE-EQ').
    :param total_timesteps: The number of steps to train the agent for.
    """
    print(f"--- Starting RL Agent Training for {stock_symbol} ---")

    # 1. Fetch and Prepare Data
    print("Connecting and fetching data...")
    authenticator = Authenticator()
    api_session = authenticator.login()
    if not api_session:
        print("Authentication failed. Cannot train agent.")
        return

    data_handler = DataHandler(api_session)
    search_res = api_session.searchscrip('NSE', stock_symbol)
    if not (search_res and search_res.get('values')):
        print(f"Could not find token for {stock_symbol}. Exiting.")
        return
    stock_token = search_res['values'][0]['token']

    # Using 2 years of data for more robust training
    hist_data = data_handler.get_historical_data('NSE', stock_token, interval=60, days_back=365 * 2)
    if hist_data.empty:
        print("Failed to fetch historical data. Exiting.")
        return

    print("Engineering features...")
    feature_engineer = FeatureEngineer(hist_data)
    df_with_features = feature_engineer.add_features()

    # 2. Initialize the Trading Environment
    print("Initializing trading environment...")
    env = TradingEnv(df_with_features)

    # 3. Initialize the PPO Agent
    # We use the MlpPolicy because our observation space is a flat vector of numbers.
    # Tensorboard logs will be saved to the specified directory for monitoring training.
    log_dir = "./rl_tensorboard_logs/"
    os.makedirs(log_dir, exist_ok=True)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)

    # 4. Train the Agent
    print(f"Starting training for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)

    # 5. Save the Trained Model
    model_dir = os.path.join('trained_models', stock_symbol)
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'ppo_rl_trader.zip')
    model.save(model_path)

    print(f"\n--- RL Agent Training Complete ---")
    print(f"Model saved to: {model_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train a Reinforcement Learning agent for stock trading.")
    parser.add_argument("symbol", type=str, help="The stock symbol to train the agent on (e.g., 'RELIANCE-EQ').")
    parser.add_argument("--timesteps", type=int, default=25000, help="The total number of timesteps to train for.")

    args = parser.parse_args()

    train_rl_agent(stock_symbol=args.symbol, total_timesteps=args.timesteps)
