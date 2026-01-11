import pandas as pd
import customtkinter as ctk
from main import Screen1
from datetime import date, timedelta

def test_showPlot_shows_plot(monkeypatch):
    root = ctk.CTk()

    fake_df = pd.DataFrame(
        {"Close": [10, 12, 11]},
        index=pd.date_range("2024-01-01", periods=3)
    )

    calls = {"get": 0, "plot": 0}

    monkeypatch.setattr(
        "CDPdata.getCdpData",
        lambda period: calls.__setitem__("get", calls["get"] + 1) or fake_df
    )

    monkeypatch.setattr(
        "CDPplot.createCdpPlot",
        lambda *args, **kwargs: calls.__setitem__("plot", calls["plot"] + 1)
    )

    monkeypatch.setattr(
        "CDPdata.getCurrentPrice",
        lambda: 123.45
    )

    monkeypatch.setattr(
        "CDPdata.getMinMaxPrice",
        lambda df: (10, 12)
    )
    
    screen = Screen1(root)
    screen.showPlot("7d")
    
    assert calls["get"] == 1
    assert calls["plot"] == 1
    assert screen.price_label_value.cget("text") == "123.45 PLN"
    assert screen.min_label_value.cget("text") == "10 PLN"
    assert screen.max_label_value.cget("text") == "12 PLN"
    
    
def test_custom_date_valid(monkeypatch):
    root = ctk.CTk()

    fake_df = pd.DataFrame(
        {"Close": [100, 110]},
        index=pd.date_range("2024-01-01", periods=2)
    )

    calls = {"data": 0, "plot": 0}

    monkeypatch.setattr(
        "CDPdata.getCustomCdpData",
        lambda start, end: calls.__setitem__("data", calls["data"] + 1) or fake_df
    )

    monkeypatch.setattr(
        "CDPplot.createCustomDataCdpPlot",
        lambda *args, **kwargs: calls.__setitem__("plot", calls["plot"] + 1)
    )

    monkeypatch.setattr(
        "CDPdata.getMinMaxPrice",
        lambda df: (100, 110)
    )

    screen = Screen1(root)

    screen.start_date_entry.set_date(fake_df.index.min().date())
    screen.end_date_entry.set_date(fake_df.index.max().date())

    screen.showCustomDatePlot()

    assert calls["data"] == 1
    assert calls["plot"] == 1
    assert screen.min_label_value.cget("text") == "100 PLN"
    assert screen.max_label_value.cget("text") == "110 PLN"

def test_custom_date_invalid_range(monkeypatch):
    root = ctk.CTk()
    screen = Screen1(root)

    errors = []

    monkeypatch.setattr(
        screen,
        "showError",
        lambda title, message, icon="warning": errors.append((title, message))
    )

    screen.start_date_entry.set_date(date(2024, 5, 10))
    screen.end_date_entry.set_date(date(2024, 5, 1))

    screen.showCustomDatePlot()

    assert len(errors) == 1
    assert "Błędny zakres dat" in errors[0][0]
    
def test_custom_date_future_date(monkeypatch):
    root = ctk.CTk()
    screen = Screen1(root)

    errors = []

    monkeypatch.setattr(
        screen,
        "showError",
        lambda title, message, icon="warning": errors.append((title, message))
    )

    tomorrow = date.today() + timedelta(days=1)

    screen.start_date_entry.set_date(date.today())
    screen.end_date_entry.set_date(tomorrow)

    screen.showCustomDatePlot()

    assert len(errors) == 1
    assert "przyszłości" in errors[0][1]

    root.destroy()