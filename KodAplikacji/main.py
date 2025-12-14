import customtkinter
import CDPplot
import CDPdata
import CDPQuarter
import Splash
from tkcalendar import DateEntry
import tkinter as tk
from tkinter import ttk
from CTkMessagebox import CTkMessagebox
from datetime import datetime
import pandas as pd

class App(customtkinter.CTk):
    def __init__(self, preloaded_data=None, preloaded_trends=None):
        super().__init__()
        
        self.geometry("1280x720")
        self.title("CD Projekt SA - Wykres akcji")

        self.screen1 = Screen1(self)
        self.screen2 = Screen2(self)
        self.screen3 = Screen3(self)

        self.show_frame(self.screen1, " Wykres akcji")
        self.screen1.showPlot("7d")

    def show_frame(self, frame, text):
        for f in (self.screen1, self.screen2, self.screen3):
            f.pack_forget()
            self.title("CD Projekt SA - " + text)
        frame.pack(fill="both", expand=True)

#Ekran wykresu akcji
class Screen1(customtkinter.CTkFrame):
    def __init__(self, master, preloaded_data=None, preloaded_trends=None):
        super().__init__(master)

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

        btn_left = customtkinter.CTkButton(nav_frame, text="Google Trends", command=lambda: master.show_frame(master.screen2, "Google Trends"))
        btn_left.pack(side="left", anchor="sw")

        btn_right = customtkinter.CTkButton(nav_frame, text="Sprawozdanie kwartalne", command=lambda: master.show_frame(master.screen3, "Sprawozdanie kwartalne"))
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

        self.master = master
        self.trends_data = preloaded_trends

        self.trends_cache = {}  # pamięć podręczna
        self.trend_queries = ["CD Projekt", "Cyberpunk 2077", "Wiedźmin"]
        self.current_query = customtkinter.StringVar(value="CD Projekt")

        #Ramka na wykres Google Trends 
        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=20, pady=20)

        #Domyślny zakres (7d)
        self.current_period = "7d"

        #Górny pasek z przyciskami okresów i odświeżania
        top_bar = customtkinter.CTkFrame(self)
        top_bar.pack(fill="x", pady=(10, 0))

        self.query_dropdown = customtkinter.CTkOptionMenu(
            top_bar,
            values=self.trend_queries,
            variable=self.current_query,
            command=lambda _: self.showTrendsPlot(self.current_period)
        )
        self.query_dropdown.pack(side="left", padx=5)

        for period in ["1d", "7d", "1m"]:
            btn = customtkinter.CTkButton(top_bar, text=period, width=70,command=lambda p=period: self.showTrendsPlot(p))
            btn.pack(side="left", padx=5)

        refresh_btn = customtkinter.CTkButton(top_bar, text="Odśwież dane", width=100,command=self.refreshTrends)
        refresh_btn.pack(side="right", padx=10)

        # --- Pierwsze wyświetlenie domyślnego wykresu ---
        self.showTrendsPlot(self.current_period)

        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        btn_left = customtkinter.CTkButton(nav_frame, text="Sprawozdanie kwartalne", command=lambda: master.show_frame(master.screen3, "Sprawozdanie kwartalne"))
        btn_left.pack(side="left", anchor="sw")

        btn_right = customtkinter.CTkButton(nav_frame, text="Wykres akcji", command=lambda: master.show_frame(master.screen1, "Wykres akcji"))
        btn_right.pack(side="right", anchor="se")

    def showTrendsPlot(self, period):
        self.current_period = period
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        query = self.current_query.get()
        data = CDPdata.getTrendsData(query, period)
        CDPplot.createTrendsPlot(self.plot_frame, period, data, query)

    #Usuwa cache dla bieżącej pary (query, period) i pobiera na nowo
    def refreshTrends(self):
        # Pobierz bieżące ustawienia
        keyword = self.current_query.get()
        period = self.current_period
        
        self.trends_cache.pop((keyword, period), None)
        
        try:
            CDPdata.invalidate_trends_period(keyword, period)
        except Exception as e:
            print(f"Błąd przy invalidacji cache: {e}")
    
        # Ponowne narysowanie (które spowoduje pobranie nowych danych)
        self.showTrendsPlot(period)
            
#Ekran sprawozdań kwartalnych
class Screen3(customtkinter.CTkFrame):
    class Screen3(customtkinter.CTkFrame):
    def __init__(self, master, preloaded_data=None, preloaded_trends=None):
        super().__init__(master)
        self.master = master

        #TYTUŁ
        title = customtkinter.CTkLabel(self, text="Sprawozdania kwartalne CD Projekt", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        #WYBÓR KWARTAŁU
        self.quarter_var = tk.StringVar(value="Wybierz kwartał")

        available_quarters = list(CDPdata.QUARTER_REPORTS.keys())

        order = ["I", "II", "III", "IV"]  # kolejność rosnąca
        available_quarters.sort(
             key=lambda x: (
             int(x.split()[1]),                    # rok
             order.index(x.split()[0])),           # indeks kwartału
             reverse=True)                         # od największego do najmniejszego

        self.quarter_combobox = ttk.Combobox(self, textvariable=self.quarter_var, values=available_quarters, state="readonly", width=20)
        self.quarter_combobox.pack(pady=10)
        self.show_info_btn = customtkinter.CTkButton(self, text="Pokaż tabele z informacjami",command=self.onQuarterButtonClick)
        self.show_info_btn.pack(pady=10)

        #SEKCJA INFORMACYJNA
        self.info_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="both", pady=10)
        self.info_label = customtkinter.CTkLabel(self.info_frame, text="", font=("Arial", 16))
        self.info_label.pack()

        #PRZYCISKI POBIERANIA
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.pack(pady=10)
        self.btn_download_pdf = customtkinter.CTkButton(btn_frame, text="Pobierz PDF", command=self.download_pdf)
        self.btn_download_pdf.pack(side="left", padx=5)
        self.btn_download_xlsx = customtkinter.CTkButton(btn_frame, text="Pobierz XLSX", command=self.download_xlsx)
        self.btn_download_xlsx.pack(side="left", padx=5)
        self.btn_download_press_pdf = customtkinter.CTkButton(btn_frame, text="Pobierz PDF info prasowej", command=self.download_press_pdf)
        self.btn_download_press_pdf.pack(side="left", padx=5)

        #DOLNY PASEK
        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="bottom", fill="x", pady=10, padx=10)
        btn_left = customtkinter.CTkButton(
            nav_frame, text="Wykres akcji",
            command=lambda: master.show_frame(master.screen1, "Wykres akcji")
        )
        btn_left.pack(side="left", anchor="sw")
        btn_right = customtkinter.CTkButton(
            nav_frame, text="Google Trends",
            command=lambda: master.show_frame(master.screen2, "Google Trends")
        )
        btn_right.pack(side="right", anchor="se")

    #Wywołanie po wybraniu kwartału
    def onQuarterButtonClick(self):
        quarter = self.quarter_var.get()
        if quarter == "Wybierz kwartał":
           self.showError("Brak wybranego kwartału", "Przed wyświetleniem tabeli wybierz kwartał")
           return

        data, error = CDPQuarter.getQuarterTableData(quarter)
        if error:
           self.showError(error)
           return

        self.after_idle(lambda: self.showQuarterTable(data, quarter))
    
    def showQuarterTable(self, extracted, selected_quarter):
        #Czyści poprzedni widget
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        style = ttk.Style() 
        style.theme_use("default") 
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638", bordercolor="#343638", borderwidth=0) 
        style.map('Treeview', background=[('selected', '#22559b')]) 
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat") 
        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        columns = ["Pozycja", selected_quarter, "Poprzedni rok"]
        tree = ttk.Treeview(self.info_frame, columns=columns, show="headings")

        tree.heading("Pozycja", text="Pozycja", anchor="center")
        tree.column("Pozycja", anchor="w", width=360)

        tree.heading(selected_quarter, text=selected_quarter, anchor="center")
        tree.column(selected_quarter, anchor="center", width=120)

        tree.heading("Poprzedni rok", text="Poprzedni rok", anchor="center")
        tree.column("Poprzedni rok", anchor="center", width=120)

        for label, current, previous in extracted:
            tree.insert("", "end", values=(
                 label,
                 f"{current:,}".replace(",", " ") if current is not None else "-",
                 f"{previous:,}".replace(",", " ") if previous is not None else "-"
            ))

        tree.pack(padx=20, pady=8)

    #Wywołanie po wybraniu kwartału
    def onQuarterSelect(self, quarter):
        CDPQuarter.showQuarterInfo(quarter, self.info_label)      
    
    def get_xlsx_path(self, quarter):
        roman, year = quarter.split()
        return f"dane_finansowe_{roman} {year}.xlsx"

    #Pobieranie plików
    def download_pdf(self):
        quarter = self.quarter_var.get()
        if quarter not in CDPdata.QUARTER_REPORTS:
            print("Brak raportu dla tego kwartału.")
            return
        url = CDPdata.QUARTER_REPORTS[quarter]["pdf"]
        path = CDPdata.download_file(url, f"skonsolidowany_{quarter}.pdf")
        print(f"Pobrano PDF: {path}")

    def download_xlsx(self):
        quarter = self.quarter_var.get()
        if quarter not in CDPdata.QUARTER_REPORTS:
            print("Brak raportu dla tego kwartału.")
            return
        url = CDPdata.QUARTER_REPORTS[quarter]["xlsx"]
        path = CDPdata.download_file(url, f"dane_finansowe_{quarter}.xlsx")
        print(f"Pobrano XLSX: {path}")

    def download_press_pdf(self):
        quarter = self.quarter_var.get()
        if quarter not in CDPdata.QUARTER_REPORTS:
            print("Brak raportu dla tego kwartału.")
            return
        url = CDPdata.QUARTER_REPORTS[quarter]["press_pdf"]
        path = CDPdata.download_file(url, f"informacja_prasowa_{quarter}.pdf")
        print(f"Pobrano PDF info prasowej: {path}")

    def showError(self, title="", message="", icon="warning"):
        CTkMessagebox(title=title, message=message, icon=icon)


if __name__ == "__main__":
   start = Splash.SplashScreen()
   start.mainloop()




