"""Pré-processamento do verso (partição de pré-processamento do TCC, Figura 3a)."""

import re
import unicodedata

LETRAS = "a-zçáéíóúâêôàãõü"

# Apóstrofo da elisão poética: em "minh'alma" o poeta já fundiu as vogais.
_APOSTROFOS = re.compile(r"['’‘`´]")

# Tudo o que não for letra, hífen ou espaço vira espaço.
_NAO_LETRA = re.compile(rf"[^{LETRAS}\-\s]")


def limpar_verso(verso: str) -> str:
    """Normaliza o verso para a análise métrica (atributo textoLimpo do Verso).

    Args:
        verso: o verso como o escritor digitou, com pontuação e maiúsculas.

    Returns:
        O verso em minúsculas, só com letras, hífens internos e espaços simples.
    """
    texto = unicodedata.normalize("NFC", verso).lower()
    texto = _APOSTROFOS.sub("", texto)
    texto = _NAO_LETRA.sub(" ", texto)
    palavras = [palavra.strip("-") for palavra in texto.split()]
    return " ".join(palavra for palavra in palavras if palavra)