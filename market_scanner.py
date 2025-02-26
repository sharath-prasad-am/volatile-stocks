import os
import time
import requests
import pandas as pd
from alpaca_trade_api.rest import REST
from datetime import datetime, timedelta

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = "https://paper-api.alpaca.markets"

# Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL, api_version="v2")

# Dictionary to store price history
price_tracking = {}

def send_telegram_alert(message):
    """Sends an alert message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def track_volatile_stocks():
    """Scans the market every 2 minutes to track consistently rising stocks under $10 with 100%+ gains."""

    # Get all tradable stock symbols
    assets = api.list_assets()
    tickers = [asset.symbol for asset in assets if asset.tradable]

    for ticker in tickers:
        try:
            # Fetch last 1-minute bar
            bar = api.get_barset(ticker, "minute", limit=1).df

            if ticker in bar and not bar[ticker].empty:
                current_price = bar[ticker]["close"].iloc[-1]

                # Only track stocks with price < $10
                if current_price >= 10:
                    continue  
                
                # Store price history
                if ticker not in price_tracking:
                    price_tracking[ticker] = []

                price_tracking[ticker].append(current_price)

                # Keep only the last 7 price points (14-minute window)
                if len(price_tracking[ticker]) > 7:
                    price_tracking[ticker].pop(0)

                # Check if price has increased for 7 consecutive runs
                if len(price_tracking[ticker]) == 7 and all(
                    price_tracking[ticker][i] < price_tracking[ticker][i + 1] for i in range(6)
                ):
                    # Check if the price has jumped 100%+
                    initial_price = price_tracking[ticker][0]
                    percent_change = ((current_price - initial_price) / initial_price) * 100

                    if percent_change >= 100:
                        alert_msg = f"🚨 ALERT: {ticker} has increased over 100% in 14 minutes! Current Price: ${current_price}"
                        print(alert_msg)
                        send_telegram_alert(alert_msg)  # Send Telegram notification
                        del price_tracking[ticker]  # Reset tracking for this stock

        except Exception as e:
            continue  # Skip if data isn't available

# Main loop to run every 2 minutes
while True:
    scan_market()
    time.sleep(120)  # Wait for 2 minutes
