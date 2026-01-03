from src.database import CryptoDatabase

db = CryptoDatabase('data/crypto_prices.db')
cur = db.conn.cursor()

cur.execute("SELECT COUNT(*) FROM binance_transactions WHERE source='BinanceCSV'")
count = cur.fetchone()[0]
print(f'BinanceCSV count: {count}')

cur.execute("SELECT user_id, coin, utc_time FROM binance_transactions WHERE source='BinanceCSV' ORDER BY rowid LIMIT 3")
print('First 3:')
for row in cur.fetchall():
    print(f'  user_id={row[0]}, coin={row[1]}, utc_time={row[2]}')

db.close()
