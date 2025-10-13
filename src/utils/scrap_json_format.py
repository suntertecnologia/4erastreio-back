import json

# ==============================================================================
# PASSO 1: SIMULAÇÃO DOS DADOS EXTRAÍDOS DO SCRAPER
# Em seu código real, esta variável viria do retorno da sua função de scraping.
# ==============================================================================
dados_brutos_simulados = {
    "numero_documento": "1431",
    "numero_nf": "118895",
    "data_entrega": "06/10/2025",
    "data_emissao_doc": "26/09/2025",
    "remetente": {"nome":"HUNTER DOUGLAS TOLDOS DO BRASIL LTDA","cnpj":"48.775.191/0001-90"},
    "destinatario": {"nome":"QUATRO ESTACOES COM E SERV DE DECORACOES LTDA","cnpj":"48.775.191/0001-90"},
    "ocorrencias": [
        "001 - MATERIAL ENTREGUE",
        "604 - CHEGADA UND.DESTINO",
        "603 - EM VIAGEM UND.DESTINO",
        "603 - EM VIAGEM UND.DESTINO",
        "602 - DOC.EMBARQUE AUTORIZADO",
        "601 - DOC.EMBARQUE EMITIDO"
    ]
}


# ==============================================================================
# PASSO 2: A FUNÇÃO "TRADUTORA" (MAPPER)
# Esta função converte o dicionário de dados brutos para o nosso padrão.
# ==============================================================================
def map_scrap_json(dados_brutos: dict, nome_transportadora: str) -> dict:
    """
    Recebe um dicionário com dados extraídos de um scraper e o converte
    para o formato JSON padrão da nossa aplicação.

    Args:
        dados_brutos: dicionário com os dados extraídos do scraper.
        nome_transportadora: Nome da transportadora (ex: "Accert").

    Returns:
        Um dicionário com as informações extraídas ou uma mensagem de erro.
    """
    
    historico_mapeado = []
    for ocorrencia_str in dados_brutos.get("ocorrencias", []):
        historico_mapeado.append({
            "timestamp": None,  # Data/hora não disponível por evento na fonte
            "status": ocorrencia_str.strip(),
            "local": {
                "cidade": None, # Não disponível por evento
                "estado": None  # Não disponível por evento
            },
            "detalhes": "" # Não disponível
        })
        
    # --- Mapeia a seção "informacoes_gerais" ---
    info_gerais = {
        "transportadora": nome_transportadora,
        "codigo_rastreio": dados_brutos.get("numero_documento"),
        "numero_nf": dados_brutos.get("numero_nf"),
        "previsao_entrega": dados_brutos.get("data_entrega"),
        "data_postagem": dados_brutos.get("data_emissao_doc"), # Assumindo que emissão do doc é a data de postagem
        "remetente": dados_brutos.get("remetente"),
        "destinatario":dados_brutos.get("destinatario")
    }
    
    # --- Monta a estrutura final ---
    json_padronizado = {
        "informacoes_gerais": info_gerais,
        "historico": historico_mapeado,
        "erro": None
    }
    
    return json_padronizado

# ==============================================================================
# PASSO 3: EXECUÇÃO E DEMONSTRAÇÃO
# ==============================================================================

# Chamamos a função de mapeamento, passando os dados brutos e o nome da transportadora
json_final_obj = map_scrap_json(dados_brutos_simulados, "GFL Logística")

# Imprime o resultado final em formato JSON legível
print(json.dumps(json_final_obj, indent=2, ensure_ascii=False))