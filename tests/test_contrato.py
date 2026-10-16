"""Testes do contrato de dados do microsserviço (formato JSON)."""

import json

import pytest
from pydantic import ValidationError

from motor_pln.motor import analisar_verso
from servico.contrato import TAMANHO_MAXIMO_VERSO, RequisicaoAnalise, para_resposta


def gerar_json(verso: str) -> dict:
    """Atalho: analisa o verso e devolve o JSON da resposta como dicionário."""
    return json.loads(para_resposta(analisar_verso(verso)).model_dump_json())


def test_nomes_dos_campos_seguem_o_contrato():
    """Fixa o formato da resposta: qualquer mudança aqui quebra a API REST."""
    resposta = gerar_json("Amor é fogo que arde sem se ver;")
    assert set(resposta) == {
        "textoLimpo", "analiseMetrica", "analiseRima",
        "avisos", "versaoMotor", "modeloSpacy",
    }
    assert set(resposta["analiseMetrica"]) == {
        "separacaoGramatical", "separacaoPoetica", "totalSilabas", "classificacao",
    }
    assert set(resposta["analiseRima"]) == {
        "palavraFinal", "fonemaTonico", "classeGramatical",
    }


def test_valores_da_resposta():
    resposta = gerar_json("Amor é fogo que arde sem se ver;")
    assert resposta["analiseMetrica"]["totalSilabas"] == 10
    assert resposta["analiseRima"]["fonemaTonico"] == "er"
    assert resposta["avisos"] == []


def test_analise_indisponivel_vira_null():
    resposta = gerar_json("Eram três rosas, eram 3")
    assert resposta["analiseRima"] is None
    assert resposta["analiseMetrica"] is not None


def test_requisicao_remove_espacos_das_pontas():
    assert RequisicaoAnalise(verso="  Amor é fogo  ").verso == "Amor é fogo"


@pytest.mark.parametrize("verso", ["", "     ", "x" * (TAMANHO_MAXIMO_VERSO + 1)])
def test_requisicao_rejeita_verso_vazio_ou_longo_demais(verso):
    with pytest.raises(ValidationError):
        RequisicaoAnalise(verso=verso)