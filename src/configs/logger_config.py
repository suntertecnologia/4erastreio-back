# config/logger_config.py

import logging
from logging.handlers import RotatingFileHandler

# Damos um nome específico ao nosso logger para evitar conflitos com bibliotecas de terceiros
logger = logging.getLogger('AutomacaoRastreio')
logger.setLevel(logging.INFO)

# Adicionamos um 'if not logger.handlers' para garantir que a configuração só rode uma vez
if not logger.handlers:
    # Handler para o arquivo
    file_handler = RotatingFileHandler('automacao.log', maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Handler para o console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Formato da mensagem
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)