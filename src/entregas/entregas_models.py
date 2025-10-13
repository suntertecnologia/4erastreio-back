from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class EntregaMovimentacaoOut(BaseModel):
    movimento: str
    tipo: Optional[str]
    dt_movimento: Optional[datetime]
    localizacao: Optional[str]
    detalhes: Optional[str]

    class Config:
        from_attributes = True

class EntregaOut(BaseModel):
    transportadora: str
    codigo_rastreio: str
    numero_nf: Optional[str]
    cliente: Optional[str]
    cnpj_destinatario: Optional[str]
    status: Optional[str]
    previsao_entrega: Optional[date]
    movimentacoes: List[EntregaMovimentacaoOut]

    class Config:
        from_attributes = True

class EntregaMovimentacaoCreate(BaseModel):
    movimento: str
    tipo: Optional[str]
    dt_movimento: Optional[datetime]
    localizacao: Optional[str]
    detalhes: Optional[str]

class EntregaCreate(BaseModel):
    transportadora: str
    codigo_rastreio: str
    numero_nf: Optional[str]
    cliente: Optional[str]
    cnpj_destinatario: Optional[str]
    status: Optional[str]
    previsao_entrega: Optional[date]
    movimentacoes: List[EntregaMovimentacaoCreate]

class EntregaScrapRequest(BaseModel):
    transportadora: str
    numero_nf: str
    cnpj_destinatario: str
