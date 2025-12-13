import io
import openpyxl
from tabulate import tabulate
import tkinter as tk
from tkinter import ttk

XLSX_FILES = {
    "II 2025": "dane_finansowe_II 2025.xlsx",
    "I 2025": "dane_finansowe_I 2025.xlsx",
    "IV 2024": "dane_finansowe_IV 2024.xlsx",
    "III 2024": "dane_finansowe_III 2024.xlsx",
    "II 2024": "dane_finansowe_II 2024.xlsx",
    "I 2024": "dane_finansowe_I 2024.xlsx",
    "IV 2023": "dane_finansowe_IV 2023.xlsx",
    "III 2023": "dane_finansowe_III 2023.xlsx",
    "II 2023": "dane_finansowe_II 2023.xlsx",
    "I 2023": "dane_finansowe_I 2023.xlsx",
    "IV 2022": "dane_finansowe_IV 2022.xlsx",
    "III 2022": "dane_finansowe_III 2022.xlsx",
    "II 2022": "dane_finansowe_II 2022.xlsx",
    "I 2022": "dane_finansowe_I 2022.xlsx",
    "IV 2021": "dane_finansowe_IV 2021.xlsx",
    "III 2021": "dane_finansowe_III 2021.xlsx",
    "II 2021": "dane_finansowe_II 2021.xlsx",
    "I 2021": "dane_finansowe_I 2021.xlsx",
    "IV 2020": "dane_finansowe_IV 2020.xlsx",
    "III 2020": "dane_finansowe_III 2020.xlsx",
    "II 2020": "dane_finansowe_II 2020.xlsx",
    "I 2020": "dane_finansowe_I 2020.xlsx",
    "IV 2019": "dane_finansowe_IV 2019.xlsx",
    "III 2019": "dane_finansowe_III 2019.xlsx",
    "II 2019": "dane_finansowe_II 2019.xlsx",
    "I 2019": "dane_finansowe_I 2019.xlsx",
    "IV 2018": "dane_finansowe_IV 2018.xlsx",
    "III 2018": "dane_finansowe_III 2018.xlsx",
    "II 2018": "dane_finansowe_II 2018.xlsx",
    "I 2018": "dane_finansowe_I 2018.xlsx",
    "IV 2017": "dane_finansowe_IV 2017.xlsx",
    "III 2017": "dane_finansowe_III 2017.xlsx",
    "II 2017": "dane_finansowe_II 2017.xlsx",
    "I 2017": "dane_finansowe_I 2017.xlsx",
    "IV 2016": "dane_finansowe_IV 2016.xlsx",
    "III 2016": "dane_finansowe_III 2016.xlsx",
    "II 2016": "dane_finansowe_II 2016.xlsx",
    "I 2016": "dane_finansowe_I 2016.xlsx"
}

def showQuarterInfo(selected_quarter, info_frame):
    roman_to_quarter = {"I": "Q1", "II": "Q2", "III": "Q3", "IV": "Q4"}

    CHOSEN_FIELDS = [
        "Przychody ze sprzedaży",
        "Zysk (strata) brutto na sprzedaży",
        "Zysk (strata) na działalności operacyjnej",
        "Zysk (strata) przed opodatkowaniem",
        "Zysk (strata) netto",
        "Zysk (strata) netto przypisana podmiotowi dominującemu"
        "Koszty sprzedaży"
    ]

    # Czyścimy zawartość ramki
    for w in info_frame.winfo_children():
        w.destroy()

    # Walidacja
    try:
        roman, year = selected_quarter.split()
        year = int(year)
    except:
        tk.Label(info_frame, text="Niepoprawny format kwartału.", fg="white", bg="#2a2d2e").pack()
        return

    if roman not in roman_to_quarter:
        tk.Label(info_frame, text="Nieznany kwartał.", fg="white", bg="#2a2d2e").pack()
        return

    path = str(XLSX_FILES.get(selected_quarter))
    if path is None:
        tk.Label(info_frame, text="Brak pliku XLSX.", fg="white", bg="#2a2d2e").pack()
        return

    # Wczytanie workbooka
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        tk.Label(info_frame, text=f"Błąd wczytywania XLSX:\n{e}", fg="white", bg="#2a2d2e").pack()
        return

    sheet_name = f"{roman_to_quarter[roman]}.{year}"
    if sheet_name not in wb.sheetnames:
        tk.Label(info_frame, text=f"Arkusz '{sheet_name}' nie istnieje.", fg="white", bg="#2a2d2e").pack()
        return

    ws = wb[sheet_name]

    # Zbieranie danych
    extracted = []
    for row in ws.iter_rows(min_col=2, max_col=4):
        label = row[0].value     
        current = row[1].value   
        previous = row[2].value  

        if label in CHOSEN_FIELDS:
            extracted.append([label, current, previous])

    if not extracted:
        tk.Label(info_frame, text="Nie znaleziono danych.", fg="white", bg="#2a2d2e").pack()
        return

    # TWORZENIE TABELI

    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background="#2a2d2e",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="#343638",
                    bordercolor="#343638",
                    borderwidth=0)
    style.map('Treeview', background=[('selected', '#22559b')])

    style.configure("Treeview.Heading",
                    background="#565b5e",
                    foreground="white",
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', '#3484F0')])

    # Tabela
    columns = ["Pozycja", f"{selected_quarter}", "Poprzedni rok"]
    tree = ttk.Treeview(info_frame, columns=columns, show="headings")

    # Pozycja
    tree.heading("Pozycja", text="Pozycja", anchor="center")
    tree.column("Pozycja", anchor="w", width=360, stretch=True)

    # Bieżący okres
    tree.heading(f"{selected_quarter}", text=selected_quarter, anchor="center")
    tree.column(f"{selected_quarter}", anchor="center", width=120, stretch=False)

    # Poprzedni rok
    tree.heading("Poprzedni rok", text="Poprzedni rok", anchor="center")
    tree.column("Poprzedni rok", anchor="center", width=120, stretch=False)

    tree.update_idletasks()

    for label, current, previous in extracted:
        tree.insert("", "end", values=(
             label,
             f"{current:,}".replace(",", " "),
             f"{previous:,}".replace(",", " ")
        ))

    tree.pack(fill="both", expand=True)


def show_table(parent, df):
    #STYLE
    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background="#2a2d2e",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="#343638",
                    bordercolor="#343638",
                    borderwidth=0)
    style.map('Treeview', background=[('selected', '#22559b')])

    style.configure("Treeview.Heading",
                    background="#565b5e",
                    foreground="white",
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', '#3484F0')])

    #WIDGET
    tree = ttk.Treeview(parent, columns=list(df.columns), show="headings")

    #Nagłówki
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

    #Dane
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(fill="both", expand=True)

    return tree

def insert_table_into_frame(frame, extracted):
    # Czyszczenie starej zawartości
    for widget in frame.winfo_children():
        widget.destroy()

    # Styl
    style = ttk.Style()
    style.theme_use("default")

    style.configure("Treeview",
                    background="#2a2d2e",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="#343638",
                    bordercolor="#343638",
                    borderwidth=0)
    style.map('Treeview', background=[('selected', '#22559b')])

    style.configure("Treeview.Heading",
                    background="#565b5e",
                    foreground="white",
                    relief="flat")
    style.map("Treeview.Heading",
              background=[('active', '#3484F0')])

    # Tabela
    columns = ["Pozycja", "Wartość"]
    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="w", width=350)

    # Wstawianie danych
    for row in extracted:
        tree.insert("", "end", values=row)

    tree.pack(fill="both", expand=True)



