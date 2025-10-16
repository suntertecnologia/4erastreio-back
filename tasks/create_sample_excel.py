import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.configs.logger_config import logger
from src.configs.config import CAMINHO_PLANILHA_ENTREGAS
import pandas as pd


def ler_planilha() -> pd.DataFrame:
    """Lê a planilha Excel e retorna um DataFrame com as entregas."""
    try:
        logger.info(f"Lendo planilha de entregas de: {CAMINHO_PLANILHA_ENTREGAS}")
        df = pd.read_excel(CAMINHO_PLANILHA_ENTREGAS, header=1)
        print(df)
        df = df[["TRANSPORTADORAS", "CNPJ CONSULTA", "NOTAS"]]
        df = df.rename(
            columns={
                "CNPJ CONSULTA": "cnpj_destinatario",
                "NOTAS": "numero_nf",
                "TRANSPORTADORAS": "transportadora",
            }
        )

        df["transportadora"] = df["transportadora"].apply(
            lambda x: x.lower()
        )  # Lowercase in transportadora
        df["transportadora"] = df["transportadora"].apply(
            lambda x: x.replace(" ", "")
        )  # Remove whitespace

        logger.info(f"Encontradas {len(df)} entregas para processar.")
        return df

    except FileNotFoundError:
        logger.error(
            f"ERRO CRÍTICO: Planilha não encontrada em '{CAMINHO_PLANILHA_ENTREGAS}'. Abortando execução."
        )
        return pd.DataFrame()


print(ler_planilha())
