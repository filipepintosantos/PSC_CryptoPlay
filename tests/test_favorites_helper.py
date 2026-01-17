"""
Tests for favorites_helper module.
Tests configuration management and favorite classification updates.
"""

import unittest
import configparser
from unittest.mock import Mock, patch

from src.database import CryptoDatabase
from src.favorites_helper import (
    get_favorites_from_config,
    get_all_favorites_list,
    validate_and_update_favorites,
    get_favorite_class
)


class TestGetFavoritesFromConfig(unittest.TestCase):
    """Tests for get_favorites_from_config function."""
    
    def test_get_favorites_from_config_with_data(self):
        """Test getting favorites when config has data."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA,SOL')
        config.set('symbols', 'favorites_c', 'LINK,XRP')
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], ['BTC', 'ETH'])
        self.assertEqual(result['B'], ['ADA', 'SOL'])
        self.assertEqual(result['C'], ['LINK', 'XRP'])
    
    def test_get_favorites_from_config_empty(self):
        """Test getting favorites when config is empty."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], [])
        self.assertEqual(result['B'], [])
        self.assertEqual(result['C'], [])
    
    def test_get_favorites_from_config_uppercase_conversion(self):
        """Test that symbols are converted to uppercase."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'btc, eth, ada')
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], ['BTC', 'ETH', 'ADA'])
    
    def test_get_favorites_from_config_with_whitespace(self):
        """Test parsing with extra whitespace."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', '  BTC  ,  ETH  , ADA  ')
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], ['BTC', 'ETH', 'ADA'])
    
    def test_get_favorites_from_config_with_empty_values(self):
        """Test parsing with empty values in comma-separated list."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,,ETH,,ADA')
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], ['BTC', 'ETH', 'ADA'])
    
    def test_get_favorites_from_config_partial_config(self):
        """Test when only some favorite classes are configured."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC')
        # B and C not set
        
        result = get_favorites_from_config(config)
        
        self.assertEqual(result['A'], ['BTC'])
        self.assertEqual(result['B'], [])
        self.assertEqual(result['C'], [])


class TestGetAllFavoritesList(unittest.TestCase):
    """Tests for get_all_favorites_list function."""
    
    def test_get_all_favorites_list_combined(self):
        """Test getting all favorites as flat list."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA')
        config.set('symbols', 'favorites_c', 'SOL,LINK')
        
        result = get_all_favorites_list(config)
        
        self.assertEqual(len(result), 5)
        self.assertIn('BTC', result)
        self.assertIn('ETH', result)
        self.assertIn('ADA', result)
        self.assertIn('SOL', result)
        self.assertIn('LINK', result)
    
    def test_get_all_favorites_list_empty(self):
        """Test when no favorites are configured."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        
        result = get_all_favorites_list(config)
        
        self.assertEqual(result, [])
    
    def test_get_all_favorites_list_single_class(self):
        """Test when only one class has favorites."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH,ADA')
        
        result = get_all_favorites_list(config)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), {'BTC', 'ETH', 'ADA'})


class TestGetFavoriteClass(unittest.TestCase):
    """Tests for get_favorite_class function."""
    
    def test_get_favorite_class_found_in_a(self):
        """Test getting class for symbol in class A."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA')
        
        result = get_favorite_class('BTC', config)
        
        self.assertEqual(result, 'A')
    
    def test_get_favorite_class_found_in_b(self):
        """Test getting class for symbol in class B."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC')
        config.set('symbols', 'favorites_b', 'ADA,SOL')
        
        result = get_favorite_class('SOL', config)
        
        self.assertEqual(result, 'B')
    
    def test_get_favorite_class_found_in_c(self):
        """Test getting class for symbol in class C."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_c', 'LINK')
        
        result = get_favorite_class('LINK', config)
        
        self.assertEqual(result, 'C')
    
    def test_get_favorite_class_not_found(self):
        """Test getting class for non-favorite symbol."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC')
        
        result = get_favorite_class('INVALID', config)
        
        self.assertIsNone(result)
    
    def test_get_favorite_class_case_insensitive(self):
        """Test that symbol lookup is case-insensitive."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        
        # Test lowercase input
        result_lower = get_favorite_class('btc', config)
        self.assertEqual(result_lower, 'A')
        
        # Test mixed case
        result_mixed = get_favorite_class('EtH', config)
        self.assertEqual(result_mixed, 'A')
    
    def test_get_favorite_class_empty_config(self):
        """Test with empty config."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        
        result = get_favorite_class('BTC', config)
        
        self.assertIsNone(result)


class TestValidateAndUpdateFavorites(unittest.TestCase):
    """Tests for validate_and_update_favorites function."""
    
    def setUp(self):
        """Set up test database."""
        self.db = CryptoDatabase(":memory:")
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
    
    def test_validate_and_update_favorites_success(self):
        """Test updating favorites successfully."""
        # Add cryptos to database
        self.db.add_crypto_info('BTC', 'Bitcoin')
        self.db.add_crypto_info('ETH', 'Ethereum')
        self.db.add_crypto_info('ADA', 'Cardano')
        
        # Create config with favorites
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA')
        
        # Validate and update
        updated = validate_and_update_favorites(self.db, config)
        
        # Should update all 3
        self.assertEqual(updated, 3)
        
        # Verify updates
        btc_info = self.db.get_crypto_info('BTC')
        self.assertEqual(btc_info['favorite'], 'A')
        
        eth_info = self.db.get_crypto_info('ETH')
        self.assertEqual(eth_info['favorite'], 'A')
        
        ada_info = self.db.get_crypto_info('ADA')
        self.assertEqual(ada_info['favorite'], 'B')
    
    def test_validate_and_update_favorites_no_changes_needed(self):
        """Test when all favorites are already correct."""
        # Add crypto with correct favorite class
        self.db.add_crypto_info('BTC', 'Bitcoin', favorite='A')
        self.db.add_crypto_info('ETH', 'Ethereum', favorite='A')
        
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        
        updated = validate_and_update_favorites(self.db, config)
        
        # No updates needed (both already correct)
        self.assertEqual(updated, 0)
    
    def test_validate_and_update_favorites_partial_update(self):
        """Test updating some cryptos that already have correct class."""
        self.db.add_crypto_info('BTC', 'Bitcoin', favorite='A')
        self.db.add_crypto_info('ETH', 'Ethereum', favorite=None)
        self.db.add_crypto_info('ADA', 'Cardano', favorite='C')  # Wrong class
        
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA')
        
        updated = validate_and_update_favorites(self.db, config)
        
        # Should update 2 (ETH and ADA)
        self.assertEqual(updated, 2)
    
    def test_validate_and_update_favorites_remove_favorite(self):
        """Test removing favorite status from crypto."""
        self.db.add_crypto_info('BTC', 'Bitcoin', favorite='A')
        self.db.add_crypto_info('ETH', 'Ethereum', favorite='A')
        
        # Config only has BTC as favorite
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC')
        
        updated = validate_and_update_favorites(self.db, config)
        
        # Should update ETH (remove favorite)
        self.assertEqual(updated, 1)
        
        # Verify ETH is no longer favorite
        eth_info = self.db.get_crypto_info('ETH')
        self.assertIsNone(eth_info['favorite'])
    
    def test_validate_and_update_favorites_empty_database(self):
        """Test with empty database."""
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        
        # No cryptos in database
        updated = validate_and_update_favorites(self.db, config)
        
        self.assertEqual(updated, 0)
    
    def test_validate_and_update_favorites_empty_config(self):
        """Test with empty config."""
        self.db.add_crypto_info('BTC', 'Bitcoin', favorite='A')
        self.db.add_crypto_info('ETH', 'Ethereum', favorite='A')
        
        # Empty config
        config = configparser.ConfigParser()
        config.add_section('symbols')
        
        updated = validate_and_update_favorites(self.db, config)
        
        # Should remove favorites from both (update = 2)
        self.assertEqual(updated, 2)
    
    def test_validate_and_update_favorites_multiple_classes(self):
        """Test updating across multiple favorite classes."""
        for i, symbol in enumerate(['BTC', 'ETH', 'ADA', 'SOL', 'LINK']):
            self.db.add_crypto_info(symbol, f'Crypto{i}')
        
        config = configparser.ConfigParser()
        config.add_section('symbols')
        config.set('symbols', 'favorites_a', 'BTC,ETH')
        config.set('symbols', 'favorites_b', 'ADA,SOL')
        config.set('symbols', 'favorites_c', 'LINK')
        
        updated = validate_and_update_favorites(self.db, config)
        
        # All 5 should be updated
        self.assertEqual(updated, 5)
        
        # Verify classifications
        self.assertEqual(self.db.get_crypto_info('BTC')['favorite'], 'A')
        self.assertEqual(self.db.get_crypto_info('ADA')['favorite'], 'B')
        self.assertEqual(self.db.get_crypto_info('LINK')['favorite'], 'C')


class TestFavoritesHelperIntegration(unittest.TestCase):
    """Integration tests for favorites helper functions."""
    
    def setUp(self):
        """Set up test database and config."""
        self.db = CryptoDatabase(":memory:")
        self.config = configparser.ConfigParser()
        self.config.add_section('symbols')
        self.config.set('symbols', 'favorites_a', 'BTC,ETH')
        self.config.set('symbols', 'favorites_b', 'ADA')
        self.config.set('symbols', 'favorites_c', 'SOL')
    
    def tearDown(self):
        """Clean up."""
        self.db.close()
    
    def test_workflow_add_cryptos_and_classify(self):
        """Test complete workflow: add cryptos, then classify as favorites."""
        # Add cryptos
        for symbol in ['BTC', 'ETH', 'ADA', 'SOL', 'LINK']:
            self.db.add_crypto_info(symbol, f'Crypto: {symbol}')
        
        # Get all favorites from config
        all_favs = get_all_favorites_list(self.config)
        self.assertEqual(len(all_favs), 4)  # BTC, ETH, ADA, SOL
        
        # Validate and update
        updated = validate_and_update_favorites(self.db, self.config)
        # Only 4 should be updated (BTC, ETH, ADA, SOL) - LINK has no change (None to None)
        self.assertEqual(updated, 4)
        
        # Verify non-favorite crypto
        link_info = self.db.get_crypto_info('LINK')
        self.assertIsNone(link_info['favorite'])
        
        # Verify favorite cryptos
        for symbol in ['BTC', 'ETH', 'ADA', 'SOL']:
            fav_class = get_favorite_class(symbol, self.config)
            self.assertIsNotNone(fav_class)
            crypto_info = self.db.get_crypto_info(symbol)
            self.assertEqual(crypto_info['favorite'], fav_class)
    
    def test_config_override_existing_favorites(self):
        """Test that config can override existing favorite classifications."""
        # Add cryptos with initial favorites
        self.db.add_crypto_info('BTC', 'Bitcoin', favorite='B')
        self.db.add_crypto_info('ETH', 'Ethereum', favorite='C')
        self.db.add_crypto_info('ADA', 'Cardano', favorite=None)
        
        # Config says BTC should be A, ETH should be B, ADA should be B
        self.config.set('symbols', 'favorites_a', 'BTC')
        self.config.set('symbols', 'favorites_b', 'ETH,ADA')
        self.config.set('symbols', 'favorites_c', '')
        
        # Update
        updated = validate_and_update_favorites(self.db, self.config)
        self.assertEqual(updated, 3)
        
        # Verify overrides
        self.assertEqual(self.db.get_crypto_info('BTC')['favorite'], 'A')
        self.assertEqual(self.db.get_crypto_info('ETH')['favorite'], 'B')
        self.assertEqual(self.db.get_crypto_info('ADA')['favorite'], 'B')


if __name__ == "__main__":
    unittest.main()
