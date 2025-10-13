"""
Data models for scrapers.
"""
from typing import TypedDict, Optional, Literal
from datetime import datetime


class ErrorInfo(TypedDict):
    """Error information structure."""
    tipo: Literal["timeout", "exception", "not_found"]
    mensagem: str
    timestamp: str


class ScraperResponse(TypedDict):
    """Standardized response format for all scrapers."""
    status: Literal["sucesso", "falha"]
    dados: Optional[dict]
    erro: Optional[ErrorInfo]


class LocalInfo(TypedDict):
    """Location information for tracking events."""
    cidade: Optional[str]
    estado: Optional[str]


class TrackingEvent(TypedDict):
    """Individual tracking event."""
    timestamp: Optional[str]
    status: str
    local: LocalInfo
    detalhes: str


class RemetenteDestinatario(TypedDict):
    """Sender/recipient information."""
    nome: Optional[str]
    cnpj: Optional[str]


class InformacoesGerais(TypedDict):
    """General delivery information."""
    transportadora: str
    codigo_rastreio: Optional[str]
    numero_nf: Optional[str]
    previsao_entrega: Optional[str]
    data_postagem: Optional[str]
    remetente: Optional[RemetenteDestinatario]
    destinatario: Optional[RemetenteDestinatario]


class StandardizedDeliveryData(TypedDict):
    """Standardized delivery data format."""
    informacoes_gerais: InformacoesGerais
    historico: list[TrackingEvent]
    erro: Optional[ErrorInfo]
