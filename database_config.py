"""
Database Configuration
======================

Centralized database configuration to ensure only valid databases are used.
This is the SINGLE SOURCE OF TRUTH for database paths in the codebase.
"""

import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# === VALID DATABASES - ONLY THESE THREE ARE ALLOWED ===
BONDS_DATA_DB = PROJECT_ROOT / 'bonds_data.db'
BLOOMBERG_INDEX_DB = PROJECT_ROOT / 'bloomberg_index.db'
VALIDATED_QUANTLIB_DB = PROJECT_ROOT / 'validated_quantlib_bonds.db'

# Aliases for common usage patterns
PRIMARY_DB = BONDS_DATA_DB  # Primary bond database (contains tsys_enhanced table)
SECONDARY_DB = BLOOMBERG_INDEX_DB  # Bloomberg reference data
CONVENTIONS_DB = VALIDATED_QUANTLIB_DB  # Validated bond conventions

# === TABLE LOCATIONS ===
# Document which tables are in which database
DATABASE_TABLES = {
    'bonds_data.db': [
        'bonds',  # Main bond reference table
        'tsys',  # Treasury yields
        'tsys_enhanced',  # Enhanced treasury yield curve data
        'isin_assumptions',  # ISIN mapping data
        # ... other tables
    ],
    'bloomberg_index.db': [
        'bloomberg_bonds',  # Bloomberg bond reference
        'bond_mappings',  # ISIN to Bloomberg mappings
        # ... other tables
    ],
    'validated_quantlib_bonds.db': [
        'validated_bonds',  # Bonds with validated conventions
        'convention_overrides',  # Manual convention fixes
        # ... other tables
    ]
}

# === DEPRECATED DATABASES - DO NOT USE ===
INVALID_DATABASES = {
    'yield_curves.db': 'Use bonds_data.db instead (contains tsys_enhanced table)',
    'tsys_enhanced.db': 'Use bonds_data.db instead (tsys_enhanced is a table, not a database)',
    'validated_conventions.db': 'Use validated_quantlib_bonds.db instead',
    'conventions.db': 'Use validated_quantlib_bonds.db instead'
}


def get_database_path(db_type: str) -> Path:
    """
    Get the path to a specific database by type.
    
    Args:
        db_type: One of 'primary', 'secondary', 'conventions'
        
    Returns:
        Path to the database file
        
    Raises:
        ValueError: If invalid database type is requested
    """
    db_map = {
        'primary': PRIMARY_DB,
        'secondary': SECONDARY_DB,
        'conventions': CONVENTIONS_DB,
        'bonds': BONDS_DATA_DB,
        'bloomberg': BLOOMBERG_INDEX_DB,
        'validated': VALIDATED_QUANTLIB_DB
    }
    
    if db_type not in db_map:
        raise ValueError(f"Invalid database type: {db_type}. Valid types: {list(db_map.keys())}")
    
    return db_map[db_type]


def validate_database_exists(db_path: Path) -> bool:
    """Check if a database file exists and is valid."""
    if not db_path.exists():
        return False
    
    # Check if file is not empty
    if db_path.stat().st_size == 0:
        return False
    
    return True


def get_all_valid_databases() -> dict:
    """Get status of all valid databases."""
    return {
        'bonds_data.db': {
            'path': str(BONDS_DATA_DB),
            'exists': validate_database_exists(BONDS_DATA_DB),
            'size_mb': BONDS_DATA_DB.stat().st_size / 1024 / 1024 if BONDS_DATA_DB.exists() else 0,
            'tables': DATABASE_TABLES.get('bonds_data.db', [])
        },
        'bloomberg_index.db': {
            'path': str(BLOOMBERG_INDEX_DB),
            'exists': validate_database_exists(BLOOMBERG_INDEX_DB),
            'size_mb': BLOOMBERG_INDEX_DB.stat().st_size / 1024 / 1024 if BLOOMBERG_INDEX_DB.exists() else 0,
            'tables': DATABASE_TABLES.get('bloomberg_index.db', [])
        },
        'validated_quantlib_bonds.db': {
            'path': str(VALIDATED_QUANTLIB_DB),
            'exists': validate_database_exists(VALIDATED_QUANTLIB_DB),
            'size_mb': VALIDATED_QUANTLIB_DB.stat().st_size / 1024 / 1024 if VALIDATED_QUANTLIB_DB.exists() else 0,
            'tables': DATABASE_TABLES.get('validated_quantlib_bonds.db', [])
        }
    }


# For backward compatibility - to be used during migration
def get_db_path(db_name: str) -> str:
    """
    Legacy function for backward compatibility.
    Maps old database names to new valid ones.
    """
    # Map invalid names to valid ones
    if db_name == 'yield_curves.db':
        return str(BONDS_DATA_DB)
    elif db_name == 'tsys_enhanced.db':
        return str(BONDS_DATA_DB)
    elif db_name == 'validated_conventions.db':
        return str(VALIDATED_QUANTLIB_DB)
    elif db_name == 'conventions.db':
        return str(VALIDATED_QUANTLIB_DB)
    elif db_name == 'bonds_data.db':
        return str(BONDS_DATA_DB)
    elif db_name == 'bloomberg_index.db':
        return str(BLOOMBERG_INDEX_DB)
    elif db_name == 'validated_quantlib_bonds.db':
        return str(VALIDATED_QUANTLIB_DB)
    else:
        raise ValueError(f"Invalid database name: {db_name}. Valid databases: bonds_data.db, bloomberg_index.db, validated_quantlib_bonds.db")


if __name__ == "__main__":
    # Display database configuration when run directly
    print("🗄️ XTrillion Bond Analytics - Database Configuration")
    print("=" * 60)
    
    db_status = get_all_valid_databases()
    for db_name, info in db_status.items():
        status = "✅" if info['exists'] else "❌"
        print(f"\n{status} {db_name}")
        print(f"   Path: {info['path']}")
        if info['exists']:
            print(f"   Size: {info['size_mb']:.1f} MB")
            print(f"   Tables: {', '.join(info['tables'][:5])}...")
        else:
            print("   Status: NOT FOUND")
    
    print("\n" + "=" * 60)
    print("⚠️  Only these three databases should be used in the codebase!")
    print("=" * 60)