import asyncio
from datetime import datetime
from tasks.orchestrator import main


async def agendador_principal(time_cron: int):
    """
    Loop principal que executa a tarefa em intervalos definidos.
    """
    print(
        f"[{datetime.now():%H:%M:%S}] Agendador assíncrono iniciado. Executando a cada {time_cron} minutos."
    )
    while True:
        await main()
        print(f"[{datetime.now():%H:%M:%S}] Próxima execução em {time_cron} minutos...")
        await asyncio.sleep(time_cron)


if __name__ == "__main__":
    INTERVALO = 30 * 60  # minutos
    try:
        # Usa asyncio.run para iniciar o agendador principal
        asyncio.run(agendador_principal(INTERVALO))
    except KeyboardInterrupt:
        print("\nEncerrando o programa.")
