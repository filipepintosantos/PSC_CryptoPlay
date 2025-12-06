"""
Script to mark favorite cryptocurrencies from config.ini
"""
import configparser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')
favorites_str = config.get('symbols', 'favorites', fallback='')
favorites = [s.strip().upper() for s in favorites_str.split(',') if s.strip()]

print(f'Favorites from config.ini: {", ".join(favorites)}')
print()

# Update database
db = CryptoDatabase()

# First, unmark all as non-favorites
db.conn.execute('UPDATE crypto_info SET favorite = 0')

# Then mark the ones from config as favorites
updated = 0
for code in favorites:
    result = db.conn.execute('UPDATE crypto_info SET favorite = 1 WHERE code = ?', (code,))
    updated += result.rowcount

db.conn.commit()

print(f'Marked {updated} cryptocurrencies as favorites')
print()

# Show current favorites
result = db.conn.execute('SELECT code, name FROM crypto_info WHERE favorite = 1 ORDER BY code').fetchall()
print('Current favorites in database:')
for code, name in result:
    print(f'  ⭐ {code} - {name}')

db.close()
