"""Testes do corte métrico (Quadro 14 do TCC)."""

import pytest

from motor_pln.metrica import (
    OXITONA,
    PAROXITONA,
    PROPAROXITONA,
    aplicar_corte_metrico,
)

# "Amor é fogo que arde sem se ver" (Camões), decassílabo terminado em oxítona.
CAMOES = ["A", "mo", "ré", "fo", "go", "quear", "de", "sem", "se", "ver"]

# "Ora (direis) ouvir estrelas! Certo" (Bilac), decassílabo terminado em paroxítona.
BILAC = ["O", "ra", "di", "reis", "ou", "vir", "es", "tre", "las", "Cer", "to"]


def test_oxitona_nao_descarta_silabas():
    assert aplicar_corte_metrico(CAMOES, OXITONA) == 10


def test_paroxitona_descarta_a_ultima_silaba():
    assert aplicar_corte_metrico(BILAC, PAROXITONA) == 10


def test_proparoxitona_descarta_as_duas_ultimas_silabas():
    # "a luz da lâmpada": a contagem para em "lâm".
    silabas = ["a", "luz", "da", "lâm", "pa", "da"]
    assert aplicar_corte_metrico(silabas, PROPAROXITONA) == 4


def test_monossilabo_tonico_conta_como_oxitona():
    assert aplicar_corte_metrico(["sol"], OXITONA) == 1


def test_tonicidade_desconhecida_gera_erro():
    with pytest.raises(ValueError):
        aplicar_corte_metrico(CAMOES, "átona")


def test_corte_maior_que_o_verso_gera_erro():
    with pytest.raises(ValueError):
        aplicar_corte_metrico(["sol"], PAROXITONA)