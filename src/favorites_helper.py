"""
Utility functions for managing favorite classifications from config.
"""
import configparser
from typing import Dict, List, Optional
from src.database import CryptoDatabase


def get_favorites_from_config(config: configparser.ConfigParser) -> Dict[str, List[str]]:
    """
    Get favorites organized by class from config.

    Args:
        config: ConfigParser instance with loaded config.ini

    Returns:
        Dictionary with keys 'A', 'B', 'C' and lists of symbol strings
    """
    favorites = {}
    for cls in ['A', 'B', 'C']:
        key = f'favorites_{cls.lower()}'
        favorites_str = config.get('symbols', key, fallback='')
        favorites[cls] = [s.strip().upper() for s in favorites_str.split(',') if s.strip()]
    return favorites


def get_all_favorites_list(config: configparser.ConfigParser) -> List[str]:
    """
    Get all favorites as a flat list, regardless of class.

    Args:
        config: ConfigParser instance with loaded config.ini

    Returns:
        List of all favorite symbols
    """
    favorites_dict = get_favorites_from_config(config)
    all_favs = []
    for cls in ['A', 'B', 'C']:
        all_favs.extend(favorites_dict[cls])
    return all_favs


def validate_and_update_favorites(db: CryptoDatabase, config: configparser.ConfigParser) -> int:
    """
    Validate and update favorite classifications based on config.
    This ensures all symbols in crypto_info have correct favorite_class values.

    Args:
        db: Database instance
        config: ConfigParser instance with loaded config.ini

    Returns:
        Number of records updated
    """
    favorites_dict = get_favorites_from_config(config)

    # Build a mapping of symbol -> class
    symbol_to_class = {}
    for cls, symbols in favorites_dict.items():
        for symbol in symbols:
            symbol_to_class[symbol] = cls

    # Get all crypto_info records
    all_cryptos = db.get_all_crypto_info()

    updated = 0
    for crypto in all_cryptos:
        code = crypto['code']
        current_class = crypto.get('favorite_class')
        expected_class = symbol_to_class.get(code)

        # Update if classification doesn't match
        if current_class != expected_class:
            db.set_favorite_class(code, expected_class)
            updated += 1

    return updated


def get_favorite_class(symbol: str, config: configparser.ConfigParser) -> Optional[str]:
    """
    Get the favorite class for a specific symbol.

    Args:
        symbol: Cryptocurrency symbol
        config: ConfigParser instance with loaded config.ini

    Returns:
        'A', 'B', 'C', or None if not a favorite
    """
    favorites_dict = get_favorites_from_config(config)
    symbol = symbol.upper()

    for cls, symbols in favorites_dict.items():
        if symbol in symbols:
            return cls

    return None  # type: ignore
