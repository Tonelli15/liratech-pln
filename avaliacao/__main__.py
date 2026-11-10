"""Avaliação do motor de PLN sobre o corpus anotado (Seção 3.4 do TCC).

Uso, a partir da pasta do projeto:
    python -m avaliacao --corpus corpus/corpus.csv --modelos sm md lg
"""

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import spacy

from avaliacao.corpus import SUBCORPORA, CorpusInvalido, VersoAnotado, ler_corpus
from avaliacao.metricas import (
    ComparacaoDePares,
    ResumoDeTempos,
    Taxa,
    avaliar,
    classe_obtida,
    fonema_obtido,
    pares_de_rima,
    resumir_tempos,
    silabas_obtidas,
)
from motor_pln import __version__
from motor_pln.morfologia import carregar_modelo
from motor_pln.motor import analisar_verso
from motor_pln.resultados import AnaliseVerso

META_DE_TEMPO_MS = 10.0  # RNF02: tempo médio por verso, excluída a carga do modelo
APELIDOS = {"sm": "pt_core_news_sm", "md": "pt_core_news_md", "lg": "pt_core_news_lg"}


def main(argumentos: list[str] | None = None) -> int:
    """Executa a avaliação e devolve o código de saída do programa (0 = sucesso)."""
    opcoes = _ler_argumentos(argumentos)

    try:
        versos = ler_corpus(opcoes.corpus)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {opcoes.corpus}", file=sys.stderr)
        return 1
    except CorpusInvalido as erro:
        print(f"Corpus inválido: {erro}", file=sys.stderr)
        return 1

    modelos = [APELIDOS.get(nome, nome) for nome in opcoes.modelos]
    ausentes = [nome for nome in modelos if not spacy.util.is_package(nome)]
    if ausentes:
        print(f"Modelo(s) não instalado(s): {', '.join(ausentes)}.", file=sys.stderr)
        print("Instale com: python -m pip install -r requirements-avaliacao.txt", file=sys.stderr)
        return 1

    resultados = {nome: _avaliar_modelo(versos, nome) for nome in modelos}

    opcoes.saida.mkdir(parents=True, exist_ok=True)
    _gravar_metricas(opcoes.saida / "metricas.json", opcoes.corpus, versos, resultados)
    principal = modelos[0]
    _gravar_divergencias(opcoes.saida, versos, resultados[principal]["analises"])

    for nome, resultado in resultados.items():
        _imprimir_resumo(nome, resultado)
    print(f"Resultados gravados em {opcoes.saida}/ (divergências do modelo {principal}).")
    return 0


def _ler_argumentos(argumentos: list[str] | None) -> argparse.Namespace:
    leitor = argparse.ArgumentParser(
        prog="python -m avaliacao",
        description="Avalia o motor de PLN sobre o corpus anotado.",
    )
    leitor.add_argument("--corpus", type=Path, default=Path("corpus/corpus.csv"),
                        help="arquivo CSV com o gabarito (padrão: corpus/corpus.csv)")
    leitor.add_argument("--modelos", nargs="+", default=["sm"],
                        help="modelos do spaCy: sm, md, lg ou o nome completo (padrão: sm)")
    leitor.add_argument("--saida", type=Path, default=Path("resultados"),
                        help="pasta onde gravar os resultados (padrão: resultados)")
    return leitor.parse_args(argumentos)


def _avaliar_modelo(versos: list[VersoAnotado], modelo: str) -> dict:
    """Analisa o corpus inteiro com um modelo, medindo o tempo de cada verso."""
    inicio = time.perf_counter()
    carregar_modelo(modelo)
    carga = time.perf_counter() - inicio
    analisar_verso(versos[0].verso, modelo)  # aquecimento: a primeira análise é mais lenta

    analises: list[AnaliseVerso] = []
    tempos: list[float] = []
    for verso in versos:
        inicio = time.perf_counter()
        analises.append(analisar_verso(verso.verso, modelo))
        tempos.append((time.perf_counter() - inicio) * 1000)

    grupos = {"total": list(range(len(versos)))}
    for subcorpus in SUBCORPORA:
        posicoes = [p for p, verso in enumerate(versos) if verso.subcorpus == subcorpus]
        if posicoes:
            grupos[subcorpus] = posicoes

    por_autor = {}
    for posicao, verso in enumerate(versos):
        por_autor.setdefault(verso.autor, []).append(posicao)

    resumo = resumir_tempos(tempos)
    return {
        "analises": analises,
        "carga_s": carga,
        "tempo_por_verso_ms": resumo,
        "meta_de_tempo_cumprida": resumo.media < META_DE_TEMPO_MS,
        "metricas": {nome: _avaliar_posicoes(versos, analises, posicoes)
                     for nome, posicoes in grupos.items()},
        "escansao_por_autor": {autor: _avaliar_posicoes(versos, analises, posicoes)["escansao"]
                               for autor, posicoes in sorted(por_autor.items())},
    }


def _avaliar_posicoes(versos: list[VersoAnotado], analises: list[AnaliseVerso],
                      posicoes: list[int]) -> dict:
    return avaliar([versos[p] for p in posicoes], [analises[p] for p in posicoes])


# --- Gravação dos resultados ------------------------------------------------

def _gravar_metricas(
    caminho: Path, corpus: Path, versos: list[VersoAnotado], resultados: dict
) -> None:
    dados = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "versao_motor": __version__,
        "ambiente": {"python": platform.python_version(), "spacy": spacy.__version__},
        "corpus": {
            "arquivo": corpus.as_posix(),
            "sha256": hashlib.sha256(corpus.read_bytes()).hexdigest(),
            "versos": len(versos),
        },
        "meta_de_tempo_ms": META_DE_TEMPO_MS,
        "modelos": {
            nome: {chave: valor for chave, valor in resultado.items() if chave != "analises"}
            for nome, resultado in resultados.items()
        },
    }
    texto = json.dumps(dados, default=_para_json, ensure_ascii=False, indent=2)
    caminho.write_text(texto + "\n", encoding="utf-8")


def _para_json(valor: object) -> dict:
    """Ensina o json.dumps a gravar as estruturas de métricas."""
    if isinstance(valor, Taxa):
        return {"acertos": valor.acertos, "total": valor.total,
                "taxa": valor.valor, "intervalo_95": valor.intervalo_95}
    if isinstance(valor, ComparacaoDePares):
        return {
            "verdadeiros_positivos": valor.verdadeiros_positivos,
            "falsos_positivos": valor.falsos_positivos,
            "falsos_negativos": valor.falsos_negativos,
            "precisao": valor.precisao, "revocacao": valor.revocacao, "f1": valor.f1,
        }
    if isinstance(valor, ResumoDeTempos):
        return {"media": valor.media, "mediana": valor.mediana,
                "percentil_95": valor.percentil_95, "maximo": valor.maximo}
    raise TypeError(f"Tipo não serializável: {type(valor).__name__}")


def _gravar_divergencias(
    pasta: Path, versos: list[VersoAnotado], analises: list[AnaliseVerso]
) -> None:
    """Grava as divergências em CSV, com a coluna 'causa' para a análise manual."""
    escansao = [
        [v.id, v.autor, v.poema, v.verso, v.silabas_esperadas, silabas_obtidas(a),
         a.analise_metrica.separacao_poetica if a.analise_metrica else "", ""]
        for v, a in zip(versos, analises)
        if v.silabas_esperadas is not None and v.silabas_esperadas != silabas_obtidas(a)
    ]
    _gravar_csv(pasta / "divergencias_escansao.csv",
                ["id", "autor", "poema", "verso", "esperado", "obtido",
                 "separacao_poetica", "causa"],
                escansao)

    classes = [
        [v.id, v.autor, v.poema, v.verso, _palavra_final(a),
         v.classe_esperada, classe_obtida(a), ""]
        for v, a in zip(versos, analises)
        if v.classe_esperada is not None and v.classe_esperada != classe_obtida(a)
    ]
    _gravar_csv(pasta / "divergencias_classe.csv",
                ["id", "autor", "poema", "verso", "palavra_final",
                 "esperado", "obtido", "causa"],
                classes)

    esperados, obtidos = pares_de_rima(versos, analises)
    rimas = [
        [versos[i].id, versos[j].id, versos[i].poema,
         _palavra_final(analises[i]), _palavra_final(analises[j]),
         fonema_obtido(analises[i]) or "", fonema_obtido(analises[j]) or "",
         "rimam" if (i, j) in esperados else "não rimam",
         "rimam" if (i, j) in obtidos else "não rimam", ""]
        for i, j in sorted(esperados ^ obtidos)
    ]
    _gravar_csv(pasta / "divergencias_rima.csv",
                ["id_1", "id_2", "poema", "palavra_1", "palavra_2", "fonema_1", "fonema_2",
                 "gabarito", "motor", "causa"],
                rimas)


def _palavra_final(analise: AnaliseVerso) -> str:
    return analise.analise_rima.palavra_final if analise.analise_rima else ""


def _gravar_csv(caminho: Path, cabecalho: list[str], linhas: list[list]) -> None:
    """Grava no formato que o Excel em português abre corretamente."""
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


# --- Resumo no terminal -------------------------------------------------------

def _imprimir_resumo(nome: str, resultado: dict) -> None:
    metricas = resultado["metricas"]
    grupos = list(metricas)
    print(f"\n{nome}  (carga do modelo: {_numero(resultado['carga_s'], 2)} s)")
    print(f"  {'':<22}" + "".join(f"{grupo:>18}" for grupo in grupos))
    linhas = {
        "escansão": lambda m: _taxa(m["escansao"]),
        "classe gramatical": lambda m: _taxa(m["classe_gramatical"]),
        "pares de rima (F1)": lambda m: _numero(m["pares_de_rima"].f1, 3),
        "riqueza da rima": lambda m: _taxa(m["riqueza_da_rima"]),
    }
    for rotulo, extrair in linhas.items():
        print(f"  {rotulo:<22}" + "".join(f"{extrair(metricas[grupo]):>18}" for grupo in grupos))
    tempos = resultado["tempo_por_verso_ms"]
    situacao = "cumprida" if resultado["meta_de_tempo_cumprida"] else "NÃO cumprida"
    print(f"  tempo por verso: média {_numero(tempos.media, 2)} ms"
          f" | p95 {_numero(tempos.percentil_95, 2)} ms"
          f" | meta do RNF02 (< {META_DE_TEMPO_MS:.0f} ms): {situacao}")


def _taxa(taxa: Taxa) -> str:
    if taxa.valor is None:
        return "—"
    return f"{taxa.acertos}/{taxa.total} {taxa.valor * 100:.1f}%".replace(".", ",")


def _numero(valor: float | None, casas: int) -> str:
    """Formata com vírgula decimal, como no texto do TCC."""
    return "—" if valor is None else f"{valor:.{casas}f}".replace(".", ",")


if __name__ == "__main__":
    sys.exit(main())