"""Estruturas de dados que o motor devolve (entidades do diagrama de classes)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnaliseMetrica:
    """Resultado da análise métrica de um verso (entidade AnaliseMetrica)."""

    separacao_gramatical: str
    separacao_poetica: str
    total_silabas: int
    classificacao: str


@dataclass(frozen=True)
class EtiquetaMorfologica:
    """Classe gramatical da palavra que encerra o verso (entidade AnaliseRima)."""

    palavra: str
    etiqueta_upos: str
    classe_gramatical: str

@dataclass(frozen=True)
class AnaliseRima:
    """Resultado da análise de rima de um verso (entidade AnaliseRima)."""

    palavra_final: str
    fonema_tonico: str
    classe_gramatical: str