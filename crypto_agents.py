import requests
import smtplib
import json
import csv
import time
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime

# === CONFIG ===
YOUR_EMAIL = "francisc_florinel@yahoo.com"
APP_PASSWORD = "mppusawbifwqdwyy"  # Replace this with your real Yahoo app password
TO_EMAIL = "francisc_florinel@yahoo.com"
COINS = {"vechain": "VET", "terra-luna-classic": "LUNC"}
ALERT_THRESHOLD = 3.0
PRICE_FILE = "coin_prices.json"
TREND_FILE = "trend_history.json"

# === AGENTS ===

class DataAgent:
    def fetch_prices(self, retries=3):
        ids = ",".join(COINS.keys())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"

        for attempt in range(retries):
            try:
                res = requests.get(url)
                data = res.json()

                # Check if all coins are included
                missing = [coin for coin in COINS if coin not in data]
                if not missing:
                    return data

                print(f"⚠️ Missing: {', '.join(missing)} — retrying ({attempt + 1}/{retries})...")
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error fetching prices: {e}")
                time.sleep(2)

        print("⚠️ Warning: Could not fetch complete price data after retries.")
        return data if 'data' in locals() else {}

class AnalyzerAgent:
    def __init__(self):
        self.previous = self._load_previous_prices()

    def _load_previous_prices(self):
        if Path(PRICE_FILE).exists():
            with open(PRICE_FILE, "r") as f:
                return json.load(f)
        return {}

    def analyze(self, current_prices):
        alerts = {}
        for coin_id, symbol in COINS.items():
            if coin_id not in current_prices or "usd" not in current_prices[coin_id]:
                print(f"⚠️ Skipping {symbol} — no price returned from CoinGecko.")
                continue

            current = current_prices[coin_id]["usd"]
            previous = self.previous.get(coin_id, current)
            change = ((current - previous) / previous) * 100

            if abs(change) >= ALERT_THRESHOLD:
                alerts[symbol] = {
                    "current": current,
                    "previous": previous,
                    "change": round(change, 2)
                }

            self.previous[coin_id] = current
        self._save_current_prices()
        return alerts

    def _save_current_prices(self):
        with open(PRICE_FILE, "w") as f:
            json.dump(self.previous, f)

class PredictorAgent:
    def __init__(self):
        self.trend_data = self._load_trend_data()

    def _load_trend_data(self):
        if Path(TREND_FILE).exists():
            with open(TREND_FILE, "r") as f:
                return json.load(f)
        return {coin: [] for coin in COINS.keys()}

    def update_trends(self, prices):
        for coin_id in COINS:
            if coin_id in prices and "usd" in prices[coin_id]:
                self.trend_data.setdefault(coin_id, []).append(prices[coin_id]["usd"])
                self.trend_data[coin_id] = self.trend_data[coin_id][-3:]

        with open(TREND_FILE, "w") as f:
            json.dump(self.trend_data, f)

    def get_forecast_and_advice(self):
        results = {}
        for coin_id, history in self.trend_data.items():
            symbol = COINS[coin_id]
            trend = "Unknown"
            advice = "No advice available."

            if len(history) < 3:
                trend = "Not enough data"
                advice = "Wait for more data before taking action."
            elif history[-1] < history[-2] < history[-3]:
                trend = "Bearish"
                advice = "Be cautious. If you're in profit, it may be time to sell."
            elif history[-1] > history[-2] > history[-3]:
                trend = "Bullish"
                advice = "Consider holding. Uptrend may continue."
            else:
                trend = "Neutral"
                advice = "Market is moving sideways. Holding is a safe option."

            results[symbol] = {
                "trend": trend,
                "advice": advice
            }
        return results

class LoggerAgent:
    def log_to_csv(self, alerts, forecast_text):
        log_file = "price_log.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        for symbol in COINS.values():
            alert = alerts.get(symbol)
            if alert:
                price = f"{alert['current']:.6f}"
                change = f"{alert['change']}%"
                trend = self.extract_trend_for(symbol, forecast_text)
            else:
                price = "N/A"
                change = "-"
                trend = "Missing"
            rows.append([now, symbol, price, change, trend])

        file_exists = Path(log_file).exists()
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Coin", "Price", "Change", "Trend"])
            writer.writerows(rows)

    def extract_trend_for(self, symbol, forecast_text):
        for line in forecast_text.splitlines():
            if line.startswith(symbol):
                return line.split(": ")[1]
        return "Unknown"

class AlertAgent:
    def send_summary(self, prices, trends_with_advice):
        subject = "Crypto Daily Summary: VET / LUNC"
        body = "DAILY SUMMARY – {}\n\n".format(datetime.now().strftime("%Y-%m-%d %H:%M"))

        for coin_id, symbol in COINS.items():
            price = "N/A"
            if coin_id in prices and "usd" in prices[coin_id]:
                price = f"${prices[coin_id]['usd']:.6f}"

            trend_info = trends_with_advice.get(symbol, {})
            trend = trend_info.get("trend", "Unknown")
            advice = trend_info.get("advice", "No advice available.")

            body += (
                f"{symbol}:\n"
                f"Price: {price}\n"
                f"Trend: {trend}\n"
                f"Advice: {advice}\n\n"
            )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = YOUR_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as smtp:
                smtp.login(YOUR_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)
            print("📧 Daily summary email sent!")
        except Exception as e:
            print(f"❌ Failed to send summary email: {e}")

# === TIME CHECK ===

def is_summary_time(target_hour=16):
    now = datetime.now()
    return now.hour == target_hour

# === MAIN FUNCTION ===

def main():
    data_agent = DataAgent()
    analyzer_agent = AnalyzerAgent()
    predictor_agent = PredictorAgent()
    logger_agent = LoggerAgent()
    alert_agent = AlertAgent()

    current_prices = data_agent.fetch_prices()
    alerts = analyzer_agent.analyze(current_prices)
    predictor_agent.update_trends(current_prices)
    forecast_data = predictor_agent.get_forecast_and_advice()
    logger_agent.log_to_csv(alerts, "\n".join([f"{k}: {v['trend']}" for k, v in forecast_data.items()]))

    if is_summary_time():
        alert_agent.send_summary(current_prices, forecast_data)
    else:
        print("🕐 Not time for summary email yet.")

# === RUN EVERY 60 MINUTES ===

if __name__ == "__main__":
    print("⏳ Running every 60 minutes... Press Ctrl+C to stop.")
    while True:
        main()
        time.sleep(3600)
