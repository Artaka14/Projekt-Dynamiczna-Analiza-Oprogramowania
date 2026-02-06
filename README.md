# XD PROJEKT  
### Desktopowa aplikacja do analizy akcji CD PROJEKT S.A.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/Artaka14/Projekt-Dynamiczna-Analiza-Oprogramowania)

**XD PROJEKT** to aplikacja desktopowa napisana w Pythonie, której celem jest monitorowanie kursu akcji CD PROJEKT S.A., analiza historycznych zmian cen oraz zestawienie danych giełdowych z zainteresowaniem użytkowników w Internecie (Google Trends).  
Aplikacja umożliwia również pobieranie i przegląd podstawowych raportów finansowych spółki.

---

## 📄 Dokumentacja

Projekt posiada dwie uzupełniające się dokumentacje:

- **Dokumentacja techniczna aplikacji**  
  Zawiera opis funkcjonalności, architektury, struktury kodu oraz zastosowanych rozwiązań technicznych.  
  📁 [`Dokumentacja`](./Dokumentacja)

- **Dynamiczna analiza oprogramowania**  
  Obejmuje testy jednostkowe, integracyjne, funkcjonalne (GUI), wydajnościowe oraz analizę stabilności aplikacji.  
  📄 [`Dynamiczna Analiza Oprogramowania`](./Dynamiczna%20Analiza%20Oprogramowania.pdf)

## 🎯 Cel projektu

Projekt został zrealizowany jako połączenie:
- praktycznej analizy danych giełdowych,
- wizualizacji danych,
- pracy z API zewnętrznymi,
- oraz dynamicznej analizy i testowania aplikacji desktopowej.

Aplikacja kładzie duży nacisk na **stabilność**, **wydajność** i **bezpieczeństwo danych** (cache, obsługa błędów, testy).

---

## 🚀 Główne funkcjonalności

### 📈 Analiza kursu akcji
- pobieranie **aktualnej ceny akcji CD PROJEKT S.A.**
- wykresy cen dla zakresów:
  - ostatni dzień
  - ostatni tydzień
  - ostatni miesiąc
  - dowolny zakres dat wybrany z kalendarza
- automatyczne wyliczanie **ceny minimalnej i maksymalnej** dla wybranego okresu

### 🔍 Google Trends
- wizualizacja zainteresowania w czasie dla wybranych słów kluczowych:
  - `CD Projekt`
  - `Cyberpunk 2077`
  - `Wiedźmin`
- obsługa zakresów czasowych (dzień / tydzień / miesiąc)
- mechanizm **cache**, ograniczający liczbę zapytań do Google Trends

### 📄 Raporty finansowe
- pobieranie dokumentów spółki w formatach:
  - PDF (raporty i informacje prasowe)
  - XLSX (dane finansowe)
- prezentacja **tabeli z kluczowymi danymi liczbowymi** dla wybranego kwartału
- porównanie danych z analogicznym okresem poprzedniego roku

---

## 🧠 Architektura aplikacji

Aplikacja została podzielona na logiczne moduły zgodnie z zasadą separacji odpowiedzialności:

| Moduł | Opis |
|-----|-----|
| **App** | Główna klasa aplikacji, zarządza ekranami |
| **Screen1** | Analiza i wykresy kursu akcji |
| **Screen2** | Wykresy Google Trends |
| **Screen3** | Obsługa raportów kwartalnych |
| **CDPdata** | Pobieranie danych, obsługa API i cache |
| **CDPplot** | Generowanie i osadzanie wykresów |
| **SplashScreen** | Ekran startowy i preload danych |

---

## 🗂 Cache i obsługa danych

- dane zapisywane lokalnie w formacie **JSON**
- automatyczna obsługa:
  - uszkodzonych plików cache (backup i reset),
  - unieważniania wpisów,
  - fallbacku do danych lokalnych w razie błędów API
- sanitacja nazw plików (ochrona przed path traversal)

Dzięki temu aplikacja:
- działa szybciej,
- jest odporna na limity API,
- nie blokuje interfejsu przy problemach sieciowych.

---

## 🧪 Testy i dynamiczna analiza

Projekt został objęty rozbudowanym zestawem testów:

### ✅ Testy jednostkowe
- zapis i odczyt cache,
- obsługa błędnych i pustych danych JSON,
- konwersja danych do `DataFrame`,
- unieważnianie wpisów cache.

### 🔗 Testy integracyjne
- współpraca Google Trends z cache,
- fallback do danych lokalnych przy błędzie API,
- weryfikacja ograniczenia liczby zapytań.

### 🖥 Testy funkcjonalne (GUI)
- poprawne renderowanie wykresów,
- obsługa odświeżania danych,
- komunikaty błędów w interfejsie,
- walidacja zakresów dat (w tym daty przyszłe).

### ⚡ Testy wydajnościowe
- szybki odczyt dużych zbiorów danych z cache (poniżej 50 ms).

---

## ⚙️ Wymagania i instalacja

### Wymagania
- Python 3.11 lub nowszy
- Połączenie z Internetem (do pobierania danych giełdowych i trendów)

### Instalacja krok po kroku

1. Sprawdź wersję Pythona:
```bash
python --version
```
Jeżeli wersja jest niższa niż 3.11, pobierz nowszą ze strony https://www.python.org

2. Pobierz pliki apliakcji z folderu KodAplikacji

3. Zainstaluj wymagane biblioteki:
```bash
pip install --upgrade pip
pip install -r req.txt
```

4. Uruchom aplikację:
```bash
python main.py
```

## ⚠️ Zagrożenia i zastosowane rozwiązania

- **Limity zapytań Google Trends (HTTP 429)**  
  Zbyt duża liczba zapytań w krótkim czasie może skutkować blokadą dostępu do API.  
  **Rozwiązanie:** zastosowanie pamięci podręcznej (cache) w formacie JSON oraz ograniczenie liczby zapytań.

- **Limity serwisu Yahoo Finance**  
  Serwis wprowadza dzienne limity zapytań dla jednego adresu IP.  
  **Rozwiązanie:** zapisywanie danych historycznych w cache oraz pobieranie danych w większych interwałach czasowych.

- **Uszkodzenie plików cache (JSON)**  
  Niepoprawny zapis danych może prowadzić do błędów podczas uruchamiania aplikacji.  
  **Rozwiązanie:** obsługa wyjątków, tworzenie kopii zapasowych oraz automatyczne czyszczenie uszkodzonych plików.

- **Niebezpieczne pobieranie plików z internetu**  
  Pobieranie plików PDF lub XLSX bez weryfikacji może stanowić zagrożenie bezpieczeństwa.  
  **Rozwiązanie:** sprawdzanie typu pliku, rozmiaru oraz zapisywanie danych wyłącznie w wybranym katalogu.

- **Brak odpowiedzi serwisów zewnętrznych (timeouty)**  
  Problemy sieciowe mogą powodować zawieszenie aplikacji.  
  **Rozwiązanie:** ustawienie limitów czasowych zapytań oraz fallback do danych zapisanych lokalnie.

---

## 📝 Historia rozwoju

- **27.10.2025** – podział aplikacji na moduły, dodanie obsługi zakresów dat oraz integracja bibliotek CTkMessagebox i tkcalendar.  
- **02.11.2025** – dodanie obsługi Google Trends oraz integracja biblioteki pytrends.  
- **09.11.2025** – zapis danych trendów do plików JSON oraz podział aplikacji na trzy niezależne ekrany.  
- **16.11.2025** – rozszerzenie wykresów Google Trends o frazy „Cyberpunk 2077” i „Wiedźmin”, dodanie pobierania raportów finansowych.  
- **23.11.2025** – poprawki i uzupełnienia dokumentacji.  
- **01.12.2025** – dodanie tabel z danymi kwartalnymi oraz testów jednostkowych i integracyjnych.  
- **08.12.2025** – przeprowadzenie testów wydajnościowych i funkcjonalnych.
- **15.12.2025** - sfinalizowanie dokumentacji i skończenie rozwoju projektu

---

## 👨‍💻 Autorzy

- **Dariusz Kołodziejczyk**  
- **Mikołaj Maliszewski**
