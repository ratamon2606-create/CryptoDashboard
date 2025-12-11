# components/technical.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import COLORS

class ChartPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["card_bg"])
        
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=COLORS["card_bg"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS["card_bg"])
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color(COLORS["text_light"])
        self.ax.spines['left'].set_color(COLORS["text_light"])
        self.ax.tick_params(axis='x', colors=COLORS["text_light"])
        self.ax.tick_params(axis='y', colors=COLORS["text_light"])

    def draw_chart(self, klines):
        self.ax.clear()
        
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
        
        # วาดแท่งเทียน
        for i in range(len(klines)):
            color = COLORS["green"] if closes[i] >= opens[i] else COLORS["red"]
            self.ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1)
            self.ax.bar(i, abs(closes[i]-opens[i]), bottom=min(opens[i], closes[i]), 
                        color=color, width=0.6)

        # [NEW] คำนวณและวาด Moving Averages (MA)
        # MA 7 (เส้นสีส้ม/เหลือง)
        if len(closes) >= 7:
            ma7 = [sum(closes[i-7:i])/7 for i in range(7, len(closes)+1)]
            # plot เริ่มที่ index 6 (เพราะต้องรอครบ 7 แท่งแรก)
            self.ax.plot(range(6, len(closes)), ma7, color= COLORS["active_bg"], linewidth=1.5, label="MA7")

        # MA 25 (เส้นสีม่วง)
        if len(closes) >= 25:
            ma25 = [sum(closes[i-25:i])/25 for i in range(25, len(closes)+1)]
            self.ax.plot(range(24, len(closes)), ma25, color= COLORS["accent_blue"], linewidth=1.5, label="MA25")

        # แสดง Legend (คำอธิบายเส้น) ตัวเล็กๆ มุมซ้ายบน
        self.ax.legend(loc='upper left', fontsize='x-small', frameon=False, labelcolor=COLORS["text_light"])
            
        self.canvas.draw()