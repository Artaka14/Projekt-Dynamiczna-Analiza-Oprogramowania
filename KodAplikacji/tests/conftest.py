import pytest

@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Każdy test dostaje własny folderinio"""
    fake_cache_dir = tmp_path / "cache"
    fake_cache_dir.mkdir()

    monkeypatch.setattr("CDPdata.CACHE_DIR", str(fake_cache_dir))
    monkeypatch.setattr("CDPdata.CACHE_FILE", str(fake_cache_dir / "trends_cache.json"))

    yield  # test działa