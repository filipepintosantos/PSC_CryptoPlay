"""
Module for analyzing cryptocurrency volatility and price oscillations.
Calculates events based on rolling windows and percentage thresholds.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta


class VolatilityAnalyzer:
    """Analyzes price oscillations and volatility events for cryptocurrencies."""
    
    # Rolling windows for calculating returns (short periods only)
    WINDOWS = {
        "24h": 1,
        "72h": 3,
        "7d": 7
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
        Detects unique events and counts only the highest threshold reached.
        
        Args:
            df: DataFrame with timestamp and price_eur columns
            window_days: Window size in days
            
        Returns:
            Dictionary with event counts per threshold
        """
        # Calculate rolling returns
        df = df.copy()
        df['return_pct'] = df['price_eur'].pct_change(periods=window_days) * 100
        
        # Initialize event counters
        events = {f'positive_{t}': 0 for t in self.THRESHOLDS}
        events.update({f'negative_{t}': 0 for t in self.THRESHOLDS})
        
        # Sort thresholds from highest to lowest to count bigger events first
        sorted_thresholds = sorted(self.THRESHOLDS, reverse=True)
        
        # Count positive and negative events separately
        self._count_threshold_events(df, sorted_thresholds, window_days, events, 'positive')
        self._count_threshold_events(df, sorted_thresholds, window_days, events, 'negative')
        
        return events
    
    def _count_threshold_events(self, df: pd.DataFrame, sorted_thresholds: list, 
                                window_days: int, events: dict, direction: str) -> None:
        """
        Count events for a specific direction (positive or negative).
        
        Args:
            df: DataFrame with return_pct column
            sorted_thresholds: Thresholds sorted from highest to lowest
            window_days: Window size in days
            events: Dictionary to update with event counts
            direction: 'positive' or 'negative'
        """
        used_indices = set()
        
        for threshold in sorted_thresholds:
            # Determine mask based on direction
            if direction == 'positive':
                mask = df['return_pct'] >= threshold
            else:  # negative
                mask = df['return_pct'] <= -threshold
            
            for idx in df[mask].index:
                # Only count if this index hasn't been used by a higher threshold
                if idx not in used_indices:
                    events[f'{direction}_{threshold}'] += 1
                    # Mark this index and nearby indices as used to avoid overlap
                    start_idx = max(0, idx - window_days)
                    end_idx = min(len(df), idx + window_days + 1)
                    for i in range(start_idx, end_idx):
                        used_indices.add(i)
    
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
        Uses only the 7d window to avoid overlapping between different window sizes.
        
        Args:
            symbol: Cryptocurrency symbol
            days: Number of days to analyze
            
        Returns:
            Dictionary with aggregated volatility stats
        """
        oscillations = self.calculate_oscillations(symbol, days)
        
        # Use only 7d window to avoid overlap with shorter windows
        # This gives the most comprehensive view without double counting
        window_7d = oscillations.get('7d', {})
        
        total_positive_5 = window_7d.get('positive_5', 0)
        total_positive_10 = window_7d.get('positive_10', 0)
        total_positive_15 = window_7d.get('positive_15', 0)
        total_positive_20 = window_7d.get('positive_20', 0)
        total_negative_5 = window_7d.get('negative_5', 0)
        total_negative_10 = window_7d.get('negative_10', 0)
        total_negative_15 = window_7d.get('negative_15', 0)
        total_negative_20 = window_7d.get('negative_20', 0)
        
        # Calculate weighted score (5*1, 10*2, 15*3, 20*4)
        score_5 = (total_positive_5 + total_negative_5) * 1
        score_10 = (total_positive_10 + total_negative_10) * 2
        score_15 = (total_positive_15 + total_negative_15) * 3
        score_20 = (total_positive_20 + total_negative_20) * 4
        volatility_score = score_5 + score_10 + score_15 + score_20
        
        return {
            'volatility_positive_5': total_positive_5,
            'volatility_positive_10': total_positive_10,
            'volatility_positive_15': total_positive_15,
            'volatility_positive_20': total_positive_20,
            'volatility_negative_5': total_negative_5,
            'volatility_negative_10': total_negative_10,
            'volatility_negative_15': total_negative_15,
            'volatility_negative_20': total_negative_20,
            'volatility_score': volatility_score
        }
    
    def get_period_stats(self, symbol: str, period_days: int) -> Dict:
        """
        Get volatility statistics for a specific analysis period.
        Uses only the 7d window to avoid overlapping between different window sizes.
        
        Args:
            symbol: Cryptocurrency symbol
            period_days: Analysis period in days (365, 180, 90, 30)
            
        Returns:
            Dictionary with volatility stats for the period
        """
        # Calculate oscillations for this period using SHORT windows (24h, 72h, 7d)
        oscillations = self.calculate_oscillations(symbol, days=period_days)
        
        # Use only 7d window to avoid overlap with shorter windows
        window_7d = oscillations.get('7d', {})
        
        total_positive_5 = window_7d.get('positive_5', 0)
        total_positive_10 = window_7d.get('positive_10', 0)
        total_positive_15 = window_7d.get('positive_15', 0)
        total_positive_20 = window_7d.get('positive_20', 0)
        total_negative_5 = window_7d.get('negative_5', 0)
        total_negative_10 = window_7d.get('negative_10', 0)
        total_negative_15 = window_7d.get('negative_15', 0)
        total_negative_20 = window_7d.get('negative_20', 0)
        
        # Calculate weighted score
        score_5 = (total_positive_5 + total_negative_5) * 1
        score_10 = (total_positive_10 + total_negative_10) * 2
        score_15 = (total_positive_15 + total_negative_15) * 3
        score_20 = (total_positive_20 + total_negative_20) * 4
        volatility_score = score_5 + score_10 + score_15 + score_20
        
        return {
            'volatility_positive_5': total_positive_5,
            'volatility_positive_10': total_positive_10,
            'volatility_positive_15': total_positive_15,
            'volatility_positive_20': total_positive_20,
            'volatility_negative_5': total_negative_5,
            'volatility_negative_10': total_negative_10,
            'volatility_negative_15': total_negative_15,
            'volatility_negative_20': total_negative_20,
            'volatility_score': volatility_score
        }
