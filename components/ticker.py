# components/ticker.py
import tkinter as tk
import os
from PIL import Image, ImageTk 
from config import COLORS, FONTS
from utils.ui_helpers import create_shadow_card

# ... CryptoCard เหมือนเดิม ...
class CryptoCard(tk.Frame):
    def __init__(self, parent, symbol, select_callback):
        super().__init__(parent, bg=COLORS["bg_main"]) 
        self.symbol = symbol
        self.selected = False
        self.callback = select_callback

        self.container, self.content = create_shadow_card(self, padx=10, pady=10)
        self.container.pack(fill="both", expand=True)

        self.lbl_name = tk.Label(self.content, text=symbol.replace("USDT", ""), 
                                 font=FONTS["h2"], bg=COLORS["card_bg"], fg=COLORS["text_dark"])
        self.lbl_name.pack(pady=15)
        
        self.content.bind("<Button-1>", self.toggle_select)
        self.lbl_name.bind("<Button-1>", self.toggle_select)

    def toggle_select(self, event=None):
        success = self.callback(self.symbol, not self.selected)
        if success:
            self.selected = not self.selected
            if self.selected:
                self.content.config(highlightbackground=COLORS["accent_blue"], highlightthickness=3)
            else:
                self.content.config(highlightthickness=0)

# ... [EDITED] PulseGraph ...
class PulseGraph(tk.Canvas):
    """กราฟชีพจร (หน้า 2) แบบ Responsive"""
    def __init__(self, parent, width=600, height=250):
        # ลบ width=width ออกจากการเรียก super เพื่อให้มันจัดการเอง
        super().__init__(parent, height=height, bg=COLORS["bg_main"], highlightthickness=0)
        
        self.H = height
        self.center_y = height / 2 - 20 
        self.image_cache = {} 
        self.cached_data = [] # เก็บข้อมูลล่าสุดไว้ใช้วาดใหม่ตอน Resize

        # Bind event เมื่อขนาด Canvas เปลี่ยน (เช่น ย่อขยายจอ)
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """เมื่อขนาดเปลี่ยน ให้วาดกราฟใหม่ด้วยข้อมูลเดิม"""
        if self.cached_data:
            self.draw_graph(self.cached_data)

    def get_icon(self, symbol):
        # ... (โค้ดส่วน get_icon เหมือนเดิมเป๊ะ) ...
        clean_symbol = symbol.replace("USDT", "").upper()
        if clean_symbol in self.image_cache:
            return self.image_cache[clean_symbol]
        try:
            for ext in [".png", ".jpg", ".jpeg"]:
                file_path = f"{clean_symbol}{ext}"
                if os.path.exists(file_path):
                    forced_size = (50, 50) 
                    pil_img = Image.open(file_path).resize(forced_size, Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(pil_img)
                    self.image_cache[clean_symbol] = tk_img
                    return tk_img
        except Exception as e:
            print(f"Error loading icon: {e}")
        return None

    def draw_graph(self, coin_data_list):
        self.cached_data = coin_data_list # บันทึกข้อมูลไว้
        self.delete("all")

        # หาความกว้างจริง ณ ปัจจุบัน
        current_w = self.winfo_width()
        if current_w < 100: current_w = 950 # ค่า Default กันพลาดตอนเริ่มโปรแกรม

        self.create_line(20, self.center_y, current_w - 20, self.center_y, 
                         fill=COLORS["text_light"], dash=(4, 4))
        
        if not coin_data_list: return
        
        num_points = len(coin_data_list)
        # คำนวณระยะห่างใหม่ตามความกว้างหน้าจอจริง
        segment_width = (current_w - 100) / max(1, num_points - 1)
        start_x = 50
        
        coords = []
        for i, data in enumerate(coin_data_list):
            pct = float(data['priceChangePercent'])
            offset_y = -(pct * 3) 
            target_y = max(40, min(self.H - 80, self.center_y + offset_y))
            x_pos = start_x + (i * segment_width)
            coords.append((x_pos, target_y))

            symbol = data['symbol']
            icon = self.get_icon(symbol)

            if icon:
                self.create_image(x_pos, target_y, image=icon, anchor="center")
            else:
                color = COLORS["green"] if pct >= 0 else COLORS["red"]
                self.create_oval(x_pos-6, target_y-6, x_pos+6, target_y+6, 
                                 fill=color, outline=COLORS["white"], width=2)
            
            color = COLORS["green"] if pct >= 0 else COLORS["red"]
            self.create_text(x_pos, target_y - 35 if pct >= 0 else target_y + 40, 
                             text=f"{pct:+.2f}%", fill=color, font=FONTS["body_bold"])
            self.create_text(x_pos, self.H - 20, 
                             text=symbol.replace("USDT",""), 
                             fill=COLORS["text_light"], font=FONTS["body_bold"])

        if len(coords) > 1:
            flat_coords = [item for sublist in coords for item in sublist]
            line_id = self.create_line(flat_coords, fill=COLORS["accent_brown"], width=3, 
                                       smooth=True, splinesteps=50, capstyle="round")
            self.tag_lower(line_id)
