import pandas as pd
import openpyxl

XLSX_FILES = {
    "III 2025": "dane_finansowe_III 2025.xlsx",
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

def getQuarterTableData(selected_quarter):
    roman_to_quarter = {"I": "Q1", "II": "Q2", "III": "Q3", "IV": "Q4"}

    CHOSEN_FIELDS = [
        "Przychody ze sprzedaży",
        "Zysk  (strata) brutto na sprzedaży",
        "Zysk/(strata) brutto na sprzedaży",
        "Zysk (strata) na działalności operacyjnej",
        "Zysk/(strata) na działalności operacyjnej",
        "Zysk (strata) przed opodatkowaniem",
        "Zysk/(strata) przed opodatkowaniem ",
        "Zysk (strata) netto",
        "Zysk/(strata) netto",
        "Zysk (strata) netto przypisana podmiotowi dominującemu",
        "Zysk/(strata) netto przypisana podmiotowi dominującemu",
        "Koszty sprzedaży",
        "Koszty ogólnego zarządu",
        "Koszty ogólnego zarządu, w tym:"
        "Suma dochodów całkowitych",
    ]

    # Walidacja
    try:
        roman, year = selected_quarter.split()
        year = int(year)
    except:
        return None, "Niepoprawny format kwartału"

    if roman not in roman_to_quarter:
        return None, "Nieznany kwartał"

    path = str(XLSX_FILES.get(selected_quarter))
    if path is None:
        return None, "Brak pliku XLSX"

    sheet_names = [f"{roman_to_quarter[roman]}.{year}", f"{roman_to_quarter[roman]}{year}"]

    # Próba wczytania konkretnego arkusza
    for sheet_name in (f"{roman_to_quarter[roman]}.{year}", f"{roman_to_quarter[roman]}{year}"):
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, usecols="B:D", engine="openpyxl", nrows=300, dtype={"B": str, "C": float, "D": float})
            break
        except Exception as e:
            df = None

    if df is None:
       return None, "Nie znaleziono arkusza"

    df.columns = ["label", "current", "previous"]

    # Filtrowanie tylko interesujących pozycji
    df["label"] = df["label"].fillna("")
    df["label"] = df["label"].replace({"Koszty ogólnego zarządu, w tym:": "Koszty ogólnego zarządu"})

    CHOSEN_FIELDS_set = set(CHOSEN_FIELDS)
    df = df[df["label"].isin(CHOSEN_FIELDS_set)]

    if df.empty:
        return None, "Nie znaleziono danych"

    # Zachowanie kolejności CHOSEN_FIELDS
    df = df.drop_duplicates(subset=["label"])
    df = df.set_index("label").reindex(CHOSEN_FIELDS).reset_index()
    df = df.dropna(subset=["current", "previous"], how="all")
    
    extracted = list(df[["label", "current", "previous"]].itertuples(index=False, name=None))

    return extracted, None



