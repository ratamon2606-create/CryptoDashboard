# components/technical.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import COLORS

class ChartPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["card_bg"])
        
        # สร้างกราฟ พื้นหลังขาว
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=COLORS["card_bg"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS["card_bg"])
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # ปรับแต่งแกน (ซ่อนเส้นบน/ขวา, สีเส้นแกนเป็นน้ำตาลอ่อน)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color(COLORS["text_light"])
        self.ax.spines['left'].set_color(COLORS["text_light"])
        self.ax.tick_params(axis='x', colors=COLORS["text_light"])
        self.ax.tick_params(axis='y', colors=COLORS["text_light"])

    def draw_chart(self, klines):
        self.ax.clear()
        
        # ต้องเซ็ตค่า Theme ใหม่ทุกครั้งหลัง clear
        self.ax.set_facecolor(COLORS["card_bg"])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color(COLORS["text_light"])
        self.ax.spines['left'].set_color(COLORS["text_light"])
        self.ax.tick_params(axis='x', colors=COLORS["text_light"])
        self.ax.tick_params(axis='y', colors=COLORS["text_light"])

        if not klines: return
        
        opens = [float(x[1]) for x in klines]
        highs = [float(x[2]) for x in klines]
        lows = [float(x[3]) for x in klines]
        closes = [float(x[4]) for x in klines]
        
        for i in range(len(klines)):
            color = COLORS["green"] if closes[i] >= opens[i] else COLORS["red"]
            # ไส้เทียน
            self.ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1)
            # ตัวเทียน
            self.ax.bar(i, abs(closes[i]-opens[i]), bottom=min(opens[i], closes[i]), 
                        color=color, width=0.6)
            
        self.canvas.draw()