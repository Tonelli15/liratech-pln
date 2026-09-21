"""Identificação da sílaba tônica a partir da grafia (Seção 3.3.3 do TCC).

As regras de acentuação do português dizem quando uma palavra recebe acento.
Aplicadas ao contrário, elas revelam a sílaba tônica de qualquer palavra.
"""

OXITONA = "oxítona"
PAROXITONA = "paroxítona"
PROPAROXITONA = "proparoxítona"

# A posição na tupla é a distância da tônica até o fim da palavra.
TONICIDADES = (OXITONA, PAROXITONA, PROPAROXITONA)

ACENTOS_TONICOS = "áéíóúâêô"
TIL = "ãõ"

# Sem acento gráfico, palavras com estas terminações são paroxítonas.
TERMINACOES_PAROXITONAS = ("a", "e", "o", "as", "es", "os", "am", "em", "ens")

# Sufixos que conservam o til da palavra original, mas levam a tônica para si.
SUFIXOS_QUE_ANULAM_O_TIL = ("mente", "zinho", "zinha", "zinhos", "zinhas")


def indice_silaba_tonica(silabas: list[str]) -> int:
    """Encontra a sílaba tônica de uma palavra.

    Args:
        silabas: as sílabas de uma única palavra, como devolvidas pela silabação.

    Returns:
        A posição da sílaba tônica na lista, contada a partir de 0.

    Raises:
        ValueError: se a lista de sílabas estiver vazia.
    """
    if not silabas:
        raise ValueError("A palavra precisa ter ao menos uma sílaba.")
    if len(silabas) == 1:
        return 0

    minusculas = [silaba.lower() for silaba in silabas]
    palavra = "".join(minusculas)

    indice = _primeira_silaba_com(minusculas, ACENTOS_TONICOS)
    if indice is not None:
        return indice

    if not palavra.endswith(SUFIXOS_QUE_ANULAM_O_TIL):
        indice = _primeira_silaba_com(minusculas, TIL)
        if indice is not None:
            return indice

    if palavra.endswith(TERMINACOES_PAROXITONAS):
        return len(silabas) - 2
    return len(silabas) - 1


def classificar_tonicidade(silabas: list[str]) -> str:
    """Classifica uma palavra em oxítona, paroxítona ou proparoxítona.

    Raises:
        ValueError: se a tônica cair antes da antepenúltima sílaba, o que não
            existe em português e indica erro na separação silábica.
    """
    distancia_do_fim = len(silabas) - 1 - indice_silaba_tonica(silabas)
    if distancia_do_fim >= len(TONICIDADES):
        raise ValueError(f"Tônica impossível em {'-'.join(silabas)!r}.")
    return TONICIDADES[distancia_do_fim]


def _primeira_silaba_com(silabas: list[str], marcas: str) -> int | None:
    """Devolve a posição da primeira sílaba que contém uma das marcas, ou None."""
    for indice, silaba in enumerate(silabas):
        if any(letra in marcas for letra in silaba):
            return indice
    return None