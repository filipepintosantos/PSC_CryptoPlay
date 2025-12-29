"""
Module for statistical analysis of cryptocurrency prices.
Calculates min, max, mean, standard deviation, and mean-std metrics.
"""

from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import pandas as pd

class StatisticalAnalyzer:
    """Performs statistical analysis on cryptocurrency price data."""

    ROLLING_PERIODS = {
        "12_months": 365,
        "6_months": 182,
        "3_months": 91,
        "1_month": 30,
    }

    @staticmethod
    def calculate_statistics(prices: List[float]) -> Dict[str, float]:
        """
        Calculate statistical metrics for a list of prices.

        Args:
            prices: List of price values

        Returns:
            Dictionary with statistical metrics
        """
        if not prices:
            return {
                "min": None,
                "max": None,
                "mean": None,
                "std": None,
                "mean_minus_std": None,
                "count": 0,
            }

        prices_array = np.array(prices, dtype=float)
        mean_val = float(np.mean(prices_array))
        std_val = float(np.std(prices_array))
        median_val = float(np.median(prices_array))
        # MAD: Median Absolute Deviation
        mad_val = float(np.median(np.abs(prices_array - median_val)))

        return {
            "min": float(np.min(prices_array)),
            "max": float(np.max(prices_array)),
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "mad": mad_val,
            "mean_minus_std": mean_val - std_val,
            "median_minus_mad": median_val - mad_val,
            "count": len(prices),
        }

    @staticmethod
    def _create_empty_period_result() -> Dict:
        """Create an empty result structure for a period with no data."""
        return {
            "stats": {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
                "mad": None,
                "mean_minus_std": None,
                "median_minus_mad": None,
                "count": 0,
            },
            "latest_quote": None,
            "latest_date": None,
            "second_latest_quote": None,
            "second_latest_date": None,
            "latest_deviation_from_mean": None,
            "latest_deviation_from_mean_pct": None,
            "latest_deviation_from_mean_minus_std": None,
            "latest_deviation_from_mean_minus_std_pct": None,
            "second_deviation_from_mean": None,
            "second_deviation_from_mean_pct": None,
            "second_deviation_from_mean_minus_std": None,
            "second_deviation_from_mean_minus_std_pct": None,
            "latest_deviation_from_median": None,
            "latest_deviation_from_median_pct": None,
            "latest_deviation_from_median_minus_mad": None,
            "latest_deviation_from_median_minus_mad_pct": None,
            "second_deviation_from_median": None,
            "second_deviation_from_median_pct": None,
            "second_deviation_from_median_minus_mad": None,
            "second_deviation_from_median_minus_mad_pct": None,
        }

    @staticmethod
    def _calculate_deviation(price: float, baseline: float) -> tuple:
        """Calculate absolute and percentage deviation from baseline."""
        if not baseline:
            return None, None
        deviation = price - baseline
        deviation_pct = (deviation / baseline) * 100
        return deviation, deviation_pct

    @staticmethod
    def _analyze_period_data(period_data: pd.DataFrame) -> Dict:
        """Analyze data for a specific period and calculate all metrics."""
        prices = period_data['close_eur'].tolist()
        stats = StatisticalAnalyzer.calculate_statistics(prices)

        # Extract latest and second latest prices
        latest_price = period_data.iloc[0]['close_eur']
        latest_date = period_data.iloc[0]['timestamp']
        second_latest_price = period_data.iloc[1]['close_eur'] if len(period_data) > 1 else None
        second_latest_date = period_data.iloc[1]['timestamp'] if len(period_data) > 1 else None

        # Calculate deviations for latest price
        latest_dev_mean, latest_dev_mean_pct = StatisticalAnalyzer._calculate_deviation(
            latest_price, stats['mean']
        )
        latest_dev_mean_std, latest_dev_mean_std_pct = StatisticalAnalyzer._calculate_deviation(
            latest_price, stats['mean_minus_std']
        )

        # Calculate deviations for second latest price
        second_dev_mean, second_dev_mean_pct = (None, None)
        second_dev_mean_std, second_dev_mean_std_pct = (None, None)
        if second_latest_price:
            second_dev_mean, second_dev_mean_pct = StatisticalAnalyzer._calculate_deviation(
                second_latest_price, stats['mean']
            )
            second_dev_mean_std, second_dev_mean_std_pct = StatisticalAnalyzer._calculate_deviation(
                second_latest_price, stats['mean_minus_std']
            )

        # Calculate deviations from median for latest price
        latest_dev_median, latest_dev_median_pct = StatisticalAnalyzer._calculate_deviation(
            latest_price, stats['median']
        )
        latest_dev_median_mad, latest_dev_median_mad_pct = StatisticalAnalyzer._calculate_deviation(
            latest_price, stats['median_minus_mad']
        )

        # Calculate deviations from median for second latest price
        second_dev_median, second_dev_median_pct = (None, None)
        second_dev_median_mad, second_dev_median_mad_pct = (None, None)
        if second_latest_price:
            second_dev_median, second_dev_median_pct = StatisticalAnalyzer._calculate_deviation(
                second_latest_price, stats['median']
            )
            second_dev_median_mad, second_dev_median_mad_pct = StatisticalAnalyzer._calculate_deviation(
                second_latest_price, stats['median_minus_mad']
            )

        return {
            "stats": stats,
            "latest_quote": float(latest_price),
            "latest_date": latest_date.strftime('%d/%m/%Y'),
            "second_latest_quote": float(second_latest_price) if second_latest_price else None,
            "second_latest_date": second_latest_date.strftime('%d/%m/%Y') if second_latest_date else None,
            "latest_deviation_from_mean": latest_dev_mean,
            "latest_deviation_from_mean_pct": latest_dev_mean_pct,
            "latest_deviation_from_mean_minus_std": latest_dev_mean_std,
            "latest_deviation_from_mean_minus_std_pct": latest_dev_mean_std_pct,
            "second_deviation_from_mean": second_dev_mean,
            "second_deviation_from_mean_pct": second_dev_mean_pct,
            "second_deviation_from_mean_minus_std": second_dev_mean_std,
            "second_deviation_from_mean_minus_std_pct": second_dev_mean_std_pct,
            "latest_deviation_from_median": latest_dev_median,
            "latest_deviation_from_median_pct": latest_dev_median_pct,
            "latest_deviation_from_median_minus_mad": latest_dev_median_mad,
            "latest_deviation_from_median_minus_mad_pct": latest_dev_median_mad_pct,
            "second_deviation_from_median": second_dev_median,
            "second_deviation_from_median_pct": second_dev_median_pct,
            "second_deviation_from_median_minus_mad": second_dev_median_mad,
            "second_deviation_from_median_minus_mad_pct": second_dev_median_mad_pct,
        }

    @staticmethod
    def analyze_rolling_periods(quotes_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Analyze prices for rolling periods (12m, 6m, 3m, 1m).

        Args:
            quotes_df: DataFrame with price quotes

        Returns:
            Dictionary with statistics for each period
        """
        if quotes_df.empty:
            return {period: {} for period in StatisticalAnalyzer.ROLLING_PERIODS}

        results = {}
        now = datetime.now()

        for period_name, days in StatisticalAnalyzer.ROLLING_PERIODS.items():
            cutoff_date = now - timedelta(days=days)
            period_data = quotes_df[quotes_df['timestamp'] >= cutoff_date]

            if period_data.empty:
                results[period_name] = StatisticalAnalyzer._create_empty_period_result()
            else:
                results[period_name] = StatisticalAnalyzer._analyze_period_data(period_data)

        return results

    @staticmethod
    def prepare_dataframe_from_quotes(quotes: List[Dict]) -> pd.DataFrame:
        """
        Convert quotes list to pandas DataFrame.

        Args:
            quotes: List of quote dictionaries

        Returns:
            DataFrame with parsed data
        """
        if not quotes:
            return pd.DataFrame()

        df = pd.DataFrame(quotes)

        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Sort by timestamp in descending order (most recent first)
        df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)

        return df

    @staticmethod
    def generate_report(symbol: str, quotes: List[Dict]) -> Dict:
        """
        Generate complete statistical report for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol
            quotes: List of quote dictionaries from database

        Returns:
            Dictionary with complete analysis
        """
        df = StatisticalAnalyzer.prepare_dataframe_from_quotes(quotes)

        if df.empty:
            return {
                "symbol": symbol,
                "data_points": 0,
                "date_range": None,
                "periods": {},
            }

        # Analyze rolling periods
        period_analysis = StatisticalAnalyzer.analyze_rolling_periods(df)

        return {
            "symbol": symbol,
            "data_points": len(df),
            "date_range": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat(),
            },
            "periods": period_analysis,
        }

    @staticmethod
    def batch_generate_reports(symbols: List[str], get_quotes_func) -> Dict[str, Dict]:
        """
        Generate reports for multiple cryptocurrencies.

        Args:
            symbols: List of cryptocurrency symbols
            get_quotes_func: Function that takes symbol and returns quotes list

        Returns:
            Dictionary with reports for each symbol
        """
        reports = {}
        for symbol in symbols:
            try:
                quotes = get_quotes_func(symbol)
                reports[symbol] = StatisticalAnalyzer.generate_report(symbol, quotes)
            except Exception as e:
                print(f"Error generating report for {symbol}: {e}")
                reports[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                }

        return reports
