import customtkinter
import time
import threading
from PIL import Image
import CDPplot
import CDPprice
import Splash

class App(customtkinter.CTk):
    def __init__(self, preloaded_data=None):
        super().__init__()
        self.geometry("1920x1080")
        self.title("CD Projekt SA")

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
            self.price_frame, text="...", font=("Arial", 16)
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
                command=lambda p=period: self.showPlot(p)
            )
            btn.pack(side="left", padx=5)
            
         # Jak sa dane pobrane w splash to uzywane
        if preloaded_data is not None:
             CDPplot.createCdpPlot(self.plot_frame, "7d")  
        self.updatePriceLabel()

    def showPlot(self, period):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        CDPplot.createCdpPlot(self.plot_frame, period)
        self.state("zoomed")

    def updatePriceLabel(self):
        price = CDPprice.getCurrentPrice()
        self.price_label_value.configure(text=f"{price} PLN")
        self.state("zoomed")

if __name__ == "__main__":
   start = SplashScreen()
   start.mainloop()


