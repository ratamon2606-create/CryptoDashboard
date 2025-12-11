# utils/binance_api.py
import requests

def get_binance_ticker(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        return requests.get(url, timeout=3).json()
    except:
        return None

def get_klines(symbol, interval="1h"): # <--- เพิ่ม parameter interval
    try:
        # ดึงมา 40 แท่งเพื่อให้กราฟดูเต็มขึ้น
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=40"
        data = requests.get(url, timeout=3).json()
        return data 
    except:
        return []