from __future__ import annotations
from ..configs.logger_config import logger
from playwright.async_api import Error
from .base_scraper import BaseScraper
from ..configs.config import SCRAPER_URLS, TIMEOUTS
from .scrapper_data_model import ScraperResponse
from . import braspress_handler
import asyncio
import random
import re
from playwright.async_api import TimeoutError


class BrasspressScraper(BaseScraper):
    """Scraper BRASPRESS com antidetecção e antiscroll/overlay agressivo."""

    def __init__(self):
        super().__init__("braspress")

    # ==================== Anti-detecção ====================

    async def _stealth_init(self, page):
        await page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR','pt','en-US','en'] });
            Object.defineProperty(navigator, 'plugins',   { get: () => [1,2,3] });
            window.chrome = window.chrome || { runtime: {} };
            try { Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 }); } catch(e){}
        """
        )

    def _rand_delay(self, a=80, b=160) -> int:
        return random.randint(a, b)

    async def _type_like_human(
        self, page, selector: str, text: str, trigger_keypress: bool = False
    ):
        # usa JS focus para evitar auto-scroll do Playwright
        await page.evaluate(
            """sel => {
            const el = document.querySelector(sel);
            if (el) el.focus({preventScroll:true});
        }""",
            selector,
        )
        await page.type(selector, text, delay=self._rand_delay())
        if trigger_keypress:
            await page.press(selector, "Tab")

    # ==================== Anti-scroll & Overlays ====================

    async def _quarantine_scroll_jank(self, page):
        """
        Desativa temporariamente scroll automático/forçado e locks comuns.
        - neutraliza scrollIntoView/scrollTo/scrollBy com no-ops
        - remove classes de lock (modal-open, no-scroll...)
        - força overflow:auto
        - aplica scroll-behavior: auto
        """
        await page.add_init_script(
            """
            // no-ops (mantemos referência para restaurar ao recarregar página)
            try {
                const noop = function(){};
                window.__PL_ORIG_SCROLL_TO__ = window.scrollTo;
                window.__PL_ORIG_SCROLL_BY__ = window.scrollBy;
                window.__PL_ORIG_EL_SCROLL_INTO_VIEW__ = Element.prototype.scrollIntoView;

                window.scrollTo = noop;
                window.scrollBy = noop;
                Element.prototype.scrollIntoView = noop;
            } catch(e){}

            // Evita CSS que “ancora” layout no topo
            try {
                const st = document.createElement('style');
                st.setAttribute('data-pl-anti-scroll', '1');
                st.textContent = `
                    html, body { scroll-behavior: auto !important; overflow: auto !important; position: static !important; }
                    *[data-pl-neutralized-overlay="1"] { pointer-events: none !important; opacity:0 !important; visibility:hidden !important; }
                `;
                document.documentElement.appendChild(st);
            } catch(e){}
        """
        )

        # Remove locks de body/html
        await page.evaluate(
            """
            try {
                const clsToRemove = ['modal-open','no-scroll','locked','overflow-hidden','disable-scroll'];
                document.documentElement.style.overflow = 'auto';
                document.body.style.overflow = 'auto';
                clsToRemove.forEach(c => { document.documentElement.classList.remove(c); document.body.classList.remove(c); });
            } catch(e){}
        """
        )

    async def _kill_overlays_continuous(self, page, window_ms=5000):
        """
        Neutraliza overlays de forma CONTÍNUA por alguns segundos, inclusive em shadow DOM,
        sem clicar: aplica pointer-events:none/opacity:0/visibility:hidden somente em elementos
        fixed/absolute, z-index alto, e que cubram a tela/interceptem o centro.
        """
        js = """
        (() => {
            const vw = innerWidth, vh = innerHeight, vArea = vw*vh;

            const neutralize = (root) => {
                const nodes = root.querySelectorAll ? root.querySelectorAll('*') : [];
                nodes.forEach(el => {
                    try {
                        const cs = getComputedStyle(el);
                        if (!cs) return;
                        const pos = cs.position;
                        if (pos !== 'fixed' && pos !== 'absolute') return;
                        const zi = parseInt(cs.zIndex || '0', 10);
                        if (!(zi >= 100)) return; // superposto
                        const r = el.getBoundingClientRect();
                        const area = Math.max(0, r.width) * Math.max(0, r.height);
                        if (area < (vArea * 0.3)) return;
                        const txt = ((el.id||'') + ' ' + (el.className||'')).toLowerCase();
                        const role = (el.getAttribute('role')||'').toLowerCase();
                        const aria = (el.getAttribute('aria-modal')||'').toLowerCase();
                        const overlayish = /overlay|backdrop|modal|popup|cookie|consent|gdpr|banner|dialog|lightbox/.test(txt) || role==='dialog' || aria==='true';

                        const centerEl = document.elementFromPoint(vw/2, vh/2);
                        let intercepts = false;
                        if (centerEl) {
                            let p = centerEl;
                            while (p) { if (p === el) { intercepts = true; break; } p = p.parentElement; }
                        }
                        if (overlayish && (area >= vArea*0.6 || intercepts)) {
                            el.setAttribute('data-pl-neutralized-overlay','1');
                            el.style.pointerEvents = 'none';
                            el.style.opacity = '0';
                            el.style.visibility = 'hidden';
                        }
                    } catch(e){}
                });
            };

            // varredura inicial
            neutralize(document);

            // shadow DOMs
            const walkShadow = (node) => {
                if (node && node.shadowRoot) {
                    neutralize(node.shadowRoot);
                    node.shadowRoot.querySelectorAll('*').forEach(walkShadow);
                }
                if (node && node.querySelectorAll) {
                    node.querySelectorAll('*').forEach(n => { if (n.shadowRoot) walkShadow(n); });
                }
            };
            walkShadow(document);

            // observer para neutralizar recém-inseridos
            if (!window.__PL_OVERLAY_OBSERVER__) {
                window.__PL_OVERLAY_OBSERVER__ = new MutationObserver(muts => {
                    muts.forEach(m => {
                        m.addedNodes && m.addedNodes.forEach(n => {
                            try {
                                if (n.nodeType === 1) {
                                    neutralize(n);
                                    if (n.shadowRoot) neutralize(n.shadowRoot);
                                }
                            } catch(e){}
                        });
                    });
                });
                window.__PL_OVERLAY_OBSERVER__.observe(document.documentElement, {childList:true, subtree:true});
            }
        })();"""
        # roda já e mais algumas vezes ao longo da janela de tempo
        end = asyncio.get_event_loop().time() + (window_ms / 1000.0)
        while asyncio.get_event_loop().time() < end:
            try:
                await page.evaluate(js)
            except Exception:
                pass
            await page.wait_for_timeout(200)

    async def _click_js_no_scroll(self, page, selector: str) -> bool:
        """
        Clica via JS (el.click()) sem scroll automático. Retorna True se clicou.
        """
        return (
            await page.evaluate(
                """
            (sel) => {
                const el = document.querySelector(sel);
                if (!el) return false;
                el.focus && el.focus({preventScroll:true});
                const evtOpts = {bubbles:true, cancelable:true};
                el.dispatchEvent(new MouseEvent('pointerdown', evtOpts));
                el.dispatchEvent(new MouseEvent('mousedown', evtOpts));
                el.click();
                el.dispatchEvent(new MouseEvent('mouseup', evtOpts));
                el.dispatchEvent(new MouseEvent('pointerup', evtOpts));
                return true;
            }
        """,
                selector,
            )
            or False
        )

    async def _safe_click(self, page, selector: str):
        """
        Tenta JS click (sem scroll). Se falhar, tenta mouse click por bounding box.
        Nunca usa element.click() do Playwright (que força scroll).
        """
        ok = await self._click_js_no_scroll(page, selector)
        if ok:
            return
        # fallback: coordenadas do centro do elemento
        el = page.locator(selector).first
        if await el.count() == 0:
            raise TimeoutError(f"Elemento não encontrado: {selector}")
        box = await el.bounding_box()
        if not box:
            raise TimeoutError(f"Sem bounding box para: {selector}")
        await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        await page.mouse.down()
        await page.mouse.up()

    # ==================== App readiness / iframes ====================

    async def _wait_nf_visible(self, page):
        await page.wait_for_function(
            """() => {
                const el = document.querySelector('#pedido-tracking');
                return el && getComputedStyle(el).display !== 'none' && !el.disabled;
            }""",
            timeout=12000,
        )

    async def _submit_form(self, page):
        # usa clique JS para evitar scroll
        search_sel = ".search-tracking"
        if await page.locator(search_sel).first.count() > 0:
            await self._safe_click(page, search_sel)
        else:
            await page.evaluate(
                """
                const f = document.getElementById('form-tracking');
                if (f) f.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
            """
            )
        await page.wait_for_timeout(self._rand_delay(220, 420))

    async def _wait_results_iframe(self, page):
        await page.wait_for_selector(
            "#iframe-tracking", timeout=TIMEOUTS.get("selector_wait", 20000)
        )
        frame_locator = page.frame_locator("#iframe-tracking")
        await page.wait_for_timeout(self._rand_delay(700, 1100))
        return frame_locator

    # ==================== Fluxo principal ====================

    async def scrape(self, cnpj: str, nota_fiscal: str) -> ScraperResponse:
        page = await self.create_page()
        log_prefix = self._get_log_prefix(cnpj=cnpj, nota_fiscal=nota_fiscal)
        url = SCRAPER_URLS["braspress"]

        attempts, last_err = 2, None
        for attempt in range(1, attempts + 1):
            try:
                logger.info(
                    f"{log_prefix} - Acessando {url} (tentativa {attempt}/{attempts})"
                )
                await self._stealth_init(page)

                await page.goto(
                    url,
                    timeout=TIMEOUTS.get("page_load", 45000),
                    wait_until="domcontentloaded",
                )

                # 🚫 mata auto-scroll/locks e neutraliza overlays continuamente por ~5s
                await self._quarantine_scroll_jank(page)
                await self._kill_overlays_continuous(page, window_ms=5000)

                # === Formulário ===
                logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
                await self._type_like_human(
                    page, "#cnpj-tracking", cnpj, trigger_keypress=True
                )
                await page.wait_for_timeout(self._rand_delay(250, 420))

                logger.info(f"{log_prefix} - Aguardando campo NF visível")
                await self._wait_nf_visible(page)

                logger.info(f"{log_prefix} - Preenchendo Nota Fiscal: {nota_fiscal}")
                await self._type_like_human(
                    page, "#pedido-tracking", nota_fiscal, trigger_keypress=True
                )
                await page.wait_for_timeout(self._rand_delay(220, 380))

                logger.info(f"{log_prefix} - Submetendo busca")
                await self._submit_form(page)

                try:
                    await page.wait_for_load_state(
                        "networkidle", timeout=TIMEOUTS.get("Brasspress_wait", 30000)
                    )
                except TimeoutError:
                    pass

                logger.info(f"{log_prefix} - Aguardando resultados no iframe")
                frame_locator = await self._wait_results_iframe(page)

                # “Detalhes” e “Mais Detalhes” com clique JS
                det = frame_locator.get_by_text(
                    re.compile(r"Detalhes do Rastreamento", re.I)
                ).first
                if await det.is_visible():
                    # usa evaluate no frame
                    try:
                        await det.evaluate("(el) => el.click()")
                    except Exception:
                        pass
                    await page.wait_for_timeout(self._rand_delay(300, 600))

                mais = frame_locator.get_by_text(
                    re.compile(r"Mais Detalhes", re.I)
                ).first
                if await mais.is_visible():
                    try:
                        await mais.evaluate("(el) => el.click()")
                    except Exception:
                        pass
                    await page.wait_for_timeout(self._rand_delay(300, 600))

                logger.info(f"{log_prefix} - Extraindo informações")
                movimentacoes = await braspress_handler.parse_detailed_history(
                    frame_locator
                )
                resumo_entrega = await braspress_handler.parse_summary_steps(
                    frame_locator
                )
                data = {
                    "resumo_etapas": resumo_entrega,
                    "historico_detalhado": movimentacoes,
                }

                logger.info(f"{log_prefix} - Dados extraídos com sucesso")
                return self.success_response(data)

            except TimeoutError as e:
                last_err = e
                logger.warning(f"{log_prefix} - Timeout na tentativa {attempt}: {e}")
            except Error as e:
                last_err = e
                logger.warning(
                    f"{log_prefix} - Erro Playwright na tentativa {attempt}: {e}"
                )
            except Exception as e:
                last_err = e
                logger.exception(
                    f"{log_prefix} - Erro inesperado na tentativa {attempt}: {e}"
                )

            await asyncio.sleep(2.0 * attempt + random.random())

        msg = "Não foi possível obter o rastreamento agora. O site pode ter aplicado verificação ou estar instável."
        return self.error_response("parse_error", f"{msg} Detalhes: {last_err}")
