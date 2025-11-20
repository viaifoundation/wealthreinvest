import datetime
import sys
import argparse
import numpy as np
import pytz

import yfinance as yf

def show_help():
    # This function is now handled by argparse, but kept for reference or if needed elsewhere.
    pass

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

def _is_num(v):
    """Return True if v is a real number and not NaN."""
    return isinstance(v, (int, float, np.floating)) and v == v

def generate_klines(ticker, step):
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
    parser = argparse.ArgumentParser(
        description='Generates historical text-based K-lines (candlesticks).',
        epilog='Example: python history.py AAPL --step 5'
    )
    parser.add_argument('ticker', nargs='?', default='NVDA',
                        help='Stock ticker symbol (positional, default: NVDA)')
    parser.add_argument('-t', '--ticker_named', dest='ticker_k',
                        help='Stock ticker symbol (named)')
    parser.add_argument('-s', '--step', type=int, default=1,
                        help='Interval in days for K-lines (default: 1)')
    # Kept for positional argument compatibility
    parser.add_argument('ignored_step', nargs='?', help=argparse.SUPPRESS)

    args = parser.parse_args()

    ticker = args.ticker_k or args.ticker
    # Allow step to be provided as a 2nd positional argument
    step = args.step if args.ignored_step is None else int(args.ignored_step)

    generate_klines(ticker=ticker, step=step)
