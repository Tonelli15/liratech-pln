"""Identificação da sílaba tônica a partir da grafia (Seção 3.3.3 do TCC).

As regras de acentuação do português dizem quando uma palavra recebe acento.
Aplicadas ao contrário, elas revelam a sílaba tônica de qualquer palavra.
"""

from motor_pln.silabacao import separar_silabas

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

# Pronomes átonos que se prendem ao verbo por hífen (entendê-las, amá-lo).
PRONOMES_ENCLITICOS = frozenset({
    "o", "a", "os", "as", "lo", "la", "los", "las", "no", "na", "nos", "nas",
    "me", "te", "se", "lhe", "lhes", "vos",
})


def silabas_e_tonica(palavra: str) -> tuple[list[str], int]:
    """Separa a palavra em sílabas e localiza a tônica, tratando o hífen.

    Pronomes enclíticos são átonos e apoiam-se na forma verbal, de modo que a
    tônica permanece no verbo; nos compostos, prevalece a tônica do último
    elemento.

    Args:
        palavra: uma única palavra, podendo conter hífen.

    Returns:
        As sílabas da palavra inteira e a posição da tônica dentro dessa lista.
    """
    partes = [parte for parte in palavra.split("-") if parte]
    if not partes:
        raise ValueError("A palavra não pode ser vazia.")

    nucleo = list(partes)
    while len(nucleo) > 1 and nucleo[-1].lower() in PRONOMES_ENCLITICOS:
        nucleo.pop()

    anteriores = sum(len(separar_silabas(parte)) for parte in nucleo[:-1])
    tonica = anteriores + indice_silaba_tonica(separar_silabas(nucleo[-1]))
    return separar_silabas(palavra), tonica

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