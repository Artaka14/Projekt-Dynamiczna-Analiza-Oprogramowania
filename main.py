import customtkinter
import CDPplot
import CDPdata
import Splash
from tkcalendar import DateEntry
from CTkMessagebox import CTkMessagebox
from datetime import datetime

class App(customtkinter.CTk):
    def __init__(self, preloaded_data=None, preloaded_trends=None):
        super().__init__()
        
        self.geometry("1280x720")
        self.title("CD Projekt SA - Wykres akcji")

        self.screen1 = Screen1(self)
        self.screen2 = Screen2(self)
        self.screen3 = Screen3(self)

        self.show_frame(self.screen1)
        self.screen1.showPlot("7d")

    def show_frame(self, frame):
        for f in (self.screen1, self.screen2, self.screen3):
            f.pack_forget()

        frame.pack(fill="both", expand=True)

#Ekran wykresu akcji
class Screen1(customtkinter.CTkFrame):
    def __init__(self, master, preloaded_data=None, preloaded_trends=None):
        super().__init__(master)

        master.title("CD Projekt SA - Wykres akcji")
        self.trends_cache = preloaded_trends or {}

        # Główna ramka
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Lewa strona – wykres
        self.plot_frame = customtkinter.CTkFrame(self.main_frame)
        self.plot_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Prawa strona – panele z informacjami i przyciskami
        self.right_frame = customtkinter.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)

        # Dolne przyciski nawigacyjne
        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        btn_left = customtkinter.CTkButton(nav_frame, text="Google Trends", command=lambda: master.show_frame(master.screen2))
        btn_left.pack(side="left", anchor="sw")

        btn_right = customtkinter.CTkButton(nav_frame, text="Sprawozdanie kwartalne", command=lambda: master.show_frame(master.screen3))
        btn_right.pack(side="right", anchor="se")

        # Aktualna cena
        self.price_frame = customtkinter.CTkFrame(self.right_frame)
        self.price_frame.pack(pady=(10, 20))

        self.price_label_title = customtkinter.CTkLabel(self.price_frame, text="Aktualna cena:", font=("Arial", 14, "bold"))
        self.price_label_title.pack()

        self.price_label_value = customtkinter.CTkLabel(self.price_frame, text="...", font=("Arial", 16))
        self.price_label_value.pack(pady=(5, 0))

        # Min/Max
        self.minmax_frame = customtkinter.CTkFrame(self.right_frame)
        self.minmax_frame.pack(pady=(10, 20))

        self.minmax_values_frame = customtkinter.CTkFrame(self.minmax_frame)
        self.minmax_values_frame.pack()

        self.min_frame = customtkinter.CTkFrame(self.minmax_values_frame)
        self.min_frame.pack(side="left", padx=20)

        self.min_label_title = customtkinter.CTkLabel(self.min_frame, text="Min", font=("Arial", 14, "bold"))
        self.min_label_title.pack()

        self.min_label_value = customtkinter.CTkLabel(self.min_frame, text="...", font=("Arial", 16))
        self.min_label_value.pack(pady=(5, 0))

        self.max_frame = customtkinter.CTkFrame(self.minmax_values_frame)
        self.max_frame.pack(side="left", padx=20)

        self.max_label_title = customtkinter.CTkLabel(self.max_frame, text="Max", font=("Arial", 14, "bold"))
        self.max_label_title.pack()

        self.max_label_value = customtkinter.CTkLabel(self.max_frame, text="...", font=("Arial", 16))
        self.max_label_value.pack(pady=(5, 0))

        # Zakres danych
        label = customtkinter.CTkLabel(self.right_frame, text="Zakres danych", font=("Arial", 14, "bold"))
        label.pack(pady=(0, 10))

        button_frame = customtkinter.CTkFrame(self.right_frame)
        button_frame.pack(pady=10)

        for period in ["1d", "7d", "1m"]:
            btn = customtkinter.CTkButton(button_frame, text=period, width=70, command=lambda p=period: self.showPlot(p))
            btn.pack(side="left", padx=5)

        # Własny zakres
        self.date_picker_frame = customtkinter.CTkFrame(self.right_frame, width=300)
        self.date_picker_frame.pack(pady=20)

        customtkinter.CTkLabel(self.date_picker_frame, text="Własny zakres danych", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        self.date_inputs_frame = customtkinter.CTkFrame(self.date_picker_frame)
        self.date_inputs_frame.pack(padx=10, pady=5)

        customtkinter.CTkLabel(self.date_inputs_frame, text="Od:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.start_date_entry = DateEntry(self.date_inputs_frame, width=12, date_pattern="yyyy-mm-dd")
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.date_inputs_frame, text="Do:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.end_date_entry = DateEntry(self.date_inputs_frame, width=12, date_pattern="yyyy-mm-dd")
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        self.custom_date_button = customtkinter.CTkButton(self.date_picker_frame, text="Pokaż wykres", command=self.showCustomDatePlot)
        self.custom_date_button.pack(pady=10)

        if preloaded_data is not None:
            self.after(200, lambda: self.showPlot("7d"))

    def showPlot(self, period):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        data = CDPdata.getCdpData(period)
        CDPplot.createCdpPlot(self.plot_frame, period, data)

        self.updatePriceLabel()
        self.updateMinMaxLabels(data)

    def showCustomDatePlot(self):
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        today = datetime.now().date()

        if start_date > end_date:
            self.showError("Błędny zakres dat", "Data początkowa nie może być późniejsza niż końcowa.")
            return

        if start_date > today or end_date > today:
            self.showError("Błędny zakres dat", "Nie można wybrać dat z przyszłości.")
            return

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        data = CDPdata.getCustomCdpData(start_date, end_date)
        CDPplot.createCustomDataCdpPlot(self.plot_frame, start_date, end_date, data)

        self.updateMinMaxLabels(data)

    def updatePriceLabel(self):
        price = CDPdata.getCurrentPrice()
        self.price_label_value.configure(text=f"{price} PLN")

    def updateMinMaxLabels(self, data):
        min_price, max_price = CDPdata.getMinMaxPrice(data)
        self.min_label_value.configure(text=f"{min_price} PLN")
        self.max_label_value.configure(text=f"{max_price} PLN")

    def showError(self, title="", message="", icon="warning"):
        CTkMessagebox(title=title, message=message, icon=icon)

#Ekran Google Trends
class Screen2(customtkinter.CTkFrame):
    def __init__(self, master, preloaded_data=None, preloaded_trends=None):
        super().__init__(master)
        master.title("CD Projekt SA - Google Trends")

        self.master = master
        self.trends_data = preloaded_trends

        self.trends_cache = {}  # pamięć podręczna

         # --- Ramka na wykres Google Trends ---
        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Domyślny zakres (7d) ---
        self.current_period = "7d"

        # --- Górny pasek z przyciskami okresów i odświeżania ---
        top_bar = customtkinter.CTkFrame(self)
        top_bar.pack(fill="x", pady=(10, 0))

        for period in ["1d", "7d", "1m"]:
            btn = customtkinter.CTkButton(
                top_bar, text=period, width=70,
                command=lambda p=period: self.showTrendsPlot(p)
            )
            btn.pack(side="left", padx=5)

        refresh_btn = customtkinter.CTkButton(
            top_bar, text="Odśwież dane", width=100,
            command=self.refreshTrends
        )
        refresh_btn.pack(side="right", padx=10)

        # --- Pierwsze wyświetlenie domyślnego wykresu ---
        self.showTrendsPlot(self.current_period)

        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        btn_left = customtkinter.CTkButton(nav_frame, text="Sprawozdanie kwartalne", command=lambda: master.show_frame(master.screen3))
        btn_left.pack(side="left", anchor="sw")

        btn_right = customtkinter.CTkButton(nav_frame, text="Wykres akcji", command=lambda: master.show_frame(master.screen1))
        btn_right.pack(side="right", anchor="se")

    def showTrendsPlot(self, period):

        self.current_period = period
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        data = CDPdata.getTrendsData(period)
        CDPplot.createTrendsPlot(self.plot_frame, period, data)

    def refreshTrends(self):
        if hasattr(self, "current_period"):
            CDPdata.invalidate_trends_period(self.current_period)
            self.showTrendsPlot(self.current_period)
            
#Ekran sprawozdań kwartalnych
class Screen3(customtkinter.CTkFrame):
    def __init__(self, master, preloaded_data=None, preloaded_trends=None):
        super().__init__(master)
        master.title("CD Projekt SA - Sprawozdanie kwartalne")

        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        btn_left = customtkinter.CTkButton(nav_frame, text="Wykres akcji", command=lambda: master.show_frame(master.screen1))
        btn_left.pack(side="left", anchor="sw")

        btn_right = customtkinter.CTkButton(nav_frame, text="Google Trends", command=lambda: master.show_frame(master.screen2))
        btn_right.pack(side="right", anchor="se")

if __name__ == "__main__":
   start = Splash.SplashScreen()
   start.mainloop()



