
#!/usr/bin/env python3
import sqlite3
import os

def test_treasury_fetch(date_str="2025-07-31"):
    """Test if we can fetch treasury yields."""
    db_path = os.environ.get('DATABASE_PATH', './bonds_data.db')
    print(f"Using database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return None
        
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT M2Y, M5Y, M10Y FROM tsys_enhanced WHERE Date = '{date_str}'")
            row = cursor.fetchone()
            if row:
                print(f"Treasury yields for {date_str}: 2Y={row[0]:.3f}%, 5Y={row[1]:.3f}%, 10Y={row[2]:.3f}%")
                return {"2Y": row[0], "5Y": row[1], "10Y": row[2]}
            else:
                print(f"No treasury yields found for {date_str}")
                return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

if __name__ == "__main__":
    test_treasury_fetch()
