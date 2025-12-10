# utils/binance_api.py
import requests

def get_binance_ticker(symbol):
    """ดึงราคา 24hr แบบ REST API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        return requests.get(url, timeout=3).json()
    except:
        return None

def get_klines(symbol):
    """ดึงข้อมูลแท่งเทียนย้อนหลัง 1h จำนวน 24 แท่ง"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=24"
        data = requests.get(url, timeout=3).json()
        return data # [time, open, high, low, close, ...]
    except:
        return []