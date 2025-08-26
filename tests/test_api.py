import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app import app
from src.agente_ia import ResearchWorkflow, ContentGeneratorAgent, ImageGeneratorTool


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_generate_success(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ResearchWorkflow, "__init__", lambda self: None)

    def fake_run(self, tema, generate_image=True, estilo_imagem="realista", tamanho=None):
        return {
            "tema": tema,
            "data_geracao": "2024-01-01T00:00:00",
            "conteudo": {
                "titulo": "Titulo",
                "subtitulo": "Sub",
                "conteudo": "Texto",
                "imagem": {"local_path": "/tmp/img.png"},
            },
            "workflow_version": "test",
        }

    monkeypatch.setattr(ResearchWorkflow, "run", fake_run)
    monkeypatch.setattr(ResearchWorkflow, "save_results", lambda self, data, output_dir="output": None)

    response = client.post(
        "/api/generate",
        json={"tema": "IA", "gerar_imagem": True, "estilo_imagem": "realista"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["conteudo"]["titulo"] == "Titulo"
    assert data["conteudo"]["imagem"]["public_url"].endswith("img.png")


def test_generate_missing_api_key(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/api/generate", json={"tema": "IA"})
    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_regenerate_text_success(client, monkeypatch):
    monkeypatch.setattr(ContentGeneratorAgent, "__init__", lambda self: None)

    def fake_generate(self, tema, generate_image=False, estilo_imagem="realista", tamanho=None):
        return {"titulo": "Titulo", "subtitulo": "Sub", "conteudo": "Texto"}

    monkeypatch.setattr(ContentGeneratorAgent, "generate_structured_content", fake_generate)
    response = client.post("/api/regenerate-text", json={"tema": "IA"})
    assert response.status_code == 200
    data = response.json()
    assert data["conteudo"]["titulo"] == "Titulo"


def test_regenerate_text_failure(client, monkeypatch):
    monkeypatch.setattr(ContentGeneratorAgent, "__init__", lambda self: None)

    def fake_generate(self, *args, **kwargs):
        raise Exception("boom")

    monkeypatch.setattr(ContentGeneratorAgent, "generate_structured_content", fake_generate)
    response = client.post("/api/regenerate-text", json={"tema": "IA"})
    assert response.status_code == 500
    assert "Erro ao gerar texto" in response.json()["detail"]


def test_regenerate_image_success(client, monkeypatch):
    monkeypatch.setattr(ImageGeneratorTool, "__init__", lambda self: None)

    def fake_image(self, *args, **kwargs):
        return {"local_path": "/tmp/img.png"}

    monkeypatch.setattr(ImageGeneratorTool, "generate_image", fake_image)
    response = client.post("/api/regenerate-image", json={"titulo": "Titulo"})
    assert response.status_code == 200
    data = response.json()
    assert data["imagem"]["public_url"].endswith("img.png")


def test_regenerate_image_failure(client, monkeypatch):
    monkeypatch.setattr(ImageGeneratorTool, "__init__", lambda self: None)

    def fake_image(self, *args, **kwargs):
        return None

    monkeypatch.setattr(ImageGeneratorTool, "generate_image", fake_image)
    response = client.post("/api/regenerate-image", json={"titulo": "Titulo"})
    assert response.status_code == 200
    data = response.json()
    assert data["imagem"] is None
    assert "Falha ao gerar imagem" in data["error"]
