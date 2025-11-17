import datetime
import sys
import os
import requests  # For manual API calls if needed

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

def get_current_price(ticker, source='yfinance'):
    if source == 'yfinance' and yf:
        stock = yf.Ticker(ticker)
        info = stock.info
        current = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        open_price = info.get('regularMarketOpen', 0)
        pct_change = ((current - open_price) / open_price * 100) if open_price != 0 else 0
        sign = '+' if pct_change > 0 else '-'
        pre_market = info.get('preMarketPrice')
        after_market = info.get('postMarketPrice')
        print(f"Ticker: {ticker}")
        print(f"Current/Regular Market Price: {current} ({sign}{abs(pct_change):.2f}% from open)")
        if pre_market:
            print(f"Pre-Market Price: {pre_market}")
        if after_market:
            print(f"After-Market Price: {after_market}")
    elif source == 'massive' and MassiveClient:
        client = MassiveClient(api_key=os.getenv('MASSIVE_API_KEY'))
        # Free tier lacks real-time; use last daily close
        today = datetime.date.today().isoformat()
        aggs = client.get_aggs(ticker, 1, 'day', today, today)
        if aggs:
            agg = aggs[0]
            pct_change = ((agg.close - agg.open) / agg.open * 100) if agg.open != 0 else 0
            sign = '+' if pct_change > 0 else '-'
            print(f"Ticker: {ticker}")
            print(f"Last Close (EOD, no real-time): {agg.close} ({sign}{abs(pct_change):.2f}% from open)")
        else:
            print(f"No data for {ticker}")
    elif source == 'finnhub' and finnhub:
        client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
        quote = client.quote(ticker)
        current = quote['c']
        open_price = quote['o']
        pct_change = ((current - open_price) / open_price * 100) if open_price != 0 else 0
        sign = '+' if pct_change > 0 else '-'
        print(f"Ticker: {ticker}")
        print(f"Current Price: {current} ({sign}{abs(pct_change):.2f}% from open)")
        print(f"Open: {open_price}")
        print(f"High: {quote['h']}")
        print(f"Low: {quote['l']}")
        # Finnhub free has real-time, but no explicit off-hours separation
    elif source == 'twelvedata' and TDClient:
        client = TDClient(apikey=os.getenv('TWELVEDATA_API_KEY'))
        ts = client.time_series(symbol=ticker, interval="1min", outputsize=1)
        data = ts.as_json()
        if data:
            latest = data[0]
            current = latest['close']
            open_price = latest['open']
            pct_change = ((current - open_price) / open_price * 100) if open_price != 0 else 0
            sign = '+' if pct_change > 0 else '-'
            print(f"Ticker: {ticker}")
            print(f"Current Price: {current} ({sign}{abs(pct_change):.2f}% from open)")
            print(f"Open: {open_price}")
            print(f"High: {latest['high']}")
            print(f"Low: {latest['low']}")
            # Supports real-time/off-hours in latest bar
    else:
        print(f"Source '{source}' not available or library not installed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'NVDA'
    source = sys.argv[2] if len(sys.argv) > 2 else 'yfinance'
    get_current_price(ticker, source)