import sqlite3
import gzip
import json
import pandas as pd
from datetime import datetime


def read_trades_to_dataframe(db_file, symbol, starttime=None, endtime=None):
    """
    Read trade data from SQLite and return it as a Pandas DataFrame, filtered by time range.

    Args:
        db_file (str): Path to the SQLite database file (e.g., 'trade.db').
        symbol (str): Trading symbol (e.g., 'BTC', 'ETH').
        starttime (str, optional): Start time in ISO format (e.g., '2025-03-08T12:00:00').
        endtime (str, optional): End time in ISO format (e.g., '2025-03-08T13:00:00').

    Returns:
        pd.DataFrame: DataFrame with trade data and timestamps.
    """
    table_name = f'binance_{symbol.lower()}'

    try:
        # Connect to the SQLite database
        with sqlite3.connect(db_file) as conn:
            # Base query
            query = f'SELECT timestamp, compressed_trades FROM {table_name}'
            conditions = []
            params = []

            # Add time filters if provided
            if starttime:
                conditions.append('timestamp >= ?')
                params.append(starttime)
            if endtime:
                conditions.append('timestamp <= ?')
                params.append(endtime)

            # Append conditions to query
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            query += ' ORDER BY id ASC'  # ASC to get trades in chronological order

            # Read raw data into a DataFrame
            df_raw = pd.read_sql_query(query, conn, params=params)

            if df_raw.empty:
                print(f"No data found in table {table_name} for the given time range")
                return pd.DataFrame()

            # List to hold all trades
            all_trades = []

            # Process each row
            for index, row in df_raw.iterrows():
                timestamp = row['timestamp']
                compressed_data = row['compressed_trades']

                # Decompress and deserialize
                decompressed_bytes = gzip.decompress(compressed_data)
                trades = json.loads(decompressed_bytes.decode('utf-8'))

                # Add the batch timestamp to each trade and append to list
                for trade in trades:
                    trade['batch_timestamp'] = timestamp
                    all_trades.append(trade)

            # Create DataFrame from all trades
            df_trades = pd.DataFrame(all_trades)

            # Rename columns for clarity
            df_trades = df_trades.rename(columns={
                'price': 'Price',
                'qty': 'Quantity',
                'timestamp': 'TradeTimestamp',
                'is_buyer_maker': 'IsBuyerMaker',
                'order_id': 'OrderID',
                'batch_timestamp': 'BatchTimestamp'
            })

            # Convert timestamps to datetime
            df_trades['TradeTimestamp'] = pd.to_datetime(df_trades['TradeTimestamp'], unit='s')
            df_trades['BatchTimestamp'] = pd.to_datetime(df_trades['BatchTimestamp'])

            # Filter trades by TradeTimestamp if more granularity is needed
            if starttime:
                df_trades = df_trades[df_trades['TradeTimestamp'] >= pd.to_datetime(starttime)]
            if endtime:
                df_trades = df_trades[df_trades['TradeTimestamp'] <= pd.to_datetime(endtime)]

            return df_trades

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error during processing: {e}")
        return pd.DataFrame()


# Example usage
def get_data(symbol, starttime=None, endtime=None):
    """
    Retrieve trade data for a symbol within a time range as a Pandas DataFrame.

    Args:
        symbol (str): Trading symbol (e.g., 'BTC', 'ETH').
        starttime (str, optional): Start time in ISO format (e.g., '2025-03-08T12:00:00').
        endtime (str, optional): End time in ISO format (e.g., '2025-03-08T13:00:00').

    Returns:
        pd.DataFrame: DataFrame with trade data.
    """
    db_file = "trade.db"  # Path to your SQLite file

    # Read into DataFrame
    df = read_trades_to_dataframe(db_file, symbol, starttime, endtime)

    if not df.empty:
        # Print basic info (optional, can be removed)
        print("DataFrame Info:")
        print(df.info())
        print("\nFirst few rows:")
        print(df.head())
        print("\nSummary statistics:")
        print(df.describe())

    return df


if __name__ == "__main__":
    # Example parameters
    symbol = "btc"
    starttime = "2025-03-08T04:00:00"  # Adjust based on your data
    endtime = "2025-03-08T12:35:00"  # Adjust based on your data

    # Get the data
    df = get_data(symbol, starttime, endtime)