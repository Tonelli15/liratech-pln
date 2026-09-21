"""Testes da sinalefa (Seção 3.3.3 do TCC)."""

import pytest

from motor_pln.metrica import aplicar_corte_metrico
from motor_pln.silabacao import separar_verso
from motor_pln.sinalefa import aplicar_sinalefas
from motor_pln.tonicidade import classificar_tonicidade


def fundir(verso: str) -> list[str]:
    """Atalho para os testes: separa as sílabas e aplica as sinalefas."""
    return aplicar_sinalefas(separar_verso(verso))


def test_exemplo_do_tcc():
    assert fundir("de amor") == ["dea", "mor"]


def test_vogal_atona_final_funde_com_vogal_inicial():
    assert fundir("Amor é fogo que arde sem se ver") == [
        "A", "mor", "é", "fo", "go", "quear", "de", "sem", "se", "ver",
    ]


def test_h_inicial_nao_impede_a_fusao():
    assert fundir("de homem") == ["deho", "mem"]


def test_fusoes_podem_se_encadear():
    assert fundir("que o amor") == ["queoa", "mor"]


@pytest.mark.parametrize("trecho", [
    "café amargo",     # a vogal final de uma oxítona é tônica
    "dói e",           # monossílabo tônico
    "amor eterno",     # a palavra termina em consoante
    "cantam alegres",  # vogal nasal grafada com m
    "que desatina",    # a palavra seguinte começa por consoante
])
def test_casos_sem_sinalefa(trecho):
    palavras = separar_verso(trecho)
    total_sem_fusao = sum(len(palavra) for palavra in palavras)
    assert len(aplicar_sinalefas(palavras)) == total_sem_fusao


DECASSILABOS = [
    "Amor é fogo que arde sem se ver",             # Camões
    "É ferida que dói e não se sente",             # Camões
    "É solitário andar por entre a gente",         # Camões
    "E viva eu cá na terra sempre triste",         # Camões
    "Direis agora Tresloucado amigo",              # Bilac
    "Perdeste o senso E eu vos direi no entanto",  # Bilac
]


@pytest.mark.parametrize("verso", DECASSILABOS)
def test_decassilabos_classicos_somam_dez_silabas(verso):
    palavras = separar_verso(verso)
    silabas = aplicar_sinalefas(palavras)
    tonicidade = classificar_tonicidade(palavras[-1])
    assert aplicar_corte_metrico(silabas, tonicidade) == 10