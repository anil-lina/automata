import argparse
import pandas as pd
import os

# To run as a script, we need to handle the imports carefully
try:
    from .auth import Authenticator
    from .data import DataHandler
    from .ai_feature_engineering import FeatureEngineer
    from .ai_predictive_model import PredictiveModel
except ImportError:
    from auth import Authenticator
    from data import DataHandler
    from ai_feature_engineering import FeatureEngineer
    from ai_predictive_model import PredictiveModel

def main(stock_symbol, train_mode=False):
    """
    Main function to run the predictive AI pipeline.
    :param stock_symbol: The stock symbol to process (e.g., 'RELIANCE-EQ').
    :param train_mode: If True, models will be retrained. Otherwise, loads pre-trained models.
    """
    print(f"--- Starting Predictive AI for {stock_symbol} ---")
    print(f"--- Mode: {'Training' if train_mode else 'Prediction'} ---")

    authenticator = Authenticator()
    api_session = authenticator.login()
    if not api_session:
        print("Authentication failed. Exiting.")
        return

    model = PredictiveModel()
    model_dir = os.path.join('trained_models', stock_symbol)

    if train_mode:
        print("\nFetching data for training...")
        data_handler = DataHandler(api_session)
        search_res = api_session.searchscrip('NSE', stock_symbol)
        if not (search_res and search_res.get('values')):
            print(f"Could not find token for {stock_symbol}. Exiting.")
            return
        stock_token = search_res['values'][0]['token']

        hist_data = data_handler.get_historical_data('NSE', stock_token, interval=60, days_back=365 * 2) # 2 years for robust training
        if hist_data.empty:
            print("Could not fetch historical data for training. Exiting.")
            return

        print("\nEngineering features and targets...")
        feature_engineer = FeatureEngineer(hist_data)
        feature_engineer.add_features()
        feature_engineer.add_targets()
        processed_df = feature_engineer.get_data()

        feature_cols = [col for col in processed_df.columns if col not in ['signal', 'next_price']]
        X = processed_df[feature_cols]
        y_signal = processed_df['signal']
        y_price = processed_df['next_price']

        print("\nTraining models...")
        model.train(X, y_signal, y_price)
        model.save_models(directory=model_dir)
        print("\n--- Training Complete ---")

    else: # Prediction Mode
        try:
            model.load_models(directory=model_dir)
        except FileNotFoundError:
            print(f"Error: No trained models found for {stock_symbol} in '{model_dir}'.")
            print("Please run the script in training mode first: --train")
            return

        print("\nFetching latest data for prediction...")
        data_handler = DataHandler(api_session)
        search_res = api_session.searchscrip('NSE', stock_symbol)
        stock_token = search_res['values'][0]['token']
        # Fetch last ~100 candles to have enough data for feature calculation
        latest_data = data_handler.get_historical_data('NSE', stock_token, interval=60, days_back=10)

        if latest_data.empty:
            print("Could not fetch latest data for prediction. Exiting.")
            return

        print("Engineering features for prediction...")
        feature_engineer = FeatureEngineer(latest_data)
        df_with_features = feature_engineer.add_features()

        # Get the very last row for prediction
        live_features = df_with_features.tail(1)

        # Note on live option greeks:
        # At this point, you would fetch the live greeks for a relevant option contract.
        # You would then add these greeks as columns to the `live_features` DataFrame.
        # This requires the model to have been trained on data that included columns for greeks
        # (even if they were filled with 0 or a mean value during historical training).

        print("\n--- Generating Prediction ---")
        predictions = model.predict(live_features)

        signal_map = {-1: 'Sell', 0: 'Hold', 1: 'Buy'}
        predicted_signal = signal_map.get(predictions['signal'][0], 'Unknown')

        print(f"Prediction for {stock_symbol} based on data up to {live_features.index[0]}:")
        print(f"  - Predicted Signal: {predicted_signal}")
        print(f"  - Probabilities (Sell, Hold, Buy): {predictions['probability'][0]}")
        print(f"  - Predicted Next Price: {predictions['predicted_price'][0]:.2f}")
        print("--- Prediction Complete ---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to train or run the predictive AI model.")
    parser.add_argument("symbol", type=str, help="The stock symbol to process (e.g., 'RELIANCE-EQ').")
    parser.add_argument("--train", action="store_true", help="Run in training mode to retrain and save models.")

    args = parser.parse_args()

    main(args.symbol, args.train)
