"""Testes da separação silábica (Seção 3.2 do TCC)."""

import pytest

from motor_pln.silabacao import separar_silabas, separar_verso

# Casos em que a hifenização do pyphen já coincide com a separação gramatical.
CASOS_DIRETOS = [
    ("amor", ["a", "mor"]),
    ("poesia", ["po", "e", "si", "a"]),
    ("saudade", ["sau", "da", "de"]),
    ("coração", ["co", "ra", "ção"]),
    ("transporte", ["trans", "por", "te"]),
    ("sol", ["sol"]),
]

# Regra 1: hiato antes do dígrafo "nh".
CASOS_REGRA_1 = [
    ("rainha", ["ra", "i", "nha"]),
    ("bainha", ["ba", "i", "nha"]),
    ("campainha", ["cam", "pa", "i", "nha"]),
]

# Regra 2: í ou ú acentuados logo depois de vogal.
CASOS_REGRA_2 = [
    ("saúde", ["sa", "ú", "de"]),
    ("baú", ["ba", "ú"]),
    ("saída", ["sa", "í", "da"]),
]

# Regra 3: i ou u tônicos sem acento, fechados por l, m, n, r ou z.
CASOS_REGRA_3 = [
    ("juiz", ["ju", "iz"]),
    ("cair", ["ca", "ir"]),
    ("ruim", ["ru", "im"]),
    ("ainda", ["a", "in", "da"]),
    ("possuir", ["pos", "su", "ir"]),
]

# Regra 4: ditongo crescente final em palavra com acento gráfico.
CASOS_REGRA_4 = [
    ("série", ["sé", "rie"]),
    ("espécie", ["es", "pé", "cie"]),
    ("tênue", ["tê", "nue"]),
]

# Ditongos que não podem ser quebrados: protegem as regras contra exageros.
CASOS_DITONGOS = [
    ("baile", ["bai", "le"]),
    ("muito", ["mui", "to"]),
    ("seguinte", ["se", "guin", "te"]),
    ("depois", ["de", "pois"]),
    ("Paulo", ["Pau", "lo"]),
    ("ao", ["ao"]),
    ("copie", ["co", "pi", "e"]),
]


@pytest.mark.parametrize(
    "palavra, esperado",
    CASOS_DIRETOS + CASOS_REGRA_1 + CASOS_REGRA_2 + CASOS_REGRA_3
    + CASOS_REGRA_4 + CASOS_DITONGOS,
)
def test_separacao_silabica(palavra, esperado):
    assert separar_silabas(palavra) == esperado


def test_preserva_a_grafia_original_da_palavra():
    assert separar_silabas("Rainha") == ["Ra", "i", "nha"]


def test_palavra_vazia_gera_erro():
    with pytest.raises(ValueError):
        separar_silabas("   ")


def test_separar_verso_devolve_as_silabas_de_cada_palavra():
    verso = "Amor é fogo que arde sem se ver"
    assert separar_verso(verso) == [
        ["A", "mor"], ["é"], ["fo", "go"], ["que"],
        ["ar", "de"], ["sem"], ["se"], ["ver"],
    ]

def test_palavra_com_hifen_e_separada_por_partes():
    assert separar_silabas("entendê-las") == ["en", "ten", "dê", "las"]
    assert separar_silabas("guarda-chuva") == ["guar", "da", "chu", "va"]