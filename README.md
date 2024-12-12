
# Binance RSI Scanner 🚀

This repository contains a Python-based Binance RSI Scanner that fetches trading pairs, retrieves historical price data, and calculates the Relative Strength Index (RSI) using an EMA-based method similar to TradingView's approach. The tool identifies USDT trading pairs with an RSI below 30, signaling potential oversold conditions in the market.

![image](https://github.com/user-attachments/assets/49527be9-ccfa-4805-b79c-6ba348d4e835)

---

## **Features**
- 📈 **Real-Time Data Fetching:** Retrieves live market data from Binance API.
- 🔍 **EMA-Based RSI Calculation:** Uses Exponential Moving Average (EMA) for precise RSI calculations.
- ⚡ **Multi-threaded Scanning:** Utilizes `ThreadPoolExecutor` for parallel processing of multiple trading pairs.
- 💾 **Persistent Caching:** Caches USDT pairs locally to minimize API requests.
- 🔒 **Thread-Safe Logging:** Ensures clean output with synchronized log messages.

---

## **How It Works**
1. Fetches all USDT trading pairs from Binance.
2. Retrieves historical kline (candlestick) data for each symbol.
3. Calculates RSI using a custom EMA-based approach.
4. Prints pairs with an RSI below the threshold (default: 30).
5. Optionally checks a single coin by setting the `SYMBOL` environment variable.

---

## **Installation**
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/binance-rsi-scanner.git
   cd binance-rsi-scanner
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the scanner:**
   ```bash
   python main.py
   ```

---

## **Usage with Docker**
1. **Build the Docker image:**
   ```bash
   docker build -t rsi-binance .
   ```

2. **Run the scanner using Docker:**
   ```bash
   docker run --rm -v "$(pwd):/app" --name rsi-binance-container rsi-binance python /app/main.py
   ```

---

## **Environment Variables**
- `SYMBOL` - (Optional) Specific coin to query (e.g., `BTCUSDT`).
- `MAX_WORKERS` - Number of threads for parallel processing (default: `40`).
- `INTERVAL` - Binance kline interval (default: `1m`).

---

## **Requirements**
- **Python Version:** Python 3.8+
- **Libraries:** 
  - `requests`
  - `pandas`
  - `numpy`
  - `colorama`

---

## **Contributions**
We welcome contributions! Feel free to submit a pull request or raise an issue.

---

## **Disclaimer**
> **⚠️ Disclaimer:**  
> This tool is for educational and informational purposes only. Trading cryptocurrencies involves risk, and this repository is not financial advice. Use responsibly.

---

**Happy Trading!** 🚀 **MIT License** 📄 
