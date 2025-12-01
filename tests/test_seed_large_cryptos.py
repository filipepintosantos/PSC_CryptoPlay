"""Compatibility shim for environments without pytest installed.

This module used to contain a pytest-style test. The project also includes a
unittest-based test `test_seed_large_cryptos_unittest.py`. Keep a trivial test
here to ensure unittest discovery can import the module without pytest.
"""


def test_smoke():
    # Trivial smoke test — real tests are in the unittest file.
    assert True
