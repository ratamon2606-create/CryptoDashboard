# components/trades.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import COLORS, FONTS

class TradeFeedPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["card_bg"])
        
        tk.Label(self, text="RECENT TRADES", bg=COLORS["card_bg"], fg=COLORS["text_dark"], 
                 font=FONTS["body_bold"]).pack(fill="x", pady=(0, 10), anchor="w")
        
        self.tree = ttk.Treeview(self, columns=("p","q","t"), show="headings", height=8)
        self.tree.heading("p", text="Price"); self.tree.column("p", width=80)
        self.tree.heading("q", text="Qty"); self.tree.column("q", width=80)
        self.tree.heading("t", text="Time"); self.tree.column("t", width=60)
        
        # Style ตกแต่ง Treeview
        style = ttk.Style()
        style.theme_use("clam")
        
        # หัวตาราง: สีน้ำตาลอ่อน ตัวหนังสือขาว
        style.configure("Treeview.Heading", background=COLORS["text_light"], 
                        foreground=COLORS["white"], font=FONTS["small"], relief="flat")
        
        # เนื้อหา: พื้นขาว ตัวหนังสือเข้ม
        style.configure("Treeview", background=COLORS["card_bg"], 
                        foreground=COLORS["text_dark"], fieldbackground=COLORS["card_bg"], 
                        font=FONTS["monospace"], borderwidth=0, rowheight=25)
        
        # ปิดสีตอนเลือกบรรทัด
        style.map("Treeview", background=[('selected', COLORS["bg_main"])], 
                  foreground=[('selected', COLORS["text_dark"])])
        
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("buy", foreground=COLORS["green"])
        self.tree.tag_configure("sell", foreground=COLORS["red"])

    def add(self, p, q, is_sell):
        time_str = datetime.now().strftime("%H:%M:%S")
        tag = "sell" if is_sell else "buy"
        self.tree.insert("", 0, values=(f"{float(p):.2f}", f"{float(q):.5f}", time_str), tags=(tag,))
        if len(self.tree.get_children()) > 15:
            self.tree.delete(self.tree.get_children()[-1])