"""
Add this endpoint to google_analysis10_api.py to check treasury data freshness
"""

# Add this to your API routes in google_analysis10_api.py:

@app.route('/api/v1/treasury/status', methods=['GET'])
@require_api_key_soft
def treasury_status():
    """
    Check the status and freshness of treasury yield data
    
    Returns:
    - Latest treasury data date
    - Number of yields available
    - Data age in days
    - Sample yields for verification
    """
    try:
        import sqlite3
        from datetime import datetime
        
        # Connect to database
        db_path = './bonds_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest treasury data
        cursor.execute("""
            SELECT date, COUNT(*) as yield_count, 
                   MAX(date) as latest_date
            FROM tsys_enhanced 
            GROUP BY date 
            ORDER BY date DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            latest_date_str = result[2]
            yield_count = result[1]
            
            # Get sample yields for the latest date
            cursor.execute("""
                SELECT maturity, yield 
                FROM tsys_enhanced 
                WHERE date = ? 
                ORDER BY 
                    CASE 
                        WHEN maturity LIKE '%Y' THEN CAST(REPLACE(maturity, 'Y', '') AS INTEGER) * 12
                        ELSE CAST(maturity AS INTEGER)
                    END
            """, (latest_date_str,))
            
            yields = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Calculate data age
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
            age_days = (datetime.now() - latest_date).days
            
            # Determine if data is fresh (less than 2 days old on weekdays)
            is_fresh = age_days < 2 if datetime.now().weekday() < 5 else age_days < 4
            
            return jsonify({
                'status': 'success',
                'treasury_data': {
                    'latest_date': latest_date_str,
                    'age_days': age_days,
                    'is_fresh': is_fresh,
                    'yield_count': yield_count,
                    'sample_yields': {
                        '3M': yields.get('3', 'N/A'),
                        '1Y': yields.get('1Y', 'N/A'),
                        '5Y': yields.get('5Y', 'N/A'),
                        '10Y': yields.get('10Y', 'N/A'),
                        '30Y': yields.get('30Y', 'N/A')
                    },
                    'all_maturities': list(yields.keys())
                },
                'database_location': 'local' if os.environ.get('DATABASE_SOURCE') != 'gcs' else 'gcs',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No treasury data found in database',
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Treasury status check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()