from CDPdata import load_cache, save_cache, invalidate_trends_period

def test_save_and_load_cache():
    data = {"test": {"7d": {"json": "{}", "period": "7d"}}}
    save_cache(data)

    loaded = load_cache()
    assert loaded == data


def test_invalid_json_moves_file(tmp_path, monkeypatch):
    import importlib
    mod = importlib.import_module("CDPdata")
    
    moved = []
    def fake_replace(src, dst):
        moved.append((src, dst))
    
    monkeypatch.setattr(mod.os, "replace", fake_replace)
    
    # teraz stwórz uszkodzony plik w CACHE_FILE
    with open(mod.CACHE_FILE, "w", encoding="utf-8") as f:
        f.write("{zlezlezle}")
    
    cache = mod.load_cache()
    assert cache == {}
    assert len(moved) == 1


def test_invalidate_removes_entry():
    data = {"bitcoin": {"7d": {"json": "{}", "period": "7d"}}}
    save_cache(data)

    invalidate_trends_period("bitcoin", "7d")

    loaded = load_cache()
    assert loaded == {}