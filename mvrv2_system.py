import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt

def fetch_market_data(crypto_symbol):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto_symbol.upper()}&tsym=USD&limit=365"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching data from API. Status code: {response.status_code}")
    
    data = response.json()
    if 'Data' not in data or 'Data' not in data['Data']:
        raise KeyError("'Data' not found in the API response.")
    
    prices = [(item['time']*1000, item['close']) for item in data['Data']['Data']]
    return prices

def simulate_realized_value_data(market_data):
    realized_values = [(timestamp, value * np.random.uniform(0.8, 1.2)) for timestamp, value in market_data]
    return realized_values

def calculate_mvrv(market_data, realized_value_data):
    market_df = pd.DataFrame(market_data, columns=['timestamp', 'market_value'])
    realized_df = pd.DataFrame(realized_value_data, columns=['timestamp', 'realized_value'])
    
    market_df['timestamp'] = pd.to_datetime(market_df['timestamp'], unit='ms')
    realized_df['timestamp'] = pd.to_datetime(realized_df['timestamp'], unit='ms')
    
    merged_df = pd.merge(market_df, realized_df, on='timestamp', suffixes=('_market', '_realized'))
    merged_df['mvrv_ratio'] = merged_df['market_value'] / merged_df['realized_value']
    
    return merged_df

def plot_mvrv(mvrv_data, crypto_symbol):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(mvrv_data['timestamp'], mvrv_data['mvrv_ratio'], label=f'{crypto_symbol} MVRV Ratio', color='blue')
    
    # Plot 30-Day Moving Average if there are at least 30 days of data
    if len(mvrv_data) >= 30:
        mvrv_data['mvrv_ratio_ma'] = mvrv_data['mvrv_ratio'].rolling(window=30).mean()
        ax.plot(mvrv_data['timestamp'], mvrv_data['mvrv_ratio_ma'], label='30-Day Moving Average', color='red', linestyle='--')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('MVRV Ratio')
    ax.set_title(f'{crypto_symbol} MVRV Ratio Over Time')
    ax.legend()
    
    current_mvrv = mvrv_data['mvrv_ratio'].iloc[-1]
    ax.annotate(f'Current MVRV Ratio ({current_mvrv:.2f})', xy=(mvrv_data['timestamp'].iloc[-1], current_mvrv), xytext=(-80, 20),
                textcoords='offset points', arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2"))
    
    plt.tight_layout()
    plt.show()

def main():
    crypto_symbol = 'SOL'
    market_data = fetch_market_data(crypto_symbol)
    realized_value_data = simulate_realized_value_data(market_data)
    mvrv_data = calculate_mvrv(market_data, realized_value_data)
    plot_mvrv(mvrv_data, crypto_symbol)

if __name__ == "__main__":
    main()
