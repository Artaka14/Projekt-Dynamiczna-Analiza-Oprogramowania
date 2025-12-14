import pandas as pd
import customtkinter as ctk
from main import Screen2

def test_trends_screen_shows_plot(monkeypatch):
    df = pd.DataFrame(
        {"CD Projekt": [10, 20, 30]},
        index=pd.date_range("2024-01-01", periods=3)
    )
    monkeypatch.setattr("CDPdata.getTrendsData", lambda keyword, period: df)

    root = ctk.CTk()
    screen = Screen2(root)

    # akcja użytkownika
    screen.showTrendsPlot("7d")

    # coś się narysowało
    widgets = screen.plot_frame.winfo_children()
    assert len(widgets) > 0
    
def test_refresh_forces_reload(monkeypatch):
    calls = {"count": 0}

    def fake_get(keyword, period):
        calls["count"] += 1
        return pd.DataFrame(
            {"CD Projekt": [calls["count"]]},
            index=pd.date_range("2024-01-01", periods=1)
        )

    monkeypatch.setattr("CDPdata.getTrendsData", fake_get)

    root = ctk.CTk()
    screen = Screen2(root)
    
    calls["count"]=0

    screen.showTrendsPlot("7d")
    first = screen.plot_frame.winfo_children()

    screen.refreshTrends()
    second = screen.plot_frame.winfo_children()

    assert calls["count"] == 2
    assert first != second
    
def test_trends_error_message(monkeypatch):
    monkeypatch.setattr(
        "CDPdata.getTrendsData",
        lambda keyword, period: None
    )

    root = ctk.CTk()
    screen = Screen2(root)

    screen.showTrendsPlot("7d")

    labels = [
        w for w in screen.plot_frame.winfo_children()
        if "Nie udało się" in getattr(w, "cget", lambda *_: "")("text")
    ]

    assert len(labels) == 1