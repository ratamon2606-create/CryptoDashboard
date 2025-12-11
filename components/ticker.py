# components/ticker.py
import tkinter as tk
from config import COLORS, FONTS
from utils.ui_helpers import create_shadow_card

class CryptoCard(tk.Frame):
    def __init__(self, parent, symbol, select_callback):
        super().__init__(parent, bg=COLORS["bg_main"]) 
        self.symbol = symbol
        self.selected = False
        self.callback = select_callback

        # Wrapper สำหรับเงา
        self.container, self.content = create_shadow_card(self, padx=10, pady=10)
        self.container.pack(fill="both", expand=True)

        # ชื่อเหรียญ
        self.lbl_name = tk.Label(self.content, text=symbol.replace("USDT", ""), 
                                 font=FONTS["h2"], bg=COLORS["card_bg"], fg=COLORS["text_dark"])
        self.lbl_name.pack(pady=15)
        
        # เอาติ๊กถูกออกตามที่ขอ (ลบ self.select_indicator ทิ้ง)

        # Bind events
        self.content.bind("<Button-1>", self.toggle_select)
        self.lbl_name.bind("<Button-1>", self.toggle_select)

    def toggle_select(self, event=None):
        success = self.callback(self.symbol, not self.selected)
        if success:
            self.selected = not self.selected
            if self.selected:
                # เลือก: เปลี่ยนขอบของ content (ตัวบล็อกขาว) เป็นสีน้ำเงิน
                self.content.config(highlightbackground=COLORS["accent_blue"], highlightthickness=3)
            else:
                # ไม่เลือก: เอาขอบออก (หรือสีเดียวกับพื้นหลัง)
                self.content.config(highlightthickness=0)

class PulseGraph(tk.Canvas):
    def __init__(self, parent, width=600, height=250):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_main"], highlightthickness=0)
        self.W = width
        self.H = height
        self.center_y = height / 2 - 20 

    def draw_graph(self, coin_data_list):
        self.delete("all")
        self.create_line(20, self.center_y, self.W - 20, self.center_y, 
                         fill=COLORS["text_light"], dash=(4, 4))
        
        if not coin_data_list: return
        
        num_points = len(coin_data_list)
        segment_width = (self.W - 100) / max(1, num_points - 1)
        start_x = 50
        
        coords = []
        for i, data in enumerate(coin_data_list):
            pct = float(data['priceChangePercent'])
            offset_y = -(pct * 3) 
            target_y = max(40, min(self.H - 80, self.center_y + offset_y))
            x_pos = start_x + (i * segment_width)
            coords.append((x_pos, target_y))

            color = COLORS["green"] if pct >= 0 else COLORS["red"]
            self.create_oval(x_pos-6, target_y-6, x_pos+6, target_y+6, fill=color, outline=COLORS["white"], width=2)
            
            self.create_text(x_pos, target_y - 30 if pct >= 0 else target_y + 35, 
                             text=f"{pct:+.2f}%", fill=color, font=FONTS["body_bold"])
            
            self.create_text(x_pos, self.H - 20, 
                             text=data['symbol'].replace("USDT",""), 
                             fill=COLORS["text_light"], font=FONTS["body"])

        if len(coords) > 1:
            flat_coords = [item for sublist in coords for item in sublist]
            self.create_line(flat_coords, fill=COLORS["accent_brown"], width=3, 
                             smooth=True, splinesteps=50, capstyle="round")