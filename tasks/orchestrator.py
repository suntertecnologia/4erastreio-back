import sys
import os
import asyncio
import aiohttp
from tasks.create_orchestrator_user import create_user

# Add the project root to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tasks.create_sample_excel import ler_planilha
from src.configs.logger_config import logger
from src.configs.config import (
    TENTATIVAS_MAXIMAS,
    DELAY_ENTRE_TENTATIVAS_SEGUNDOS,
    ENDPOINT_SCRAPING,
    ENDPOINT_NOTIFICACAO,
    ORCHESTRATOR_USER_EMAIL,
    ORCHESTRATOR_USER_PASSWORD,
    BASE_URL,
    TIMEOUTS,
)

Braspress_wait = TIMEOUTS["Brasspress_wait"] / 1000


async def get_auth_token(session: aiohttp.ClientSession) -> str:
    """Autentica e retorna o token de acesso."""
    try:
        logger.info("Autenticando para obter o token de acesso...")
        async with session.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": ORCHESTRATOR_USER_EMAIL,
                "password": ORCHESTRATOR_USER_PASSWORD,
            },
        ) as response:
            response.raise_for_status()
            data = await response.json()
            token = data["access_token"]
            logger.info("Autenticação bem-sucedida.")
            return token
    except aiohttp.ClientError as e:
        logger.error(f"ERRO CRÍTICO: Falha na autenticação: {e}")
        raise


async def executar_scraping_com_retentativa(
    session: aiohttp.ClientSession, entrega: dict, headers: dict
) -> dict:
    """Chama o endpoint de scraping para uma entrega, com lógica de retentativa."""
    for tentativa in range(1, TENTATIVAS_MAXIMAS + 1):
        try:
            logger.info(
                f"Tentativa {tentativa}/{TENTATIVAS_MAXIMAS} para NF {entrega['numero_nf']} da {entrega['transportadora']}..."
            )

            async with session.post(
                ENDPOINT_SCRAPING, json=entrega, headers=headers
            ) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(
                    f"Scraping request sent for NF {entrega['numero_nf']}. Task ID: {data.get('task_id')}"
                )
                return {
                    "status": "sent",
                    "task_id": data.get("task_id"),
                    "entrega": entrega,
                }

        except aiohttp.ClientError as e:
            logger.warning(
                f"FALHA na tentativa {tentativa} para NF {entrega['numero_nf']}. Erro: {e}"
            )
            if tentativa < TENTATIVAS_MAXIMAS:
                logger.info(
                    f"Aguardando {DELAY_ENTRE_TENTATIVAS_SEGUNDOS}s para a próxima tentativa..."
                )
                await asyncio.sleep(DELAY_ENTRE_TENTATIVAS_SEGUNDOS)
            else:
                logger.error(
                    f"Todas as {TENTATIVAS_MAXIMAS} tentativas falharam para a NF {entrega['numero_nf']}."
                )
                return {"status": "failed_to_send", "error": str(e), "entrega": entrega}


async def check_task_status(
    session: aiohttp.ClientSession, task_id: str, headers: dict
) -> dict:
    """Verifica o status de uma tarefa de scraping."""
    try:
        async with session.get(
            f"{BASE_URL}/entrega/scrap/status/{task_id}", headers=headers
        ) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Erro ao verificar status da tarefa {task_id}: {e}")
        return {"status": "ERROR", "error_message": str(e)}


async def notificar_resultados(
    session: aiohttp.ClientSession, resultados: list, headers: dict
):
    """Chama o endpoint de notificação com um resumo dos resultados."""
    sucessos = sum(1 for r in resultados if r and r["status"] == "SUCCESS")
    falhas = sum(1 for r in resultados if r and r["status"] == "FAILED")

    payload = {
        "mensagem": f"Rotina de rastreamento finalizada. {sucessos} sucesso(s) e {falhas} falha(s).",
        "detalhes_falhas": [
            {"entrega": r["entrega"], "error": r.get("error_message", "Unknown error")}
            for r in resultados
            if r and r["status"] == "FAILED"
        ],
    }

    try:
        logger.info("Acionando endpoint de notificação...")
        async with session.post(
            ENDPOINT_NOTIFICACAO, json=payload, headers=headers
        ) as response:
            response.raise_for_status()
            logger.info("Notificação enviada com sucesso.")
    except aiohttp.ClientError as e:
        logger.error(f"Falha ao enviar notificação: {e}")


async def main():
    """Função principal que orquestra todo o fluxo."""
    logger.info("=" * 50)
    logger.info(" INICIANDO ROTINA DE RASTREAMENTO AGENDADA ")
    logger.info("=" * 50)
    create_user()

    async with aiohttp.ClientSession() as session:
        try:
            token = await get_auth_token(session)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
        except Exception:
            return

        df_entregas = ler_planilha()

        if df_entregas.empty:
            logger.warning(
                "Nenhuma entrega encontrada na planilha. Encerrando a rotina."
            )
            return

        active_tasks = (
            {}
        )  # {task_id: {"entrega": {...}, "retries": 0, "initial_task_id": "..."}}
        completed_results = []

        # Send initial scraping requests
        for index, entrega in df_entregas.iterrows():
            entrega_data = {
                "transportadora": str(entrega["transportadora"]),
                "numero_nf": str(entrega["numero_nf"]),
                "cnpj_destinatario": str(entrega["cnpj_destinatario"]),
            }
            result = await executar_scraping_com_retentativa(
                session, entrega_data, headers
            )
            if result["status"] == "sent":
                active_tasks[result["task_id"]] = {
                    "entrega": entrega_data,
                    "retries": 0,
                    "initial_task_id": result["task_id"],
                }
            else:
                completed_results.append(
                    {
                        "status": "FAILED",
                        "error_message": result.get("error"),
                        "entrega": entrega_data,
                    }
                )

            # --- NEW LOGIC FOR BRASPRESS ---
            if entrega_data["transportadora"].lower() == "braspress":
                logger.info(
                    f"Braspress detected. Waiting {Braspress_wait} seconds before next request to avoid blocking."
                )
                await asyncio.sleep(Braspress_wait)

        logger.info(f"Sent {len(active_tasks)} scraping requests. Starting polling...")

        # Polling loop
        while active_tasks:
            tasks_to_check = list(active_tasks.keys())
            for task_id in tasks_to_check:
                status_data = await check_task_status(session, task_id, headers)
                current_status = status_data.get("status")
                error_message = status_data.get("error_message")
                entrega_id = status_data.get("entrega_id")

                if current_status == "SUCCESS":
                    logger.info(
                        f"Task {task_id} for NF {active_tasks[task_id]['entrega']['numero_nf']} completed successfully."
                    )
                    completed_results.append(
                        {
                            "status": "SUCCESS",
                            "entrega": active_tasks[task_id]["entrega"],
                            "entrega_id": entrega_id,
                        }
                    )
                    del active_tasks[task_id]
                elif current_status == "FAILED" or current_status == "ERROR":
                    logger.warning(
                        f"Task {task_id} for NF {active_tasks[task_id]['entrega']['numero_nf']} failed. Error: {error_message}"
                    )
                    if active_tasks[task_id]["retries"] < TENTATIVAS_MAXIMAS:
                        active_tasks[task_id]["retries"] += 1
                        logger.info(
                            f"Retrying task {task_id} for NF {active_tasks[task_id]['entrega']['numero_nf']} (Retry {active_tasks[task_id]["retries"]}/{TENTATIVAS_MAXIMAS})..."
                        )
                        # Re-send the scraping request, which will create a new task_id
                        entrega_data = active_tasks[task_id]["entrega"]
                        new_result = await executar_scraping_com_retentativa(
                            session, entrega_data, headers
                        )
                        if new_result["status"] == "sent":
                            # Replace old task_id with new one, keep retry count
                            active_tasks[new_result["task_id"]] = active_tasks.pop(
                                task_id
                            )
                            active_tasks[new_result["task_id"]]["initial_task_id"] = (
                                new_result["task_id"]
                            )  # Update initial_task_id
                        else:
                            # Failed to even send retry request
                            completed_results.append(
                                {
                                    "status": "FAILED",
                                    "error_message": new_result.get(
                                        "error", "Failed to resend scraping request."
                                    ),
                                    "entrega": entrega_data,
                                }
                            )
                            del active_tasks[task_id]
                    else:
                        logger.error(
                            f"Task {task_id} for NF {active_tasks[task_id]['entrega']['numero_nf']} failed after {TENTATIVAS_MAXIMAS} retries."
                        )
                        completed_results.append(
                            {
                                "status": "FAILED",
                                "error_message": error_message,
                                "entrega": active_tasks[task_id]["entrega"],
                            }
                        )
                        del active_tasks[task_id]
                # If status is PENDING or IN_PROGRESS, do nothing and check again later

            if active_tasks:
                logger.info(f"Waiting for {len(active_tasks)} tasks to complete...")
                await asyncio.sleep(
                    DELAY_ENTRE_TENTATIVAS_SEGUNDOS
                )  # Wait before polling again

        logger.info("All scraping tasks completed or failed after retries.")
        await notificar_resultados(session, completed_results, headers)

    logger.info("=" * 50)
    logger.info(" ROTINA DE RASTREAMENTO FINALIZADA ")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
