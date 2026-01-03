import csv
from pathlib import Path

csv_path = Path('external/in/8ce3d284-e80d-11f0-b15e-0688bfc90b95-1.csv')
with csv_path.open('r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        count += 1

print(f'CSV data rows (excluding header): {count}')

from src.database import CryptoDatabase
db = CryptoDatabase('data/crypto_prices.db')
cur = db.conn.cursor()
cur.execute("SELECT COUNT(*) FROM binance_transactions WHERE source='BinanceCSV'")
db_count = cur.fetchone()[0]
print(f'DB BinanceCSV rows: {db_count}')

# Check for duplicates
cur.execute("""
    SELECT user_id, utc_time, account, operation, coin, change, remark, COUNT(*) as cnt
    FROM binance_transactions
    WHERE source='BinanceCSV'
    GROUP BY user_id, utc_time, account, operation, coin, change, remark
    HAVING cnt > 1
""")
dups = cur.fetchall()
if dups:
    print(f'Found {len(dups)} duplicate rows:')
    for row in dups[:5]:
        print(f'  user_id={row[0]}, utc_time={row[1]}, account={row[2]}, operation={row[3]}, coin={row[4]}, change={row[5]}, remark={row[6]}, count={row[7]}')
else:
    print('No duplicates found')

db.close()
