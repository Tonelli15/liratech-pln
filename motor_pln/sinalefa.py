"""Sinalefa: fusão de vogais entre palavras consecutivas do verso.

Implementa a ação "Aplicar Fusão de Vogais/Sinalefa (Regex)" do diagrama de
atividades (Seção 3.3.3 do TCC).
"""

import re

from motor_pln.silabacao import VOGAIS
from motor_pln.tonicidade import OXITONA, classificar_tonicidade

# As regras de acentuação tratam todo monossílabo como tônico; estes, porém,
# são átonos (artigos, preposições, conjunções e pronomes oblíquos). Só entram
# os que terminam em vogal, porque apenas esses podem participar da sinalefa.
MONOSSILABOS_ATONOS = frozenset({
    "a", "à", "o", "e", "ao", "de", "da", "do", "na", "no",
    "que", "se", "me", "te", "lhe", "lo", "la", "ou",
})

_TERMINA_EM_VOGAL = re.compile(rf"[{VOGAIS}]$")
_COMECA_COM_VOGAL = re.compile(rf"^h?[{VOGAIS}]")


def aplicar_sinalefas(palavras: list[list[str]]) -> list[str]:
    """Junta as sílabas do verso, fundindo vogais entre palavras.

    Args:
        palavras: as sílabas de cada palavra, como devolvidas por separar_verso.

    Returns:
        A lista única de sílabas poéticas do verso, já com as fusões aplicadas.
    """
    silabas: list[str] = []
    anterior: list[str] | None = None
    for atual in palavras:
        if anterior is not None and _ha_sinalefa(anterior, atual):
            silabas[-1] += atual[0]
            silabas.extend(atual[1:])
        else:
            silabas.extend(atual)
        anterior = atual
    return silabas


def _ha_sinalefa(anterior: list[str], atual: list[str]) -> bool:
    """Diz se a última sílaba de uma palavra se funde com a primeira da seguinte."""
    return _termina_em_vogal_atona(anterior) and bool(_COMECA_COM_VOGAL.match(atual[0].lower()))


def _termina_em_vogal_atona(silabas: list[str]) -> bool:
    """Diz se a palavra termina em vogal e se essa vogal final é átona."""
    palavra = "".join(silabas).lower()
    if not _TERMINA_EM_VOGAL.search(palavra):
        return False
    if len(silabas) == 1:
        return palavra in MONOSSILABOS_ATONOS
    return classificar_tonicidade(silabas) != OXITONA