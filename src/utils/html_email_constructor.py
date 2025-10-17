from datetime import datetime
import html

# Configure aqui se quiser
COMPANY_NAME = "QUATRO ESTAÇÕES"
LOGO_URL = ""  # ex.: "https://seu-dominio.com/logo.png" (deixe vazio para mostrar somente o nome)


def esc(text):
    """Escapa valores para uso seguro no HTML."""
    if text is None:
        return ""
    return html.escape(str(text))


def classify_status_from_emoji(emoji_text: str):
    """
    Mapeia seu emoji atual para classes visuais:
    - Contém '🔴' -> atrasado
    - Contém '🟢' -> entregue
    - Caso contrário -> em trânsito/andamento
    """
    s = (emoji_text or "").strip()
    if "🔴" in s:
        return "late"
    if "🟢" in s:
        return "ok"
    return "intransit"


def build_email_html(
    deliveries_by_carrier,
    now: datetime,
    get_status_emoji,
    logo_url=LOGO_URL,
    company_name=COMPANY_NAME,
):
    generated_at_br = now.strftime("%d/%m/%Y às %H:%M")

    # Paleta/cores
    brand_text = "#1E1E3D"
    brand_bg_soft = "#FFFFFF"  # email majoritariamente branco
    brand_accent = "#f74177"  # seu "rosa"
    ok_border = "#80D27C"  # entregue
    late_border = "#E25757"  # atraso (corrigido p/ vermelho)
    intransit_border = brand_accent

    # CSS amigável para e-mail
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
    .brandbar {{ height:6px; background:linear-gradient(90deg,{brand_accent} 0%, #6fc3de 60%, {brand_accent} 100%); }}
    .header {{ padding:22px 24px; background:#ffffff; border-bottom:1px solid rgba(30,30,61,.06); }}
    .logo-row {{
      display:flex; align-items:center; justify-content:space-between; gap:12px;
    }}
    .logo {{
      width:140px; height:40px; object-fit:contain; display:block;
    }}
    .brandname {{
      font-weight:800; font-size:16px; letter-spacing:.2px; color:{brand_text};
    }}
    .title {{ font-size:20px; font-weight:700; margin:8px 0 6px; }}
    .subtitle {{ font-size:14px; margin:0; opacity:.85; }}
    .content {{ padding:16px 24px 8px; }}
    .carrier {{ font-weight:700; font-size:15px; letter-spacing:.3px; margin:18px 0 10px; }}
    .card {{
      border:1px dashed rgba(30,30,61,.18);
      border-left:6px solid {brand_accent};
      border-radius:12px;
      padding:14px 16px;
      margin:10px 0 18px;
      background:#ffffff;
    }}
    .card.ok {{ border-left-color: {ok_border}; }}
    .card.late {{ border-left-color: {late_border}; }}
    .card.intransit {{ border-left-color: {intransit_border}; }}
    .kv {{ margin:0 0 6px; font-size:14px; }}
    .kv strong {{ display:inline-block; min-width:160px; }}
    .status-badge {{
      display:inline-block; font-weight:700; font-size:12px; padding:3px 8px; border-radius:999px; border:1px solid; margin-left:8px;
    }}
    .ok-badge {{ background:#EAF8EF; border-color:{ok_border}; }}
    .late-badge {{ background:#FDEAEA; border-color:{late_border}; }}
    .intransit-badge {{ background:#e9f6fb; border-color:{brand_accent}; }}
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

    html_parts = []
    html_parts.append(
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
          <div class="logo-row">
            <div class="brandname">{esc(company_name)}</div>"""
    )

    if logo_url:
        html_parts.append(
            f"""            <img src="{esc(logo_url)}" alt="Logo" class="logo" />"""
        )
    else:
        # Espaço reservado para logo (mantém o layout)
        html_parts.append(
            """            <div style="width:140px;height:40px;border:1px dashed rgba(37,150,190,.45); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:11px; color:#7aaec4;">LOGO</div>"""
        )

    html_parts.append(
        f"""          </div>
          <p class="title">Olá, abaixo o resumo das suas entregas 🚚</p>
          <p class="subtitle">Status verificados em: <strong>{esc(generated_at_br)}</strong></p>
        </td>
      </tr>
      <tr><td class="content">
    """
    )

    # Percorre transportadoras / entregas (mantém sua ordenação)
    first_carrier = True
    for carrier, deliveries in deliveries_by_carrier.items():
        if not first_carrier:
            html_parts.append('<div class="divider"></div>')
        first_carrier = False

        html_parts.append(f'<div class="carrier">{esc(carrier).upper()}:</div>')

        for idx, entrega in enumerate(deliveries):
            # Monta linhas (mantém sua lógica de campos opcionais)
            previsao = (
                entrega.previsao_entrega
                if getattr(entrega, "previsao_entrega", None)
                else None
            )
            cliente = entrega.cliente if getattr(entrega, "cliente", None) else None
            numero_nf = (
                entrega.numero_nf if getattr(entrega, "numero_nf", None) else None
            )

            # Determina classe de status a partir do emoji existente
            emoji_text = get_status_emoji(entrega)
            status_class = classify_status_from_emoji(emoji_text)
            badge_class = {
                "ok": "ok-badge",
                "late": "late-badge",
                "intransit": "intransit-badge",
            }.get(status_class, "intransit-badge")

            # Construção do card
            html_parts.append(f'<div class="card {status_class}">')

            if previsao:
                html_parts.append(
                    f'<p class="kv"><strong>Previsão de entrega:</strong> {esc(previsao)}</p>'
                )
            if cliente:
                html_parts.append(
                    f'<p class="kv"><strong>Cliente:</strong> {esc(cliente)}</p>'
                )
            if numero_nf:
                html_parts.append(
                    f'<p class="kv"><strong>NF:</strong> {esc(numero_nf)}</p>'
                )

            html_parts.append(
                f'<p class="kv"><strong>Status:</strong> {esc(emoji_text)} <span class="status-badge {badge_class}"></span></p>'
            )

            # Movimentações (duas mais recentes)
            html_parts.append('<p class="moves-title">Últimas movimentações</p>')
            if getattr(entrega, "movimentacoes", None):
                movs = sorted(
                    entrega.movimentacoes,
                    key=lambda m: (m.dt_movimento or datetime.min),
                    reverse=True,
                )[:2]
                html_parts.append('<ul class="moves">')
                if movs:
                    for mov in movs:
                        if getattr(mov, "movimento", None):
                            if getattr(mov, "dt_movimento", None):
                                html_parts.append(
                                    f'<li>- {esc(mov.movimento)} | {mov.dt_movimento.strftime("%d/%m/%Y às %H:%M")}</li>'
                                )
                            else:
                                html_parts.append(f"<li>- {esc(mov.movimento)}</li>")
                else:
                    html_parts.append("<li>Sem novas movimentações</li>")
                html_parts.append("</ul>")
            else:
                html_parts.append(
                    '<p style="margin:0 0 6px;font-size:14px;">Sem novas movimentações</p>'
                )

            html_parts.append("</div>")  # fecha .card

            # Linha longa entre cards (como no seu exemplo)
            if idx < len(deliveries) - 1:
                html_parts.append('<hr class="longline" />')

    # Rodapé
    html_parts.append(
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

    return "".join(html_parts)
