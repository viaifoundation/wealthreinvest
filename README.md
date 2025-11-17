# WealthReinvest

A Python-based tool for researching stock options, retrieving market data, and supporting investment strategies focused on reinvestment and wealth management.

## Overview

This repository contains scripts to fetch current stock price data (including off-hours/pre/after-market where available) from multiple sources, generate text-based K-lines (candlesticks) for intraday and historical analysis. It's designed for programmatic analysis to aid in smart investing and long-term wealth growth.

## Features
- Fetch current/regular market price, with pre/after-market where supported.
- Supports multiple sources for prices: yfinance (default, no key), massive, finnhub, twelvedata.
- Generate text-based K-lines for daily intervals (from market open to now) with time in PT/ET.
- Generate historical K-lines over days (last 11 bars).
- Customizable via command-line parameters (ticker, step interval, start time).
- Help function for usage (--help or -h) in all scripts.

## Setup
1. **Clone the repo**: git clone git@github.com:wealthreinvest/wealthreinvest.git
2. **Install dependencies**: pip install -r requirements.txt
3. **Set API Keys** (optional for yfinance): 
   - For massive: export MASSIVE_API_KEY=your_key_here
   - For finnhub: export FINNHUB_API_KEY=your_key_here
   - For twelvedata: export TWELVEDATA_API_KEY=your_key_here
   (Use a .env file if preferred).
4. **Run scripts**:
   - Price: python price.py [TICKER] [SOURCE] (e.g., python price.py AAPL finnhub). Defaults: NVDA and yfinance.
   - Daily K-lines: python daily.py [TICKER] [STEP] [START_TIME] (e.g., python daily.py AAPL 15 1000). Defaults: NVDA, 5 min, 0930.
   - Historical K-lines: python history.py [TICKER] [STEP] (e.g., python history.py AAPL 15). Defaults: NVDA, 1 day.

## Requirements
- Python 3.10+
- Libraries: See `requirements.txt`

## Usage Examples
Run in your terminal:  
python price.py NVDA yfinance  
This outputs current price data.  

python daily.py NVDA 15  
This outputs daily K-lines.  

python history.py NVDA 5  
This outputs historical K-lines.  

For help: Add --help or -h to any script.

## Contributing
Feel free to fork and submit pull requests. Focus on adding more analysis features or option strategies.

## License
MIT License (see LICENSE file).

## Related
- Domain: [wealthreinvest.com](https://wealthreinvest.com) (coming soon with AI chatbot integration).