"""Testes do ponto de entrada do motor (partição de Consolidação do TCC)."""

import pytest

from motor_pln import __version__
from motor_pln.morfologia import MODELO_PADRAO
from motor_pln.motor import analisar_verso


def test_analise_completa_de_um_verso():
    analise = analisar_verso("Amor é fogo que arde sem se ver;")
    assert analise.texto_limpo == "amor é fogo que arde sem se ver"
    assert analise.analise_metrica.total_silabas == 10
    assert analise.analise_metrica.classificacao == "decassílabo"
    assert analise.analise_rima.fonema_tonico == "er"
    assert analise.analise_rima.classe_gramatical == "verbo"
    assert analise.avisos == ()


def test_registra_a_versao_do_motor_e_o_modelo():
    analise = analisar_verso("Minha terra tem palmeiras,")
    assert analise.versao_motor == __version__
    assert analise.modelo_spacy == MODELO_PADRAO


def test_falha_de_uma_analise_nao_impede_a_outra():
    """O verso termina em número: a rima falha, mas a métrica é devolvida."""
    analise = analisar_verso("Eram três rosas, eram 3")
    assert analise.analise_metrica is not None
    assert analise.analise_rima is None
    assert len(analise.avisos) == 1
    assert analise.avisos[0].startswith("Análise de rima indisponível")


def test_verso_sem_palavras_gera_erro():
    with pytest.raises(ValueError):
        analisar_verso("...!")