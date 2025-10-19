import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter
import pandas as pd

def get_cdp_data(period):
    end_time = datetime.now()

    if end_time.weekday() >= 5: 
       days_to_subtract = end_time.weekday() - 4 
       end_time -= timedelta(days=days_to_subtract)

    if period == "1d":
        start_time = end_time - timedelta(days=1)
        interval = "1m"
    elif period == "7d":
        start_time = end_time - timedelta(days=7)
        interval = "5m"
    elif period == "1m":
        start_time = end_time - timedelta(days=30)
        interval = "15m"
    elif period == "1r":
        start_time = end_time - timedelta(days=365)
        interval = "1d"
    else:
        raise ValueError("Nieznany okres czasu.")

    data = yf.download(
        "CDR.WA",
        start=start_time,
        end=end_time,
        interval=interval,
        progress=False
    )

    if data.empty:
        raise ValueError("Brak danych dla wybranego okresu.")

    data = data.between_time("09:00", "17:00")
    data = data[data.index.dayofweek < 5]

    data_reset = data.reset_index(drop=False)
    data_reset["sample_index"] = range(len(data_reset))

    return data_reset


def create_cdp_plot(frame, period):
    data_reset = get_cdp_data(period)

    if period == "1d":
        periodName = "1 dzień"
    elif period == "7d":
        periodName = "7 dni"
    elif period == "1m":
        periodName = "1 miesiąc"
        period = "1mo"
    elif period == "1r":
        periodName = "1 rok"
        period = "1y"

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(data_reset["sample_index"], data_reset["Close"], label="CD Projekt S.A.")
    ax.set_title(f"CD Projekt S.A. — okres: {periodName}")
    ax.set_ylabel("Cena (PLN)")
    ticks = []

    if "Datetime" in data_reset.columns:
        try:
            session_bounds = data_reset.groupby(data_reset["Datetime"].dt.date)["sample_index"].agg(['min', 'max'])

            ticks = session_bounds['min'].tolist()
            labels = [str(d) for d in session_bounds.index]

            ticks.append(session_bounds['max'].iloc[-1])
            labels.append(str(session_bounds.index[-1]+timedelta(days=1)))

            ax.set_xticks(ticks)
            ax.set_xticklabels(labels, rotation=45)

            ylim = ax.get_ylim()

            ax.set_xlim(data_reset['sample_index'].min(), data_reset['sample_index'].max())

        except Exception:
            pass


    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def get_current_price():
    """Pobiera bieżącą cenę akcji CD Projekt S.A."""
    ticker = yf.Ticker("CDR.WA")
    data = ticker.history(period="1d", interval="1m")
    if not data.empty:
        return round(data["Close"].iloc[-1], 2)
    return None


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1920x1080")
        self.title("CD Projekt S.A. — Notowania")

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.plot_frame = customtkinter.CTkFrame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_frame = customtkinter.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)

        self.price_frame = customtkinter.CTkFrame(self.right_frame)
        self.price_frame.pack(pady=(10, 20))

        self.price_label_title = customtkinter.CTkLabel(
            self.price_frame, text="Aktualna cena:", font=("Arial", 14, "bold")
        )
        self.price_label_title.pack()

        self.price_label_value = customtkinter.CTkLabel(
            self.price_frame, text="Pobieranie...", font=("Arial", 16)
        )
        self.price_label_value.pack(pady=(5, 0))

        label = customtkinter.CTkLabel(
            self.right_frame, text="Zakres danych", font=("Arial", 14, "bold")
        )
        label.pack(pady=(0, 10))

        button_frame = customtkinter.CTkFrame(self.right_frame)
        button_frame.pack(pady=10)

        for period in ["1d", "7d", "1m"]:
            btn = customtkinter.CTkButton(
                button_frame,
                text=period,
                width=70,
                command=lambda p=period: self.show_plot(p)
            )
            btn.pack(side="left", padx=5)
        create_cdp_plot(self.plot_frame, "7d")
        self.update_price_label()


    def show_plot(self, period):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        create_cdp_plot(self.plot_frame, period)
        self.state("zoomed")

    def update_price_label(self):
        try:
            price = get_current_price()
            if price:
                self.price_label_value.configure(text=f"{price} PLN")
            else:
                self.price_label_value.configure(text="Brak danych")
        except Exception:
            self.price_label_value.configure(text="Błąd pobierania")
        self.state("zoomed")

app = App()
app.mainloop()

