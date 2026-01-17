import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from database import CryptoDatabase

db = CryptoDatabase('data/test_update.db')
cur = db.conn.cursor()
cur.execute("SELECT code, last_quote_date FROM crypto_info WHERE code='BTC'")
row = cur.fetchone()
print('row:', row)
if row:
    print('last_quote_date:', row[1])
else:
    print('BTC not found')
db.close()
