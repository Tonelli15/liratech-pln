"""Métricas de avaliação do motor (Seção 3.4 do TCC).

Compara a saída do motor com o gabarito do corpus em quatro dimensões:
escansão, classe gramatical da palavra final, pares de rima e riqueza da rima.
"""

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from statistics import fmean, median, quantiles

from avaliacao.corpus import VersoAnotado
from motor_pln.resultados import AnaliseVerso

INDISPONIVEL = "indisponível"
Z_95 = 1.96  # valor crítico da distribuição normal para 95% de confiança


@dataclass(frozen=True)
class Taxa:
    """Proporção de acertos sobre os casos avaliados."""

    acertos: int
    total: int

    @property
    def valor(self) -> float | None:
        return self.acertos / self.total if self.total else None

    @property
    def intervalo_95(self) -> tuple[float, float] | None:
        """Intervalo de confiança de 95% pelo método de Wilson."""
        if not self.total:
            return None
        n, p = self.total, self.acertos / self.total
        denominador = 1 + Z_95**2 / n
        centro = (p + Z_95**2 / (2 * n)) / denominador
        margem = Z_95 * sqrt(p * (1 - p) / n + Z_95**2 / (4 * n**2)) / denominador
        return (centro - margem, centro + margem)


@dataclass(frozen=True)
class ComparacaoDePares:
    """Confronto entre os pares de rima do gabarito e os do motor."""

    verdadeiros_positivos: int
    falsos_positivos: int
    falsos_negativos: int

    @property
    def precisao(self) -> float | None:
        identificados = self.verdadeiros_positivos + self.falsos_positivos
        return self.verdadeiros_positivos / identificados if identificados else None

    @property
    def revocacao(self) -> float | None:
        esperados = self.verdadeiros_positivos + self.falsos_negativos
        return self.verdadeiros_positivos / esperados if esperados else None

    @property
    def f1(self) -> float | None:
        p, r = self.precisao, self.revocacao
        if p is None or r is None:
            return None
        return 2 * p * r / (p + r) if p + r else 0.0


@dataclass(frozen=True)
class ResumoDeTempos:
    """Estatísticas do tempo de análise por verso, em milissegundos."""

    media: float
    mediana: float
    percentil_95: float
    maximo: float


def taxa_de_acerto(pares: Iterable[tuple[object, object]]) -> Taxa:
    """Conta quantos pares (esperado, obtido) coincidem."""
    pares = list(pares)
    return Taxa(sum(esperado == obtido for esperado, obtido in pares), len(pares))


def pares_que_rimam(rotulos: Sequence[str | None]) -> set[tuple[int, int]]:
    """Pares de posições com o mesmo rótulo de rima; None nunca forma par."""
    return {
        (i, j)
        for i, j in combinations(range(len(rotulos)), 2)
        if rotulos[i] is not None and rotulos[i] == rotulos[j]
    }


def comparar_pares(esperados: set, obtidos: set) -> ComparacaoDePares:
    """Classifica os pares em acertos, falsos alarmes e omissões."""
    return ComparacaoDePares(
        verdadeiros_positivos=len(esperados & obtidos),
        falsos_positivos=len(obtidos - esperados),
        falsos_negativos=len(esperados - obtidos),
    )


def resumir_tempos(milissegundos: Sequence[float]) -> ResumoDeTempos:
    """Resume os tempos medidos; o percentil 95 exige ao menos dois valores."""
    if len(milissegundos) > 1:
        p95 = quantiles(milissegundos, n=20, method="inclusive")[-1]
    else:
        p95 = milissegundos[0]
    return ResumoDeTempos(fmean(milissegundos), median(milissegundos), p95, max(milissegundos))


# --- Métricas aplicadas ao corpus ------------------------------------------

def silabas_obtidas(analise: AnaliseVerso) -> int | None:
    return analise.analise_metrica.total_silabas if analise.analise_metrica else None


def classe_obtida(analise: AnaliseVerso) -> str | None:
    return analise.analise_rima.classe_gramatical if analise.analise_rima else None


def fonema_obtido(analise: AnaliseVerso) -> str | None:
    return analise.analise_rima.fonema_tonico if analise.analise_rima else None


def pares_de_rima(
    versos: Sequence[VersoAnotado], analises: Sequence[AnaliseVerso]
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    """Pares de versos que rimam segundo o gabarito e segundo o motor.

    Só se comparam versos de um mesmo poema que tenham a rima anotada. Os
    pares são devolvidos como posições no corpus, para que se possa consultar
    os versos de cada par.
    """
    poemas: dict[tuple[str, str], list[int]] = {}
    for posicao, verso in enumerate(versos):
        if verso.rima_esperada is not None:
            poemas.setdefault((verso.autor, verso.poema), []).append(posicao)

    esperados: set[tuple[int, int]] = set()
    obtidos: set[tuple[int, int]] = set()
    for posicoes in poemas.values():
        for i, j in pares_que_rimam([versos[p].rima_esperada for p in posicoes]):
            esperados.add((posicoes[i], posicoes[j]))
        for i, j in pares_que_rimam([fonema_obtido(analises[p]) for p in posicoes]):
            obtidos.add((posicoes[i], posicoes[j]))
    return esperados, obtidos


def avaliar(versos: Sequence[VersoAnotado], analises: Sequence[AnaliseVerso]) -> dict:
    """Calcula todas as métricas de um conjunto de versos já analisados."""
    escansao = [(v.silabas_esperadas, silabas_obtidas(a))
                for v, a in zip(versos, analises) if v.silabas_esperadas is not None]
    diferencas = Counter(
        INDISPONIVEL if obtido is None else obtido - esperado for esperado, obtido in escansao
    )
    classes = [(v.classe_esperada, classe_obtida(a))
               for v, a in zip(versos, analises) if v.classe_esperada is not None]

    esperados, obtidos = pares_de_rima(versos, analises)
    riqueza = [
        (versos[i].classe_esperada != versos[j].classe_esperada,
         classe_obtida(analises[i]) != classe_obtida(analises[j]))
        for i, j in esperados & obtidos
        if versos[i].classe_esperada and versos[j].classe_esperada
    ]

    return {
        "escansao": taxa_de_acerto(escansao),
        "diferencas_de_silabas": {
            chave: diferencas[chave] for chave in sorted(diferencas, key=_ordem)
        },
        "classe_gramatical": taxa_de_acerto(classes),
        "pares_de_rima": comparar_pares(esperados, obtidos),
        "riqueza_da_rima": taxa_de_acerto(riqueza),
    }


def _ordem(chave: int | str) -> tuple[int, int]:
    """Ordena as diferenças numericamente, deixando 'indisponível' por último."""
    return (1, 0) if chave == INDISPONIVEL else (0, chave)