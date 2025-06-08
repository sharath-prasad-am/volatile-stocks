
# 📈 Volatile Stock Tracker (Sub-$10 Momentum Scanner)

This Python-based project scans the entire U.S. stock market for low-priced stocks that exhibit strong intraday momentum and alerts you via Telegram.

## 🚀 Features

- Tracks all **NYSE/NASDAQ stocks** priced between **$0.30 and $10**
- Uses **Yahoo Finance (`yfinance`)** for live data (price, volume, market cap, etc.)
- Applies filters:
  - Price > $0.30 and < $10
  - Avg. volume > 500,000 shares/day
  - Market cap > $50 million
  - Price increase > 10% from market open
- Stores price history in a local **SQLite database**
- Detects:
  - 📈 Consistent price uptrends (alert if price climbs steadily)
  - ⚠️ Consistent price drops (alert if 5 consecutive dips)
- Sends alerts via **Telegram Bot**

## 🧠 Future Extensions

- Trend scoring (momentum strength)
- Machine Learning integration
- Streamlit dashboard
- Google Sheets integration
- Webhook or Discord alerting

## 📅 GitHub Actions Automation

Runs automatically **Monday–Friday**:
- From **8:00 AM to 11:00 AM EST** → every **1 minute**
- From **11:00 AM to 3:00 PM EST** → every **2 minutes**

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/volatile-stocks.git
cd volatile-stocks
```

### 2. Add Secrets to GitHub

Go to your GitHub repo → Settings → Secrets → Actions:

- `TELEGRAM_BOT_TOKEN` — From @BotFather on Telegram
- `TELEGRAM_CHAT_ID` — Your personal chat or group ID

### 3. Python Dependencies (for local run)

```bash
pip install yfinance requests
```

### 4. Run Locally

```bash
python sqlite_stock_tracker.py
```

This script runs indefinitely and scans every 2 minutes by default.

## 📦 File Structure

```
.
├── sqlite_stock_tracker.py        # Main stock tracker script
├── stock_tracker.db               # SQLite DB (auto-created)
├── .github
│   └── workflows
│       └── market_scan.yml        # GitHub Actions runner
└── README.md
```

## ✅ Example Alerts

- 🚀 `XYZ surged 35.2% in 14 mins! Current: $1.52`
- ⚠️ `ABC dropped 21.7% in 10 mins! Current: $0.74`

---

Built for active traders who want to catch early signs of momentum in high-risk, high-reward zones.
