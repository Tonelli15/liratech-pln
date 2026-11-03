"""Testes do microsserviço HTTP (Seção 3.3.5 do TCC)."""

import pytest
from fastapi.testclient import TestClient

from motor_pln import __version__
from motor_pln.morfologia import MODELO_PADRAO, carregar_modelo
from servico.contrato import TAMANHO_MAXIMO_VERSO
from servico.main import app


@pytest.fixture(scope="module")
def cliente():
    """Cliente HTTP de teste, com o ciclo de vida do serviço ativo."""
    with TestClient(app) as cliente_http:
        yield cliente_http


def test_analisa_um_verso(cliente):
    resposta = cliente.post("/analises", json={"verso": "Amor é fogo que arde sem se ver;"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["analiseMetrica"]["totalSilabas"] == 10
    assert corpo["analiseRima"]["fonemaTonico"] == "er"


def test_analise_parcial_devolve_null_e_aviso(cliente):
    corpo = cliente.post("/analises", json={"verso": "Eram três rosas, eram 3"}).json()
    assert corpo["analiseRima"] is None
    assert len(corpo["avisos"]) == 1


@pytest.mark.parametrize("corpo", [
    {"verso": "...!"},                             # sem palavras
    {"verso": "   "},                              # só espaços
    {"verso": "x" * (TAMANHO_MAXIMO_VERSO + 1)},   # longo demais
    {"texto": "Amor é fogo"},                      # nome de campo errado
    {},                                            # corpo vazio
])
def test_requisicao_invalida_recebe_422(cliente, corpo):
    resposta = cliente.post("/analises", json=corpo)
    assert resposta.status_code == 422
    assert isinstance(resposta.json()["detail"], list)  # mesmo formato em todos os erros


def test_verificacao_de_saude(cliente):
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok", "versaoMotor": __version__, "modeloSpacy": MODELO_PADRAO,
    }


def test_o_modelo_e_carregado_na_inicializacao():
    carregar_modelo.cache_clear()
    with TestClient(app):
        assert carregar_modelo.cache_info().currsize == 1


def test_a_documentacao_openapi_e_gerada(cliente):
    esquema = cliente.get("/openapi.json").json()
    assert set(esquema["paths"]) == {"/analises", "/saude"}
    assert esquema["info"]["version"] == __version__