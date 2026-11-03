"""Microsserviço HTTP do motor de PLN do LiraTech (Seção 3.3.5 do TCC).

Expõe o motor à API REST por meio de duas rotas: a análise de um verso e a
verificação de saúde do serviço.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from motor_pln import __version__
from motor_pln.morfologia import MODELO_PADRAO, carregar_modelo
from motor_pln.motor import analisar_verso
from servico.contrato import (
    EstadoServico,
    RequisicaoAnalise,
    RespostaAnalise,
    para_resposta,
)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    """Carrega o modelo do spaCy antes de o serviço aceitar requisições."""
    carregar_modelo(MODELO_PADRAO)
    yield


app = FastAPI(
    title="LiraTech: motor de PLN",
    description="Escansão métrica e análise de rima de versos em língua portuguesa.",
    version=__version__,
    lifespan=ciclo_de_vida,
)


@app.post("/analises", tags=["Análise"])
def analisar(requisicao: RequisicaoAnalise) -> RespostaAnalise:
    """Analisa um verso e devolve a métrica e os dados da palavra final para a rima."""
    return para_resposta(analisar_verso(requisicao.verso))


@app.get("/saude", tags=["Operação"])
def verificar_saude() -> EstadoServico:
    """Confirma que o serviço está no ar, informando a versão do motor e o modelo."""
    return EstadoServico(status="ok", versao_motor=__version__, modelo_spacy=MODELO_PADRAO)