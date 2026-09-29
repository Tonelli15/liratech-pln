"""Análise métrica do verso: corte métrico, tonicidade final e nome do metro.

Implementa a partição "Análise de Métrica" do diagrama de atividades (Seção
3.3.3 do TCC), incluindo o algoritmo AplicarCorteMetrico do Quadro 14.
"""

from motor_pln.preprocessamento import limpar_verso
from motor_pln.resultados import AnaliseMetrica
from motor_pln.silabacao import separar_silabas, separar_verso
from motor_pln.sinalefa import aplicar_sinalefas
from motor_pln.tonicidade import (
    OXITONA,
    PAROXITONA,
    PROPAROXITONA,
    TONICIDADES,
    indice_silaba_tonica,
)

# Nome do metro pelo número de sílabas poéticas.
METROS = {
    1: "monossílabo",
    2: "dissílabo",
    3: "trissílabo",
    4: "tetrassílabo",
    5: "redondilha menor",
    6: "hexassílabo",
    7: "redondilha maior",
    8: "octossílabo",
    9: "eneassílabo",
    10: "decassílabo",
    11: "hendecassílabo",
    12: "dodecassílabo",
}
METRO_BARBARO = "verso bárbaro"

# Pronomes átonos que se prendem ao verbo por hífen (entendê-las, amá-lo).
PRONOMES_ENCLITICOS = frozenset({
    "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas",
    "me", "te", "se", "lhe", "lhes", "vos",
})


def escandir_verso(verso: str) -> AnaliseMetrica:
    """Executa a análise métrica completa de um verso.

    Args:
        verso: o verso como o escritor digitou, com pontuação e maiúsculas.

    Returns:
        A análise métrica, com os campos da entidade AnaliseMetrica.

    Raises:
        ValueError: se o verso não contiver nenhuma palavra.
    """
    texto_limpo = limpar_verso(verso)
    if not texto_limpo:
        raise ValueError("O verso não contém palavras.")

    palavras = separar_verso(texto_limpo)
    silabas_poeticas = aplicar_sinalefas(palavras)
    tonicidade = tonicidade_da_ultima_palavra(texto_limpo.split()[-1])
    total = aplicar_corte_metrico(silabas_poeticas, tonicidade)

    return AnaliseMetrica(
        separacao_gramatical=" ".join("-".join(silabas) for silabas in palavras),
        separacao_poetica="-".join(silabas_poeticas),
        total_silabas=total,
        classificacao=classificar_metro(total),
    )


def tonicidade_da_ultima_palavra(palavra: str) -> str:
    """Diz a que distância do fim está a tônica da palavra que fecha o verso.

    Pronomes enclíticos são átonos e apoiam-se fonologicamente na forma verbal,
    comportando-se como se fossem uma de suas sílabas: em "entendê-las" a tônica
    é "dê", com uma átona depois; em "transforma-se" é "for", com duas.

    Esta é a classificação prosódica, que é a que o corte métrico exige. Ela não
    se confunde com a classificação ortográfica: as regras de acentuação gráfica
    desconsideram o pronome átono, e por isso "transforma-se" não recebe acento,
    embora a tônica do conjunto ocupe a antepenúltima posição.

    Nos compostos, como "guarda-chuva", prevalece a tônica do último elemento.
    """
    partes = [parte for parte in palavra.split("-") if parte]
    silabas_encliticas = 0
    while len(partes) > 1 and partes[-1].lower() in PRONOMES_ENCLITICOS:
        partes.pop()
        silabas_encliticas += 1

    silabas = separar_silabas(partes[-1])
    distancia = len(silabas) - 1 - indice_silaba_tonica(silabas) + silabas_encliticas
    if distancia >= len(TONICIDADES):
        raise ValueError(f"Tônica impossível em {palavra!r}.")
    return TONICIDADES[distancia]


def aplicar_corte_metrico(silabas: list[str], tonicidade: str) -> int:
    """Conta as sílabas poéticas de um verso.

    Args:
        silabas: sílabas do verso, já com a hifenização e as sinalefas aplicadas.
        tonicidade: tonicidade da última palavra do verso.

    Returns:
        O total de sílabas poéticas, sempre maior ou igual a 1.

    Raises:
        ValueError: se a tonicidade for desconhecida ou se o corte resultar em
            uma contagem menor que 1.
    """
    total = len(silabas)

    if tonicidade == OXITONA:
        descartadas = 0
    elif tonicidade == PAROXITONA:
        descartadas = 1
    elif tonicidade == PROPAROXITONA:
        descartadas = 2
    else:
        raise ValueError(f"Tonicidade desconhecida: {tonicidade!r}")

    silabas_poeticas = total - descartadas

    if silabas_poeticas < 1:
        raise ValueError(
            f"Corte maior que o verso: {total} sílaba(s) e tonicidade {tonicidade!r}."
        )

    return silabas_poeticas


def classificar_metro(silabas_poeticas: int) -> str:
    """Dá o nome do metro a partir do total de sílabas poéticas."""
    if silabas_poeticas < 1:
        raise ValueError("O verso precisa ter ao menos uma sílaba poética.")
    return METROS.get(silabas_poeticas, METRO_BARBARO)