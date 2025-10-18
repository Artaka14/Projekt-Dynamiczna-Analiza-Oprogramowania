import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter
import pandas as pd
from datetime import datetime
from PIL import Image

def get_cdp_data(period):
    if period in ["1d", "7d"]:
        interval = "1m"
    elif period in ["1mo"]:
        interval = "15m"
    else:
        interval = "60m"

    data = yf.download("CDR.WA", period=period, interval=interval, progress=False)

    if data.empty:
        raise ValueError("Brak danych dla wybranego okresu.")

    if data.index.tz is None:
        data.index = data.index.tz_localize('Europe/Warsaw')
    else:
        data.index = data.index.tz_convert('Europe/Warsaw')

    data = data.between_time("09:00", "17:00")
    data = data[data.index.dayofweek < 5]

    data_reset = data.reset_index(drop=False)
    data_reset["sample_index"] = range(len(data_reset))

    return data_reset


def create_cdp_plot(frame, period):
    data_reset = get_cdp_data(period)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data_reset["sample_index"], data_reset["Close"], label="CD Projekt S.A.")
    ax.set_title(f"CD Projekt S.A. — okres: {period}")
    ax.set_xlabel("Numer próbki (kolejny punkt notowań)")
    ax.set_ylabel("Cena (PLN)")
    ax.legend()

    if "Datetime" in data_reset.columns:
        try:
            session_ends = (
                data_reset.groupby(data_reset["Datetime"].dt.date)["sample_index"].max()
            )
            ax.set_xticks(session_ends.values)
            ax.set_xticklabels([str(d) for d in session_ends.index], rotation=45)
        except Exception:
            pass

    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


class SplashScreen(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ekran startowy")
        #ten caly shit zeby byl na srodku splashor
        width, height = 400, 250
        self.geometry(f"{width}x{height}+{self.center_x(width)}+{self.center_y(height)}")
        self.resizable(False, False)
        self.overrideredirect(True)  # borderless

        self.logo = customtkinter.CTkImage(light_image=Image.open("XDlogo.png"), size=(400, 250))
        customtkinter.CTkLabel(self, image=self.logo, text="").pack(pady=10)       

        # po 2,5 sekundy opening
        self.after(2500, self.open_main_app)

    def center_x(self, window_width):
        screen_width = self.winfo_screenwidth()
        return int((screen_width / 2) - (window_width / 2))

    def center_y(self, window_height):
        screen_height = self.winfo_screenheight()
        return int((screen_height / 2) - (window_height / 2))

    def open_main_app(self):
        self.destroy()
        app = App()
        app.mainloop()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1100x600")
        self.title("CD Projekt S.A. — Notowania")

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.plot_frame = customtkinter.CTkFrame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.right_frame = customtkinter.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)

        label = customtkinter.CTkLabel(self.right_frame, text="Zakres danych", font=("Arial", 14, "bold"))
        label.pack(pady=(10, 20))

        for period in ["1d", "7d", "1mo", "1y"]:
            btn = customtkinter.CTkButton(
                self.right_frame, 
                text=period,
                command=lambda p=period: self.show_plot(p)
            )
            btn.pack(pady=10, padx=10)

        create_cdp_plot(self.plot_frame, "7d")

    def show_plot(self, period):
      for widget in self.plot_frame.winfo_children():
            widget.destroy()

      create_cdp_plot(self.plot_frame, period)


if __name__ == "__main__":
    start = SplashScreen()
    start.mainloop()

