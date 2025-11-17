# WealthReinvest

A Python-based tool for researching stock options, retrieving market data, and supporting investment strategies focused on reinvestment and wealth management.

## Overview

This repository contains scripts to fetch current stock price data (including off-hours/pre/after-market where available) from multiple sources and generate intraday histograms. It's designed for programmatic analysis to aid in smart investing and long-term wealth growth.

## Features
- Fetch current/regular market price, with pre/after-market where supported.
- Supports multiple sources: yfinance (default, no key), massive, finnhub, twelvedata.
- Generate histograms of close prices for 5,10,15,20,30,60-minute intervals over the last 8 hours (using yfinance).
- Print additional current data: open, high, low, 52wk high/low, off-hours prices.
- Customizable via command-line parameters (ticker and source for price retriever).
- Help function for usage (--help or -h) in both scripts.

## Setup
1. **Clone the repo**: git clone git@github.com:wealthreinvest/wealthreinvest.git
2. **Install dependencies**: pip install -r requirements.txt
3. **Set API Keys** (optional for yfinance): 
   - For massive: export MASSIVE_API_KEY=your_key_here
   - For finnhub: export FINNHUB_API_KEY=your_key_here
   - For twelvedata: export TWELVEDATA_API_KEY=your_key_here
   (Use a .env file if preferred).
4. **Run scripts**:
   - Price retriever: python stock_data_retriever.py [TICKER] [SOURCE] (e.g., python stock_data_retriever.py AAPL finnhub). Defaults: GOOGL and yfinance.
   - Histogram: python intraday_histogram.py [TICKER] (e.g., python intraday_histogram.py AAPL). Default: GOOGL.

## Requirements
- Python 3.10+
- Libraries: See `requirements.txt`

## Usage Examples
Run in your terminal:  
python stock_data_retriever.py GOOGL yfinance  
This outputs current price data.  

python intraday_histogram.py GOOGL  
This outputs histograms and current data.  

For help: Add --help or -h to either script.

## Contributing
Feel free to fork and submit pull requests. Focus on adding more analysis features or option strategies.

## License
MIT License (see LICENSE file).

## Related
- Domain: [wealthreinvest.com](https://wealthreinvest.com) (coming soon with AI chatbot integration).