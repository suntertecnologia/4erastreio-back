from src.entregas.entregas_models import EntregaCreate, EntregaMovimentacaoCreate
from datetime import datetime

def parse_braspress(scraped_data: dict, scrap_request: dict) -> EntregaCreate:
    movimentacoes = []
    for evento in scraped_data.get("historico_detalhado", []):
        dt_movimento = None
        if evento.get("timestamp"):
            try:
                dt_movimento = datetime.strptime(evento["timestamp"], "%d/%m/%Y %H:%M")
            except ValueError:
                pass
        
        movimentacoes.append(EntregaMovimentacaoCreate(
            movimento=evento.get("status", "N/A"),
            dt_movimento=dt_movimento
        ))

    status = None
    if movimentacoes:
        status = movimentacoes[-1].movimento

    return EntregaCreate(
        transportadora=scrap_request["transportadora"],
        numero_nf=scrap_request["numero_nf"],
        cnpj_destinatario=scrap_request["cnpj_destinatario"],
        codigo_rastreio="N/A",
        status=status,
        movimentacoes=movimentacoes
    )

def parse_accert(scraped_data: dict, scrap_request: dict) -> EntregaCreate:
    detalhes = scraped_data.get("detalhes", "")
    movimentacoes = [EntregaMovimentacaoCreate(movimento=detalhes)]
    return EntregaCreate(
        transportadora=scrap_request["transportadora"],
        numero_nf=scrap_request["numero_nf"],
        cnpj_destinatario=scrap_request["cnpj_destinatario"],
        codigo_rastreio="N/A",
        status=detalhes.split('\n')[0] if detalhes else None,
        movimentacoes=movimentacoes
    )

def parse_jamef(scraped_data: dict, scrap_request: dict) -> EntregaCreate:
    detalhes = scraped_data.get("detalhes", "")
    movimentacoes = [EntregaMovimentacaoCreate(movimento=detalhes)]
    return EntregaCreate(
        transportadora=scrap_request["transportadora"],
        numero_nf=scrap_request["numero_nf"],
        cnpj_destinatario=scrap_request["cnpj_destinatario"],
        codigo_rastreio="N/A",
        status=detalhes.split('\n')[0] if detalhes else None,
        movimentacoes=movimentacoes
    )

def parse_viaverde(scraped_data: dict, scrap_request: dict) -> EntregaCreate:
    movimentacoes = []
    for ocorrencia in scraped_data.get("ocorrencias", []):
        movimentacoes.append(EntregaMovimentacaoCreate(
            movimento=ocorrencia.get("status", "N/A")
        ))

    previsao_entrega = None
    if scraped_data.get("data_entrega"):
        try:
            previsao_entrega = datetime.strptime(scraped_data["data_entrega"], "%d/%m/%Y").date()
        except ValueError:
            pass

    return EntregaCreate(
        transportadora=scrap_request["transportadora"],
        numero_nf=scrap_request["numero_nf"],
        cnpj_destinatario=scrap_request["cnpj_destinatario"],
        codigo_rastreio=scraped_data.get("n_rastreio"),
        cliente=scraped_data.get("destinatario"),
        status=movimentacoes[-1].movimento if movimentacoes else None,
        previsao_entrega=previsao_entrega,
        movimentacoes=movimentacoes
    )

PARSER_MAPPING = {
    "braspress": parse_braspress,
    "accert": parse_accert,
    "jamef": parse_jamef,
    "viaverde": parse_viaverde,
}

def parse_scraped_data(transportadora: str, scraped_data: dict, scrap_request: dict) -> EntregaCreate:
    if transportadora not in PARSER_MAPPING:
        raise ValueError(f"Parser for '{transportadora}' not found.")
    
    parser_function = PARSER_MAPPING[transportadora]
    return parser_function(scraped_data, scrap_request)
