"""Testes da etiquetagem morfológica (partição de Análise de Rima do TCC)."""

import pytest

from motor_pln.morfologia import (
    CLASSE_INDEFINIDA,
    carregar_modelo,
    classe_gramatical,
    etiquetar_palavra_final,
)
from motor_pln.preprocessamento import limpar_verso


# --- Mapeamento das etiquetas (não depende do modelo) ----------------------

@pytest.mark.parametrize("etiqueta, classe", [
    ("NOUN", "substantivo"),
    ("PROPN", "substantivo"),   # próprio e comum são a mesma classe
    ("VERB", "verbo"),
    ("AUX", "verbo"),           # auxiliar e principal são a mesma classe
    ("ADJ", "adjetivo"),
    ("ADV", "advérbio"),
    ("CCONJ", "conjunção"),
    ("SCONJ", "conjunção"),
])
def test_classe_gramatical(etiqueta, classe):
    assert classe_gramatical(etiqueta) == classe


def test_etiqueta_fora_do_mapeamento_e_indefinida():
    assert classe_gramatical("INEXISTENTE") == CLASSE_INDEFINIDA


# --- Extração da palavra final (usa o modelo) ------------------------------

@pytest.mark.parametrize("verso, palavra, classe", [
    ("Minha terra tem palmeiras,", "palmeiras", "substantivo"),
    ("Onde canta o Sabiá;", "Sabiá", "substantivo"),
    ("Última flor do Lácio, inculta e bela,", "bela", "adjetivo"),
    ("Repousa lá no Céu eternamente,", "eternamente", "advérbio"),
])
def test_etiquetar_palavra_final(verso, palavra, classe):
    etiqueta = etiquetar_palavra_final(verso)
    assert etiqueta.palavra == palavra
    assert etiqueta.classe_gramatical == classe


def test_a_pontuacao_final_e_ignorada():
    assert etiquetar_palavra_final("Ora (direis) ouvir estrelas!").palavra == "estrelas"


def test_a_enclise_permanece_num_unico_token():
    etiqueta = etiquetar_palavra_final('E eu vos direi: "Amai para entendê-las!"')
    assert etiqueta.palavra == "entendê-las"
    assert etiqueta.classe_gramatical == "verbo"


def test_verso_sem_palavras_gera_erro():
    with pytest.raises(ValueError):
        etiquetar_palavra_final("...!")


def test_o_modelo_e_carregado_uma_unica_vez():
    assert carregar_modelo() is carregar_modelo()


def test_o_texto_original_desambigua_melhor_que_o_normalizado():
    """Justifica a decisão de enviar ao spaCy o texto original, e não o limpo.

    Com a maiúscula preservada, "Sabiá" é reconhecido como substantivo; no
    texto normalizado, o modelo perde essa pista e erra a classe.
    """
    verso = "Onde canta o Sabiá;"
    assert etiquetar_palavra_final(verso).classe_gramatical == "substantivo"
    assert etiquetar_palavra_final(limpar_verso(verso)).classe_gramatical != "substantivo"