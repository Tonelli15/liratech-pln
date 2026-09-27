"""Estruturas de dados que o motor devolve (entidades do diagrama de classes)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnaliseMetrica:
    """Resultado da análise métrica de um verso (entidade AnaliseMetrica)."""

    separacao_gramatical: str
    separacao_poetica: str
    total_silabas: int
    classificacao: str