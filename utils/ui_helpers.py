import tkinter as tk
from config import COLORS, SHADOW_OFFSET

def create_shadow_card(parent, **kwargs):
    """
    สร้าง Frame ที่มีเงาซ้อนด้านหลัง (แก้ไข Layout ให้แสดงผลถูกต้อง)
    """
    bg_color = kwargs.pop('bg', COLORS["card_bg"])
    padx = kwargs.pop('padx', 0)
    pady = kwargs.pop('pady', 0)
    
    # 1. Container หลัก (ใช้ Grid เพื่อให้ขยายตามเนื้อหาได้)
    container = tk.Frame(parent, bg=COLORS["bg_main"], **kwargs)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # 2. เลเยอร์เงา (อยู่ Row 0, Col 0 เหมือนกัน แต่ดัน Padding ซ้าย/บน)
    # ผลลัพธ์: เงาจะโผล่ออกมาทางขวาล่าง
    shadow = tk.Frame(container, bg=COLORS["shadow"])
    shadow.grid(row=0, column=0, sticky="nsew", 
                padx=(SHADOW_OFFSET, 0), pady=(SHADOW_OFFSET, 0))

    # 3. เลเยอร์การ์ด (อยู่ Row 0, Col 0 ทับเงา แต่ดัน Padding ขวา/ล่าง)
    # ผลลัพธ์: การ์ดจะอยู่เยื้องไปทางซ้ายบน เปิดช่องให้เงาโผล่
    card = tk.Frame(container, bg=bg_color)
    card.grid(row=0, column=0, sticky="nsew", 
              padx=(0, SHADOW_OFFSET), pady=(0, SHADOW_OFFSET))
    
    # 4. พื้นที่ใส่เนื้อหา (Content)
    content_frame = tk.Frame(card, bg=bg_color)
    content_frame.pack(fill="both", expand=True, padx=padx, pady=pady)

    # ยกการ์ดขึ้นมาอยู่เหนือเงาเสมอ
    card.tkraise()

    return container, content_frame