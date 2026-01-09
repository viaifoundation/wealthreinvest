import datetime
import sys
import argparse
import pandas as pd
import numpy as np
import pytz

import yfinance as yf

from _version import __version__

def show_help():
    # This function is now handled by argparse, but kept for reference or if needed elsewhere.
    pass

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

def str_to_bool(value):
    """Convert string to boolean for argparse."""
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1', 'show'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0', 'hide'):
        return False
    else:
        raise argparse.ArgumentTypeError(f'Boolean value expected, got: {value}')

def is_extended_hours():
    """
    Determine if current time is during extended trading hours (pre-market or after-hours).
    Returns True if currently in pre-market (4:00-9:30 ET) or after-hours (16:00-20:00 ET),
    or if market is closed (outside 4:00-20:00 ET).
    Returns False if currently in regular market hours (9:30-16:00 ET).
    """
    et = pytz.timezone('US/Eastern')
    now_et = datetime.datetime.now(et)
    current_time = now_et.time()
    
    pre_market_start = datetime.time(4, 0)
    market_start = datetime.time(9, 30)
    market_end = datetime.time(16, 0)
    post_market_end = datetime.time(20, 0)
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    weekday = now_et.weekday()
    is_weekday = weekday < 5  # Monday through Friday
    
    if not is_weekday:
        # Weekend - market is closed, show off-hours by default
        return True
    
    # Pre-market: 4:00 - 9:30 ET
    if pre_market_start <= current_time < market_start:
        return True
    
    # Regular market: 9:30 - 16:00 ET
    if market_start <= current_time < market_end:
        return False
    
    # After-hours: 16:00 - 20:00 ET
    if market_end <= current_time < post_market_end:
        return True
    
    # Outside trading hours (before 4:00 or after 20:00 ET)
    return True

def generate_klines(ticker, step, date_str, show_extended_hours=None):
    # Parse date
    if date_str:
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            print("Invalid DATE format. Use yyyymmdd (e.g., 20231027).")
            # Argparse will show help on error.
            sys.exit(1)
    else:
        target_date = datetime.date.today()

    # Fetch hourly data for the target day, including pre and post market
    stock = yf.Ticker(ticker)
    start_fetch_date = target_date
    end_fetch_date = target_date + datetime.timedelta(days=1)
    # Fetch 1-minute data to allow for resampling at custom 'step' intervals
    hist = stock.history(start=start_fetch_date, end=end_fetch_date, interval="1m", prepost=True)

    if hist.empty:
        print(f"No data available for {ticker} on {target_date.strftime('%Y-%m-%d')}.")
        return

    # Define market session times in US/Eastern
    et = pytz.timezone('US/Eastern')
    pre_market_start = datetime.time(4, 0)
    market_start = datetime.time(9, 30)
    market_end = datetime.time(16, 0)
    post_market_end = datetime.time(20, 0)

    # Ensure index is in Eastern Time for filtering
    hist.index = hist.index.tz_convert(et)

    # Filter data into sessions
    pre_market_data = hist[(hist.index.time >= pre_market_start) & (hist.index.time < market_start)]
    regular_market_data = hist[(hist.index.time >= market_start) & (hist.index.time < market_end)]
    post_market_data = hist[(hist.index.time >= market_end) & (hist.index.time < post_market_end)]

    # Helper to print K-lines for a session
    def print_session_klines(session_name, data):
        if data.empty:
            return

        resampled = data.resample(f'{step}min').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last'
        }).dropna()

        if resampled.empty:
            return

        print(f"\n--- {session_name} ({step}-Minute) ---")
        for idx, row in resampled.iterrows():
            dt_et = idx.strftime("%H:%M")
            dt_pt = idx.astimezone(pytz.timezone('US/Pacific')).strftime("%H:%M")
            print_kline_row(dt_pt, dt_et, row)

    def print_kline_row(dt_pt, dt_et, row):
        low = row['Low']
        high = row['High']
        start = row['Open']
        end = row['Close']
        pct_change = ((end - start) / start * 100) if start != 0 else 0
        sign = '+' if pct_change >= 0 else '-'
        direction = '↑' if end > start else '↓'
        body = f"[{start:10.2f} {direction} {end:10.2f}] ({sign}{abs(pct_change):5.2f}%)"
        print(f"{dt_pt}/{dt_et}e: {low:10.2f}L | {body} | {high:10.2f}H")

    # Determine default for show_extended_hours if not specified
    if show_extended_hours is None:
        show_extended_hours = is_extended_hours()
    
    print(f"\n{ticker} Hourly K-lines for {target_date.strftime('%Y-%m-%d')}")
    
    # Conditionally show pre-market and after-hours based on flag
    if show_extended_hours:
        print_session_klines("Pre-Market", pre_market_data)
    
    print_session_klines("Regular Market", regular_market_data)
    
    if show_extended_hours:
        print_session_klines("After-Hours", post_market_data)
    
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
    parser = argparse.ArgumentParser(
        description='Generates text-based K-lines for pre-market, regular, and after-hours sessions for a given day.',
        epilog='Example: python daily.py AAPL -s 5 -d 20231027'
    )
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s v{__version__}')
    parser.add_argument('ticker', nargs='?', default='NVDA',
                        help='Stock ticker symbol (positional, default: NVDA)')
    parser.add_argument('-t', '--ticker_named', dest='ticker_k',
                        help='Stock ticker symbol (named)')
    parser.add_argument('-s', '--step', type=int, default=15,
                        help='Interval in minutes for K-lines (default: 15)')
    parser.add_argument('-d', '--date',
                        help='The date to fetch data for in yyyymmdd format (default: today)')
    parser.add_argument('--extended-hours', dest='show_extended_hours', type=str_to_bool, default=None, nargs='?', const=True,
                        help='Control extended trading hours (pre-market and after-hours) display: --extended-hours or --extended-hours true (show), --extended-hours false (hide), omit for auto-detect (default: auto-detect based on current time)')
    # Kept for positional argument compatibility, but ignored.
    parser.add_argument('ignored_start_time', nargs='?', help=argparse.SUPPRESS)
    parser.add_argument('ignored_date', nargs='?', help=argparse.SUPPRESS)

    args = parser.parse_args()

    ticker = args.ticker_k or args.ticker
    step = args.step
    # Allow date to be provided as a 4th positional argument for backward compatibility
    date_str = args.date or args.ignored_date
    show_extended_hours = args.show_extended_hours

    generate_klines(ticker=ticker, step=step, date_str=date_str, show_extended_hours=show_extended_hours)
