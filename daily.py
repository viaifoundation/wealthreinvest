import datetime
import sys
import numpy as np
import pytz

import yfinance as yf

def show_help():
    print("Usage: python daily.py [TICKER] [STEP] [START_TIME] [DATE]")
    print("  - TICKER: Stock ticker symbol (default: NVDA)")
    print("  - STEP: Interval in minutes for K-lines (default: 15)")
    print("  - START_TIME: Start time of the day in hhmm format (default: 0930 for market open)")
    print("  - DATE: The date to fetch data for in yyyymmdd format (default: today)")
    print("Description: Generates text-based K-lines (candlesticks) for the specified interval from start time to the end of the market day.")
    print("Also prints current data including open, high, low, 52wk high/low, off-hours prices, and previous close.")
    print("Example:")
    print("  python daily.py AAPL 15 1000")

def fmt_price_field(info, key):
    """
    Safely format a numeric field from yfinance .info as a 10.2f string.
    If the value is missing or non-numeric, return a right-aligned 'N/A'.
    """
    v = info.get(key, None)
    if isinstance(v, (int, float, np.floating)) and v == v:  # v == v filters out NaN
        return f"{v:10.2f}"
    else:
        return f"{'N/A':>10}"

def _is_num(v):
    """Return True if v is a real number and not NaN."""
    return isinstance(v, (int, float, np.floating)) and v == v

def generate_klines(ticker='NVDA', step=15, start_time_str='0930', date_str=None):
    # Parse start time
    try:
        start_hour = int(start_time_str[:2])
        start_min = int(start_time_str[2:])
        start_time = datetime.time(start_hour, start_min)
    except ValueError:
        print("Invalid START_TIME format. Use hhmm (e.g., 0930).")
        show_help()
        sys.exit(1)

    # Parse date
    if date_str:
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            print("Invalid DATE format. Use yyyymmdd (e.g., 20231027).")
            show_help()
            sys.exit(1)
    else:
        target_date = datetime.date.today()

    # Fetch 1-minute data for the target day
    stock = yf.Ticker(ticker)
    start_fetch_date = target_date
    end_fetch_date = target_date + datetime.timedelta(days=1)
    hist = stock.history(start=start_fetch_date, end=end_fetch_date, interval="1m")

    if hist.empty:
        print(f"No data available for {ticker} on {target_date.strftime('%Y-%m-%d')}.")
        return

    # Filter from start time onwards for that day
    start_datetime_local = datetime.datetime.combine(target_date, start_time)
    hist = hist[hist.index.time >= start_datetime_local.time()]

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
    
    display_date_str = target_date.strftime("%Y-%m-%d")
    print(f"\n{ticker} K-lines for {step}-minute intervals on {display_date_str} (from {start_time_str}):")
    for idx, row in resampled.iterrows():
        idx_pt = idx.astimezone(pytz.timezone('US/Pacific'))
        dt_pt = idx_pt.strftime("%H:%M")
        dt_et = idx.astimezone(pytz.timezone('US/Eastern')).strftime("%H:%M")
        low = row['Low']
        high = row['High']
        start = row['Open']
        end = row['Close']
        pct_change = ((end - start) / start * 100) if start != 0 else 0
        sign = '+' if pct_change > 0 else '-'
        direction = '↑' if end > start else '↓'
        body = f"[{start:10.2f} {direction} {end:10.2f}] ({sign}{abs(pct_change):5.2f}%)"
        print(f"{dt_pt}/{dt_et}e: {low:10.2f}L | {body} | {high:10.2f}H")
    
    # Additional current data with current date/time
    now_pt = datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %H:%M PT")
    now_et = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%H:%M ET")
    print(f"\nCurrent Data as of {now_pt} ({now_et}) (Close Prices Summary):")
    info = stock.info

    # Current & change from open, robust to missing/non-numeric
    current = info.get('currentPrice', info.get('regularMarketPrice', 0))
    open_price = info.get('regularMarketOpen', 0) or 0

    if _is_num(current) and _is_num(open_price) and open_price != 0:
        pct_change = (current - open_price) / open_price * 100
    else:
        pct_change = 0
    sign = '+' if pct_change > 0 else '-'
    current_str = f"{current:10.2f}" if _is_num(current) else f"{'N/A':>10}"

    print(f"Previous Close: {fmt_price_field(info, 'previousClose')}")
    print(f"Open: {fmt_price_field(info, 'regularMarketOpen')}")
    print(f"High: {fmt_price_field(info, 'regularMarketDayHigh')}H")
    print(f"Low: {fmt_price_field(info, 'regularMarketDayLow')}L")
    print(f"Current/Regular Market Price: {current_str} ({sign}{abs(pct_change):5.2f}% from open)")
    print(f"52wk High: {fmt_price_field(info, 'fiftyTwoWeekHigh')}")
    print(f"52wk Low: {fmt_price_field(info, 'fiftyTwoWeekLow')}")

    previous_close = info.get('previousClose')
    regular_market_price = info.get('regularMarketPrice')

    # Pre-Market Price
    pre_market_price = info.get('preMarketPrice')
    pre_market_str = fmt_price_field(info, 'preMarketPrice')
    if _is_num(pre_market_price) and _is_num(previous_close) and previous_close != 0:
        pre_market_pct = (pre_market_price - previous_close) / previous_close * 100
        sign = '+' if pre_market_pct >= 0 else '-'
        pre_market_str = f"{pre_market_str} ({sign}{abs(pre_market_pct):.2f}%)"
    print(f"Pre-Market Price: {pre_market_str}")

    # After-Market Price
    post_market_price = info.get('postMarketPrice')
    post_market_str = fmt_price_field(info, 'postMarketPrice')
    if _is_num(post_market_price) and _is_num(regular_market_price) and regular_market_price != 0:
        post_market_pct = (post_market_price - regular_market_price) / regular_market_price * 100
        sign = '+' if post_market_pct >= 0 else '-'
        post_market_str = f"{post_market_str} ({sign}{abs(post_market_pct):.2f}%)"
    print(f"After-Market Price: {post_market_str}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
        sys.exit(0)
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    start_time_str = sys.argv[3] if len(sys.argv) > 3 else '0930'
    date_str = sys.argv[4] if len(sys.argv) > 4 else None
    generate_klines(ticker, step, start_time_str, date_str)
