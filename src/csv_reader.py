"""
CSV Reader module for importing cryptocurrency data from CSV files.

Provides functionality to read and parse cryptocurrency price data from CSV files
with flexible column mapping and date format handling.
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class CSVConfig:
    """Configuration for CSV file reading."""
    date_column: Union[str, int] = 0  # Column name (if header=True) or index
    price_column: Union[str, int] = 1
    has_header: bool = True
    encoding: str = 'utf-8'
    delimiter: str = ','
    date_format: Optional[str] = None  # If None, tries common formats
    skip_rows: int = 0  # Number of rows to skip at the beginning


class CSVReader:
    """Reader for cryptocurrency price data from CSV files."""
    
    # Common date formats to try if not specified
    COMMON_DATE_FORMATS = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%m-%d-%Y',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%ISO8601',
    ]
    
    def __init__(self, config: Optional[CSVConfig] = None):
        """
        Initialize CSV reader.
        
        Args:
            config: CSVConfig instance with reading parameters
        """
        self.config = config or CSVConfig()
    
    @staticmethod
    def _parse_date(date_str: str, date_format: Optional[str] = None) -> datetime:
        """
        Parse date string with flexible format handling.
        
        Args:
            date_str: Date string to parse
            date_format: Specific date format, or None to try common formats
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If date cannot be parsed
        """
        date_str = date_str.strip()
        
        if date_format:
            if date_format == '%ISO8601':
                return datetime.fromisoformat(date_str)
            return datetime.strptime(date_str, date_format)
        
        # Try common formats
        for fmt in CSVReader.COMMON_DATE_FORMATS:
            try:
                if fmt == '%ISO8601':
                    return datetime.fromisoformat(date_str)
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")
    
    @staticmethod
    def _parse_price(price_str: str) -> float:
        """
        Parse price string, removing common currency symbols.
        
        Args:
            price_str: Price string to parse
            
        Returns:
            Float price value
            
        Raises:
            ValueError: If price cannot be converted to float
        """
        # Remove common currency symbols and whitespace
        cleaned = (price_str
                   .strip()
                   .replace('€', '')
                   .replace('$', '')
                   .replace('£', '')
                   .replace('¥', '')
                   .replace(',', '.'))
        
        return float(cleaned)
    
    def read_file(self, file_path: Union[str, Path]) -> List[Dict[str, Union[str, float, datetime]]]:
        """
        Read and parse CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of dictionaries with parsed data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If CSV format is invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        rows = []
        with open(file_path, 'r', encoding=self.config.encoding) as f:
            reader = csv.reader(f, delimiter=self.config.delimiter)
            
            # Skip initial rows
            for _ in range(self.config.skip_rows):
                next(reader, None)
            
            # Get header if present
            header = None
            if self.config.has_header:
                header = next(reader, None)
                if not header:
                    raise ValueError("CSV file has no header but has_header=True")
            
            # Determine column indices
            date_idx, price_idx = self._get_column_indices(header)
            
            # Read data rows
            for row_num, row in enumerate(reader, start=self.config.skip_rows + (2 if self.config.has_header else 1)):
                if len(row) <= max(date_idx, price_idx):
                    print(f"Warning: Row {row_num} has insufficient columns, skipping")
                    continue
                
                try:
                    date_val = self._parse_date(row[date_idx], self.config.date_format)
                    price_val = self._parse_price(row[price_idx])
                    
                    rows.append({
                        'date': date_val,
                        'price': price_val,
                        'date_str': row[date_idx],
                        'price_str': row[price_idx],
                    })
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse row {row_num}: {e}")
                    continue
        
        return rows
    
    def _get_column_indices(self, header: Optional[List[str]]) -> Tuple[int, int]:
        """
        Get column indices from header or config.
        
        Args:
            header: List of header column names (or None)
            
        Returns:
            Tuple of (date_idx, price_idx)
            
        Raises:
            ValueError: If columns cannot be found
        """
        if header is not None:
            # Try to use header names
            if isinstance(self.config.date_column, str):
                try:
                    date_idx = header.index(self.config.date_column)
                except ValueError:
                    raise ValueError(f"Date column '{self.config.date_column}' not found in header")
            else:
                date_idx = int(self.config.date_column)
            
            if isinstance(self.config.price_column, str):
                try:
                    price_idx = header.index(self.config.price_column)
                except ValueError:
                    raise ValueError(f"Price column '{self.config.price_column}' not found in header")
            else:
                price_idx = int(self.config.price_column)
        else:
            # Use numeric indices
            date_idx = int(self.config.date_column)
            price_idx = int(self.config.price_column)
        
        return date_idx, price_idx
    
    def read_and_validate(self, file_path: Union[str, Path]) -> Tuple[List[Dict], List[str]]:
        """
        Read CSV file and return both data and any warnings encountered.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (rows, warnings)
        """
        # This is a simplified version; warnings would be collected during read
        rows = self.read_file(file_path)
        return rows, []
    
    @staticmethod
    def guess_config(file_path: Union[str, Path], sample_size: int = 5) -> CSVConfig:
        """
        Guess appropriate configuration from CSV file sample.
        
        Args:
            file_path: Path to CSV file
            sample_size: Number of rows to sample
            
        Returns:
            Guessed CSVConfig instance
        """
        file_path = Path(file_path)
        config = CSVConfig()
        
        # Try to detect delimiter
        with open(file_path, 'r', encoding=config.encoding) as f:
            sample = f.read(1024)
            dialect = csv.Sniffer().sniff(sample)
            config.delimiter = dialect.delimiter
        
        # Default config with detected delimiter
        return config


def import_crypto_data(file_path: Union[str, Path], symbol: str, 
                       config: Optional[CSVConfig] = None) -> List[Dict]:
    """
    Convenience function to import cryptocurrency data from CSV.
    
    Args:
        file_path: Path to CSV file
        symbol: Cryptocurrency symbol
        config: Optional CSVConfig with custom parameters
        
    Returns:
        List of quote dictionaries ready for database insertion
    """
    reader = CSVReader(config)
    rows = reader.read_file(file_path)
    
    # Format for database insertion
    return [
        {
            'symbol': symbol,
            'name': symbol,
            'close_eur': row['price'],
            'price_eur': row['price'],  # Backward compatibility
            'timestamp': row['date'],
        }
        for row in rows
    ]
