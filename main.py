"""
##############################################################
#                  Binance RSI Scanner 🚀                    #
# ---------------------------------------------------------- #
# Author: enes sönmez
# Created: 2024-12-12                                        #
# Version: 1.0.0                                             #
# License: MIT                                               #
# ---------------------------------------------------------- #
# Description:                                               #
# This Python script scans Binance trading pairs for USDT   #
# pairs with an RSI value below a specified threshold (30   #
# by default), indicating potential oversold conditions.    #
# It uses Binance's official API to fetch historical        #
# kline (candlestick) data, calculates RSI using an EMA-    #
# based approach similar to TradingView's method, and       #
# displays results in real time.                            #
#                                                           #
# Key Features:                                              #
# - Real-time Binance market data fetching.                 #
# - EMA-based precise RSI calculation.                      #
# - Multi-threaded processing with ThreadPoolExecutor.      #
# - Persistent caching of USDT pairs.                      #
# - Thread-safe logging with color-coded output.            #
#                                                           #
# Disclaimer:                                                #
# This project is for educational and informational         #
# purposes only. Trading cryptocurrencies involves risks.   #
# Use at your own discretion.                              #
##############################################################
"""
import requests
import pandas as pd
import numpy as np
import time
import os
import sys
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Initialize colorama
init(autoreset=True)

# Thread-safe printing lock
print_lock = Lock()

# Binance API Endpoints
BINANCE_BASE_URL = "https://api.binance.com"
SYMBOLS_ENDPOINT = f"{BINANCE_BASE_URL}/api/v3/exchangeInfo"
KLINES_ENDPOINT = f"{BINANCE_BASE_URL}/api/v3/klines"
PRICE_ENDPOINT = f"{BINANCE_BASE_URL}/api/v3/ticker/price"

# RSI Settings
RSI_THRESHOLD = 30
RSI_PERIOD = 14

# Persistent File Path
PERSISTENT_PATH = "/app"
COINS_FILE = os.path.join(PERSISTENT_PATH, "coins.txt")

# Environment variables with default values
MAX_WORKERS = 40
INTERVAL = "1m"

# Ensure data directory exists
os.makedirs(PERSISTENT_PATH, exist_ok=True)

# Thread-safe print function
def print_flush(message, color=None):
    with print_lock:
        if color:
            print(color + message + Style.RESET_ALL)
        else:
            print(message)
        sys.stdout.flush()

# Correct RSI Calculation Using EMA (TradingView-like)
def calculate_precise_rsi(prices, period=RSI_PERIOD):
    delta = prices.diff()

    # Initialize gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Use first SMA for initial average gain/loss
    avg_gain = gain[:period].mean()
    avg_loss = loss[:period].mean()

    # Lists for tracking EMA values
    gains = [avg_gain]
    losses = [avg_loss]

    # EMA smoothing factor
    alpha = 1 / period

    for i in range(period, len(prices)):
        current_gain = gain.iloc[i]
        current_loss = loss.iloc[i]

        # EMA formula
        avg_gain = (current_gain * alpha) + (gains[-1] * (1 - alpha))
        avg_loss = (current_loss * alpha) + (losses[-1] * (1 - alpha))

        gains.append(avg_gain)
        losses.append(avg_loss)

    # Avoid division by zero in RS calculation
    gains = np.array(gains)
    losses = np.array(losses)
    rs = np.divide(gains, losses, out=np.zeros_like(gains), where=losses != 0)

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi[-1]  # Return the last RSI value

# Get USDT Trading Pairs from Binance
def get_usdt_pairs():
    if os.path.exists(COINS_FILE):
        print_flush(f"\n'{COINS_FILE}' found. Skipping API request.\n")
        with open(COINS_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]

    print_flush("\nFetching USDT pairs from Binance API...\n")
    response = requests.get(SYMBOLS_ENDPOINT)

    if response.status_code == 200:
        data = response.json()
        usdt_pairs = [symbol['symbol'] for symbol in data['symbols'] 
                      if symbol['symbol'].endswith("USDT") and symbol['status'] == 'TRADING']

        print_flush(f"{len(usdt_pairs)} USDT pairs found.\n")

        # Save pairs persistently
        with open(COINS_FILE, "w") as f:
            for pair in usdt_pairs:
                f.write(pair + "\n")

        return usdt_pairs
    else:
        print_flush("Failed to fetch trading pairs from Binance.")
        return []

# Get Current Price of a Symbol
def get_current_price(symbol):
    response = requests.get(PRICE_ENDPOINT, params={"symbol": symbol})
    if response.status_code == 200:
        data = response.json()
        return float(data['price'])
    else:
        print_flush(f"Failed to fetch current price for {symbol}.")
        return None

# Fetch Kline Data and Calculate RSI
def fetch_and_calculate_rsi(symbol):
    response = requests.get(KLINES_ENDPOINT, params={
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 1000
    })

    if response.status_code == 200:
        data = response.json()
        
        if not data or len(data) < RSI_PERIOD:
            print_flush(f"Not enough data for {symbol}.")
            return None

        close_prices = pd.Series([float(kline[4]) for kline in data])

        # Calculate RSI using improved method
        last_rsi = calculate_precise_rsi(close_prices)
        return last_rsi
    else:
        print_flush(f"Failed to fetch data for {symbol}. HTTP Code: {response.status_code}")
        return None

# Process Each Symbol
def process_symbol(symbol):
    # print_flush(f"CHECKING ({symbol}) ...", Fore.RED)
    try:
        last_rsi = fetch_and_calculate_rsi(symbol)
        if last_rsi is not None and last_rsi < RSI_THRESHOLD:
            current_price = get_current_price(symbol)
            print_flush(f"Coin: {symbol} | RSI: {last_rsi:.2f} | Price: {current_price:.4f} USDT (RSI below 30)")
    except Exception as e:
        print_flush(f"Error occurred: {symbol} - {e}")

# Main Function with Parallel Processing
def find_low_rsi_coins():
    target_coin = os.getenv("SYMBOL", "").strip().upper()

    if target_coin:
        print_flush(f"\nQuerying single coin: {target_coin}\n", Fore.RED)
        process_symbol(target_coin)
    else:
        print_flush("\nQuerying all coins...\n")
        symbols = get_usdt_pairs()

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(process_symbol, symbols)

if __name__ == "__main__":
    find_low_rsi_coins()
