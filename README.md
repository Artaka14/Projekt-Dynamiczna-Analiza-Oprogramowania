# XD PROJEKT – Aplikacja do monitorowania akcji CD PROJEKT S.A.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/Artaka14/Projekt-Dynamiczna-Analiza-Oprogramowania)

XD PROJEKT to aplikacja desktopowa napisana w Pythonie, służąca do śledzenia cen akcji CD PROJEKT S.A., analizy trendów oraz pobierania raportów finansowych spółki.

---

## 🚀 Funkcjonalności

* **Monitorowanie bieżącej ceny akcji CD PROJEKT S.A.**
* **Wykresy kursu akcji** dla wybranych okresów:

  * ostatni dzień
  * ostatni tydzień
  * ostatni miesiąc
  * dowolny zakres wybrany z kalendarza
* **Wykresy popularności w Google Trends** dla słów kluczowych:

  * `CD Projekt`
  * `Cyberpunk 2077`
  * `Wiedźmin`
* **Pobieranie raportów finansowych** spółki w formacie PDF lub XLSX
* **Cache danych** w formacie JSON, aby ograniczyć liczbę zapytań do API

---

## ⚙️ Wymagania

* **Python 3.11+**
* Biblioteki:

  * `yfinance` – pobieranie danych giełdowych
  * `matplotlib` – generowanie wykresów
  * `Pillow` – obsługa grafiki
  * `customtkinter` – nowoczesny interfejs graficzny
  * `CTkMessagebox` – obsługa okien komunikatów
  * `tkcalendar` – wybór zakresu dat
  * `pytrends` – integracja z Google Trends

**Instalacja pakietów:**

```bash
pip install -r req.txt
```

---

## 🏗 Struktura aplikacji

* **App** – główne okno aplikacji, zarządza ekranami
* **Screen1** – wykresy kursu akcji
* **Screen2** – wykresy Google Trends
* **Screen3** – raporty finansowe
* **CDPdata** – logika pobierania danych i cache
* **CDPplot** – generowanie wykresów
* **SplashScreen** – ekran startowy

---

## 📄 Dokumentacja

Pełną dokumentację aplikacji znajdziesz w folderze: [Dokumentacja](./Dokumentacja)

---

## ⚠️ Zagrożenia i rozwiązania

* **Błąd 429 Google Trends** – stosowanie cache i ograniczenie liczby zapytań
* **Limity Yahoo Finance** – cache danych i interwały pobierania
* **Problemy z plikami JSON** – obsługa wyjątków, backup uszkodzonych plików
* **Bezpieczeństwo pobierania plików PDF/XLSX** – walidacja typu i rozmiaru pliku
* **Timeouty w zapytaniach sieciowych** – ustawienie timeoutów i obsługa wyjątków

---

## 📝 Aktualizacje

| Data       | Zmiany                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------ |
| 27.10.2025 | Podział aplikacji na moduły, dodanie funkcji zakresów dat, nowe biblioteki: CTkMessagebox i tkcalendar |
| 02.11.2025 | Integracja pytrends, obsługa wykresów Google Trends                                                    |
| 09.11.2025 | Zapis trendów do JSON, podział aplikacji na 3 ekrany                                                   |
| 16.11.2025 | Wykresy Google Trends dla Cyberpunk 2077 i Wiedźmina, pobieranie sprawozdań finansowych                |
| 23.11.2025 | Poprawki w dokumentacji                                                                                |

---

## 💻 Uruchomienie aplikacji

1. Sklonuj repozytorium:

```bash
git clone <URL_REPOZYTORIUM>
cd <NAZWA_FOLDERU>
```

2. Zainstaluj wymagane pakiety:

```bash
pip install -r req.txt
```

3. Uruchom aplikację:

```bash
python main.py
```

---

## 📬 Kontakt

Autorzy projektu:

* Dariusz Kołodziejczyk
* Sebastian Bek
* Mikołaj Maliszewski


