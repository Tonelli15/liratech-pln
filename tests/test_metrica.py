"""Testes da análise métrica (Quadro 14 e partição de métrica do TCC)."""

import pytest

from motor_pln.metrica import (
    OXITONA,
    PAROXITONA,
    PROPAROXITONA,
    aplicar_corte_metrico,
    classificar_metro,
    escandir_verso,
    tonicidade_da_ultima_palavra,
)

# "Amor é fogo que arde sem se ver" (Camões), decassílabo terminado em oxítona.
CAMOES = ["A", "mo", "ré", "fo", "go", "quear", "de", "sem", "se", "ver"]

# "Ora (direis) ouvir estrelas! Certo" (Bilac), decassílabo terminado em paroxítona.
BILAC = ["O", "ra", "di", "reis", "ou", "vir", "es", "tre", "las", "Cer", "to"]


# --- Corte métrico (Quadro 14) ---------------------------------------------

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


# --- Tonicidade da última palavra (ênclise e compostos) ----------------------

@pytest.mark.parametrize("palavra, esperada", [
    ("amor", OXITONA),
    ("entendê-las", PAROXITONA),       # tônica em "dê": uma átona depois
    ("amá-lo", PAROXITONA),
    ("transforma-se", PROPAROXITONA),  # tônica em "for": duas átonas depois
    ("guarda-chuva", PAROXITONA),      # vale o último elemento
    ("beija-flor", OXITONA),
])
def test_tonicidade_da_ultima_palavra(palavra, esperada):
    # Classificação prosódica, que é a exigida pelo corte métrico: conta as
    # átonas posteriores à tônica. Não se confunde com a acentuação gráfica,
    # que desconsidera o pronome enclítico ("transforma-se" não leva acento).
    assert tonicidade_da_ultima_palavra(palavra) == esperada


# --- Nome do metro -------------------------------------------------------

@pytest.mark.parametrize("silabas, metro", [
    (5, "redondilha menor"),
    (7, "redondilha maior"),
    (10, "decassílabo"),
    (12, "dodecassílabo"),
    (14, "verso bárbaro"),
])
def test_classificar_metro(silabas, metro):
    assert classificar_metro(silabas) == metro


def test_metro_de_zero_silabas_gera_erro():
    with pytest.raises(ValueError):
        classificar_metro(0)


# --- Análise completa do verso -------------------------------------------

@pytest.mark.parametrize("verso, total, metro", [
    ("Ora (direis) ouvir estrelas! Certo", 10, "decassílabo"),         # Bilac
    ('E eu vos direi: "Amai para entendê-las!"', 10, "decassílabo"),   # Bilac
    ("Transforma-se o amador na cousa amada,", 10, "decassílabo"),     # Camões
    ("Última flor do Lácio, inculta e bela,", 10, "decassílabo"),      # Bilac
    ("Minha terra tem palmeiras,", 7, "redondilha maior"),             # Gonçalves Dias
    ("Onde canta o Sabiá;", 7, "redondilha maior"),                    # Gonçalves Dias
])
def test_escandir_verso(verso, total, metro):
    analise = escandir_verso(verso)
    assert analise.total_silabas == total
    assert analise.classificacao == metro


def test_escandir_verso_preenche_as_separacoes():
    analise = escandir_verso("Amor é fogo que arde sem se ver")
    assert analise.separacao_gramatical == "a-mor é fo-go que ar-de sem se ver"
    assert analise.separacao_poetica == "a-mor-é-fo-go-quear-de-sem-se-ver"


def test_verso_sem_palavras_gera_erro():
    with pytest.raises(ValueError):
        escandir_verso("...!")