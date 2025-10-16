import yfinance as yf
import matplotlib.pyplot as plt
import customtkinter
import pandas as pd

def CheckCDP():

    data = yf.download("CDR.WA", period="5d", interval="1m")

    if data.index.tz is None:
       data.index = data.index.tz_localize('Europe/Warsaw')
    else:
       data.index = data.index.tz_convert('Europe/Warsaw')

    data = data.between_time("09:00", "17:00")

    data = data[data.index.dayofweek < 5]
    data_reset = data.reset_index(drop=False)
    data_reset["sample_index"] = range(len(data_reset))

    #Wykres
    plt.figure(figsize=(12,6))
    plt.plot(data_reset["sample_index"], data_reset["Close"], label="CD Projekt S.A. (1m)")
    plt.title("CD Projekt S.A. — dane minutowe (ciągłe, bez przerw między sesjami)")
    plt.xlabel("Numer próbki (kolejny punkt notowań)")
    plt.ylabel("Cena (PLN)")
    plt.legend()
    session_ends = data_reset.groupby(data_reset["Datetime"].dt.date)["sample_index"].max()
    plt.xticks(session_ends.values, [str(d) for d in session_ends.index], rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")

        self.button = customtkinter.CTkButton(self, text="my button", command=self.button_callbck)
        self.button.pack(padx=20, pady=20)

    def button_callbck(self):
        CheckCDP()

app = App()
app.mainloop()