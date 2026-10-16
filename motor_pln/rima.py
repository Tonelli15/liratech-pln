"""Terminação sonora da palavra final do verso.

Implementa a ação "Mapear Terminação Sonora (Fonema)" da partição de Análise
de Rima (Seção 3.3.3 do TCC).
"""

import re

from motor_pln.morfologia import MODELO_PADRAO, etiquetar_palavra_final
from motor_pln.preprocessamento import limpar_verso
from motor_pln.resultados import AnaliseRima
from motor_pln.silabacao import VOGAIS
from motor_pln.tonicidade import silabas_e_tonica

# O agudo e o circunflexo marcam tonicidade e timbre, não fonemas distintos
# para efeito de rima; o til marca nasalidade, que é distintiva, e permanece.
_SEM_TIMBRE = str.maketrans("áéíóúâêô", "aeiouaeo")

# Entre vogais, o "s" soa /z/ ("casa"); "ss" e "ç" soam /s/ ("massa", "taça").
_S_ENTRE_VOGAIS = re.compile(rf"(?<=[{VOGAIS}])s(?=[{VOGAIS}])")

# Em final de palavra, "s" e "z" neutralizam-se ("voz" rima com "após").
_Z_FINAL = re.compile(r"z$")


def terminacao_sonora(palavra: str) -> str:
    """Extrai a terminação que define a rima, a partir da vogal tônica.

    Args:
        palavra: uma única palavra, já sem pontuação.

    Returns:
        A terminação normalizada, usada para comparar rimas entre versos.

    Raises:
        ValueError: se a palavra não contiver vogal.
    """
    palavra = palavra.lower()
    silabas, tonica = silabas_e_tonica(palavra)
    trecho_tonico = "".join(silabas[tonica:])
    letras_atonas = sum(len(silaba) for silaba in silabas[:tonica])
    inicio = letras_atonas + _posicao_da_vogal_tonica(trecho_tonico)
    return _normalizar(_cortar_na_vogal_tonica(palavra, inicio))


def analisar_rima(verso: str, modelo: str = MODELO_PADRAO) -> AnaliseRima:
    """Executa a análise de rima completa de um verso.

    Args:
        verso: o verso como o escritor digitou (atributo textoOriginal do Verso).
        modelo: o pacote do spaCy a utilizar.

    Returns:
        A análise de rima, com os campos da entidade AnaliseRima.

    Raises:
        ValueError: se o verso não contiver palavras.
    """
    etiqueta = etiquetar_palavra_final(verso, modelo)
    palavra = limpar_verso(etiqueta.palavra)
    if not palavra:
        raise ValueError(f"A palavra final {etiqueta.palavra!r} não contém letras.")

    return AnaliseRima(
        palavra_final=etiqueta.palavra,
        fonema_tonico=terminacao_sonora(palavra),
        classe_gramatical=etiqueta.classe_gramatical,
    )


def _cortar_na_vogal_tonica(palavra: str, letras_a_pular: int) -> str:
    """Corta a palavra na vogal tônica, preservando o hífen que houver depois.

    O hífen é mantido porque marca fronteira entre o verbo e o pronome: em
    "transforma-se", o "s" do pronome soa /s/, e não /z/ como soaria entre
    vogais de uma mesma palavra.
    """
    for posicao, letra in enumerate(palavra):
        if letra == "-":
            continue
        if letras_a_pular == 0:
            return palavra[posicao:]
        letras_a_pular -= 1
    raise ValueError(f"Palavra sem vogal tônica: {palavra!r}.")


def _posicao_da_vogal_tonica(trecho: str) -> int:
    """Acha a primeira vogal do trecho, ignorando o u mudo de "gu" e "qu"."""
    for posicao, letra in enumerate(trecho):
        if letra not in VOGAIS:
            continue
        if _e_u_mudo(trecho, posicao):
            continue
        return posicao
    raise ValueError(f"Trecho sem vogal: {trecho!r}.")


def _e_u_mudo(trecho: str, posicao: int) -> bool:
    """Diz se o u da posição é o u mudo de "gue", "gui", "que" ou "qui"."""
    return (
        trecho[posicao] == "u"
        and posicao > 0
        and trecho[posicao - 1] in "gq"
        and posicao + 1 < len(trecho)
        and trecho[posicao + 1] in VOGAIS
    )


def _normalizar(terminacao: str) -> str:
    """Aproxima a grafia da pronúncia, unificando letras de mesmo som."""
    aproximada = terminacao.translate(_SEM_TIMBRE)
    aproximada = _S_ENTRE_VOGAIS.sub("z", aproximada)
    aproximada = aproximada.replace("ç", "s").replace("ss", "s")
    return _Z_FINAL.sub("s", aproximada).replace("-", "")