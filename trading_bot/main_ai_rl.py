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


def run_rl_simulation(stock_symbol: str, timesteps=500):
    """
    Loads a trained RL agent and runs it in the trading environment for simulation.
    :param stock_symbol: The stock symbol to run the simulation for.
    :param timesteps: The number of steps to simulate.
    """
    print(f"--- Starting RL Simulation for {stock_symbol} ---")

    model_path = os.path.join('trained_models', stock_symbol, 'ppo_rl_trader.zip')
    if not os.path.exists(model_path):
        print(f"Error: Trained model not found at '{model_path}'.")
        print(f"Please train the agent for {stock_symbol} first by running ai_rl_agent.py.")
        return

    # 1. Fetch Data for Simulation
    # It's good practice to test on a different period than the one used for training.
    print("Connecting and fetching data for simulation...")
    authenticator = Authenticator()
    api_session = authenticator.login()
    if not api_session:
        print("Authentication failed. Cannot run simulation.")
        return

    data_handler = DataHandler(api_session)
    search_res = api_session.searchscrip('NSE', stock_symbol)
    stock_token = search_res['values'][0]['token']

    # Fetch a different, more recent period for testing
    hist_data = data_handler.get_historical_data('NSE', stock_token, interval=60, days_back=100)
    if hist_data.empty:
        print("Failed to fetch data for simulation. Exiting.")
        return

    print("Engineering features for simulation data...")
    feature_engineer = FeatureEngineer(hist_data)
    df_with_features = feature_engineer.add_features()

    # 2. Initialize Environment and Load Model
    print("Initializing environment and loading trained agent...")
    env = TradingEnv(df_with_features)
    model = PPO.load(model_path, env=env)

    # 3. Run the Simulation
    print("\n--- Running Simulation ---")
    obs, _ = env.reset()
    for i in range(timesteps):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, _, info = env.step(action)

        action_map = {0: 'Sell', 1: 'Hold', 2: 'Buy'}
        print(f"Step {i+1}: Action: {action_map[action]}", end=" | ")
        env.render()

        if terminated:
            print("\nEpisode finished because the end of the dataset was reached.")
            break

    print("\n--- Simulation Complete ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run a trained Reinforcement Learning agent in a simulated trading environment.")
    parser.add_argument("symbol", type=str, help="The stock symbol to run the simulation for (e.g., 'RELIANCE-EQ').")
    parser.add_argument("--timesteps", type=int, default=500, help="The number of steps to simulate.")

    args = parser.parse_args()

    run_rl_simulation(stock_symbol=args.symbol, timesteps=args.timesteps)
