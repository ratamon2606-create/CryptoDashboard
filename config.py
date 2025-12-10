# config.py

COINS_OPTIONS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]

# --- Costra Bakery Theme Palette ---
COLORS = {
    "bg_main": "#F8F4E3",       # ครีม (พื้นหลังแอพ)
    "card_bg": "#FFFFFF",       # ขาว (พื้นหลังการ์ด)
    "shadow": "#E0D8C0",        # เทาครีมจางๆ (สำหรับเงา)
    "text_dark": "#5A3E2B",     # น้ำตาลเข้ม (หัวข้อ)
    "text_light": "#8C7B6E",    # น้ำตาลอ่อน (รายละเอียด)
    "accent_blue": "#4A5C8C",   # น้ำเงิน (ปุ่มหลัก, ไอคอน)
    "accent_brown": "#A07855",  # น้ำตาลส้ม (กราฟ, ปุ่มรอง)
    
    # สีเขียว-แดง สำหรับราคา (คงเดิม)
    "green": "#6d9760",         
    "red": "#b84040",          
    "white": "#ffffff",
}

# --- Font Settings ---
# พยายามใช้ Helvetica ถ้าไม่มีระบบจะหาตัวอื่น
FONT_FAMILY = "Helvetica" 

FONTS = {
    "h1": (FONT_FAMILY, 24, "bold"),    # หัวข้อใหญ่
    "h2": (FONT_FAMILY, 18, "bold"),    # หัวข้อรอง
    "body": (FONT_FAMILY, 12),          # เนื้อหาทั่วไป
    "body_bold": (FONT_FAMILY, 12, "bold"),
    "small": (FONT_FAMILY, 10),         # ตัวเล็ก
    "monospace": ("Consolas", 10),      # สำหรับตัวเลข Orderbook
}

SHADOW_OFFSET = 4  # ระยะห่างของเงา