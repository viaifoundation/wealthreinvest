import datetime
import sys
import os
import requests  # For manual API calls if needed
import numpy as np  # for robust numeric checks

try:
    from massive import RESTClient as MassiveClient
except ImportError:
    MassiveClient = None
try:
    import finnhub
except ImportError:
    finnhub = None
try:
    from twelvedata import TDClient
except ImportError:
    TDClient = None
try:
    import yfinance as yf
except ImportError:
    yf = None

def show_help():
    print("Usage: python price.py [TICKER] [SOURCE]")
    print("  - TICKER: Stock ticker symbol (default: NVDA)")
    print("  - SOURCE: Data source (default: yfinance). Options: yfinance, massive, finnhub, twelvedata")
    print("Examples:")
    print("  python price.py NVDA")
    print("  python price.py AAPL finnhub")
    print("Requirements:")
    print("  - For massive: Set MASSIVE_API_KEY env var")
    print("  - For finnhub: Set FINNHUB_API_KEY env var")
    print("  - For twelvedata: Set TWELVEDATA_API_KEY env var")
    print("  - yfinance: No key needed")
    sys.exit(0)

def _is_num(v):
    """Return True if v is a real number and not NaN."""
    return isinstance(v, (int, float, np.floating)) and v == v  # v == v filters out NaN

def _fmt_price(v):
    """Format a value as 10.2f if numeric, otherwise right-aligned 'N/A'."""
    return f"{v:10.2f}" if _is_num(v) else f"{'N/A':>10}"

def get_current_price(ticker, source='yfinance'):
    if source == 'yfinance' and yf:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Current price fallback chain
        current = info.get('currentPrice')
        if not _is_num(current):
            current = info.get('regularMarketPrice')

        open_price = info.get('regularMarketOpen')
        if not _is_num(open_price):
            open_price = None

        pct_change = 0.0
        if _is_num(current) and _is_num(open_price) and open_price != 0:
            pct_change = (current - open_price) / open_price * 100.0
        sign = '+' if pct_change >= 0 else '-'

        pre_market = info.get('preMarketPrice')
        after_market = info.get('postMarketPrice')

        print(f"Ticker: {ticker}")
        print(f"Current/Regular Market Price: {_fmt_price(current)} ({sign}{abs(pct_change):5.2f}% from open)")
        print(f"Pre-Market Price: {_fmt_price(pre_market)}")
        print(f"After-Market Price: {_fmt_price(after_market)}")

    elif source == 'massive' and MassiveClient:
        client = MassiveClient(api_key=os.getenv('MASSIVE_API_KEY'))
        # Free tier lacks real-time; use last daily close
        today = datetime.date.today().isoformat()
        aggs = client.get_aggs(ticker, 1, 'day', today, today)
        if aggs:
            agg = aggs[0]
            open_price = agg.open
            close_price = agg.close
            pct_change = ((close_price - open_price) / open_price * 100) if open_price != 0 else 0
            sign = '+' if pct_change >= 0 else '-'
            print(f"Ticker: {ticker}")
            print(f"Last Close (EOD, no real-time): {close_price:10.2f} ({sign}{abs(pct_change):5.2f}% from open)")
        else:
            print(f"No data for {ticker}")

    elif source == 'finnhub' and finnhub:
        client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
        quote = client.quote(ticker)
        current = quote.get('c', 0.0)
        open_price = quote.get('o', 0.0)
        pct_change = ((current - open_price) / open_price * 100) if open_price != 0 else 0
        sign = '+' if pct_change >= 0 else '-'
        print(f"Ticker: {ticker}")
        print(f"Current Price: {current:10.2f} ({sign}{abs(pct_change):5.2f}% from open)")
        print(f"Open: {open_price:10.2f}")
        print(f"High: {quote.get('h', 0.0):10.2f}")
        print(f"Low: {quote.get('l', 0.0):10.2f}")
        # Finnhub free has real-time, but no explicit off-hours separation

    elif source == 'twelvedata' and TDClient:
        client = TDClient(apikey=os.getenv('TWELVEDATA_API_KEY'))
        ts = client.time_series(symbol=ticker, interval="1min", outputsize=1)
        data = ts.as_json()
        if data:
            latest = data[0]
            # TwelveData returns strings – cast to float
            try:
                current = float(latest['close'])
                open_price = float(latest['open'])
                high = float(latest['high'])
                low = float(latest['low'])
            except (KeyError, ValueError, TypeError):
                print(f"Could not parse TwelveData response for {ticker}")
                return

            pct_change = ((current - open_price) / open_price * 100) if open_price != 0 else 0
            sign = '+' if pct_change >= 0 else '-'
            print(f"Ticker: {ticker}")
            print(f"Current Price: {current:10.2f} ({sign}{abs(pct_change):5.2f}% from open)")
            print(f"Open: {open_price:10.2f}")
            print(f"High: {high:10.2f}")
            print(f"Low: {low:10.2f}")
            # Supports real-time/off-hours in latest bar
        else:
            print(f"No data from TwelveData for {ticker}")

    else:
        print(f"Source '{source}' not available or library not installed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    source = sys.argv[2] if len(sys.argv) > 2 else 'yfinance'
    get_current_price(ticker, source)
