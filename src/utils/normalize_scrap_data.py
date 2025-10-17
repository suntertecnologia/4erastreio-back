from datetime import datetime
import re


def normalize_braspress(data, cnpj, nota_fiscal):
    """
    Normalizes the data scraped from Braspress.
    """
    if not data or "historico_detalhado" not in data:
        return None

    unique_history = []
    seen = set()
    for item in data["historico_detalhado"]:
        item_tuple = tuple(item.items())
        if item_tuple not in seen:
            unique_history.append(item)
            seen.add(item_tuple)

    if not unique_history:
        return None

    post_date_str = unique_history[0]["timestamp"].split(" ")[0]
    post_date = datetime.strptime(post_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

    previsao_entrega = None
    if data["resumo_etapas"]:
        previsao_entrega = data["resumo_etapas"]["previsao_entrega"]
        status = data["resumo_etapas"]["status"]

    # Fallback to last event if "ENTREGA REALIZADA" and previsao_entrega not found yet
    if (
        not previsao_entrega
        and unique_history
        and "ENTREGA REALIZADA" in unique_history[-1]["status"]
    ):
        previsao_entrega_str = unique_history[-1]["timestamp"].split(" ")[0]
        previsao_entrega = datetime.strptime(previsao_entrega_str, "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )

    normalized_history = []
    for item in unique_history:
        parts = item["status"].split(" - ")
        status = parts[0].strip()

        local = None
        if len(parts) > 1:
            location_str = parts[1].strip()
            location_parts = location_str.split(" - ")
            if len(location_parts) == 2:
                cidade = location_parts[0].strip()
                estado = location_parts[1].strip()
                local = {"cidade": cidade, "estado": estado}

        timestamp_obj = datetime.strptime(item["timestamp"], "%d/%m/%Y %H:%M")
        timestamp_iso = timestamp_obj.isoformat()

        normalized_history.append(
            {
                "timestamp": timestamp_iso,
                "status": status,
                "local": local,
                "detalhes": "",
            }
        )

    return {
        "informacoes_gerais": {
            "transportadora": "BRASPRESS",
            "codigo_rastreio": nota_fiscal,
            "numero_nf": nota_fiscal,
            "previsao_entrega": previsao_entrega,
            "data_postagem": post_date,
            "remetente": None,
            "destinatario": None,
            "cnpj_destinatario": cnpj,
        },
        "historico": normalized_history,
        "erro": None,
    }


def normalize_accert(data, cnpj, nota_fiscal):
    """
    Normalizes the data scraped from Accert.
    """
    if not data or "detalhes" not in data:
        return None

    details_str = data["detalhes"]

    previsao_match = re.search(r"Previsão de entrega: (\d{2}/\d{2}/\d{2})", details_str)
    previsao_entrega = None
    if previsao_match:
        previsao_entrega_str = previsao_match.group(1)
        previsao_entrega = datetime.strptime(previsao_entrega_str, "%d/%m/%y").strftime(
            "%Y-%m-%d"
        )

    history_blocks = re.findall(
        r"(\d{2}/\d{2} \d{2}:\d{2})\n\n(.*?)\n\n(.*?)(?=\n\n\d{2}/\d{2} \d{2}:\d{2}|$)",
        details_str,
        re.DOTALL,
    )

    normalized_history = []
    for block in history_blocks:
        timestamp_str, status, details = block
        timestamp = datetime.strptime(
            f"{timestamp_str}/{datetime.now().year}", "%d/%m %H:%M/%Y"
        ).isoformat()

        local = None
        location_match = re.search(r"na cidade de (.*?)\\.", details)
        if not location_match:
            location_match = re.search(r"unidade (.*?)(?: em| na)", details)
        if location_match:
            cidade = location_match.group(1).strip()
            local = {"cidade": cidade, "estado": None}

        normalized_history.append(
            {
                "timestamp": timestamp,
                "status": status.strip(),
                "local": local,
                "detalhes": details.strip(),
            }
        )

    post_date = None
    if normalized_history:
        post_date = datetime.fromisoformat(normalized_history[0]["timestamp"]).strftime(
            "%Y-%m-%d"
        )

    return {
        "informacoes_gerais": {
            "transportadora": "ACCERT",
            "codigo_rastreio": nota_fiscal,
            "numero_nf": nota_fiscal,
            "previsao_entrega": previsao_entrega,
            "data_postagem": post_date,
            "remetente": None,
            "destinatario": None,
            "cnpj_destinatario": cnpj,
        },
        "historico": normalized_history,
        "erro": None,
    }


def normalize_viaverde(data, cnpj, nota_fiscal):
    """
    Normalizes the data scraped from Via Verde.
    """
    if not data:
        return None

    previsao_entrega = None
    if data.get("data_entrega"):
        previsao_entrega = datetime.strptime(data["data_entrega"], "%d/%m/%Y").strftime(
            "%Y-%m-%d"
        )

    post_date = None

    normalized_history = []
    if "ocorrencias" in data:
        for item in data["ocorrencias"]:
            normalized_history.append(
                {
                    "timestamp": None,
                    "status": item["status"],
                    "local": item["local"],
                    "detalhes": item["detalhes"],
                }
            )

    return {
        "informacoes_gerais": {
            "transportadora": "VIAVERDE",
            "codigo_rastreio": data.get("n_rastreio"),
            "numero_nf": data.get("n_notafiscal"),
            "previsao_entrega": previsao_entrega,
            "data_postagem": post_date,
            "remetente": None,
            "destinatario": None,
            "cnpj_destinatario": cnpj,
        },
        "historico": normalized_history,
        "erro": None,
    }


def normalize_jamef(data, cnpj, nota_fiscal):
    """
    Normalizes the data scraped from Jamef.
    """
    if not data or "detalhes" not in data:
        return None

    details_str = data["detalhes"]

    history_blocks = re.findall(
        r"Data: (.*?)\n\nStatus: (.*?)\n\nEstado origem: (.*?)\n\nMunicípio origem: (.*?)\n\nEstado destino: (.*?)\n\nMunicípio destino: (.*?)(?=\n\nData:|$)",
        details_str,
        re.DOTALL,
    )

    normalized_history = []
    for block in history_blocks:
        timestamp_str, status, _, cidade_origem, _, cidade_destino = block
        timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M").isoformat()

        local = {
            "cidade": cidade_destino.strip(),
            "estado": None,
        }

        normalized_history.append(
            {
                "timestamp": timestamp,
                "status": status.strip(),
                "local": local,
                "detalhes": f"Origem: {cidade_origem.strip()}",
            }
        )

    post_date = None
    if normalized_history:
        post_date = datetime.fromisoformat(
            normalized_history[-1]["timestamp"]
        ).strftime("%Y-%m-%d")

    previsao_entrega = None
    if normalized_history and "ENTREGA REALIZADA" in normalized_history[0]["status"]:
        previsao_entrega = datetime.fromisoformat(
            normalized_history[0]["timestamp"]
        ).strftime("%Y-%m-%d")

    return {
        "informacoes_gerais": {
            "transportadora": "JAMEF",
            "codigo_rastreio": nota_fiscal,
            "numero_nf": nota_fiscal,
            "previsao_entrega": previsao_entrega,
            "data_postagem": post_date,
            "remetente": None,
            "destinatario": None,
            "cnpj_destinatario": cnpj,
        },
        "historico": normalized_history,
        "erro": None,
    }
