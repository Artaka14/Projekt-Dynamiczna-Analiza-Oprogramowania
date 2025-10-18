import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter
import pandas as pd

def get_cdp_data():
    data = yf.download("CDR.WA", period="5d", interval="1m")

    if data.index.tz is None:
        data.index = data.index.tz_localize('Europe/Warsaw')
    else:
        data.index = data.index.tz_convert('Europe/Warsaw')

    data = data.between_time("09:00", "17:00")
    data = data[data.index.dayofweek < 5]

    data_reset = data.reset_index(drop=False)
    data_reset["sample_index"] = range(len(data_reset))

    return data_reset

def create_cdp_plot(frame):
    data_reset = get_cdp_data()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data_reset["sample_index"], data_reset["Close"], label="CD Projekt S.A. (1m)")
    ax.set_title("CD Projekt SA)
    ax.set_xlabel("Numer próbki (kolejny punkt notowań)")
    ax.set_ylabel("Cena (PLN)")
    ax.legend()
    session_ends = data_reset.groupby(data_reset["Datetime"].dt.date)["sample_index"].max()
    ax.set_xticks(session_ends.values)
    ax.set_xticklabels([str(d) for d in session_ends.index], rotation=45)
    ax.grid(True)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x600")
        self.title("CD Projekt S.A. — Notowania")

        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.pack(side="top", fill="x", pady=10)

        self.button = customtkinter.CTkButton(
            self.top_frame, text="Pokaż wykres", command=self.show_plot
        )
        self.button.pack(padx=20, pady=10)

        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def show_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        create_cdp_plot(self.plot_frame)

app = App()
app.mainloop()
