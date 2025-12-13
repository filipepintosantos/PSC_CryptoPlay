"""
Script to mark favorite cryptocurrencies from config.ini with classification A, B, C
"""
import configparser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import CryptoDatabase

def get_favorites_from_config(config, class_name):
    """Get favorites list for a specific class from config."""
    favorites_str = config.get('symbols', f'favorites_{class_name.lower()}', fallback='')
    return [s.strip().upper() for s in favorites_str.split(',') if s.strip()]

# Load config
config = configparser.ConfigParser()
config.read('config/config.ini')

# Get favorites for each class
favorites_a = get_favorites_from_config(config, 'A')
favorites_b = get_favorites_from_config(config, 'B')
favorites_c = get_favorites_from_config(config, 'C')

print('Favorites from config.ini:')
print(f'  Class A (Top priority): {", ".join(favorites_a) if favorites_a else "None"}')
print(f'  Class B (Secondary): {", ".join(favorites_b) if favorites_b else "None"}')
print(f'  Class C (Tertiary): {", ".join(favorites_c) if favorites_c else "None"}')
print()

# Update database
db = CryptoDatabase()

# First, unmark all as non-favorites
db.conn.execute('UPDATE crypto_info SET favorite = NULL')

# Then mark the ones from config with their respective classes
updated = {'A': 0, 'B': 0, 'C': 0}

for code in favorites_a:
    result = db.conn.execute('UPDATE crypto_info SET favorite = ? WHERE code = ?', ('A', code))
    updated['A'] += result.rowcount

for code in favorites_b:
    result = db.conn.execute('UPDATE crypto_info SET favorite = ? WHERE code = ?', ('B', code))
    updated['B'] += result.rowcount

for code in favorites_c:
    result = db.conn.execute('UPDATE crypto_info SET favorite = ? WHERE code = ?', ('C', code))
    updated['C'] += result.rowcount

db.conn.commit()

print('Marked cryptocurrencies as favorites:')
print(f'  Class A: {updated["A"]}')
print(f'  Class B: {updated["B"]}')
print(f'  Class C: {updated["C"]}')
print()

# Show current favorites by class
for cls in ['A', 'B', 'C']:
    result = db.conn.execute(
        'SELECT code, name FROM crypto_info WHERE favorite = ? ORDER BY code', 
        (cls,)
    ).fetchall()
    
    if result:
        emoji = {'A': '⭐⭐⭐', 'B': '⭐⭐', 'C': '⭐'}[cls]
        print(f'Class {cls} favorites in database:')
        for code, name in result:
            print(f'  {emoji} {code} - {name}')
        print()

db.close()
