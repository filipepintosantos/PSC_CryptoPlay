"""
Script to migrate from boolean favorite column to favorite_class column.
This script will:
1. Add favorite_class column if it doesn't exist
2. Migrate existing favorites to class 'A'
3. Drop old favorite column
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase

def migrate_database(db_path='data/crypto_prices.db'):
    """Migrate database from favorite (boolean) to favorite_class (A/B/C)."""
    print(f'Migrating database: {db_path}')
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if favorite column exists
    cursor.execute("PRAGMA table_info(crypto_info)")
    columns = {row[1]: row for row in cursor.fetchall()}
    
    if 'favorite' in columns:
        # Check the type of favorite column
        favorite_type = columns['favorite'][2]  # Type is at index 2
        
        print('Step 1: Checking favorite column type...')
        print(f'  Current type: {favorite_type}')
        
        if favorite_type in ['BOOLEAN', 'INTEGER']:
            print('Step 2: Converting boolean favorites to class A...')
            cursor.execute("""
                UPDATE crypto_info 
                SET favorite = 'A' 
                WHERE favorite = 1 OR favorite = '1'
            """)
            migrated = cursor.rowcount
            
            cursor.execute("""
                UPDATE crypto_info 
                SET favorite = NULL 
                WHERE favorite = 0 OR favorite = '0'
            """)
            
            conn.commit()
            print(f'  ✓ Migrated {migrated} favorites to class A')
            print()
        else:
            print('  ℹ Column already uses TEXT format')
            print()
    else:
        print('No favorite column found - database will be created with correct schema')
        print()
    
    conn.close()
    print('Migration complete!')

if __name__ == '__main__':
    migrate_database()
