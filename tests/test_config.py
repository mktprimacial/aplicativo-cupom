from app.config import load_settings


def test_load_settings_trims_required_env(monkeypatch):
    monkeypatch.setenv("NUVEMSHOP_APP_ID", " 123 ")
    monkeypatch.setenv("NUVEMSHOP_CLIENT_SECRET", " secret\n")

    settings = load_settings()

    assert settings.app_id == "123"
    assert settings.client_secret == "secret"


def test_load_settings_rejects_whitespace_only(monkeypatch):
    monkeypatch.setenv("NUVEMSHOP_APP_ID", "   ")
    monkeypatch.setenv("NUVEMSHOP_CLIENT_SECRET", "   ")

    try:
        load_settings()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert str(exc) == "NUVEMSHOP_APP_ID is required"

    monkeypatch.setenv("NUVEMSHOP_APP_ID", "abc")
    monkeypatch.setenv("NUVEMSHOP_CLIENT_SECRET", "   ")

    try:
        load_settings()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert str(exc) == "NUVEMSHOP_CLIENT_SECRET is required"
