"""
Module for analyzing cryptocurrency volatility and price oscillations.
Calculates events based on rolling windows and percentage thresholds.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta


class VolatilityAnalyzer:
    """Analyzes price oscillations and volatility events for cryptocurrencies."""
    
    WINDOWS = {
        "24h": 1,
        "72h": 3,
        "7d": 7,
        "1M": 30,
        "3M": 90,
        "6M": 180
    }
    
    THRESHOLDS = [5, 10, 15, 20]
    
    def __init__(self, database):
        """
        Initialize the volatility analyzer.
        
        Args:
            database: CryptoDatabase instance
        """
        self.database = database
    
    def calculate_oscillations(self, symbol: str, days: int = 365) -> Dict:
        """
        Calculate oscillation events for a cryptocurrency across different windows.
        
        Args:
            symbol: Cryptocurrency symbol
            days: Number of days to analyze (default: 365 for 12 months)
            
        Returns:
            Dictionary with oscillation counts per window and threshold
        """
        # Get historical data
        quotes = self.database.get_quotes(symbol, days=days)
        
        if not quotes or len(quotes) < 7:  # Need at least 7 days
            return self._create_empty_result()
        
        # Convert to DataFrame
        df = pd.DataFrame(quotes, columns=['timestamp', 'price_eur'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=True).reset_index(drop=True)
        
        results = {}
        
        # Calculate for each window
        for window_name, window_days in self.WINDOWS.items():
            window_results = self._analyze_window(df, window_days)
            results[window_name] = window_results
        
        return results
    
    def _analyze_window(self, df: pd.DataFrame, window_days: int) -> Dict:
        """
        Analyze oscillations for a specific rolling window.
        
        Args:
            df: DataFrame with timestamp and price_eur columns
            window_days: Window size in days
            
        Returns:
            Dictionary with event counts per threshold
        """
        # Calculate rolling returns
        df = df.copy()
        df['return_pct'] = df['price_eur'].pct_change(periods=window_days) * 100
        
        # Count events for each threshold
        events = {}
        
        for threshold in self.THRESHOLDS:
            # Positive oscillations
            events[f'positive_{threshold}'] = (df['return_pct'] >= threshold).sum()
            
            # Negative oscillations
            events[f'negative_{threshold}'] = (df['return_pct'] <= -threshold).sum()
        
        return events
    
    def _create_empty_result(self) -> Dict:
        """Create empty result structure for symbols with insufficient data."""
        empty_window = {f'positive_{t}': 0 for t in self.THRESHOLDS}
        empty_window.update({f'negative_{t}': 0 for t in self.THRESHOLDS})
        
        return {window: empty_window.copy() for window in self.WINDOWS.keys()}
    
    def analyze_all_symbols(self, symbols: List[str], days: int = 365) -> Dict[str, Dict]:
        """
        Analyze oscillations for multiple cryptocurrencies.
        
        Args:
            symbols: List of cryptocurrency symbols
            days: Number of days to analyze
            
        Returns:
            Dictionary mapping symbols to their oscillation results
        """
        results = {}
        
        for symbol in symbols:
            print(f"Analyzing volatility for {symbol}...")
            results[symbol] = self.calculate_oscillations(symbol, days)
        
        return results
    
    def export_to_csv(self, results: Dict[str, Dict], filename: str = "reports/volatility_analysis.csv"):
        """
        Export oscillation results to CSV file.
        
        Args:
            results: Dictionary with analysis results from analyze_all_symbols
            filename: Output CSV file path
        """
        rows = []
        
        for symbol, windows in results.items():
            for window_name, events in windows.items():
                row = {
                    'Symbol': symbol,
                    'Window': window_name
                }
                
                # Add positive events
                for threshold in self.THRESHOLDS:
                    row[f'+{threshold}%'] = events.get(f'positive_{threshold}', 0)
                
                # Add negative events
                for threshold in self.THRESHOLDS:
                    row[f'-{threshold}%'] = events.get(f'negative_{threshold}', 0)
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Order columns
        column_order = ['Symbol', 'Window']
        column_order += [f'+{t}%' for t in self.THRESHOLDS]
        column_order += [f'-{t}%' for t in self.THRESHOLDS]
        
        df = df[column_order]
        
        # Save to CSV
        import os
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        df.to_csv(filename, index=False)
        print(f"Volatility analysis exported to: {filename}")
        
        return df
    
    def get_summary_stats(self, symbol: str, days: int = 365) -> Dict:
        """
        Get summary statistics for a symbol to add to Excel report.
        
        Args:
            symbol: Cryptocurrency symbol
            days: Number of days to analyze
            
        Returns:
            Dictionary with aggregated volatility stats
        """
        oscillations = self.calculate_oscillations(symbol, days)
        
        # Aggregate across all windows
        total_positive_5 = sum(w.get('positive_5', 0) for w in oscillations.values())
        total_positive_10 = sum(w.get('positive_10', 0) for w in oscillations.values())
        total_negative_5 = sum(w.get('negative_5', 0) for w in oscillations.values())
        total_negative_10 = sum(w.get('negative_10', 0) for w in oscillations.values())
        
        return {
            'volatility_positive_5': total_positive_5,
            'volatility_positive_10': total_positive_10,
            'volatility_negative_5': total_negative_5,
            'volatility_negative_10': total_negative_10,
            'volatility_score': total_positive_5 + total_positive_10 + total_negative_5 + total_negative_10
        }
    
    def get_period_stats(self, symbol: str, period_days: int) -> Dict:
        """
        Get volatility statistics for a specific analysis period.
        Maps report periods (12M, 6M, 3M, 1M) to appropriate rolling windows.
        
        Args:
            symbol: Cryptocurrency symbol
            period_days: Analysis period (365, 180, 90, 30)
            
        Returns:
            Dictionary with volatility stats for the period
        """
        oscillations = self.calculate_oscillations(symbol, days=period_days)
        
        # Select appropriate windows based on period
        if period_days >= 180:  # 6M or 12M - use longer windows
            windows_to_use = ["7d", "1M", "3M"]
        elif period_days >= 90:  # 3M - use medium windows
            windows_to_use = ["72h", "7d", "1M"]
        else:  # 1M - use shorter windows
            windows_to_use = ["24h", "72h", "7d"]
        
        # Aggregate selected windows
        total_positive_5 = sum(oscillations.get(w, {}).get('positive_5', 0) for w in windows_to_use if w in oscillations)
        total_positive_10 = sum(oscillations.get(w, {}).get('positive_10', 0) for w in windows_to_use if w in oscillations)
        total_negative_5 = sum(oscillations.get(w, {}).get('negative_5', 0) for w in windows_to_use if w in oscillations)
        total_negative_10 = sum(oscillations.get(w, {}).get('negative_10', 0) for w in windows_to_use if w in oscillations)
        
        return {
            'volatility_positive_5': total_positive_5,
            'volatility_positive_10': total_positive_10,
            'volatility_negative_5': total_negative_5,
            'volatility_negative_10': total_negative_10,
            'volatility_score': total_positive_5 + total_positive_10 + total_negative_5 + total_negative_10,
            'windows_used': windows_to_use
        }
