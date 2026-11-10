"""Leitura e validação do corpus anotado (Seção 3.4 do TCC)."""

import csv
import io
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from motor_pln.morfologia import CLASSE_INDEFINIDA, CLASSES_GRAMATICAIS
from motor_pln.preprocessamento import limpar_verso

COLUNAS = (
    "id", "subcorpus", "autor", "poema", "verso",
    "silabas_esperadas", "classe_esperada", "rima_esperada",
)
OBRIGATORIAS = ("id", "subcorpus", "autor", "poema", "verso")
SUBCORPORA = ("clássico", "livre")
CLASSES = tuple(sorted(set(CLASSES_GRAMATICAIS.values()) | {CLASSE_INDEFINIDA}))

_ROTULO_DE_RIMA = re.compile(r"[A-Z]{1,2}")


class CorpusInvalido(ValueError):
    """Erro de preenchimento do corpus, com a indicação da linha."""


@dataclass(frozen=True)
class VersoAnotado:
    """Um verso do corpus, com o gabarito construído manualmente."""

    id: str
    subcorpus: str
    autor: str
    poema: str
    verso: str
    silabas_esperadas: int | None
    classe_esperada: str | None
    rima_esperada: str | None


def ler_corpus(caminho: Path) -> list[VersoAnotado]:
    """Lê o corpus de um arquivo CSV, validando cada linha.

    Aceita o ponto e vírgula, separador do Excel em português, e a vírgula,
    separador do Google Planilhas e do LibreOffice.

    Raises:
        CorpusInvalido: se o arquivo ou alguma linha estiver mal preenchido.
    """
    try:
        texto = caminho.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise CorpusInvalido(
            f"{caminho} não está em UTF-8. No Excel, use Salvar como > CSV UTF-8."
        ) from None

    cabecalho = texto.partition("\n")[0]
    separador = ";" if cabecalho.count(";") >= cabecalho.count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=separador)

    ausentes = [coluna for coluna in COLUNAS if coluna not in (leitor.fieldnames or [])]
    if ausentes:
        raise CorpusInvalido(f"Colunas ausentes no cabeçalho: {', '.join(ausentes)}.")

    versos: list[VersoAnotado] = []
    ids: set[str] = set()
    for registro in leitor:
        valores = {coluna: (registro.get(coluna) or "").strip() for coluna in COLUNAS}
        if not any(valores.values()):
            continue
        try:
            verso = _validar(valores)
            if verso.id in ids:
                raise ValueError(f"o id {verso.id!r} está repetido.")
        except ValueError as erro:
            raise CorpusInvalido(f"Linha {leitor.line_num}: {erro}") from None
        ids.add(verso.id)
        versos.append(verso)

    if not versos:
        raise CorpusInvalido("O corpus não contém versos.")
    return versos


def _validar(valores: dict[str, str]) -> VersoAnotado:
    """Converte os textos de uma linha em um VersoAnotado, ou levanta ValueError."""
    for coluna in OBRIGATORIAS:
        if not valores[coluna]:
            raise ValueError(f"a coluna {coluna!r} é obrigatória.")
    if not limpar_verso(valores["verso"]):
        raise ValueError("o verso não contém palavras.")

    return VersoAnotado(
        id=valores["id"],
        subcorpus=_opcao(valores["subcorpus"], SUBCORPORA, "subcorpus"),
        autor=valores["autor"],
        poema=valores["poema"],
        verso=valores["verso"],
        silabas_esperadas=_silabas(valores["silabas_esperadas"]),
        classe_esperada=_opcao(valores["classe_esperada"], CLASSES, "classe_esperada"),
        rima_esperada=_rotulo(valores["rima_esperada"]),
    )


def _opcao(texto: str, opcoes: tuple[str, ...], coluna: str) -> str | None:
    """Aceita uma das opções, sem distinguir maiúsculas nem acentos."""
    if not texto:
        return None
    for opcao in opcoes:
        if _sem_acentos(opcao) == _sem_acentos(texto):
            return opcao
    raise ValueError(f"{coluna} {texto!r} inválido; use um destes: {', '.join(opcoes)}.")


def _silabas(texto: str) -> int | None:
    if not texto:
        return None
    if not texto.isdigit() or not 1 <= int(texto) <= 30:
        raise ValueError(f"silabas_esperadas {texto!r} deve ser um número inteiro de 1 a 30.")
    return int(texto)


def _rotulo(texto: str) -> str | None:
    if not texto:
        return None
    rotulo = texto.upper()
    if not _ROTULO_DE_RIMA.fullmatch(rotulo):
        raise ValueError(f"rima_esperada {texto!r} deve ter uma ou duas letras, como A ou B.")
    return rotulo


def _sem_acentos(texto: str) -> str:
    """Remove acentos e maiúsculas para comparar ('Clássico' vira 'classico')."""
    decomposto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(letra for letra in decomposto if not unicodedata.combining(letra))