# config.py

COINS_OPTIONS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT"]

COLORS = {
    "bg_main": "#F8F4E3",       
    "card_bg": "#FFFFFF",       
    "shadow": "#E0D8C0",        
    "text_dark": "#5A3E2B",     
    "text_light": "#8C7B6E",    
    "accent_blue": "#4A5C8C",   
    "accent_brown": "#A07855",  
    "active_bg": "#D0E0F0",     # <--- (ใหม่) สีฟ้าอ่อนสำหรับเมนูที่เลือกอยู่
    
    "green": "#6d9760",         
    "red": "#b84040",          
    "white": "#ffffff",
}

FONT_FAMILY = "Helvetica" 
FONTS = {
    "h1": (FONT_FAMILY, 24, "bold"),
    "h2": (FONT_FAMILY, 18, "bold"),
    "body": (FONT_FAMILY, 12),
    "body_bold": (FONT_FAMILY, 12, "bold"),
    "small": (FONT_FAMILY, 10),
    "monospace": ("Consolas", 10), # ใช้ Consolas เพื่อให้ตัวเลข Orderbook ตรงกัน
}

SHADOW_OFFSET = 4
TIMEFRAMES = ["15m", "1h", "4h", "1d"] # ตัวเลือก Timeframe