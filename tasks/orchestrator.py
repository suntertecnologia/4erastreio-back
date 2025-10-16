import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tasks.create_sample_excel import ler_planilha
import requests
import time
from src.configs.config import (
    TENTATIVAS_MAXIMAS,
    DELAY_ENTRE_TENTATIVAS_SEGUNDOS,
    ENDPOINT_SCRAPING,
    ENDPOINT_NOTIFICACAO,
    ORCHESTRATOR_USER_EMAIL,
    ORCHESTRATOR_USER_PASSWORD,
    BASE_URL,
)
from src.configs.logger_config import logger


def get_auth_token() -> str:
    """Autentica e retorna o token de acesso."""
    try:
        logger.info("Autenticando para obter o token de acesso...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": ORCHESTRATOR_USER_EMAIL,
                "password": ORCHESTRATOR_USER_PASSWORD,
            },
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        logger.info("Autenticação bem-sucedida.")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"ERRO CRÍTICO: Falha na autenticação: {e}")
        raise


def executar_scraping_com_retentativa(entrega: dict, headers: dict) -> dict:
    """Chama o endpoint de scraping para uma entrega, com lógica de retentativa."""
    for tentativa in range(1, TENTATIVAS_MAXIMAS + 1):
        try:
            logger.info(
                f"Tentativa {tentativa}/{TENTATIVAS_MAXIMAS} para NF {entrega['numero_nf']} da {entrega['transportadora']}..."
            )
            print(entrega)
            response = requests.post(ENDPOINT_SCRAPING, json=entrega, headers=headers)
            response.raise_for_status()

            logger.info(
                f"SUCESSO para NF {entrega['numero_nf']}. Status: {response.status_code}"
            )
            return {"status": "sucesso", "dados": response.json()}

        # --- A MÁGICA ACONTECE AQUI ---
        except requests.exceptions.HTTPError as http_err:
            logger.warning(f"FALHA na tentativa {tentativa} com erro HTTP: {http_err}")
            response_de_erro = http_err.response
            erro_body = response_de_erro.json()
            logger.error(
                f"Detalhes do erro (JSON) para NF {entrega['numero_nf']}: {erro_body}"
            )

        except requests.exceptions.RequestException as e:
            logger.warning(
                f"FALHA na tentativa {tentativa} para NF {entrega['numero_nf']}. Erro: {e}"
            )
            if tentativa < TENTATIVAS_MAXIMAS:
                logger.info(
                    f"Aguardando {DELAY_ENTRE_TENTATIVAS_SEGUNDOS}s para a próxima tentativa..."
                )
                time.sleep(DELAY_ENTRE_TENTATIVAS_SEGUNDOS)
            else:
                logger.error(
                    f"Todas as {TENTATIVAS_MAXIMAS} tentativas falharam para a NF {entrega['numero_nf']}."
                )
                return {"status": "falha", "erro": str(e)}


def notificar_resultados(resultados: list, headers: dict):
    """Chama o endpoint de notificação com um resumo dos resultados."""
    sucessos = sum(1 for r in resultados if r and r["status"] == "sucesso")
    falhas = len(resultados) - sucessos

    payload = {
        "mensagem": f"Rotina de rastreamento finalizada. {sucessos} sucesso(s) e {falhas} falha(s).",
        "detalhes_falhas": [r for r in resultados if r and r["status"] == "falha"],
    }

    try:
        logger.info("Acionando endpoint de notificação...")
        response = requests.post(ENDPOINT_NOTIFICACAO, json=payload, headers=headers)
        response.raise_for_status()
        logger.info("Notificação enviada com sucesso.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao enviar notificação: {e}")


def main():
    """Função principal que orquestra todo o fluxo."""
    logger.info("=" * 50)
    logger.info(" INICIANDO ROTINA DE RASTREAMENTO AGENDADA ")
    logger.info("=" * 50)

    try:
        token = get_auth_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
    except requests.exceptions.RequestException:
        return

    df_entregas = ler_planilha()

    if df_entregas.empty:
        logger.warning("Nenhuma entrega encontrada na planilha. Encerrando a rotina.")
        return

    resultados_finais = []
    for index, entrega in df_entregas.iterrows():
        entrega = {
            "transportadora": str(entrega["transportadora"]),
            "numero_nf": str(entrega["numero_nf"]),
            "cnpj_destinatario": str(entrega["cnpj_destinatario"]),
        }
        resultado = executar_scraping_com_retentativa(entrega, headers)
        resultados_finais.append(resultado)
        time.sleep(2)

    notificar_resultados(resultados_finais, headers)

    logger.info("=" * 50)
    logger.info(" ROTINA DE RASTREAMENTO FINALIZADA ")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
