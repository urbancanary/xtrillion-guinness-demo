import sqlite3
import pandas as pd
import os
import glob

# --- Configuration ---
DB_DIRECTORY = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/'
TARGET_ISIN = 'US91282CJZ59'
TABLE_NAME = 'results_summary'

def find_latest_db_file():
    """Finds the most recently created database file in the specified directory."""
    search_pattern = os.path.join(DB_DIRECTORY, 'six_way_analysis_FIXED_*.db')
    db_files = glob.glob(search_pattern)
    if not db_files:
        return None
    latest_file = max(db_files, key=os.path.getctime)
    return latest_file

def show_treasury_results():
    """Connects to the latest results database and prints the results for the US Treasury bond."""
    db_file = find_latest_db_file()
    if not db_file:
        print(f"Error: No database files matching the pattern were found in {DB_DIRECTORY}")
        return

    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to {db_file}")

        # Use pandas to query and display the data for better formatting
        query = f"SELECT * FROM {TABLE_NAME} WHERE isin = ?"
        df = pd.read_sql_query(query, conn, params=(TARGET_ISIN,))

        conn.close()

        if df.empty:
            print(f"No results found for ISIN: {TARGET_ISIN}")
        else:
            print(f"--- Results for US Treasury Bond (ISIN: {TARGET_ISIN}) ---")
            # To ensure all data, especially the long conventions string, is visible
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 2000)
            pd.set_option('display.max_colwidth', None)
            print(df.to_string())

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    show_treasury_results()
