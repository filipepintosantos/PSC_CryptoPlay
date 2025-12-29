"""Ensure test DB files are removed after the test suite finishes.

This module registers an atexit handler so that any leftover test databases
matching `data/test*.db` are removed when the test process exits.
"""
import atexit
import glob
import os


def _cleanup_test_dbs(pattern='data/test*.db'):
    files = glob.glob(pattern)
    for f in files:
        try:
            os.remove(f)
            # Avoid printing during normal test runs to keep output clean
        except Exception:
            pass


atexit.register(_cleanup_test_dbs)
