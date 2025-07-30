import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """
    A custom stock trading environment for Reinforcement Learning.
    This environment conforms to the Gymnasium API.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, df: pd.DataFrame, window_size=10, initial_balance=100000):
        super(TradingEnv, self).__init__()

        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("A non-empty pandas DataFrame must be provided.")

        self.df = df
        self.window_size = window_size
        self.initial_balance = initial_balance

        # Define action space: 0=Sell, 1=Hold, 2=Buy
        self.action_space = spaces.Discrete(3)

        # Define observation space: A window of past data points
        # The shape is (window_size, number_of_features)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(window_size, len(df.columns)),
            dtype=np.float32
        )

        # Initialize portfolio state
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.current_step = 0

    def _get_observation(self):
        """Returns the observation for the current step."""
        # The observation is a slice of the DataFrame of size `window_size`
        return self.df.iloc[self.current_step:self.current_step + self.window_size].values

    def reset(self, seed=None, options=None):
        """Resets the environment to its initial state."""
        super().reset(seed=seed)

        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance

        # Start at a random step in the data to improve generalization
        self.current_step = np.random.randint(0, len(self.df) - self.window_size - 1)

        return self._get_observation(), {}

    def step(self, action):
        """Executes one time step in the environment."""
        current_price = self.df['close'].iloc[self.current_step + self.window_size]

        self._take_action(action, current_price)

        self.current_step += 1

        # Calculate the new net worth
        new_net_worth = self.balance + self.shares_held * current_price

        # The reward is the change in net worth from the previous step
        reward = new_net_worth - self.net_worth
        self.net_worth = new_net_worth

        # Check if the episode is done (reached the end of the data)
        terminated = self.current_step >= len(self.df) - self.window_size - 1

        obs = self._get_observation()

        return obs, reward, terminated, False, {}

    def _take_action(self, action, current_price):
        """Performs the buy, sell, or hold action."""
        # Action 0: Sell all shares
        if action == 0:
            if self.shares_held > 0:
                self.balance += self.shares_held * current_price
                self.shares_held = 0
        # Action 2: Buy with all available balance
        elif action == 2:
            if self.balance > 0:
                shares_to_buy = self.balance / current_price
                self.shares_held += shares_to_buy
                self.balance = 0
        # Action 1: Hold (do nothing)
        else:
            pass

    def render(self, mode='human'):
        """Renders the environment's state."""
        profit = self.net_worth - self.initial_balance
        print(
            f"Step: {self.current_step - self.window_size} | "
            f"Net Worth: {self.net_worth:,.2f} | "
            f"Profit: {profit:,.2f}"
        )

if __name__ == '__main__':
    # This block demonstrates how to use the TradingEnv.

    # from data import DataHandler
    # from auth import Authenticator
    # from ai_feature_engineering import FeatureEngineer
    # from stable_baselines3.common.env_checker import check_env

    # print("--- Testing Trading Environment ---")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     hist_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60, days_back=100)

    #     if not hist_data.empty:
    #         # Prepare data with features
    #         feature_engineer = FeatureEngineer(hist_data)
    #         df_with_features = feature_engineer.add_features()

    #         # Initialize the environment
    #         env = TradingEnv(df_with_features)

    #         # Check if the environment follows the gymnasium API
    #         print("\nChecking environment compatibility...")
    #         check_env(env)
    #         print("Environment check passed!")

    #         # Test the environment with a few random steps
    #         print("\nRunning a few random steps...")
    #         obs, _ = env.reset()
    #         for i in range(5):
    #             action = env.action_space.sample() # Choose a random action
    #             obs, reward, terminated, _, info = env.step(action)
    #             print(f"Action: {action}, Reward: {reward:.2f}")
    #             env.render()
    #             if terminated:
    #                 print("Episode finished.")
    #                 break
    # else:
    #     print("Login failed, cannot test TradingEnv.")
    pass
