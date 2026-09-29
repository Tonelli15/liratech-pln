"""Etiquetagem morfológica da palavra final do verso.

Implementa a ação "Extrair Classe Gramatical via POS Tagging (spaCy)" da
partição de Análise de Rima (Seção 3.3.3 do TCC).
"""

from functools import cache

import spacy

from motor_pln.resultados import EtiquetaMorfologica

MODELO_PADRAO = "pt_core_news_sm"

# Componentes do pipeline do spaCy dispensáveis para a etiquetagem morfológica.
COMPONENTES_DISPENSAVEIS = ("parser", "ner", "lemmatizer", "attribute_ruler")

# Universal POS (spaCy) -> classe gramatical da tradição gramatical portuguesa.
CLASSES_GRAMATICAIS = {
    "NOUN": "substantivo",
    "PROPN": "substantivo",
    "VERB": "verbo",
    "AUX": "verbo",
    "ADJ": "adjetivo",
    "ADV": "advérbio",
    "PRON": "pronome",
    "DET": "determinante",
    "NUM": "numeral",
    "ADP": "preposição",
    "CCONJ": "conjunção",
    "SCONJ": "conjunção",
    "INTJ": "interjeição",
    "PART": "partícula",
    "SYM": "símbolo",
    "X": "indefinida",
}
CLASSE_INDEFINIDA = "indefinida"


@cache
def carregar_modelo(nome: str = MODELO_PADRAO):
    """Carrega o modelo do spaCy, uma única vez por nome.

    A carga do modelo é a operação mais cara do motor, por isso o resultado é
    mantido em memória: a primeira chamada carrega, as demais reaproveitam.

    Args:
        nome: o pacote do spaCy a carregar (pt_core_news_sm, _md ou _lg).

    Returns:
        O objeto de processamento do spaCy, já sem os componentes dispensáveis.
    """
    return spacy.load(nome, exclude=list(COMPONENTES_DISPENSAVEIS))


def classe_gramatical(etiqueta_upos: str) -> str:
    """Traduz uma etiqueta Universal POS para a classe gramatical em português.

    Substantivos próprios e comuns são reunidos em "substantivo", e verbos
    auxiliares e principais em "verbo", porque a rima é classificada pela
    classe gramatical, e não pela subcategoria morfossintática.
    """
    return CLASSES_GRAMATICAIS.get(etiqueta_upos, CLASSE_INDEFINIDA)


def etiquetar_palavra_final(verso: str, modelo: str = MODELO_PADRAO) -> EtiquetaMorfologica:
    """Extrai a palavra que encerra o verso e a sua classe gramatical.

    Args:
        verso: o verso como o escritor digitou (atributo textoOriginal do Verso).
            A pontuação e as maiúsculas são preservadas de propósito, por serem
            pistas que o modelo estatístico usa para desambiguar as classes.
        modelo: o pacote do spaCy a utilizar.

    Returns:
        A palavra final, a sua etiqueta Universal POS e a classe gramatical.

    Raises:
        ValueError: se o verso não contiver nenhuma palavra.
    """
    documento = carregar_modelo(modelo)(verso)
    palavras = [token for token in documento if not token.is_punct and not token.is_space]
    if not palavras:
        raise ValueError("O verso não contém palavras.")

    final = palavras[-1]
    return EtiquetaMorfologica(
        palavra=final.text,
        etiqueta_upos=final.pos_,
        classe_gramatical=classe_gramatical(final.pos_),
    )