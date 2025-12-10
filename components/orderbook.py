# components/orderbook.py
import tkinter as tk
from config import COLORS, FONTS

class OrderBookPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["card_bg"])
        
        # หัวข้อ
        tk.Label(self, text="ORDER BOOK", bg=COLORS["card_bg"], fg=COLORS["text_dark"], 
                 font=FONTS["body_bold"]).pack(fill="x", pady=(0, 10), anchor="w")
        
        # --- จัดลำดับใหม่: Asks (ขาย-แดง) อยู่บน, Bids (ซื้อ-เขียว) อยู่ล่าง ---
        
        # Frame สำหรับ Asks (Red - Top)
        self.asks_frame = tk.Frame(self, bg=COLORS["card_bg"])
        self.asks_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Frame สำหรับ Bids (Green - Bottom)
        self.bids_frame = tk.Frame(self, bg=COLORS["card_bg"])
        self.bids_frame.pack(fill="both", expand=True)
        
        self.ask_lbls, self.bid_lbls = [], []
        
        def create_row(parent_frame):
            row = tk.Frame(parent_frame, bg=COLORS["card_bg"])
            row.pack(fill="x")
            # ปรับ Font เป็น monospace เพื่อให้ตัวเลขตรงกันสวยงาม
            p = tk.Label(row, text="-", width=10, anchor="w", bg=COLORS["card_bg"], font=FONTS["monospace"])
            q = tk.Label(row, text="-", width=10, anchor="e", fg=COLORS["text_dark"], bg=COLORS["card_bg"], font=FONTS["monospace"])
            p.pack(side="left"); q.pack(side="right")
            return p, q

        # สร้างแถวสำหรับ Asks (5 แถว)
        for _ in range(5):
            p, q = create_row(self.asks_frame)
            p.config(fg=COLORS["red"])
            self.ask_lbls.append((p, q))
            
        # สร้างแถวสำหรับ Bids (5 แถว)
        for _ in range(5):
            p, q = create_row(self.bids_frame)
            p.config(fg=COLORS["green"])
            self.bid_lbls.append((p, q))

    # เปลี่ยนชื่อจาก update เป็น update_data เพื่อไม่ให้ชนกับคำสั่งของ Tkinter
    def update_data(self, bids, asks):
        # Bids (ซื้อ - เขียว)
        for i, (price_lbl, qty_lbl) in enumerate(self.bid_lbls):
            if i < len(bids):
                price_lbl.config(text=f"{float(bids[i][0]):.2f}")
                qty_lbl.config(text=f"{float(bids[i][1]):.5f}")
            else:
                price_lbl.config(text="-")
                qty_lbl.config(text="-")
        
        # Asks (ขาย - แดง)
        # ต้องเรียงย้อนกลับ เพื่อให้ราคาต่ำสุด (Best Ask) อยู่ล่างสุดติดกับ Bids
        for i, (price_lbl, qty_lbl) in enumerate(self.ask_lbls):
            if i < len(asks):
                idx = len(asks) - 1 - i # กลับด้าน index
                if idx >= 0:
                    price_lbl.config(text=f"{float(asks[idx][0]):.2f}")
                    qty_lbl.config(text=f"{float(asks[idx][1]):.5f}")
                else:
                    price_lbl.config(text="-")
                    qty_lbl.config(text="-")
            else:
                price_lbl.config(text="-")
                qty_lbl.config(text="-")