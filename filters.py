
import pandas as pd

def check_ep_setup(df):
    """
    Checks for Episodic Pivot (EP) conditions.
    Rules:
    1. Gap Up > 8% (Open vs Prev Close)
    2. Huge Volume (Projected/Actual > 200% of 20d Avg)
    """
    if df is None or len(df) < 2:
        return False, 0.0, 0.0

    today = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Gap Calculation
    gap_pct = ((today['Open'] - prev['Close']) / prev['Close']) * 100
    
    # Volume Ratio
    # If market is open, 'today' volume is partial.
    # Qullamaggie suggests extrapolating volume if early, but strictly
    # let's look for "Current Vol > 2x Avg".
    # Assuming 'Vol_Avg_20' is pre-calculated in dataframe
    vol_avg = today.get('Vol_Avg_20', 1) 
    if vol_avg == 0: vol_avg = 1
    
    vol_ratio = today['Volume'] / vol_avg
    
    # Conditions
    is_ep = (gap_pct >= 8.0) and (vol_ratio >= 2.0)
    
    return is_ep, gap_pct, vol_ratio

def check_momentum_setup(df):
    """
    Checks for high momentum "Surfing" setup.
    Rules:
    1. ADR 20 > 4%
    2. Price > EMA 10 > EMA 20
    3. Price > SMA 50 (Trend)
    """
    if df is None or len(df) < 1:
        return False
        
    current = df.iloc[-1]
    
    adr = current.get('ADR_20', 0)
    close = current['Close']
    ema10 = current.get('EMA_10', 0)
    ema20 = current.get('EMA_20', 0)
    sma50 = current.get('SMA_50', 0)
    
    # Logic
    high_adr = adr > 4.0
    trend_alignment = (close > ema10) and (ema10 > ema20) and (close > sma50)
    
    return high_adr and trend_alignment

def check_swing_breakout(df):
    """
    Checks for Swing Breakout (Consolidation).
    Rules:
    1. Trend Template (Price > SMA 50 > SMA 200)
    2. Near Highs (Within 25% of 52w High)
    3. Consolidation: 10-day range is "tight" (e.g., < 15%)
    4. Holding support: Close > EMA 20
    """
    if df is None or len(df) < 10:
        return False, 0.0
        
    current = df.iloc[-1]
    
    # Trend Template
    sma50 = current.get('SMA_50', 0)
    sma200 = current.get('SMA_200', 0)
    close = current['Close']
    
    msg_trend = (close > sma50) and (sma50 > sma200)
    
    # Near Highs (High Tight Flag logic)
    high_52 = current.get('High_52W', close)
    near_high = close >= (high_52 * 0.75) # Within 25% of highs
    
    # Consolidation (Tightness)
    # Check last 10 days
    last_10 = df.iloc[-10:]
    max_price = last_10['High'].max()
    min_price = last_10['Low'].min()
    
    # Range %
    range_pct = ((max_price - min_price) / min_price) * 100
    is_tight = range_pct < 15.0 # Adjustable threshold for "tightness"
    
    # Holding Support
    ema20 = current.get('EMA_20', 0)
    holding_support = close > ema20
    
    is_swing = msg_trend and near_high and is_tight and holding_support
    
    return is_swing, range_pct
