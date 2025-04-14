# franciscrepo

# Crypto Price Monitor Bot

This is a Python-based crypto monitoring bot that tracks the prices of selected cryptocurrencies (Vechain and LUNC) using the CoinGecko API. It checks the prices every hour, logs the data to a CSV file, and sends a daily summary email with price changes and simple trend forecasts.

## Features

- Fetches real-time prices for Vechain (VET) and Terra Luna Classic (LUNC)
- Compares prices with the last recorded value
- Logs price data, percentage changes, and trend information to a CSV file
- Sends one email per day (at a set time, default 18:00) with a summary of the data
- Gracefully handles missing or unavailable data
- Runs automatically every 60 minutes

## Requirements

- Python 3.x
- The following Python packages:
  - `requests`
  - `smtplib` (standard in Python)
  - `email` (standard in Python)
  - `csv` (standard in Python)

Install `requests` with:

```bash
pip install requests


Setup
Clone or download this project to your computer.

Create two JSON files in the same folder:

coin_prices.json: stores last known prices

trend_history.json: stores price history for trend detection

Example content for coin_prices.json:

json
Kopiera kod
{
"vechain": 0.003178,
"terra-luna-classic": 0.00005942
}
Example content for trend_history.json:

json
Kopiera kod
{
"vechain": [],
"terra-luna-classic": []
}
CSV Log Example
Each row in the price_log.csv file looks like this:

csv
Kopiera kod
Timestamp,Coin,Price,Change,Trend
2025-04-14 15:00:01,VET,0.003200,+0.62%,Bullish
2025-04-14 15:00:01,LUNC,N/A,-,Missing
2025-04-14 16:00:02,VET,0.003180,-0.62%,Neutral
2025-04-14 16:00:02,LUNC,0.00005942,0.00%,Neutral
Price shows the current price

Change is the percentage change from the last known value

Trend is a simple 3-point trend: Bullish, Bearish, or Neutral
Open the Python file crypto_agents.py.

Set your Yahoo email address and app password at the top of the script.

Running the Bot
Start the bot with:

bash
Kopiera kod
python crypto_agents.py
It will run in a loop every 60 minutes. It logs each price check in price_log.csv and sends one daily summary email at 16:00.

Customization
To change the daily summary time, edit the is_summary_time() function in the script.

To add more coins, update the COINS dictionary in the script.

To change the alert threshold, adjust the ALERT_THRESHOLD value.

Notes
This script depends on the availability of the CoinGecko API.

If no data is returned for a coin, it is skipped and marked as "Missing" in the log.
```
