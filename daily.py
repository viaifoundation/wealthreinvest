import datetime
import sys
import numpy as np
import pytz

import yfinance as yf

def show_help():
    print("Usage: python daily.py [TICKER] [STEP] [START_TIME]")
    print("  - TICKER: Stock ticker symbol (default: NVDA)")
    print("  - STEP: Interval in minutes for K-lines (default: 5)")
    print("  - START_TIME: Start time of the day in hhmm format (default: 0930 for market open)")
    print("Description: Generates text-based K-lines (candlesticks) for the specified interval from start time to now.")
    print("Also prints current data including open, high, low, 52wk high/low, off-hours prices, and previous close.")
    print("Example:")
    print("  python daily.py AAPL 15 1000")
    sys.exit(0)

def generate_klines(ticker='NVDA', step=5, start_time_str='0930'):
    # Parse start time
    try:
        start_hour = int(start_time_str[:2])
        start_min = int(start_time_str[2:])
        start_time = datetime.time(start_hour, start_min)
    except ValueError:
        print("Invalid START_TIME format. Use hhmm (e.g., 0930).")
        return
    
    # Fetch 1-minute data for the last day (full day)
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")
    
    if hist.empty:
        print("No data available.")
        return
    
    # Filter from start time to now
    today = datetime.date.today()
    start_datetime = datetime.datetime.combine(today, start_time).replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    hist = hist[(hist.index >= start_datetime) & (hist.index <= now)]
    
    if hist.empty:
        print("No data from specified start time.")
        return
    
    # Resample into step-minute K-lines
    resampled = hist.resample(f'{step}min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }).dropna()
    
    date_str = today.strftime("%Y-%m-%d")
    print(f"\n{ticker} K-lines for {step}-minute intervals on {date_str} (from {start_time_str} to now):")
    for idx, row in resampled.iterrows():
        idx_pt = idx.astimezone(pytz.timezone('US/Pacific'))
        dt_pt = idx_pt.strftime("%H:%M")
        dt_et = idx.astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M")
        low = row['Low']
        high = row['High']
        start = row['Open']
        end = row['Close']
        direction = '↑' if end > start else '↓'
        body = f"[{start:.2f} {direction} {end:.2f}]"
        print(f"{dt_pt}/{dt_et}e: {low:.2f} | {body} | {high:.2f}")
    
    # Additional current data with current date/time
    now_pt = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %H:%M PT")
    now_et = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M ET")
    print(f"\nCurrent Data as of {now_pt} ({now_et}) (Close Prices Summary):")
    info = stock.info
    print(f"Previous Close: {info.get('previousClose', 'N/A')}")
    print(f"Open: {info.get('regularMarketOpen', 'N/A')}")
    print(f"High: {info.get('regularMarketDayHigh', 'N/A')}")
    print(f"Low: {info.get('regularMarketDayLow', 'N/A')}")
    print(f"52wk High: {info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"52wk Low: {info.get('fiftyTwoWeekLow', 'N/A')}")
    print(f"Pre-Market Price: {info.get('preMarketPrice', 'N/A')}")
    print(f"After-Market Price: {info.get('postMarketPrice', 'N/A')}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    start_time_str = sys.argv[3] if len(sys.argv) > 3 else '0930'
    generate_klines(ticker, step, start_time_str)