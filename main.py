import tkinter as tk
import threading
import json
import websocket
import os
from PIL import Image, ImageTk
from datetime import datetime

from config import COLORS, COINS_OPTIONS, FONTS, TIMEFRAMES
from utils.binance_api import get_binance_ticker, get_klines
from utils.ui_helpers import create_shadow_card
from components.ticker import CryptoCard, PulseGraph
from components.orderbook import OrderBookPanel
from components.trades import TradeFeedPanel
from components.technical import ChartPanel

SELECTED_COINS = []

# --- Header ---
class Header(tk.Frame):
    def __init__(self, parent, title="", show_time=True):
        super().__init__(parent, bg=COLORS["bg_main"])
        
        if title:
            tk.Label(self, text=title, font=FONTS["h1"], 
                     bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(side="left", anchor="center")

        if show_time:
            self.dt_lbl = tk.Label(self, text="Date | Time", font=FONTS["body"], 
                                     bg=COLORS["bg_main"], fg=COLORS["text_light"])
            self.dt_lbl.pack(side="right", padx=10)
            self.update_timer()

    def update_timer(self):
        now = datetime.now()
        dt_str = f"{now.strftime('%d %b %Y')}     |     {now.strftime('%H:%M:%S')}"
        self.dt_lbl.config(text=dt_str)
        self.after(1000, self.update_timer)

# --- PAGE 1: SELECTION ---
class SelectionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        
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

# --- PAGE 2: HOME ---
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        
        # 1. Header (ติดบนสุดเหมือนเดิม)
        h = Header(self, show_time=True)
        h.pack(fill="x", padx=40, pady=(50, 5))

        # ============================================================
        # [NEW] Center Wrapper: สร้างกล่องเปล่าๆ มาหุ้มเนื้อหาตรงกลาง
        # expand=True จะดันให้กล่องนี้ลอยอยู่กึ่งกลางพื้นที่ว่าง
        # ============================================================
        self.center_wrapper = tk.Frame(self, bg=COLORS["bg_main"])
        self.center_wrapper.pack(expand=True, fill="both")

        # 2. Title (ใส่ใน center_wrapper)
        tk.Label(self.center_wrapper, text="Portfolio Overview", font=FONTS["h1"], 
                 fg=COLORS["text_dark"], bg=COLORS["bg_main"]).pack(pady=(50, 15), anchor="center")
        
        # 3. Graph (ใส่ใน center_wrapper)
        # height=380 กำลังดี ไม่ยาวเกินไปจนตกจอ
        self.graph = PulseGraph(self.center_wrapper, width=950, height=380) 
        self.graph.pack(pady=(0, 15))
        
        # 4. Stats Container (ใส่ใน center_wrapper)
        self.stats_container = tk.Frame(self.center_wrapper, bg=COLORS["bg_main"])
        self.stats_container.pack(fill="x", padx=40, pady=(15, 0)) 
        
        self.stats_container.columnconfigure(0, weight=1)
        self.stats_container.columnconfigure(1, weight=1)
        self.stats_container.columnconfigure(2, weight=1)

        # Box 1: Top Gainer
        wrap1, inner1 = create_shadow_card(self.stats_container, padx=15, pady=10)
        wrap1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tk.Label(inner1, text="Top Performer", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_light"]).pack()
        self.lbl_top_gainer = tk.Label(inner1, text="-", font=FONTS["h2"], bg=COLORS["card_bg"], fg=COLORS["green"])
        self.lbl_top_gainer.pack()

        # Box 2: Overview
        wrap2, inner2 = create_shadow_card(self.stats_container, padx=15, pady=10)
        wrap2.grid(row=0, column=1, sticky="ew", padx=10)
        self.status_inner = inner2 
        self.lbl_overview = tk.Label(inner2, text="Overview", font=FONTS["small"],
                                     bg=COLORS["card_bg"], fg=COLORS["text_light"])
        self.lbl_overview.pack()
        self.lbl_portfolio = tk.Label(inner2, text="ANALYZING...", font=FONTS["h2"],
                                      bg=COLORS["card_bg"], fg=COLORS["text_dark"])
        self.lbl_portfolio.pack()

        # Box 3: Worst Performer
        wrap3, inner3 = create_shadow_card(self.stats_container, padx=15, pady=10)
        wrap3.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        tk.Label(inner3, text="Worst Performer", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_light"]).pack()
        self.lbl_worst_loser = tk.Label(inner3, text="-", font=FONTS["h2"], bg=COLORS["card_bg"], fg=COLORS["red"])
        self.lbl_worst_loser.pack()

        # 5. Footer (ติดล่างสุดเหมือนเดิม)
        self.lbl_last_update = tk.Label(self, text="Loading data...", font=FONTS["small"], 
                                        bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.lbl_last_update.pack(side="bottom", pady=20)

        threading.Thread(target=self.load_data, daemon=True).start()

    def load_data(self):
        data_list = []
        total_change = 0
        best_coin = None; worst_coin = None
        max_pct = -9999; min_pct = 9999
        
        for symbol in SELECTED_COINS:
            ticker = get_binance_ticker(symbol)
            if ticker: 
                data_list.append(ticker)
                pct = float(ticker['priceChangePercent'])
                total_change += pct
                if pct > max_pct: max_pct = pct; best_coin = symbol.replace("USDT","")
                if pct < min_pct: min_pct = pct; worst_coin = symbol.replace("USDT","")
        
        if data_list:
            avg_change = total_change / len(data_list)
            if avg_change >= 0:
                msg = f"GOOD (+{avg_change:.2f}%)"
                bg_color = COLORS["accent_brown"]
                fg_color = COLORS["white"]
                overview_fg = COLORS["white"] 
            else:
                msg = f"BAD ({avg_change:.2f}%)"
                bg_color = COLORS["red"]
                fg_color = COLORS["white"]
                overview_fg = COLORS["white"] 
            
            self.after(0, lambda: self.update_ui(msg, bg_color, fg_color, overview_fg, best_coin, max_pct, worst_coin, min_pct))
        
        self.after(0, lambda: self.graph.draw_graph(data_list))
        self.after(0, lambda: self.lbl_last_update.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}"))

    def update_ui(self, status_text, bg, fg, ov_fg, best, max_p, worst, min_p):
        self.status_inner.config(bg=bg)
        self.lbl_portfolio.config(text=status_text, bg=bg, fg=fg)
        self.lbl_overview.config(bg=bg, fg=ov_fg) 
        self.lbl_top_gainer.config(text=f"{best} ({max_p:+.2f}%)")
        self.lbl_worst_loser.config(text=f"{worst} ({min_p:+.2f}%)")

# --- PAGE 3: DETAILS ---
class ProDetailPage(tk.Frame):
    def __init__(self, parent, symbol):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.symbol = symbol.lower()
        self.symbol_upper = symbol.upper()
        self.is_running = True
        self.current_interval = "1h"
        
        h = Header(self, show_time=True)
        h.pack(fill="x", padx=30, pady=(15, 0)) 

        toggle_frame = tk.Frame(h, bg=COLORS["bg_main"])
        toggle_frame.pack(side="left")

        self.var_book = tk.BooleanVar(value=True)
        self.var_trade = tk.BooleanVar(value=True)
        for text, var in [("Trades", self.var_trade), ("Order Book", self.var_book)]:
            tk.Checkbutton(toggle_frame, text=text, variable=var, command=self.update_layout,
                           bg=COLORS["bg_main"], fg=COLORS["text_dark"], 
                           activebackground=COLORS["bg_main"], selectcolor=COLORS["bg_main"],
                           font=FONTS["body"]).pack(side="right", padx=5)

        # INFO AREA
        top_container = tk.Frame(self, bg=COLORS["bg_main"])
        top_container.pack(fill="x", padx=30, pady=(20, 5))

        info_row = tk.Frame(top_container, bg=COLORS["bg_main"])
        info_row.pack(fill="x")
        
        sym_frame = tk.Frame(info_row, bg=COLORS["bg_main"])
        sym_frame.pack(side="left")
        
        base_asset = self.symbol_upper.replace("USDT", "")
        tk.Label(sym_frame, text=base_asset, font=FONTS["h1"], 
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(side="left")
        font_light = (FONTS["h1"][0], FONTS["h1"][1], "normal")
        tk.Label(sym_frame, text="USDT", font=font_light, 
                 bg=COLORS["bg_main"], fg=COLORS["text_light"]).pack(side="left", padx=(5,0))

        self.icon_image = self.load_icon(base_asset)
        if self.icon_image:
            tk.Label(sym_frame, image=self.icon_image, bg=COLORS["bg_main"]).pack(side="left", padx=15)

        price_box = tk.Frame(info_row, bg=COLORS["text_dark"], padx=15, pady=5)
        price_box.pack(side="right")
        self.lbl_price = tk.Label(price_box, text="$ ---", font=FONTS["h2"], 
                                  bg=COLORS["text_dark"], fg=COLORS["bg_main"])
        self.lbl_price.pack()
        
        control_row = tk.Frame(top_container, bg=COLORS["bg_main"])
        control_row.pack(fill="x", pady=(15, 0))

        tf_frame = tk.Frame(control_row, bg=COLORS["bg_main"])
        tf_frame.pack(side="left")
        self.tf_buttons = {}
        for tf in TIMEFRAMES:
            btn = tk.Button(tf_frame, text=tf, font=FONTS["small"], bd=0, 
                            cursor="hand2", padx=10, pady=2,
                            command=lambda t=tf: self.change_timeframe(t))
            btn.pack(side="left", padx=2)
            self.tf_buttons[tf] = btn
        self.update_tf_buttons()

        self.lbl_stats = tk.Label(control_row, text="Vol: -   High: -   Low: -", 
                                  font=FONTS["stats"],
                                  bg=COLORS["bg_main"], fg=COLORS["text_light"])
        self.lbl_stats.pack(side="right")

        # CONTENT AREA
        self.content = tk.Frame(self, bg=COLORS["bg_main"])
        self.content.pack(fill="both", expand=True, padx=30, pady=(5, 20))
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=1)

        self.chart_wrap, self.chart_inner = create_shadow_card(self.content, padx=5, pady=5)
        self.chart_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=0)
        self.chart_panel = ChartPanel(self.chart_inner)
        self.chart_panel.pack(fill="both", expand=True)

        self.side_panel = tk.Frame(self.content, bg=COLORS["bg_main"])
        self.side_panel.grid(row=0, column=1, sticky="nsew", pady=0)
        
        self.book_wrap, self.book_inner = create_shadow_card(self.side_panel, padx=5, pady=5)
        self.book_panel = OrderBookPanel(self.book_inner)
        
        self.trade_wrap, self.trade_inner = create_shadow_card(self.side_panel, padx=5, pady=5)
        self.trade_panel = TradeFeedPanel(self.trade_inner)

        self.action_wrap, self.action_inner = create_shadow_card(self.side_panel, padx=10, pady=10)
        change_container = tk.Frame(self.action_inner, bg=COLORS["card_bg"])
        change_container.pack(fill="both", expand=True)
        tk.Label(change_container, text="24h Change", font=FONTS["small"], 
                 bg=COLORS["card_bg"], fg=COLORS["text_light"]).pack(pady=(5,0))
        self.lbl_big_change = tk.Label(change_container, text="---%", font=FONTS["h1"], 
                                       bg=COLORS["card_bg"], fg=COLORS["text_dark"])
        self.lbl_big_change.pack(pady=(0,5))
        
        self.update_layout()

        threading.Thread(target=self.fetch_chart, daemon=True).start()
        threading.Thread(target=self.start_ws, daemon=True).start()
        threading.Thread(target=self.update_24h_stats, daemon=True).start()

    def load_icon(self, symbol):
        try:
            for ext in [".png", ".jpg", ".jpeg"]:
                file_path = f"{symbol}{ext}"
                if os.path.exists(file_path):
                    pil_img = Image.open(file_path)
                    pil_img = pil_img.resize((35, 35), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(pil_img)
        except Exception as e:
            print(f"Error loading icon: {e}")
        return None

    def update_layout(self):
        self.book_wrap.pack_forget()
        self.trade_wrap.pack_forget()
        self.action_wrap.pack_forget()
        if self.var_book.get():
            self.book_wrap.pack(fill="both", expand=True, pady=(0, 10))
            self.book_panel.pack(fill="both", expand=True)
        if self.var_trade.get():
            self.trade_wrap.pack(fill="both", expand=True, pady=(0, 10))
            self.trade_panel.pack(fill="both", expand=True)
        self.action_wrap.pack(fill="x", pady=0)

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
                btn.config(bg=COLORS["shadow"], fg=COLORS["text_dark"])

    def fetch_chart(self):
        klines = get_klines(self.symbol_upper, self.current_interval)
        self.after(0, lambda: self.chart_panel.draw_chart(klines))
    
    def update_24h_stats(self):
        while self.is_running:
            ticker = get_binance_ticker(self.symbol_upper)
            if ticker:
                vol = float(ticker['volume'])
                high = float(ticker['highPrice'])
                low = float(ticker['lowPrice'])
                pct = float(ticker['priceChangePercent'])
                text_stats = f"Vol: {vol:,.0f}   High: {high:,.2f}   Low: {low:,.2f}"
                text_pct = f"{pct:+.2f}%"
                color_pct = COLORS["green"] if pct >= 0 else COLORS["red"]
                self.after(0, lambda t=text_stats, p=text_pct, c=color_pct: self._update_labels(t, p, c))
            import time
            time.sleep(5)

    def _update_labels(self, stats_text, pct_text, pct_color):
        self.lbl_stats.config(text=stats_text)
        self.lbl_big_change.config(text=pct_text, fg=pct_color)

    def start_ws(self):
        def on_message(ws, message):
            if not self.is_running: ws.close(); return
            try:
                response = json.loads(message)
                data = response.get('data', response)
                self.after(0, lambda: self.process_ws_data(data))     
            except: pass

        stream_names = f"{self.symbol}@trade/{self.symbol}@depth5@100ms"
        url = f"wss://stream.binance.com:9443/stream?streams={stream_names}"
        ws = websocket.WebSocketApp(url, on_message=on_message)
        ws.run_forever()

    def process_ws_data(self, data):
        try:
            if 'p' in data: 
                price = float(data['p'])
                self.lbl_price.config(text=f"$ {price:,.2f}")
                if self.var_trade.get() and hasattr(self, 'trade_panel'):
                    self.trade_panel.add(data['p'], data['q'], data['m']) 

            bids = data.get('bids') or data.get('b')
            asks = data.get('asks') or data.get('a')
            if bids and asks:
                if self.var_book.get() and hasattr(self, 'book_panel'):
                    self.book_panel.update_data(bids, asks)
        except: pass

    def destroy(self):
        self.is_running = False
        super().destroy()

# --- MAIN APP ---
class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cryptocurrency Dashboard")
        self.geometry("1200x842")
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
        btn_home.pack(fill="x", pady=(20, 10), ipady=10)
        
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
        btn_change.pack(side="bottom", fill="x", pady=(0, 20), padx=10, ipady=5)

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