from src.database import CryptoDatabase

db = CryptoDatabase('data/crypto_prices.db')
cur = db.conn.cursor()

# Get the duplicate row's rowids
cur.execute("""
    SELECT rowid FROM binance_transactions 
    WHERE source='BinanceCSV' 
    AND user_id='1182843341' 
    AND utc_time='2025-11-18 06:47:54' 
    AND account='Spot' 
    AND operation='Deposit' 
    AND coin='EUR' 
    AND change=100.0 
    AND remark=''
    ORDER BY rowid
""")
rowids = [row[0] for row in cur.fetchall()]
print(f'Found {len(rowids)} rows with this key: {rowids}')

if len(rowids) > 1:
    # Delete all but the first
    for rowid in rowids[1:]:
        cur.execute('DELETE FROM binance_transactions WHERE rowid=?', (rowid,))
    db.conn.commit()
    print(f'Deleted {len(rowids) - 1} duplicate(s)')

cur.execute('SELECT COUNT(*) FROM binance_transactions WHERE source="BinanceCSV"')
print('Remaining BinanceCSV rows:', cur.fetchone()[0])

db.close()
