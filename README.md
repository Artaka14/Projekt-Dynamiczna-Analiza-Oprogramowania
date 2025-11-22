# 📊 XD Projekt – Aplikacja do analizy kursu CD PROJEKT S.A.

Aplikacja napisana w Pythonie umożliwiająca analizę kursu akcji CD PROJEKT S.A. z wykorzystaniem danych z:

* Yahoo Finance
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
* obsługa cache w JSO
