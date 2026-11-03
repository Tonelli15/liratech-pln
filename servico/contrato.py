"""Contrato de dados do microsserviço de PLN.

Define o formato JSON trocado com a API REST. Os nomes seguem o padrão
camelCase, adotado pelo diagrama de classes do TCC e pelo Spring Boot.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from motor_pln.preprocessamento import limpar_verso

from motor_pln.resultados import AnaliseVerso

TAMANHO_MAXIMO_VERSO = 500


class _Esquema(BaseModel):
    """Configuração comum a todos os modelos do contrato."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        from_attributes=True,
    )


class RequisicaoAnalise(_Esquema):
    """Corpo da requisição enviada pela API REST."""

    model_config = ConfigDict(str_strip_whitespace=True)

    verso: str = Field(min_length=1, max_length=TAMANHO_MAXIMO_VERSO)
    
    @field_validator("verso")
    @classmethod
    def deve_conter_palavras(cls, verso: str) -> str:
        """Rejeita versos sem nenhuma letra, como "...!" ou "123"."""
        if not limpar_verso(verso):
            raise ValueError("O verso não contém palavras.")
        return verso


class MetricaResposta(_Esquema):
    """Campos da entidade AnaliseMetrica."""

    separacao_gramatical: str
    separacao_poetica: str
    total_silabas: int
    classificacao: str


class RimaResposta(_Esquema):
    """Campos da entidade AnaliseRima."""

    palavra_final: str
    fonema_tonico: str
    classe_gramatical: str


class RespostaAnalise(_Esquema):
    """Corpo da resposta devolvida à API REST."""

    texto_limpo: str
    analise_metrica: MetricaResposta | None
    analise_rima: RimaResposta | None
    avisos: list[str]
    versao_motor: str
    modelo_spacy: str

class EstadoServico(_Esquema):
    """Corpo da resposta da verificação de saúde do serviço."""

    status: str
    versao_motor: str
    modelo_spacy: str


def para_resposta(analise: AnaliseVerso) -> RespostaAnalise:
    """Converte o relatório interno do motor no formato do contrato."""
    return RespostaAnalise.model_validate(analise)