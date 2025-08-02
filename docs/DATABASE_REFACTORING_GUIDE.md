# Database Connection Refactoring Guide

This guide shows how to refactor the 56+ duplicate database connection patterns to use the centralized `DatabaseConnectionManager`.

## Before (Duplicate Pattern)

```python
import sqlite3

def get_bond_data(isin):
    conn = sqlite3.connect('bonds_data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM bonds WHERE isin = ?", (isin,))
        result = cursor.fetchone()
        return result
    finally:
        conn.close()
```

## After (Centralized Manager)

### Option 1: Using context manager (recommended)

```python
from core.database_manager import get_db_connection

def get_bond_data(isin):
    with get_db_connection('bonds_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bonds WHERE isin = ?", (isin,))
        return cursor.fetchone()
```

### Option 2: Using convenience functions

```python
from core.database_manager import query_one

def get_bond_data(isin):
    return query_one(
        'bonds_data.db',
        "SELECT * FROM bonds WHERE isin = ?",
        (isin,)
    )
```

### Option 3: Using the manager directly

```python
from core.database_manager import get_database_manager

def get_bond_data(isin):
    manager = get_database_manager('bonds_data.db')
    results = manager.execute_query(
        "SELECT * FROM bonds WHERE isin = ?",
        (isin,)
    )
    return results[0] if results else None
```

## Benefits

1. **Connection Pooling**: Reuses connections instead of creating new ones
2. **Automatic Cleanup**: Context managers ensure connections are properly closed
3. **Error Handling**: Built-in retry logic and proper error propagation
4. **Performance**: Optimized SQLite settings for read-heavy workloads
5. **Monitoring**: Logging of connection usage and pool statistics

## Migration Steps

1. Add import: `from core.database_manager import get_db_connection, query_one, query_all`
2. Replace manual connection code with context manager
3. Remove manual `conn.close()` calls (handled automatically)
4. Test thoroughly to ensure functionality is preserved

## Common Patterns

### Fetching single row
```python
# Before
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(query, params)
result = cursor.fetchone()
conn.close()

# After
result = query_one(db_path, query, params)
```

### Fetching multiple rows
```python
# Before
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(query, params)
results = cursor.fetchall()
conn.close()

# After
results = query_all(db_path, query, params)
```

### Complex transactions
```python
# Before
conn = sqlite3.connect(db_path)
try:
    cursor = conn.cursor()
    cursor.execute(query1)
    cursor.execute(query2)
    conn.commit()
finally:
    conn.close()

# After
with get_db_connection(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute(query1)
    cursor.execute(query2)
    conn.commit()
```