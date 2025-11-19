import datetime
import sys
import numpy as np
import pytz

import yfinance as yf

def show_help():
    print("Usage: python history.py [TICKER] [STEP]")
    print("  - TICKER: Stock ticker symbol (default: NVDA)")
    print("  - STEP: Interval in days for K-lines (default: 1)")
    print("Description: Generates text-based K-lines (candlesticks) for the specified interval over historical data (limited to last 21 lines).")
    print("Also prints current data including open, high, low, 52wk high/low, off-hours prices, and previous close.")
    print("Example:")
    print("  python history.py AAPL 15")
    sys.exit(0)

def fmt_price_field(info, key):
    """
    Safely format a numeric field from yfinance .info as a 10.2f string.
    If the value is missing or non-numeric, return a right-aligned 'N/A'.
    """
    v = info.get(key, None)
    # yfinance sometimes returns None, np.nan, or a plain number
    if isinstance(v, (int, float, np.floating)) and v == v:  # v == v filters out NaN
        return f"{v:10.2f}"
    else:
        return f"{'N/A':>10}"

def generate_klines(ticker='NVDA', step=1):
    # Fetch daily data for max period
    stock = yf.Ticker(ticker)
    hist = stock.history(period="max", interval="1d")
    
    if hist.empty:
        print("No data available.")
        return
    
    # Resample into step-day K-lines
    resampled = hist.resample(f'{step}D').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }).dropna()
    
    # Limit to last 21 lines
    resampled = resampled.tail(21)
    
    print(f"\n{ticker} K-lines for {step}-day intervals (last 21 lines):")
    for idx, row in resampled.iterrows():
        dt = idx.strftime("%Y-%m-%d")
        low = row['Low']
        high = row['High']
        start = row['Open']
        end = row['Close']
        pct_change = ((end - start) / start * 100) if start != 0 else 0
        sign = '+' if pct_change > 0 else '-'
        direction = '↑' if end > start else '↓'
        body = f"[{start:10.2f} {direction} {end:10.2f}] ({sign}{abs(pct_change):5.2f}%)"
        print(f"{dt}: {low:10.2f}L | {body} | {high:10.2f}H")
    
    # Additional current data with current date/time
    now_pt = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %H:%M PT")
    now_et = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M ET")
    print(f"\nCurrent Data as of {now_pt} ({now_et}) (Close Prices Summary):")
    info = stock.info

    # Current & change from open
    current = info.get('currentPrice', info.get('regularMarketPrice', 0))
    open_price = info.get('regularMarketOpen', 0) or 0
    if isinstance(current, (int, float, np.floating)) and isinstance(open_price, (int, float, np.floating)) and open_price != 0:
        pct_change = (current - open_price) / open_price * 100
    else:
        pct_change = 0
    sign = '+' if pct_change > 0 else '-'
    current_str = f"{current:10.2f}" if isinstance(current, (int, float, np.floating)) and current == current else f"{'N/A':>10}"

    print(f"Previous Close: {fmt_price_field(info, 'previousClose')}")
    print(f"Open: {fmt_price_field(info, 'regularMarketOpen')}")
    print(f"High: {fmt_price_field(info, 'regularMarketDayHigh')}H")
    print(f"Low: {fmt_price_field(info, 'regularMarketDayLow')}L")
    print(f"Current/Regular Market Price: {current_str} ({sign}{abs(pct_change):5.2f}% from open)")
    print(f"52wk High: {fmt_price_field(info, 'fiftyTwoWeekHigh')}")
    print(f"52wk Low: {fmt_price_field(info, 'fiftyTwoWeekLow')}")
    print(f"Pre-Market Price: {fmt_price_field(info, 'preMarketPrice')}")
    print(f"After-Market Price: {fmt_price_field(info, 'postMarketPrice')}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    generate_klines(ticker, step)
