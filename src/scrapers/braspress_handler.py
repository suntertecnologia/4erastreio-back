import regex as re
from playwright.async_api import Page


async def parse_detailed_history(page: Page) -> list[dict]:
    """Função auxiliar para extrair o histórico detalhado da timeline vertical."""
    history_events = []
    container = page.locator("#timeline2482705908231")

    event_locators = await container.locator(
        ".vertical-time-line._tracking-datail"
    ).all()

    for event_locator in event_locators:
        status_text = ""
        timestamp_text = ""

        info_loc = event_locator.locator(".vertical-time-line-info")
        if await info_loc.count() > 0:
            status_text = await info_loc.inner_text()
            status_text = re.sub(r"<br>.*", "", status_text).strip()

        date_loc = event_locator.locator(".vertical-time-line-date")
        if await date_loc.count() > 0:
            timestamp_text = (await date_loc.text_content() or "").strip()

        if status_text and timestamp_text:
            history_events.append({"timestamp": timestamp_text, "status": status_text})

    return history_events


async def parse_summary_steps(page: Page) -> dict:
    """Função auxiliar para extrair as etapas principais do resumo horizontal."""
    previsao_entrega = (
        await page.locator(".dt-previsao-entrega").first.text_content() or ""
    )
    status = await page.locator(".dt-status").first.text_content() or ""
    data_entrega = await page.locator(".dt-data-entrega").first.text_content() or ""
    data = {}
    data["previsao_entrega"] = previsao_entrega
    data["status"] = status
    data["data_entrega"] = data_entrega
    return data
