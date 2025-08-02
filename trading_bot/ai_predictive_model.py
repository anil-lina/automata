import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pandas as pd
import joblib
import os

class PredictiveModel:
    """
    Handles the training, evaluation, and prediction of the AI models.
    This class manages two models:
    1. A classifier for buy/sell/hold signals.
    2. A regressor for predicting the next price.
    """
    def __init__(self):
        self.classifier = xgb.XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            eval_metric='mlogloss',
            use_label_encoder=False # To avoid a future warning
        )
        self.regressor = xgb.XGBRegressor(
            objective='reg:squarederror',
            eval_metric='rmse'
        )

    def train(self, X: pd.DataFrame, y_signal: pd.Series, y_price: pd.Series):
        """
        Trains both the classification and regression models.
        :param X: DataFrame of features.
        :param y_signal: Series of classification targets (-1, 0, 1).
        :param y_price: Series of regression targets (next price).
        """
        # --- Classifier Training ---
        print("--- Training Classification Model (Signal Prediction) ---")
        # XGBoost's multiclass objective requires labels to be in [0, num_class-1]
        y_signal_mapped = y_signal.map({-1: 0, 0: 1, 1: 2})
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_signal_mapped, test_size=0.2, random_state=42, stratify=y_signal_mapped)

        self.classifier.fit(X_train_c, y_train_c, eval_set=[(X_test_c, y_test_c)], early_stopping_rounds=10, verbose=False)

        preds_c = self.classifier.predict(X_test_c)
        accuracy = accuracy_score(y_test_c, preds_c)
        print(f"Classification Model Accuracy: {accuracy * 100:.2f}%")

        # --- Regressor Training ---
        print("\n--- Training Regression Model (Price Prediction) ---")
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, y_price, test_size=0.2, random_state=42)

        self.regressor.fit(X_train_r, y_train_r, eval_set=[(X_test_r, y_test_r)], early_stopping_rounds=10, verbose=False)

        preds_r = self.regressor.predict(X_test_r)
        rmse = mean_squared_error(y_test_r, preds_r, squared=False)
        print(f"Regression Model RMSE: {rmse:.4f}")

    def predict(self, X_live: pd.DataFrame):
        """
        Generates predictions from the trained models.
        :param X_live: The live feature set for which to make predictions.
        :return: A dictionary with 'signal', 'probability', and 'predicted_price'.
        """
        # Predict signal
        signal_pred_mapped = self.classifier.predict(X_live)
        signal_pred = pd.Series(signal_pred_mapped).map({0: -1, 1: 0, 2: 1}).values

        # Predict probability
        signal_proba = self.classifier.predict_proba(X_live)

        # Predict price
        price_pred = self.regressor.predict(X_live)

        return {
            'signal': signal_pred,
            'probability': signal_proba,
            'predicted_price': price_pred
        }

    def save_models(self, directory='trained_models'):
        """Saves the trained models to a specified directory."""
        if not os.path.exists(directory):
            os.makedirs(directory)

        path_classifier = os.path.join(directory, 'classifier.joblib')
        path_regressor = os.path.join(directory, 'regressor.joblib')

        print(f"Saving models to '{directory}'...")
        joblib.dump(self.classifier, path_classifier)
        joblib.dump(self.regressor, path_regressor)

    def load_models(self, directory='trained_models'):
        """Loads trained models from a specified directory."""
        path_classifier = os.path.join(directory, 'classifier.joblib')
        path_regressor = os.path.join(directory, 'regressor.joblib')

        if not os.path.exists(path_classifier) or not os.path.exists(path_regressor):
            raise FileNotFoundError("Model files not found in the specified directory. Please train the models first.")

        print(f"Loading models from '{directory}'...")
        self.classifier = joblib.load(path_classifier)
        self.regressor = joblib.load(path_regressor)

if __name__ == '__main__':
    # This block demonstrates the full pipeline for using the PredictiveModel class.
    # It requires a valid API session to fetch data.

    # from data import DataHandler
    # from auth import Authenticator
    # from ai_feature_engineering import FeatureEngineer

    # print("--- Full Pipeline Test for PredictiveModel ---")
    # authenticator = Authenticator()
    # api_session = authenticator.login()

    # if api_session:
    #     data_handler = DataHandler(api_session)
    #     hist_data = data_handler.get_historical_data(exchange='NSE', token='1594', interval=60, days_back=365)

    #     if not hist_data.empty:
    #         # 1. Feature Engineering
    #         feature_engineer = FeatureEngineer(hist_data)
    #         feature_engineer.add_features()
    #         feature_engineer.add_targets()
    #         processed_df = feature_engineer.get_data()

    #         # 2. Prepare data for training
    #         feature_cols = [col for col in processed_df.columns if col not in ['signal', 'next_price']]
    #         X = processed_df[feature_cols]
    #         y_signal = processed_df['signal']
    #         y_price = processed_df['next_price']

    #         # 3. Train and Save Models
    #         model = PredictiveModel()
    #         model.train(X, y_signal, y_price)
    #         model.save_models()

    #         # 4. Load Models and Make a Prediction
    #         loaded_model = PredictiveModel()
    #         loaded_model.load_models()

    #         print("\n--- Making a sample prediction on the last row of data ---")
    #         sample_X = X.tail(1)
    #         predictions = loaded_model.predict(sample_X)

    #         print(f"Predicted Signal: {predictions['signal'][0]}")
    #         print(f"Predicted Probabilities (Sell, Hold, Buy): {predictions['probability'][0]}")
    #         print(f"Predicted Next Price: {predictions['predicted_price'][0]:.2f}")
    # else:
    #     print("Login failed, cannot run the PredictiveModel pipeline test.")
    pass
