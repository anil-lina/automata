# Trading Bot Project

This project contains a comprehensive trading bot built in Python, designed to interact with the Shoonya API. It features two distinct trading strategies: one based on technical indicators and another powered by Artificial Intelligence with two different models.

## Project Structure

The project is organized into a Python package (`trading_bot`) with the following key modules:

-   `config.py`: Main configuration file for credentials, stock lists, and strategy parameters. **You must edit this file first.**
-   `auth.py`: Handles the authentication process with the Shoonya API.
-   `data.py`: Manages fetching of historical and option data.
-   `screener.py`: Scans and filters stocks/options based on criteria in `config.py`.

### Strategy 1: Technical Indicator Bot
-   `technical_analysis.py`: Calculates MACD and HMA indicators.
-   `strategy.py`: Implements the trading logic based on MACD/HMA crossovers.
-   `backtest.py`: Simulates the technical strategy and evaluates its performance.
-   `main.py`: The main entry point to run the technical indicator-based bot.

### Strategy 2: AI-Powered Bot
-   `ai_feature_engineering.py`: Prepares data and creates features for the AI models.
-   **Predictive Model:**
    -   `ai_predictive_model.py`: Defines and trains the XGBoost models for prediction.
    -   `main_ai_predictive.py`: Entry point to train or run the predictive model.
-   **Reinforcement Learning Model:**
    -   `ai_rl_environment.py`: Defines the custom trading environment (`gymnasium`).
    -   `ai_rl_agent.py`: Defines the training process for the RL agent (`stable-baselines3`).
    -   `main_ai_rl.py`: Entry point to run a simulation with the trained RL agent.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    # Assuming the code is in a directory named 'trading_bot_project'
    cd trading_bot_project
    ```

2.  **Install Dependencies:**
    Make sure you have Python 3 installed. Then, install the required packages using pip:
    ```bash
    pip install -r trading_bot/requirements.txt
    ```
    This will install `pandas`, `pandas-ta`, `xgboost`, `stable-baselines3`, `gymnasium`, and other necessary libraries.

3.  **Configure Credentials:**
    Open `trading_bot/config.py` and fill in your Shoonya API credentials in the `credentials` dictionary. You can also customize the `stock_list` and other parameters in this file.

## How to Use

All commands should be run from the root directory of the project (e.g., `trading_bot_project`).

### 1. Running the Technical Indicator Bot

This bot runs the MACD/HMA crossover strategy on the stocks defined in your `config.py`.

```bash
python -m trading_bot.main
```

### 2. Using the Predictive AI Model

This is a two-step process: first you train the models, then you can use them for prediction.

**Step 2.1: Train the Models**
Run the following command for each stock you want to train a model on. This will fetch historical data, train the models, and save them to the `trained_models/` directory.

```bash
# Example for RELIANCE-EQ
python -m trading_bot.main_ai_predictive RELIANCE-EQ --train
```

**Step 2.2: Get Predictions**
Once a model is trained, you can run the script without the `--train` flag to get a prediction based on the latest data.

```bash
# Example for RELIANCE-EQ
python -m trading_bot.main_ai_predictive RELIANCE-EQ
```

### 3. Using the Reinforcement Learning AI Model

This is also a two-step process: train the agent, then run it in a simulation.

**Step 3.1: Train the RL Agent**
Run the following command for each stock you want to train an agent on. This process can take some time. The trained agent will be saved in the `trained_models/` directory.

```bash
# Example for RELIANCE-EQ
python -m trading_bot.ai_rl_agent RELIANCE-EQ --timesteps 50000
```

**Step 3.2: Run the Simulation**
After the agent is trained, you can run it in the simulated environment to see how it makes decisions.

```bash
# Example for RELIANCE-EQ
python -m trading_bot.main_ai_rl RELIANCE-EQ --timesteps 1000
```

### 4. Running the Standalone Stock Scanner

This script scans all available NSE stocks for a specific technical condition (a bullish or bearish MACD/HMA crossover) and prints a list of stocks that meet the criteria.

**Note:** This can take a long time to run as it iterates through every stock.

```bash
python -m trading_bot.scanner
```

---
*This `README.md` provides a guide to get started. You can explore each module to understand the implementation details.*
