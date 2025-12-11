# main.py
import tkinter as tk
import threading
import json
import websocket
from datetime import datetime

from config import COLORS, COINS_OPTIONS, FONTS, TIMEFRAMES
from utils.binance_api import get_binance_ticker, get_klines
from utils.ui_helpers import create_shadow_card
from components.ticker import CryptoCard, PulseGraph
from components.orderbook import OrderBookPanel
from components.trades import TradeFeedPanel
from components.technical import ChartPanel

SELECTED_COINS = []

# --- Helper Component: Header ---
class Header(tk.Frame):
    def __init__(self, parent, title="", show_time=True):
        super().__init__(parent, bg=COLORS["bg_main"])
        if title:
            tk.Label(self, text=title, font=FONTS["h1"], 
                     bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(side="left", anchor="center")
        if show_time:
            self.time_lbl = tk.Label(self, text="00:00", font=FONTS["body"], 
                                     bg=COLORS["bg_main"], fg=COLORS["text_light"])
            self.time_lbl.pack(side="right", padx=10)
            self.date_lbl = tk.Label(self, text="Date", font=FONTS["body"], 
                                     bg=COLORS["bg_main"], fg=COLORS["text_light"])
            self.date_lbl.pack(side="right", padx=10)
            self.update_timer()

    def update_timer(self):
        now = datetime.now()
        self.time_lbl.config(text=now.strftime("%H:%M:%S"))
        self.date_lbl.config(text=now.strftime("%d %b %Y"))
        self.after(1000, self.update_timer)

# --- PAGE 1: SELECTION (จัดกลางจอ) ---
class SelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        
        # ใช้ container กลางจอ
        center_box = tk.Frame(self, bg=COLORS["bg_main"])
        center_box.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(center_box, text="Select your coins", font=FONTS["h1"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=(0, 5))
        
        tk.Label(center_box, text="Select at least 3 coins to proceed", font=FONTS["body"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_light"]).pack(pady=(0, 30))
        
        grid = tk.Frame(center_box, bg=COLORS["bg_main"])
        grid.pack()
        
        self.cards = []
        for i, coin in enumerate(COINS_OPTIONS):
            row = i // 4
            col = i % 4
            card_wrap = tk.Frame(grid, bg=COLORS["bg_main"])
            card_wrap.grid(row=row, column=col, padx=10, pady=10)
            
            card = CryptoCard(card_wrap, coin, self.on_select)
            card.pack()
            self.cards.append(card)

        self.btn_next = tk.Button(center_box, text="NEXT >", font=FONTS["body_bold"], 
                                  bg=COLORS["shadow"], fg=COLORS["text_light"], 
                                  state="disabled", bd=0, padx=40, pady=12,
                                  command=lambda: controller.show_home_page(), cursor="hand2")
        self.btn_next.pack(pady=40)

    def on_select(self, symbol, is_selecting):
        global SELECTED_COINS
        if is_selecting:
            if symbol not in SELECTED_COINS: SELECTED_COINS.append(symbol)
        else:
            if symbol in SELECTED_COINS: SELECTED_COINS.remove(symbol)
            
        if len(SELECTED_COINS) >= 3:
            self.btn_next.config(state="normal", bg=COLORS["accent_blue"], fg=COLORS["white"])
            self.btn_next.config(text=f"CREATE PORTFOLIO ({len(SELECTED_COINS)}) >")
        else:
            self.btn_next.config(state="disabled", bg=COLORS["shadow"], fg=COLORS["text_light"])
            self.btn_next.config(text=f"Select {3 - len(SELECTED_COINS)} more")
        return True

# --- PAGE 2: HOME (มีแถบสรุป Portfolio) ---
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        
        # Header
        h = Header(self, show_time=True)
        h.pack(fill="x", padx=40, pady=(30, 10))

        tk.Label(self, text="Portfolio Overview", font=FONTS["h1"], 
                 fg=COLORS["text_dark"], bg=COLORS["bg_main"]).pack(pady=(10, 20), anchor="center")
        
        # Graph
        self.graph = PulseGraph(self, width=900, height=350)
        self.graph.pack(pady=10)
        
        # Last Update (เอาลงมาต่ำๆ)
        self.status_lbl = tk.Label(self, text="Loading data...", font=FONTS["small"], 
                                   bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.status_lbl.pack(side="bottom", pady=(5, 30))

        # Portfolio Bar (แถบสรุปสถานะ)
        self.bar_portfolio = tk.Label(self, text="ANALYZING PORTFOLIO...", font=FONTS["h2"],
                                      bg=COLORS["shadow"], fg=COLORS["text_light"], height=2)
        self.bar_portfolio.pack(side="bottom", pady=(0, 30))

        threading.Thread(target=self.load_data, daemon=True).start()

    def load_data(self):
        data_list = []
        total_change = 0
        
        for symbol in SELECTED_COINS:
            ticker = get_binance_ticker(symbol)
            if ticker: 
                data_list.append(ticker)
                total_change += float(ticker['priceChangePercent'])
        
        # Logic สรุปสถานะพอร์ต
        if data_list:
            avg_change = total_change / len(data_list)
            if avg_change >= 0:
                msg = f"YOUR PORTFOLIO LOOKS GOOD (+{avg_change:.2f}%)"
                color_bg = COLORS["accent_brown"]
            else:
                msg = f"YOUR PORTFOLIO LOOKS BAD ({avg_change:.2f}%)"
                color_bg = COLORS["text_dark"] # หรือสีเทาเข้ม
            
            self.after(0, lambda: self.bar_portfolio.config(text=msg, bg=color_bg, fg=COLORS["white"]))
        
        self.after(0, lambda: self.graph.draw_graph(data_list))
        self.after(0, lambda: self.status_lbl.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}"))

# --- PAGE 3: DETAILS (มี Toggle + 24h Data) ---
class ProDetailPage(tk.Frame):
    def __init__(self, parent, symbol):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.symbol = symbol.lower()
        self.symbol_upper = symbol.upper()
        self.is_running = True
        self.current_interval = "1h"
        
        # Header
        h = Header(self, show_time=True)
        h.pack(fill="x", padx=30, pady=(20, 0))

        # --- Top Section: Symbol & Price & 24h Data ---
        top = tk.Frame(self, bg=COLORS["bg_main"])
        top.pack(fill="x", padx=30, pady=15)
        
        # Left: Name & Timeframe
        left_top = tk.Frame(top, bg=COLORS["bg_main"])
        left_top.pack(side="left")
        
        tk.Label(left_top, text=self.symbol_upper, font=FONTS["h1"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(anchor="w")

        tf_frame = tk.Frame(left_top, bg=COLORS["bg_main"])
        tf_frame.pack(anchor="w", pady=5)
        self.tf_buttons = {}
        for tf in TIMEFRAMES:
            btn = tk.Button(tf_frame, text=tf, font=FONTS["small"], bd=0, 
                            cursor="hand2", padx=8, pady=0,
                            command=lambda t=tf: self.change_timeframe(t))
            btn.pack(side="left", padx=2)
            self.tf_buttons[tf] = btn
        self.update_tf_buttons()

        # Right: Price & 24h Stats
        right_top = tk.Frame(top, bg=COLORS["bg_main"])
        right_top.pack(side="right")
        
        # Price Box
        price_box = tk.Frame(right_top, bg=COLORS["text_dark"], padx=15, pady=5)
        price_box.pack(anchor="e")
        self.lbl_price = tk.Label(price_box, text="---", font=FONTS["h2"], 
                                  bg=COLORS["text_dark"], fg=COLORS["bg_main"])
        self.lbl_price.pack()
        
        # 24h Stats (Volume, High, Low)
        stats_frame = tk.Frame(right_top, bg=COLORS["bg_main"])
        stats_frame.pack(anchor="e", pady=5)
        
        self.lbl_stats = tk.Label(stats_frame, text="Vol: - | H: - | L: -", 
                                  font=FONTS["small"], bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.lbl_stats.pack()

        # --- Toggle Buttons (อยู่เหนือ Content) ---
        toggle_bar = tk.Frame(self, bg=COLORS["bg_main"])
        toggle_bar.pack(fill="x", padx=30, pady=(0, 10))
        
        self.var_book = tk.BooleanVar(value=True)
        self.var_trade = tk.BooleanVar(value=True)
        
        # สร้าง Checkbutton แบบเรียบๆ
        for text, var in [("Show Order Book", self.var_book), ("Show Trades", self.var_trade)]:
            cb = tk.Checkbutton(toggle_bar, text=text, variable=var, command=self.update_layout,
                                bg=COLORS["bg_main"], fg=COLORS["text_dark"], 
                                activebackground=COLORS["bg_main"], selectcolor=COLORS["bg_main"],
                                font=FONTS["body"])
            cb.pack(side="left", padx=10)

        # --- Content Grid ---
        self.content = tk.Frame(self, bg=COLORS["bg_main"])
        self.content.pack(fill="both", expand=True, padx=30, pady=10)
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=1)

        # Chart
        self.chart_wrap, self.chart_inner = create_shadow_card(self.content, padx=5, pady=5)
        self.chart_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        self.chart_panel = ChartPanel(self.chart_inner)
        self.chart_panel.pack(fill="both", expand=True)

        # Side Panel (OrderBook + Trades)
        self.side_panel = tk.Frame(self.content, bg=COLORS["bg_main"])
        self.side_panel.grid(row=0, column=1, sticky="nsew", pady=10)
        
        self.book_wrap, self.book_inner = create_shadow_card(self.side_panel, padx=5, pady=5)
        self.book_panel = OrderBookPanel(self.book_inner)
        
        self.trade_wrap, self.trade_inner = create_shadow_card(self.side_panel, padx=5, pady=5)
        self.trade_panel = TradeFeedPanel(self.trade_inner)
        
        self.update_layout() # เรียกครั้งแรกเพื่อจัดวาง

        threading.Thread(target=self.fetch_chart, daemon=True).start()
        threading.Thread(target=self.start_ws, daemon=True).start()
        threading.Thread(target=self.update_24h_stats, daemon=True).start() # Thread ใหม่สำหรับดึง stats

    def update_layout(self):
        # ล้าง Grid เก่าออกก่อน
        self.book_wrap.pack_forget()
        self.trade_wrap.pack_forget()
        
        # ตรวจสอบตัวแปรแล้ว pack ใหม่
        if self.var_book.get():
            self.book_wrap.pack(fill="both", expand=True, pady=(0, 10))
            self.book_panel.pack(fill="both", expand=True)
            
        if self.var_trade.get():
            self.trade_wrap.pack(fill="both", expand=True)
            self.trade_panel.pack(fill="both", expand=True)

    def change_timeframe(self, tf):
        if self.current_interval == tf: return
        self.current_interval = tf
        self.update_tf_buttons()
        threading.Thread(target=self.fetch_chart, daemon=True).start()

    def update_tf_buttons(self):
        for tf, btn in self.tf_buttons.items():
            if tf == self.current_interval:
                btn.config(bg=COLORS["text_dark"], fg=COLORS["white"])
            else:
                btn.config(bg=COLORS["bg_main"], fg=COLORS["text_dark"])

    def fetch_chart(self):
        klines = get_klines(self.symbol_upper, self.current_interval)
        self.after(0, lambda: self.chart_panel.draw_chart(klines))
    
    def update_24h_stats(self):
        # ดึงข้อมูล High/Low/Vol ทุกๆ 5 วินาที
        while self.is_running:
            ticker = get_binance_ticker(self.symbol_upper)
            if ticker:
                vol = float(ticker['volume'])
                high = float(ticker['highPrice'])
                low = float(ticker['lowPrice'])
                text = f"Vol: {vol:,.0f} | High: {high:,.2f} | Low: {low:,.2f}"
                self.after(0, lambda: self.lbl_stats.config(text=text))
            import time
            time.sleep(5)

    def start_ws(self):
        def on_message(ws, message):
            if not self.is_running: ws.close(); return
            try:
                response = json.loads(message)
                data = response.get('data', response)
                self.after(0, lambda: self.process_ws_data(data))     
            except Exception as e:
                print(f"WS Parsing Error: {e}")

        stream_names = f"{self.symbol}@trade/{self.symbol}@depth5@100ms"
        url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
        ws = websocket.WebSocketApp(url, on_message=on_message)
        ws.run_forever()

    def process_ws_data(self, data):
        try:
            if 'p' in data: 
                price = float(data['p'])
                self.lbl_price.config(text=f"{price:,.2f}")
                # เช็คก่อนว่า Trade Panel แสดงอยู่หรือไม่
                if self.var_trade.get() and hasattr(self, 'trade_panel'):
                    self.trade_panel.add(data['p'], data['q'], data['m']) 

            bids = data.get('bids') or data.get('b')
            asks = data.get('asks') or data.get('a')
            if bids and asks:
                # เช็คก่อนว่า Book Panel แสดงอยู่หรือไม่
                if self.var_book.get() and hasattr(self, 'book_panel'):
                    self.book_panel.update_data(bids, asks)
        except: pass

    def destroy(self):
        self.is_running = False
        super().destroy()

# --- MAIN APP (เหมือนเดิม แต่ตรวจสอบ Sidebar) ---
class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Costra Bakery Crypto")
        self.geometry("1200x800")
        self.configure(bg=COLORS["bg_main"])
        
        self.sidebar = tk.Frame(self, bg=COLORS["card_bg"], width=90)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.container = tk.Frame(self, bg=COLORS["bg_main"])
        self.container.pack(side="right", fill="both", expand=True)
        
        self.current_frame = None
        self.current_coin_symbol = None 
        
        self.show_selection_page()

    def update_sidebar(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        
        is_home = isinstance(self.current_frame, HomePage)
        bg_home = COLORS["active_bg"] if is_home else COLORS["card_bg"]
        
        btn_home = tk.Button(self.sidebar, text="🏠", font=("Arial", 20), 
                             bg=bg_home, fg=COLORS["accent_blue"], bd=0, 
                             command=self.show_home_page, cursor="hand2")
        btn_home.pack(fill="x", pady=(30, 20), ipady=10)
        
        tk.Frame(self.sidebar, height=1, bg=COLORS["shadow"]).pack(fill="x", padx=15)
        
        scroll_frame = tk.Frame(self.sidebar, bg=COLORS["card_bg"])
        scroll_frame.pack(fill="both", expand=True, pady=10)
        
        for coin in SELECTED_COINS:
            short = coin.replace("USDT","")
            is_active = self.current_coin_symbol == coin
            bg_coin = COLORS["active_bg"] if is_active else COLORS["card_bg"]
            
            tk.Button(scroll_frame, text=short, font=FONTS["body_bold"], 
                      bg=bg_coin, fg=COLORS["text_dark"], bd=0,
                      command=lambda c=coin: self.show_detail_page(c), 
                      cursor="hand2", pady=15).pack(fill="x", pady=2)

        btn_change = tk.Button(self.sidebar, text="✎ Coins", font=FONTS["body"], 
                               bg=COLORS["accent_brown"], fg=COLORS["white"], bd=0,
                               command=self.show_selection_page, cursor="hand2")
        btn_change.pack(side="bottom", fill="x", pady=20, padx=10, ipady=5)

    def show_selection_page(self):
        self.sidebar.pack_forget()
        if self.current_frame: self.current_frame.destroy()
        global SELECTED_COINS
        SELECTED_COINS = [] 
        self.current_coin_symbol = None
        self.current_frame = SelectionPage(self.container, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_home_page(self):
        self.current_coin_symbol = None
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = HomePage(self.container, self)
        self.current_frame.pack(fill="both", expand=True)
        self.sidebar.pack(side="left", fill="y")
        self.update_sidebar()

    def show_detail_page(self, symbol):
        self.current_coin_symbol = symbol
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = ProDetailPage(self.container, symbol)
        self.current_frame.pack(fill="both", expand=True)
        self.update_sidebar()

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()