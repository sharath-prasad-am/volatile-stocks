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
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

# Track stock movements
tracked_stocks = {}

# Function to send Telegram alerts
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

# Function to scan the market for stocks under $10
def scan_market():
    global tracked_stocks
    print(f"Scanning market at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    # Get the top gainers & losers (Alpaca does not provide full market scanning, so we filter later)
    active_assets = api.get_assets(status='active')
    tradable_symbols = [asset.symbol for asset in active_assets if asset.tradable]

    # Get last trade price for all symbols
    quotes = api.get_latest_trade(tradable_symbols)

    for symbol, trade in quotes.items():
        price = trade.price

        # Only track stocks under $10
        if price < 10:
            if symbol not in tracked_stocks:
                tracked_stocks[symbol] = {"prices": [], "timestamp": datetime.now()}

            tracked_stocks[symbol]["prices"].append(price)

            # Keep only the last 14 minutes of data
            if len(tracked_stocks[symbol]["prices"]) > 7:
                tracked_stocks[symbol]["prices"].pop(0)

            analyze_stock(symbol)

# Function to analyze price trends
def analyze_stock(symbol):
    prices = tracked_stocks[symbol]["prices"]
    
    if len(prices) < 7:  # Need at least 14 minutes of data for uptrend analysis
        return

    first_price = prices[0]
    latest_price = prices[-1]

    # Check for **consistent increase over 14 minutes**
    if all(prices[i] < prices[i + 1] for i in range(len(prices) - 1)):
        percentage_gain = ((latest_price - first_price) / first_price) * 100

        if percentage_gain >= 100:  # Ensure at least a 100% gain
            message = f"🚀 {symbol} has surged **{percentage_gain:.2f}%** in 14 minutes!\nPrice: ${latest_price:.2f}"
            send_telegram_message(message)
            del tracked_stocks[symbol]  # Stop tracking after alert

    # Check for **consistent drop over 10 minutes** (5 runs)
    elif len(prices) >= 5 and all(prices[i] > prices[i + 1] for i in range(4)):
        percentage_drop = ((first_price - latest_price) / first_price) * 100

        message = f"⚠️ {symbol} is dropping consistently! **-{percentage_drop:.2f}%** in 10 minutes.\nCurrent Price: ${latest_price:.2f}"
        send_telegram_message(message)
        del tracked_stocks[symbol]  # Stop tracking after alert

# Main loop to run every 2 minutes
while True:
    scan_market()
    time.sleep(120)  # Wait for 2 minutes
