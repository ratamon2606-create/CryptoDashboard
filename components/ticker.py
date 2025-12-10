# components/ticker.py
import tkinter as tk
from config import COLORS, FONTS
from utils.ui_helpers import create_shadow_card

class CryptoCard(tk.Frame):
    """การ์ดเลือกเหรียญ (หน้า 1)"""
    def __init__(self, parent, symbol, select_callback):
        # สร้าง Frame เปล่าๆ เพื่อเป็น Wrapper ให้ Grid ทำงานได้ถูกต้อง
        super().__init__(parent, bg=COLORS["bg_main"]) 
        self.symbol = symbol
        self.selected = False
        self.callback = select_callback

        # ใช้ Helper สร้างการ์ดมีเงา
        self.container, self.content = create_shadow_card(self, padx=15, pady=15)
        self.container.pack(fill="both", expand=True)

        # ชื่อเหรียญ
        self.lbl_name = tk.Label(self.content, text=symbol.replace("USDT", ""), 
                                 font=FONTS["h2"], bg=COLORS["card_bg"], fg=COLORS["text_dark"])
        self.lbl_name.pack(pady=(5, 15))
        
        # ไอคอนติ๊กถูก (วงกลม)
        self.select_indicator = tk.Label(self.content, text="✓", font=FONTS["h2"],
                                         bg=COLORS["card_bg"], fg=COLORS["shadow"], bd=0)
        self.select_indicator.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")

        # Bind Event คลิก
        self.content.bind("<Button-1>", self.toggle_select)
        self.lbl_name.bind("<Button-1>", self.toggle_select)

    def toggle_select(self, event=None):
        success = self.callback(self.symbol, not self.selected)
        if success:
            self.selected = not self.selected
            if self.selected:
                # ถ้าเลือก: ไอคอนสีน้ำเงิน, กรอบสีน้ำเงิน
                self.select_indicator.config(fg=COLORS["accent_blue"])
                self.content.config(highlightbackground=COLORS["accent_blue"], highlightthickness=2)
            else:
                # ถ้าไม่เลือก: ไอคอนสีจาง, ไม่มีกรอบ
                self.select_indicator.config(fg=COLORS["shadow"])
                self.content.config(highlightthickness=0)

class PulseGraph(tk.Canvas):
    """กราฟชีพจร (หน้า 2)"""
    def __init__(self, parent, width=600, height=250):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_main"], highlightthickness=0)
        self.W = width
        self.H = height
        self.center_y = height / 2

    def draw_graph(self, coin_data_list):
        self.delete("all")
        # เส้น Baseline
        self.create_line(20, self.center_y, self.W - 20, self.center_y, 
                         fill=COLORS["text_light"], dash=(4, 4))
        
        if not coin_data_list: return
        
        num_points = len(coin_data_list)
        segment_width = (self.W - 100) / num_points
        start_x = 50
        coords = [(20, self.center_y)]
        
        for i, data in enumerate(coin_data_list):
            pct = float(data['priceChangePercent'])
            offset_y = -(pct * 5 * 2) # Scale graph
            target_y = max(30, min(self.H - 30, self.center_y + offset_y))
            x_pos = start_x + (i * segment_width) + (segment_width/2)
            
            # จุดสำหรับเส้นโค้ง
            coords.append((x_pos - 40, self.center_y))
            coords.append((x_pos, target_y))
            coords.append((x_pos + 40, self.center_y))

            # จุดวงกลมแสดงราคา
            color = COLORS["green"] if pct >= 0 else COLORS["red"]
            self.create_oval(x_pos-6, target_y-6, x_pos+6, target_y+6, fill=color, outline=COLORS["white"], width=2)
            
            # ตัวเลข %
            self.create_text(x_pos, target_y - 25 if pct >= 0 else target_y + 25, 
                             text=f"{pct:+.2f}%", fill=color, font=FONTS["body_bold"])
            # ชื่อเหรียญ
            self.create_text(x_pos, self.center_y + 30, 
                             text=data['symbol'].replace("USDT",""), fill=COLORS["text_light"], font=FONTS["small"])

        coords.append((self.W - 20, self.center_y))
        
        # วาดเส้นกราฟเรียบ (Smooth Line) สีน้ำตาล
        flat = [item for sublist in coords for item in sublist]
        self.create_line(flat, fill=COLORS["accent_brown"], width=3, smooth=True, capstyle="round")