from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List


class EntregaBase(BaseModel):
    transportadora: str
    codigo_rastreio: str
    numero_nf: str
    cliente: Optional[str] = None
    cnpj_destinatario: Optional[str] = None
    previsao_entrega_inicial: date
    previsao_entrega: date


class EntregaCreate(EntregaBase):
    historico: Optional[List[dict]] = None


class EntregaUpdate(BaseModel):
    transportadora: Optional[str] = None
    codigo_rastreio: Optional[str] = None
    numero_nf: Optional[str] = None
    cliente: Optional[str] = None
    cnpj_destinatario: Optional[str] = None
    status: Optional[str] = None
    previsao_entrega_inicial: Optional[date] = None
    previsao_entrega: Optional[date] = None


class EntregaOut(EntregaBase):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)


class EntregaScrapRequest(BaseModel):
    transportadora: str
    numero_nf: str
    cnpj_destinatario: str
    credentials: Optional[dict] = None
