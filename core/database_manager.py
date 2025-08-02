"""
Centralized Database Connection Manager
======================================

Provides unified database connection handling with:
- Connection pooling
- Automatic cleanup via context managers
- Error handling and retry logic
- Connection monitoring and logging
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import time
import threading

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Centralized database connection manager with pooling and monitoring."""
    
    def __init__(self, db_path: Union[str, Path], pool_size: int = 5):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to the database file
            pool_size: Maximum number of concurrent connections
        """
        self.db_path = str(db_path)
        self.pool_size = pool_size
        self._connections = []
        self._lock = threading.Lock()
        self._active_connections = 0
        
        # Verify database exists
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """
        Get a database connection from the pool.
        
        Args:
            timeout: Maximum time to wait for a connection
            
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        start_time = time.time()
        
        try:
            # Get connection from pool or create new one
            with self._lock:
                if self._connections:
                    conn = self._connections.pop()
                    logger.debug(f"Reusing connection from pool (pool size: {len(self._connections)})")
                elif self._active_connections < self.pool_size:
                    conn = self._create_connection()
                    self._active_connections += 1
                    logger.debug(f"Created new connection (active: {self._active_connections})")
                else:
                    # Wait for available connection
                    while not self._connections and time.time() - start_time < timeout:
                        self._lock.release()
                        time.sleep(0.1)
                        self._lock.acquire()
                    
                    if self._connections:
                        conn = self._connections.pop()
                    else:
                        raise TimeoutError(f"No database connection available after {timeout}s")
            
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
            
        finally:
            # Return connection to pool
            if conn:
                with self._lock:
                    if len(self._connections) < self.pool_size:
                        self._connections.append(conn)
                        logger.debug(f"Returned connection to pool (pool size: {len(self._connections)})")
                    else:
                        conn.close()
                        self._active_connections -= 1
                        logger.debug(f"Closed excess connection (active: {self._active_connections})")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimized settings."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Optimize for read-heavy workloads
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        return conn
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dicts.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Convert Row objects to dicts
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute multiple INSERT/UPDATE/DELETE queries.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._connections:
                conn.close()
            self._connections.clear()
            self._active_connections = 0
            logger.info(f"Closed all database connections for {self.db_path}")


# Global connection managers for common databases
_managers: Dict[str, DatabaseConnectionManager] = {}


def get_database_manager(db_path: Union[str, Path]) -> DatabaseConnectionManager:
    """
    Get or create a database connection manager for the specified path.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        DatabaseConnectionManager instance
    """
    db_path_str = str(db_path)
    
    if db_path_str not in _managers:
        _managers[db_path_str] = DatabaseConnectionManager(db_path_str)
        logger.info(f"Created new database manager for {db_path_str}")
    
    return _managers[db_path_str]


# Convenience functions for common operations
@contextmanager
def get_db_connection(db_path: Union[str, Path]):
    """
    Simple context manager for database connections.
    
    Usage:
        with get_db_connection('bonds_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bonds WHERE isin = ?", (isin,))
            result = cursor.fetchone()
    """
    manager = get_database_manager(db_path)
    with manager.get_connection() as conn:
        yield conn


def query_one(db_path: Union[str, Path], query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """
    Execute a query and return the first result.
    
    Args:
        db_path: Path to the database
        query: SQL query to execute
        params: Query parameters
        
    Returns:
        Dictionary representing the first row, or None if no results
    """
    manager = get_database_manager(db_path)
    results = manager.execute_query(query, params)
    return results[0] if results else None


def query_all(db_path: Union[str, Path], query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a query and return all results.
    
    Args:
        db_path: Path to the database
        query: SQL query to execute
        params: Query parameters
        
    Returns:
        List of dictionaries representing all rows
    """
    manager = get_database_manager(db_path)
    return manager.execute_query(query, params)