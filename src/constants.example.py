# Copy this file to constants.py and add your keys, or set FRED_API_KEY and BLS_API_KEY
# in your environment (recommended for security).
import os

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
BLS_API_KEY = os.environ.get("BLS_API_KEY", "")
