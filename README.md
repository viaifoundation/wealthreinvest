# WealthReinvest

A Python-based tool for researching stock options, retrieving market data, and supporting investment strategies focused on reinvestment and wealth management.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
  - [Install Python with pyenv](#1-install-python-with-pyenv-recommended)
  - [Create a Virtual Environment](#2-create-a-virtual-environment)
  - [Clone the Repository](#3-clone-the-repository)
  - [Install Dependencies](#4-install-dependencies)
  - [Set API Keys](#5-set-api-keys-optional)
  - [Verify Installation](#6-verify-installation)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Related](#related)

## Overview

This repository contains scripts to fetch current stock price data (including off-hours/pre/after-market where available) from multiple sources, generate text-based K-lines (candlesticks) for intraday and historical analysis. It's designed for programmatic analysis to aid in smart investing and long-term wealth growth.

## Features
- Fetch current/regular market price, with pre/after-market where supported.
- Supports multiple sources for prices: yfinance (default, no key), massive, finnhub, twelvedata.
- Generate text-based K-lines for daily intervals (from market open to now) with time in PT/ET.
- Generate historical K-lines over days (last 11 bars).
- Customizable via command-line parameters (ticker, step interval, start time).
- Help function for usage (--help or -h) in all scripts.

## Requirements
- Python 3.10 or higher
- Libraries: See `requirements.txt`

## Setup

### 1. Install Python with pyenv (Recommended)

If you don't have Python 3.10+ installed, or want to manage multiple Python versions, use [pyenv](https://github.com/pyenv/pyenv):

#### Install pyenv

**macOS (using Homebrew):**
```bash
brew install pyenv
```

**Linux:**
```bash
curl https://pyenv.run | bash
```

**Add to your shell profile** (`.zshrc`, `.bashrc`, or `.bash_profile`):
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Then restart your terminal or run:
```bash
source ~/.zshrc  # or ~/.bashrc
```

#### Install Python with pyenv
```bash
# List available Python versions
pyenv install --list

# Install Python 3.10 or higher (e.g., 3.11.0)
pyenv install 3.11.0

# Set it as the local version for this project
cd /path/to/wealthreinvest
pyenv local 3.11.0

# Verify
python --version
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
# Navigate to the project directory
cd /path/to/wealthreinvest

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Your prompt should now show (venv)
```

**Note:** Always activate the virtual environment before working on the project. To deactivate later, simply run `deactivate`.

### 3. Clone the Repository

```bash
git clone git@github.com:wealthreinvest/wealthreinvest.git
cd wealthreinvest
```

### 4. Install Dependencies

With your virtual environment activated:

```bash
# Upgrade pip to the latest version
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Optional:** If you plan to use alternative API providers, uncomment and install the optional packages in `requirements.txt`:
```bash
# Edit requirements.txt to uncomment the optional packages, then:
pip install -r requirements.txt
```

### 5. Set API Keys (Optional)

API keys are only needed if you want to use alternative data sources (yfinance works without a key):

**Option A: Environment Variables**
```bash
# For massive API
export MASSIVE_API_KEY=your_key_here

# For finnhub API
export FINNHUB_API_KEY=your_key_here

# For twelvedata API
export TWELVEDATA_API_KEY=your_key_here
```

**Option B: .env File (Recommended)**

Create a `.env` file in the project root:
```bash
MASSIVE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
TWELVEDATA_API_KEY=your_key_here
```

**Note:** Add `.env` to your `.gitignore` to keep your keys secure.

### 6. Verify Installation

Test that everything works:
```bash
# Test price script
python price.py NVDA

# Test daily K-lines
python daily.py NVDA

# Test historical K-lines
python history.py NVDA
```

## Usage

### Scripts Overview

1. **price.py** - Fetch current stock price data
2. **daily.py** - Generate intraday K-lines (pre-market, regular, after-hours)
3. **history.py** - Generate historical K-lines over multiple days

### Usage Examples

**Get current price:**
```bash
# Using default (NVDA, yfinance)
python price.py

# Specify ticker and source
python price.py AAPL finnhub
python price.py TSLA yfinance
```

**Generate daily K-lines:**
```bash
# Default: NVDA, 15-minute intervals, today
python daily.py

# Custom ticker and interval
python daily.py AAPL -s 5

# Specify a date (format: yyyymmdd)
python daily.py AAPL -s 15 -d 20231027
```

**Generate historical K-lines:**
```bash
# Default: NVDA, 1-day intervals
python history.py

# Custom ticker and step (in days)
python history.py AAPL -s 5
python history.py TSLA --step 7
```

**Get help:**
```bash
python price.py --help
python daily.py -h
python history.py --help
```

### Command-Line Options

All scripts support `--help` or `-h` for detailed usage information. The `daily.py` and `history.py` scripts also support `--version` or `-v` to display the version number.

## Troubleshooting

### Common Issues

**Issue: `python: command not found` or wrong Python version**
- Solution: Make sure Python 3.10+ is installed. Use `pyenv` to manage versions (see Setup section).

**Issue: `ModuleNotFoundError` when running scripts**
- Solution: Ensure your virtual environment is activated (`source venv/bin/activate`) and dependencies are installed (`pip install -r requirements.txt`).

**Issue: `No data available` errors**
- Solution: 
  - Check your internet connection
  - Verify the ticker symbol is correct
  - For historical data, ensure the date is a trading day (not weekend/holiday)
  - Try a different data source if one fails

**Issue: API key errors**
- Solution: 
  - Verify your API keys are set correctly (`echo $MASSIVE_API_KEY`)
  - Check that the `.env` file is in the project root (if using that method)
  - Remember: yfinance doesn't require an API key

**Issue: Virtual environment not activating**
- Solution:
  - Make sure you're in the project directory
  - Check that `venv` directory exists (create it with `python -m venv venv` if missing)
  - On Windows, use `venv\Scripts\activate` instead

**Issue: pyenv not working after installation**
- Solution:
  - Make sure you've added pyenv initialization to your shell profile (`.zshrc`, `.bashrc`, etc.)
  - Restart your terminal or run `source ~/.zshrc`
  - Verify with `pyenv --version`

## Development

### Project Structure
```
wealthreinvest/
├── price.py          # Current price fetching script
├── daily.py          # Intraday K-lines generator
├── history.py        # Historical K-lines generator
├── _version.py       # Version information
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── LICENSE           # MIT License
```

### Adding New Features

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test thoroughly
4. Update documentation if needed
5. Submit a pull request

### Running Tests

Currently, manual testing is recommended. Run each script with various parameters to ensure functionality:
```bash
python price.py AAPL yfinance
python daily.py TSLA -s 5 -d 20231027
python history.py MSFT -s 3
```

## Contributing
Feel free to fork and submit pull requests. Focus on adding more analysis features or option strategies.

When contributing:
- Follow existing code style
- Add comments for complex logic
- Update documentation for new features
- Test your changes before submitting

## License
MIT License (see LICENSE file).

## Related
- Domain: [wealthreinvest.com](https://wealthreinvest.com) (coming soon with AI chatbot integration).