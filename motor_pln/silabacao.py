"""Separação silábica gramatical de palavras em português.

Usa o pyphen como base e corrige os casos em que a hifenização tipográfica
diverge da separação silábica gramatical (Seção 3.2 do TCC).
"""

import re

import pyphen

VOGAIS = "aeiouáéíóúâêôàãõ"
ACENTOS = "áéíóúâêô"

_HIFENIZADOR = pyphen.Pyphen(lang="pt_BR", left=1, right=1)

# Palavras em que o pyphen diverge e não há regra geral que as descreva.
EXCECOES = {
    "ao": ["ao"],
    "aos": ["aos"],
}

# Regra 1: i ou u entre uma vogal e o dígrafo "nh" (rai-nha -> ra-i-nha).
_HIATO_ANTES_DE_NH = re.compile(rf"([{VOGAIS}])(-?)([iu])(-?)(nh)")

# Regra 2: í ou ú acentuados depois de vogal (saú-de -> sa-ú-de).
_HIATO_ACENTUADO = re.compile(rf"(?<![gq])([{VOGAIS}])(-?)([íú])")

# Regra 3: i ou u tônicos sem acento, fechados por l, m, n, r ou z (juiz -> ju-iz).
_HIATO_FECHADO_POR_CONSOANTE = re.compile(
    rf"(?<![gq])([{VOGAIS}])(-?)([iu])(-?)([lmnrz])(?![{VOGAIS}])"
)


def separar_silabas(palavra: str) -> list[str]:
    """Separa uma palavra em sílabas gramaticais.

    Args:
        palavra: uma única palavra, sem espaços nem pontuação.

    Returns:
        A lista de sílabas, na ordem em que aparecem na palavra.

    Raises:
        ValueError: se a palavra for vazia.
    """
    palavra = palavra.strip()
    if not palavra:
        raise ValueError("A palavra não pode ser vazia.")

    if "-" in palavra:
        return _separar_palavra_com_hifen(palavra)

    minuscula = palavra.lower()
    if minuscula in EXCECOES:
        silabas = EXCECOES[minuscula]
    else:
        hifenizada = _HIFENIZADOR.inserted(minuscula)
        hifenizada = _HIATO_ANTES_DE_NH.sub(r"\1-\3-\5", hifenizada)
        hifenizada = _HIATO_ACENTUADO.sub(r"\1-\3", hifenizada)
        hifenizada = _HIATO_FECHADO_POR_CONSOANTE.sub(r"\1-\3\4\5", hifenizada)
        silabas = _juntar_ditongo_crescente_final(hifenizada.split("-"), minuscula)

    return _devolver_grafia_original(palavra, silabas)


def separar_verso(verso: str) -> list[list[str]]:
    """Separa cada palavra de um verso já normalizado.

    Args:
        verso: o texto limpo do verso, com as palavras separadas por espaço.

    Returns:
        Uma lista com as sílabas de cada palavra, preservando a ordem do verso.
    """
    return [separar_silabas(palavra) for palavra in verso.split()]

def _separar_palavra_com_hifen(palavra: str) -> list[str]:
    """Separa cada parte de uma palavra com hífen (guarda-chuva, entendê-las)."""
    silabas = []
    for parte in palavra.split("-"):
        if parte:
            silabas.extend(separar_silabas(parte))
    return silabas

def _juntar_ditongo_crescente_final(silabas: list[str], palavra: str) -> list[str]:
    """Regra 4: junta o "e" final ao i ou u anterior (sé-ri-e -> sé-rie).

    Só se aplica quando a palavra tem acento gráfico em outra sílaba, o que
    garante que o i ou o u final é átono. Sem o acento, o i é tônico e forma
    hiato, como em "co-pi-e".
    """
    if len(silabas) < 2 or silabas[-1] != "e":
        return silabas
    if len(silabas[-2]) < 2 or silabas[-2][-1] not in "iu":
        return silabas
    if not any(acento in palavra for acento in ACENTOS):
        return silabas
    return silabas[:-2] + [silabas[-2] + silabas[-1]]


def _devolver_grafia_original(palavra: str, silabas: list[str]) -> list[str]:
    """Recorta a palavra original nos mesmos tamanhos, preservando maiúsculas."""
    recortada, inicio = [], 0
    for silaba in silabas:
        recortada.append(palavra[inicio:inicio + len(silaba)])
        inicio += len(silaba)
    return recortada