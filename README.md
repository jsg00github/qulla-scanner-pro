# Qulla-Catalyst Scanner Pro 🚀

An algorithmic stock screener built with Streamlit, designed to detect high-momentum setups based on Kristjan Kullamägi's (Qullamaggie) strategies.

## Features

-   **Episodic Pivots (EP)**: Detects stocks gapping up >8% on huge volume (Earnings/Catalysts).
-   **Momentum Surfing**: Finds trending stocks with high ADR (>4%) and moving average alignment (10>20>50).
-   **Swing Breakouts**: Identifies contracting stocks (tightness) near 52-week highs (High Tight Flags).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd qulla_scanner
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the Streamlit app locally:

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1.  Push this code to a GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Connect your GitHub account.
4.  Select this repository and the main file `app.py`.
5.  Click **Deploy**!

## Strategies Implemented

-   **EP**: `Gap > 8%` & `Vol > 2x Avg`
-   **Momentum**: `ADR > 4%` & `Price > EMA10 > EMA20 > SMA50`
-   **Swing**: `Trend Template` & `Near 52w Highs` & `Range < 15%`
