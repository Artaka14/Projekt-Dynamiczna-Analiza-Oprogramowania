# 📊 XD Projekt – Aplikacja do analizy kursu CD PROJEKT S.A.

Aplikacja napisana w Pythonie umożliwiająca analizę kursu akcji CD PROJEKT S.A. z wykorzystaniem danych z:

* Yahoo Finance (yfinances)
* Google Trends (Pytrends)

Pozwala na wyświetlanie wykresów kursu z różnych zakresów czasowych oraz bieżącej ceny, a także trendów popularności związanych ze spółką.

---

## 🚀 Funkcje

✔ Splash screen z ładowaniem danych
✔ Wykres kursu z wyborem zakresu:

* 1 dzień
* 1 tydzień
* 1 miesiąc
* dowolny zakres dat

✔ Prezentacja popularności fraz z Google Trends
✔ Możliwość porównywania trendów związanych z:

* CD Projekt S.A.
* Cyberpunk 2077
* Wiedźmin

✔ Cache danych zapisywany w JSON (zapobiega limitom API)

---

## 🧰 Wymagania

Python **3.11.9**
Wymagane biblioteki:

```
yfinance
matplotlib
Pillow
customtkinter
CtkMessagebox
tkcalendar
pytrends
```

Instalacja zależności:

```
pip install -r req.txt
```

---

## 🏗 Struktura aplikacji

### **CDPdata**

Obsługa pobierania danych:

* `GetCdpData(period)` – pobieranie danych dla wybranego okresu
* `getCustomCDPData(start, end)` – dane dla własnego zakresu
* `GetCurrentPrice()` – obecna cena akcji
* `getMinMaxPrice(data)` – minimalna i maksymalna cena
* obsługa cache w JSON
* pobieranie danych z Google Trends

### **CDPplot**

Generowanie wykresów:

* wykres kursu akcji
* wykresy trendów Google Trends

### **SplashScreen**

Ekran startowy i ładowanie wstępnych danych.

### **App**

Główne okno aplikacji i zmiana ekranów.

### **Screen1**

Wykres kursu akcji z opcjami zmiany zakresu.

### **Screen2**

Wykresy i dane z Google Trends.

---

## 🆕 Najważniejsze aktualizacje

### **16.11.2025**

* dodano wykresy trendów Cyberpunk 2077 i Wiedźmin

### **09.11.2025**

* zapisywanie danych Google Trends w JSON
* aplikacja podzielona na 3 ekrany

### **02.11.2025**

* dodano obsługę pytrends

### **27.10.2025**

* aplikacja dzielona na moduły
* wprowadzono wybór własnego zakresu dat

---

## ⚠ Potencjalne problemy

### 🔴 Błąd 429 – Google Trends

* wynika ze zbyt wielu zapytań
* cache pozwala dalej korzystać z aplikacji

### 🟠 Limity Yahoo Finance

* maksymalnie ok. 2000 zapytań dziennie

### 🟡 JSON

* możliwe błędy odczytu i zapisu
* wymagają obsługi wyjątków

---

## 📎 Autor

Aplikacja stworzona w ramach projektu do analizy danych giełdowych i popularności w internecie.

