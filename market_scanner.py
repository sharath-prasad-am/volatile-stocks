
import os
import time
import requests
import yfinance as yf
from alpaca_trade_api.rest import REST
from datetime import datetime

# Load secrets from environment variables
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = "https://paper-api.alpaca.markets"

# Validate secrets
for key, value in {
    "ALPACA_API_KEY": ALPACA_API_KEY,
    "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
}.items():
    if not value:
        raise ValueError(f"❌ Missing required environment variable: {key}")

# Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL)

# Track price history for each symbol
tracked_stocks = {}

def send_telegram_message(message):
    """Send alert to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def chunk_list(lst, chunk_size=100):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def is_stock_eligible(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        price = info.get("regularMarketPrice")
        open_price = info.get("regularMarketOpen")
        volume = info.get("averageVolume", 0)
        market_cap = info.get("marketCap", 0)

        if not price or not open_price or price < 0.3:
            return False

        if price >= 10:
            return False

        if volume < 500000:
            return False

        if market_cap < 50000000:
            return False

        change_percent = ((price - open_price) / open_price) * 100
        if change_percent < 10:
            return False

        return True
    except Exception as e:
        return False

def scan_market():
    global tracked_stocks
    print(f"📊 Scanning at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")

    try:
        active_assets = api.list_assets()
        tradable_symbols = [a.symbol for a in active_assets if a.tradable and a.exchange in ("NYSE", "NASDAQ")]
    except Exception as e:
        print(f"Error fetching assets: {e}")
        return

    for symbol in tradable_symbols:
        if not is_stock_eligible(symbol):
            continue

        try:
            price = yf.Ticker(symbol).info.get("regularMarketPrice")
            if symbol not in tracked_stocks:
                tracked_stocks[symbol] = {"prices": [], "timestamp": datetime.now()}

            tracked_stocks[symbol]["prices"].append(price)

            if len(tracked_stocks[symbol]["prices"]) > 7:
                tracked_stocks[symbol]["prices"].pop(0)

            analyze_stock(symbol)
        except Exception as e:
            print(f"Error tracking {symbol}: {e}")

def analyze_stock(symbol):
    prices = tracked_stocks[symbol]["prices"]
    if len(prices) < 5:
        return

    first_price = prices[0]
    latest_price = prices[-1]

    if len(prices) == 7 and all(prices[i] < prices[i+1] for i in range(6)):
        percent_gain = ((latest_price - first_price) / first_price) * 100
        if percent_gain >= 100:
            msg = f"🚀 {symbol} surged {percent_gain:.2f}% in 14 mins!\nCurrent: ${latest_price:.2f}"
            send_telegram_message(msg)
            print(msg)
            del tracked_stocks[symbol]

    elif len(prices) >= 5 and all(prices[i] > prices[i+1] for i in range(4)):
        percent_drop = ((first_price - latest_price) / first_price) * 100
        msg = f"⚠️ {symbol} dropped {percent_drop:.2f}% in 10 mins!\nCurrent: ${latest_price:.2f}"
        send_telegram_message(msg)
        print(msg)
        del tracked_stocks[symbol]

if __name__ == "__main__":
    while True:
        scan_market()
        time.sleep(120)  # 2-minute intervals
