"""Testes da identificação da sílaba tônica (Seção 3.3.3 do TCC)."""

import pytest

from motor_pln.silabacao import separar_silabas
from motor_pln.tonicidade import (
    OXITONA,
    PAROXITONA,
    PROPAROXITONA,
    classificar_tonicidade,
    indice_silaba_tonica,
)

CASOS = [
    # Regra 1: monossílabos
    ("sol", OXITONA),
    ("mar", OXITONA),
    # Regra 2: acento agudo ou circunflexo
    ("café", OXITONA),
    ("você", OXITONA),
    ("fácil", PAROXITONA),
    ("história", PAROXITONA),
    ("série", PAROXITONA),
    ("lâmpada", PROPAROXITONA),
    ("música", PROPAROXITONA),
    ("órgão", PAROXITONA),
    # Regra 3: til, na ausência de agudo e circunflexo
    ("coração", OXITONA),
    ("irmã", OXITONA),
    ("mãezinha", PAROXITONA),
    ("cristãmente", PAROXITONA),
    # Regra 4: sem acento, terminações paroxítonas
    ("casa", PAROXITONA),
    ("homem", PAROXITONA),
    ("jovens", PAROXITONA),
    ("cantam", PAROXITONA),
    ("rainha", PAROXITONA),
    ("poesia", PAROXITONA),
    ("àquela", PAROXITONA),
    # Regra 5: sem acento, demais terminações
    ("amor", OXITONA),
    ("papel", OXITONA),
    ("feliz", OXITONA),
    ("tupi", OXITONA),
    ("jardim", OXITONA),
    ("juiz", OXITONA),
    ("animais", OXITONA),
]


@pytest.mark.parametrize("palavra, esperada", CASOS)
def test_classificar_tonicidade(palavra, esperada):
    assert classificar_tonicidade(separar_silabas(palavra)) == esperada


def test_indice_e_contado_a_partir_do_inicio():
    assert indice_silaba_tonica(["co", "ra", "ção"]) == 2
    assert indice_silaba_tonica(["lâm", "pa", "da"]) == 0


def test_lista_vazia_gera_erro():
    with pytest.raises(ValueError):
        indice_silaba_tonica([])


def test_tonica_antes_da_antepenultima_gera_erro():
    with pytest.raises(ValueError):
        classificar_tonicidade(["á", "ba", "ca", "te"])