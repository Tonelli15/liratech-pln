"""Testes da avaliação sobre o corpus anotado (Seção 3.4 do TCC)."""

import json
from pathlib import Path

import pytest

from avaliacao.__main__ import main
from avaliacao.corpus import CorpusInvalido, ler_corpus
from avaliacao.metricas import (
    Taxa,
    comparar_pares,
    pares_que_rimam,
    resumir_tempos,
    taxa_de_acerto,
)

CABECALHO = "id;subcorpus;autor;poema;verso;silabas_esperadas;classe_esperada;rima_esperada"
EXEMPLO = Path(__file__).parent.parent / "corpus" / "exemplo.csv"


def gravar(pasta: Path, *linhas: str, codificacao: str = "utf-8") -> Path:
    """Atalho: grava um corpus de teste numa pasta temporária."""
    caminho = pasta / "corpus.csv"
    caminho.write_text("\n".join(linhas) + "\n", encoding=codificacao)
    return caminho


# --- Leitura do corpus ---------------------------------------------------------

def test_le_o_corpus_de_exemplo():
    versos = ler_corpus(EXEMPLO)
    assert len(versos) == 22
    assert versos[0].silabas_esperadas == 10
    assert versos[0].rima_esperada == "A"


def test_aceita_virgula_e_normaliza_acentos_e_maiusculas(tmp_path):
    caminho = gravar(tmp_path, CABECALHO.replace(";", ","),
                     'v1,Classico,Bilac,Soneto,"Ora, direis",10,ADVERBIO,a')
    verso = ler_corpus(caminho)[0]
    assert verso.subcorpus == "clássico"
    assert verso.classe_esperada == "advérbio"
    assert verso.rima_esperada == "A"
    assert verso.verso == "Ora, direis"


def test_colunas_opcionais_vazias_viram_none_e_linhas_vazias_sao_ignoradas(tmp_path):
    caminho = gravar(tmp_path, CABECALHO, "v1;livre;Eu;Poema;Um verso qualquer;;;", ";;;;;;;")
    versos = ler_corpus(caminho)
    assert len(versos) == 1
    assert versos[0].silabas_esperadas is None
    assert versos[0].classe_esperada is None
    assert versos[0].rima_esperada is None


@pytest.mark.parametrize("linha, trecho_da_mensagem", [
    ("v1;livre;Eu;Poema;;7;;", "'verso' é obrigatória"),
    ("v1;épico;Eu;Poema;Um verso;7;;", "subcorpus 'épico' inválido"),
    ("v1;livre;Eu;Poema;Um verso;sete;;", "número inteiro"),
    ("v1;livre;Eu;Poema;Um verso;7;substantvo;", "classe_esperada 'substantvo' inválido"),
    ("v1;livre;Eu;Poema;Um verso;7;;A1", "uma ou duas letras"),
    ("v1;livre;Eu;Poema;...!;7;;", "não contém palavras"),
])
def test_linha_mal_preenchida_indica_o_problema_e_a_linha(tmp_path, linha, trecho_da_mensagem):
    caminho = gravar(tmp_path, CABECALHO, linha)
    with pytest.raises(CorpusInvalido, match="Linha 2") as erro:
        ler_corpus(caminho)
    assert trecho_da_mensagem in str(erro.value)


def test_id_repetido_gera_erro(tmp_path):
    caminho = gravar(tmp_path, CABECALHO,
                     "v1;livre;Eu;P;Um verso;;;", "v1;livre;Eu;P;Outro verso;;;")
    with pytest.raises(CorpusInvalido, match="Linha 3.*repetido"):
        ler_corpus(caminho)


def test_coluna_ausente_no_cabecalho_gera_erro(tmp_path):
    caminho = gravar(tmp_path, CABECALHO.replace(";rima_esperada", ""), "v1;livre;Eu;P;Um verso;;")
    with pytest.raises(CorpusInvalido, match="rima_esperada"):
        ler_corpus(caminho)


def test_arquivo_que_nao_esta_em_utf8_gera_erro_explicativo(tmp_path):
    caminho = gravar(tmp_path, CABECALHO, "v1;clássico;Camões;P;Verso;;;", codificacao="cp1252")
    with pytest.raises(CorpusInvalido, match="CSV UTF-8"):
        ler_corpus(caminho)


# --- Métricas ----------------------------------------------------------------

def test_pares_que_rimam_no_esquema_de_um_soneto():
    assert len(pares_que_rimam(list("ABBAABBACDCDCD"))) == 18


def test_rotulo_ausente_nao_forma_par():
    assert pares_que_rimam(["er", None, "er", None]) == {(0, 2)}


def test_precisao_revocacao_e_f1():
    comparacao = comparar_pares(esperados={(0, 1), (2, 3)}, obtidos={(0, 1), (4, 5)})
    assert (comparacao.precisao, comparacao.revocacao, comparacao.f1) == (0.5, 0.5, 0.5)


def test_metricas_sem_casos_ficam_indefinidas():
    assert taxa_de_acerto([]).valor is None
    assert taxa_de_acerto([]).intervalo_95 is None
    assert comparar_pares(set(), set()).f1 is None


def test_intervalo_de_confianca_de_wilson():
    intervalo = Taxa(acertos=170, total=200).intervalo_95
    assert intervalo == pytest.approx((0.7939, 0.8929), abs=1e-4)


def test_resumo_de_tempos_com_um_unico_valor():
    assert resumir_tempos([2.0]).percentil_95 == 2.0


# --- Execução completa ------------------------------------------------------------

def test_avaliacao_completa_grava_os_resultados(tmp_path):
    assert main(["--corpus", str(EXEMPLO), "--saida", str(tmp_path)]) == 0
    assert {arquivo.name for arquivo in tmp_path.iterdir()} == {
        "metricas.json", "divergencias_escansao.csv",
        "divergencias_classe.csv", "divergencias_rima.csv",
    }
    metricas = json.loads((tmp_path / "metricas.json").read_text(encoding="utf-8"))
    assert metricas["corpus"]["versos"] == 22
    escansao = metricas["modelos"]["pt_core_news_sm"]["metricas"]["total"]["escansao"]
    assert escansao["total"] == 22


def test_modelo_nao_instalado_encerra_com_erro(tmp_path, capsys):
    argumentos = ["--corpus", str(EXEMPLO), "--modelos", "xx", "--saida", str(tmp_path)]
    assert main(argumentos) == 1
    assert "não instalado" in capsys.readouterr().err


def test_corpus_inexistente_encerra_com_erro(tmp_path, capsys):
    assert main(["--corpus", str(tmp_path / "nao_existe.csv")]) == 1
    assert "não encontrado" in capsys.readouterr().err