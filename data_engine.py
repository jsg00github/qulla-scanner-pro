
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import datetime
import time
from ta.trend import EMAIndicator, SMAIndicator
from ta.volatility import AverageTrueRange

# Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_earnings_for_date(date_str):
    """
    Scrapes Yahoo Finance Earnings Calendar for a specific date.
    Date format: YYYY-MM-DD
    """
    url = f"https://finance.yahoo.com/calendar/earnings?day={date_str}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch earnings for {date_str}: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Yahoo often changes classes. Looking for the main table.
        # Fallback: Look for links that look like tickers in a table
        tickers = []
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if cols and len(cols) > 0:
                # usually the first column is ticker
                ticker_text = cols[0].get_text(strip=True)
                if ticker_text.isalpha() and len(ticker_text) <= 5: # Basic ticker validation
                    tickers.append(ticker_text)
                    
        return list(set(tickers))
    except Exception as e:
        print(f"Error scraping earnings for {date_str}: {e}")
        return []

def get_recent_earnings_tickers(days_back=2):
    """
    Get tickers with earnings from today and the last N business days.
    """
    tickers = set()
    today = datetime.date.today()
    
    # Iterate back
    for i in range(days_back + 1):
        d = today - datetime.timedelta(days=i)
        # Skip weekends
        if d.weekday() >= 5: 
            continue
            
        date_str = d.strftime("%Y-%m-%d")
        print(f"Fetching earnings for {date_str}...")
        daily_tickers = get_earnings_for_date(date_str)
        print(f"  Found {len(daily_tickers)} tickers.")
        tickers.update(daily_tickers)
        time.sleep(1) # Respect rate limits
        
    return list(tickers)

def get_ticker_data(ticker):
    """
    Fetches data and calculates indicators for a single ticker.
    Returns a DataFrame with indicators or None if failure.
    """
    try:
        # Fetch 6 months of data to ensure enough for SMA200
        df = yf.download(ticker, period="1y", interval="1d", progress=False)
        if df.empty or len(df) < 50:
            return None
            
        # Clean MultiIndex columns if present (yfinance v0.2+)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Basic Indicators using 'ta' library
        # Close is required
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # EMAs
        df['EMA_10'] = EMAIndicator(close=close, window=10).ema_indicator()
        df['EMA_20'] = EMAIndicator(close=close, window=20).ema_indicator()
        
        # SMAs
        df['SMA_50'] = SMAIndicator(close=close, window=50).sma_indicator()
        df['SMA_200'] = SMAIndicator(close=close, window=200).sma_indicator()
        
        # ADR (Average Daily Range %) - 20 days
        # Daily Range % = (High - Low) / Low * 100
        df['Daily_Range_Pct'] = ((high - low) / low) * 100
        df['ADR_20'] = df['Daily_Range_Pct'].rolling(window=20).mean()
        
        # Volume Average
        df['Vol_Avg_20'] = df['Volume'].rolling(window=20).mean()
        
        # 52 Week High (for Trend Template)
        df['High_52W'] = high.rolling(window=252).max()
        df['Low_52W'] = low.rolling(window=252).min()
        
        return df
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None
