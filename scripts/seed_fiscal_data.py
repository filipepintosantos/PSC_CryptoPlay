"""Script to add sample data to binance_fiscal table for testing."""

import sqlite3
import os
from datetime import datetime

def seed_fiscal_data():
    """Add sample fiscal records to test the UI."""
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'crypto_prices.db'))
    
    if not os.path.exists(db_path):
        print(f'Database not found: {db_path}')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='binance_fiscal'")
    if not cursor.fetchone():
        print('Table binance_fiscal does not exist. Run schema first.')
        conn.close()
        return
    
    # Clear existing data
    cursor.execute("DELETE FROM binance_fiscal")
    
    # Income examples (I) - Interest/Airdrop with 28% tax
    income_records = [
        ('2025-12-15 10:30:00', 'I', 'BTC', 0.0, 0.0, 50.0, 14.0),
        ('2025-11-20 14:20:00', 'I', 'ADA', 0.0, 0.0, 25.0, 7.0),
        ('2025-10-10 09:15:00', 'I', 'ETH', 0.0, 0.0, 100.0, 28.0),
        ('2025-09-05 16:45:00', 'I', 'BTC', 0.0, 0.0, 30.0, 8.4),
        ('2025-08-12 08:00:00', 'I', 'SOL', 0.0, 0.0, 15.0, 4.2),
    ]
    
    # Sales examples (V) - EUR/Conversions with FIFO cost basis
    sales_records = [
        ('2026-01-10 11:00:00', 'V', 'BTC', 1000.0, 1500.0, 500.0, 125.0),
        ('2026-01-08 15:30:00', 'V', 'ADA', 200.0, 250.0, 50.0, 12.5),
        ('2025-12-20 13:45:00', 'V', 'ETH', 800.0, 950.0, 150.0, 37.5),
        ('2025-11-15 10:20:00', 'V', 'BTC', 500.0, 600.0, 100.0, 25.0),
        ('2025-10-25 14:00:00', 'V', 'ADA', 100.0, 110.0, 10.0, 2.5),
        ('2025-09-18 12:30:00', 'V', 'SOL', 300.0, 350.0, 50.0, 12.5),
    ]
    
    all_records = income_records + sales_records
    
    for record in all_records:
        cursor.execute('''
            INSERT INTO binance_fiscal (trn_date_utc, type, crypto_id, buy_eur, sell_eur, gain_eur, tax_eur)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', record)
    
    conn.commit()
    print(f'✓ Added {len(all_records)} sample records to binance_fiscal')
    
    # Show summary
    cursor.execute('SELECT COUNT(*), SUM(gain_eur), SUM(tax_eur) FROM binance_fiscal')
    total, total_gain, total_tax = cursor.fetchone()
    print(f'Total records: {total}')
    print(f'Total gain: {total_gain:.2f} EUR')
    print(f'Total tax: {total_tax:.2f} EUR')
    
    # Show breakdown by type
    cursor.execute('''
        SELECT type, COUNT(*), SUM(gain_eur), SUM(tax_eur) 
        FROM binance_fiscal 
        GROUP BY type
    ''')
    print('\nBreakdown by type:')
    for tipo, count, gain, tax in cursor.fetchall():
        tipo_desc = 'Income' if tipo == 'I' else 'Sales'
        print(f'  {tipo_desc} ({tipo}): {count} records, {gain:.2f} EUR gain, {tax:.2f} EUR tax')
    
    conn.close()


if __name__ == '__main__':
    seed_fiscal_data()
