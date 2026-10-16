"""Ponto de entrada do motor de PLN (partição de Consolidação do TCC).

Executa as análises métrica e de rima sobre um mesmo verso e reúne os
resultados em um relatório único, devolvido à API REST.
"""

from motor_pln import __version__
from motor_pln.metrica import escandir_verso
from motor_pln.morfologia import MODELO_PADRAO
from motor_pln.preprocessamento import limpar_verso
from motor_pln.resultados import AnaliseVerso
from motor_pln.rima import analisar_rima


def analisar_verso(verso: str, modelo: str = MODELO_PADRAO) -> AnaliseVerso:
    """Executa a análise completa de um verso.

    As duas análises são independentes: se uma delas falhar, a outra ainda é
    devolvida, e o motivo da falha é registrado nos avisos do relatório.

    Args:
        verso: o verso como o escritor digitou (atributo textoOriginal do Verso).
        modelo: o pacote do spaCy a utilizar.

    Returns:
        O relatório consolidado do verso.

    Raises:
        ValueError: se o verso não contiver nenhuma palavra.
    """
    texto_limpo = limpar_verso(verso)
    if not texto_limpo:
        raise ValueError("O verso não contém palavras.")

    avisos: list[str] = []

    try:
        analise_metrica = escandir_verso(verso)
    except ValueError as erro:
        analise_metrica = None
        avisos.append(f"Análise métrica indisponível: {erro}")

    try:
        analise_rima = analisar_rima(verso, modelo)
    except ValueError as erro:
        analise_rima = None
        avisos.append(f"Análise de rima indisponível: {erro}")

    return AnaliseVerso(
        texto_limpo=texto_limpo,
        analise_metrica=analise_metrica,
        analise_rima=analise_rima,
        avisos=tuple(avisos),
        versao_motor=__version__,
        modelo_spacy=modelo,
    )