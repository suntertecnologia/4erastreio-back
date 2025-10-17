def treat_lista_ocorrencias(ocorrencias_raw: str) -> list:
    """
    Função para tratar a string de ocorrências retornada pelo scraper.
    Esta função pode ser expandida conforme necessário para ajustar o formato
    dos dados ou extrair informações adicionais.

    Args:
        ocorrencias_raw: String bruta com as ocorrências do scraper.

    Returns:
        Lista de dicionários com as ocorrências tratadas.
    """
    ocorrencias = []
    for linha in ocorrencias_raw.split("\n"):
        linha = linha.strip()
        if linha:
            ocorrencias.append(
                {
                    "timestamp": None,
                    "status": linha,
                    "local": {"cidade": None, "estado": None},
                    "detalhes": "",
                }
            )
    return ocorrencias
