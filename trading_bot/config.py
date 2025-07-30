# Shoonya API credentials
# Please fill in your actual credentials
credentials = {
    "user": "YOUR_USER_ID",
    "pwd": "YOUR_PASSWORD",
    "factor2": "YOUR_TOTP_PIN",
    "vc": "YOUR_VENDOR_CODE",
    "apikey": "YOUR_API_KEY",
    "imei": "YOUR_IMEI"
}

# Timeframes for analysis in minutes
timeframes = {
    "1H": 60,
    "4H": 240
}

# List of stocks to scan
# Example: ["RELIANCE-EQ", "INFY-EQ"]
stock_list = []

# Screener configuration
screener_config = {
    "min_option_volume": 1000,
    "min_stock_movement_pct": 2.0
}

# HMA period
hma_period = 20

# MACD settings
macd_fast = 12
macd_slow = 26
macd_signal = 9
