"""Corte métrico: converte a divisão silábica de um verso em sílabas poéticas.

Implementa o algoritmo AplicarCorteMetrico (Quadro 14 do TCC), que traduz a regra
literária de que a contagem de um verso se encerra na última sílaba tônica
(GOLDSTEIN, 2006).
"""

from motor_pln.tonicidade import OXITONA, PAROXITONA, PROPAROXITONA

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