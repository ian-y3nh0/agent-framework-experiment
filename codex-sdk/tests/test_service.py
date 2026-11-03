import importlib.util
import os

import pytest
from fastapi.testclient import TestClient


def application():
    assert importlib.util.find_spec("main") is not None, "尚未實作 main.py"
    import main

    return main


def test_health_without_credentials(monkeypatch):
    main = application()
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize("prompt", ["", "   ", "\n\t"])
def test_reject_blank_prompt(prompt):
    main = application()
    assert TestClient(main.app).post("/invoke", json={"prompt": prompt}).status_code == 422


def test_invoke_returns_agent_result(monkeypatch):
    main = application()

    async def run(prompt):
        return {"framework": main.FRAMEWORK, "output": "結果：" + prompt}

    monkeypatch.setattr(main, "run_agent", run)
    response = TestClient(main.app).post("/invoke", json={"prompt": "計算"})
    assert response.status_code == 200
    assert response.json()["output"] == "結果：計算"


def test_upstream_error_does_not_expose_secret(monkeypatch):
    main = application()

    async def fail(prompt):
        raise RuntimeError("secret-key-do-not-expose")

    monkeypatch.setattr(main, "run_agent", fail)
    response = TestClient(main.app).post("/invoke", json={"prompt": "測試"})
    assert response.status_code == 502
    assert "secret-key-do-not-expose" not in response.text


def test_timeout_returns_504(monkeypatch):
    main = application()

    async def fail(prompt):
        raise TimeoutError()

    monkeypatch.setattr(main, "run_agent", fail)
    assert TestClient(main.app).post("/invoke", json={"prompt": "測試"}).status_code == 504


def test_settings_precedence_and_no_environment_mutation(tmp_path, monkeypatch):
    assert importlib.util.find_spec("settings") is not None, "尚未實作 settings.py"
    from settings import Settings

    project = tmp_path / "experiment"
    project.mkdir()
    (tmp_path / ".env").write_text(
        "LITELLM_ENDPOINT=http://parent:4000/v1\nLITELLM_API_KEY=parent-key\nLITELLM_MODEL=parent-model\n"
    )
    (project / ".env").write_text("LITELLM_MODEL=child-model\n")
    for key in ("LITELLM_ENDPOINT", "LITELLM_API_KEY", "LITELLM_MODEL", "CODEX_MODEL"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.load(project)
    assert settings.model == "child-model"
    assert settings.endpoint == "http://parent:4000/v1"
    assert "LITELLM_API_KEY" not in os.environ
    monkeypatch.setenv("LITELLM_MODEL", "shell-model")
    assert Settings.load(project).model == "shell-model"
    assert "parent-key" not in repr(settings)


def test_settings_missing_model_is_actionable(tmp_path, monkeypatch):
    assert importlib.util.find_spec("settings") is not None, "尚未實作 settings.py"
    from settings import ConfigurationError, Settings

    monkeypatch.setenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")
    monkeypatch.setenv("LITELLM_API_KEY", "test")
    monkeypatch.delenv("LITELLM_MODEL", raising=False)
    monkeypatch.delenv("CODEX_MODEL", raising=False)
    with pytest.raises(ConfigurationError, match="LITELLM_MODEL"):
        Settings.load(tmp_path)


def test_container_maps_local_gateway_to_host(tmp_path, monkeypatch):
    from settings import Settings

    monkeypatch.setenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")
    monkeypatch.setenv("LITELLM_API_KEY", "test")
    monkeypatch.setenv("LITELLM_MODEL", "test")
    monkeypatch.setenv("AGENT_IN_DOCKER", "1")
    assert Settings.load(tmp_path).endpoint == "http://host.docker.internal:4000/v1"
    monkeypatch.setenv("LITELLM_ENDPOINT", "https://gateway.example/v1")
    assert Settings.load(tmp_path).endpoint == "https://gateway.example/v1"
