import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from database import CryptoDatabase
from datetime import datetime

db = CryptoDatabase('data/test_update.db')
cur = db.conn.cursor()
today = datetime.now().date().isoformat()
cur.execute('UPDATE crypto_info SET last_quote_date=? WHERE code=?', (today, 'BTC'))
db.conn.commit()
print('Set last_quote_date for BTC to', today)
db.close()
