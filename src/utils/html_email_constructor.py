from datetime import datetime
import html

LOGO_URL = ""  # ex.: "https://seu-dominio.com/logo.png"


def esc(x):
    return "" if x is None else html.escape(str(x))


def classify_status_from_emoji(emoji_text: str):
    s = (emoji_text or "").strip()
    if "🔴" in s:
        return "late"
    if "🟢" in s:
        return "ok"
    return "intransit"


def build_email_html(
    deliveries_by_carrier, now: datetime, get_status_emoji, logo_url=LOGO_URL
):
    generated_at_br = now.strftime("%d/%m/%Y às %H:%M")

    # Cores
    brand_text = "#1E1E3D"
    brand_bg_soft = "#FFFFFF"
    brand_pink = "#f74177"  # barra superior e “in transit”
    ok_border = "#80D27C"  # entregue
    late_border = "#E25757"  # atraso

    styles = f"""
    body {{ margin:0; padding:0; background:#f7f7f8; }}
    table {{ border-collapse:collapse; }}
    .outer {{
      width:100%; background:#f7f7f8; padding:24px 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Helvetica Neue", sans-serif;
      color:{brand_text};
    }}
    .container {{
      width:100%; max-width:720px; margin:0 auto; background:{brand_bg_soft};
      border-radius:14px; overflow:hidden; box-shadow:0 10px 30px rgba(30,30,61,.10);
      border:1px solid rgba(30,30,61,.06);
    }}
    /* Barra superior: apenas rosa */
    .brandbar {{ height:6px; background:{brand_pink}; }}
    /* Cabeçalho centralizado */
    .header {{ padding:28px 24px; background:#ffffff; border-bottom:1px solid rgba(30,30,61,.06); text-align:center; }}
    .logo-wrap {{ display:flex; align-items:center; justify-content:center; margin-bottom:14px; }}
    .logo {{ width:160px; height:48px; object-fit:contain; display:block; }}
    .logo-ph {{
      width:160px; height:48px; border:1px dashed rgba(247,65,119,.45); border-radius:8px;
      display:flex; align-items:center; justify-content:center; font-size:11px; color:#c74a6d;
    }}
    .title {{ font-size:20px; font-weight:800; margin:6px 0 6px; }}
    .subtitle {{ font-size:14px; margin:0; opacity:.85; }}
    .content {{ padding:16px 24px 8px; }}
    .carrier {{ font-weight:700; font-size:15px; letter-spacing:.3px; margin:18px 0 10px; }}
    .card {{
      border:1px dashed rgba(30,30,61,.18);
      border-left:6px solid {brand_pink};  /* padrão rosa para estados neutros */
      border-radius:12px;
      padding:14px 16px;
      margin:10px 0 18px;
      background:#ffffff;
    }}
    .card.ok {{ border-left-color: {ok_border}; }}
    .card.late {{ border-left-color: {late_border}; }}
    .kv {{ margin:0 0 6px; font-size:14px; }}
    .kv strong {{ display:inline-block; min-width:160px; }}
    /* Removidos badges; status ficará apenas com texto + emoji */
    .moves-title {{ margin:12px 0 6px; font-weight:700; font-size:14px; }}
    .moves {{ margin:0; padding-left:18px; font-size:14px; }}
    .longline {{ border:none; height:1px; background:#ddd; margin:18px 0; }}
    .divider {{
      height:1px;
      background:repeating-linear-gradient(90deg, rgba(30,30,61,.12), rgba(30,30,61,.12) 8px, transparent 8px, transparent 16px);
      margin:18px 0;
    }}
    .footer {{ padding:18px 24px; font-size:12px; color:{brand_text}; opacity:.7; text-align:center; }}
    @media (max-width: 480px) {{ .title {{ font-size:18px; }} .kv strong {{ min-width:140px; }} }}
    """

    parts = []
    parts.append(
        f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <meta name="x-apple-disable-message-reformatting" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Resumo de Entregas</title>
  <style>{styles}</style>
</head>
<body>
  <div class="outer">
    <table role="presentation" class="container" width="100%">
      <tr><td class="brandbar"></td></tr>
      <tr>
        <td class="header">
          <div class="logo-wrap">"""
    )

    if logo_url:
        parts.append(f'<img src="{esc(logo_url)}" alt="Logo" class="logo" />')
    else:
        parts.append('<div class="logo-ph">LOGO</div>')

    # Mensagem mais profissional no cabeçalho
    parts.append(
        f"""</div>
          <p class="title">Resumo das suas entregas</p>
          <p class="subtitle">Status atualizados em <strong>{esc(generated_at_br)}</strong></p>
        </td>
      </tr>
      <tr><td class="content">"""
    )

    first_carrier = True
    for carrier, deliveries in deliveries_by_carrier.items():
        if not first_carrier:
            parts.append('<div class="divider"></div>')
        first_carrier = False

        parts.append(f'<div class="carrier">{esc(carrier).upper()}:</div>')

        for idx, entrega in enumerate(deliveries):
            previsao = getattr(entrega, "previsao_entrega", None)
            cliente = getattr(entrega, "cliente", None)
            numero_nf = getattr(entrega, "numero_nf", None)

            emoji_text = get_status_emoji(entrega)
            status_class = classify_status_from_emoji(emoji_text)

            parts.append(f'<div class="card {status_class}">')
            if previsao:
                parts.append(
                    f'<p class="kv"><strong>Previsão de entrega:</strong> {esc(previsao)}</p>'
                )
            if cliente:
                parts.append(
                    f'<p class="kv"><strong>Cliente:</strong> {esc(cliente)}</p>'
                )
            if numero_nf:
                parts.append(f'<p class="kv"><strong>NF:</strong> {esc(numero_nf)}</p>')

            # Apenas texto + emoji (sem badge à direita)
            parts.append(
                f'<p class="kv"><strong>Status:</strong> {esc(emoji_text)}</p>'
            )

            parts.append('<p class="moves-title">Últimas movimentações</p>')
            movs = getattr(entrega, "movimentacoes", None)
            if movs:
                ordered = sorted(
                    movs,
                    key=lambda m: (m.dt_movimento or datetime.min),
                    reverse=True,
                )[:2]
                if ordered:
                    parts.append('<ul class="moves">')
                    for mov in ordered:
                        if getattr(mov, "movimento", None):
                            if getattr(mov, "dt_movimento", None):
                                parts.append(
                                    f'<li>- {esc(mov.movimento)} | {mov.dt_movimento.strftime("%d/%m/%Y às %H:%M")}</li>'
                                )
                            else:
                                parts.append(f"<li>- {esc(mov.movimento)}</li>")
                    parts.append("</ul>")
                else:
                    parts.append(
                        '<p style="margin:0 0 6px;font-size:14px;">Sem novas movimentações</p>'
                    )
            else:
                parts.append(
                    '<p style="margin:0 0 6px;font-size:14px;">Sem novas movimentações</p>'
                )

            parts.append("</div>")  # card

            if idx < len(deliveries) - 1:
                parts.append('<hr class="longline" />')

    parts.append(
        """
      </td></tr>
      <tr>
        <td class="footer">
          Este é um e-mail automático. Em caso de dúvidas, responda esta mensagem para falar com nosso time.
        </td>
      </tr>
    </table>
  </div>
</body>
</html>"""
    )

    return "".join(parts)
