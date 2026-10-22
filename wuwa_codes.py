"""
Robô de códigos do Wuthering Waves para Discord.

- Lê a página de códigos do Prydwen.
- Pega somente os códigos marcados como "Active".
- Envia para o webhook do Discord apenas os que ainda não foram enviados.
- Guarda os já enviados em sent_codes.json (o GitHub Actions faz commit desse arquivo).

Variáveis de ambiente:
  DISCORD_WEBHOOK_URL  (obrigatória) URL do webhook do canal
  DISCORD_ROLE_ID      (opcional) ID do cargo a ser mencionado
  DRY_RUN=1            (opcional) só mostra o que seria enviado, sem enviar
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString

SOURCE_URL = "https://www.prydwen.gg/wuthering-waves/codes"
STATE_FILE = Path(__file__).with_name("sent_codes.json")
CODE_RE = re.compile(r"^[A-Z0-9]{6,24}$")
HEADERS = {"User-Agent": "Mozilla/5.0 (wuwa-codes-discord-bot)"}


def fetch_html(url: str = SOURCE_URL) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_active_codes(html: str) -> dict:
    """Devolve {CODIGO: "recompensas"} só para os códigos marcados como ativos.

    A página lista cada código dentro de <code>, seguido das recompensas e de um
    selo "Active" ou "Expired". Os códigos da tabela de expirados não têm selo,
    então ficam de fora.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    active = {}
    current = None
    parts = []

    for node in soup.descendants:
        if not isinstance(node, NavigableString):
            continue
        text = " ".join(str(node).split())
        if not text:
            continue

        parent = node.parent.name if node.parent else ""
        if node.find_parent(["h1", "h2"]):  # nova seção: zera o código atual
            current = None
            continue
        if parent == "code" and CODE_RE.match(text):
            # códigos dentro de tabelas são a lista de expirados
            current = None if node.find_parent("table") else text
            parts = []
            continue
        if current is None:
            continue

        if text == "Active":
            active[current] = format_rewards(parts)
            current = None
        elif text == "Expired":
            current = None
        else:
            parts.append(text)
            if len(parts) > 60:  # segurança: nunca achou o selo
                current = None

    return active


def format_rewards(parts: list) -> str:
    """Junta pedaços como ['Astrite', '×50', 'Shell Credit', '×10,000']."""
    items = []
    for p in parts:
        if p.startswith("×") and items:
            items[-1] = f"{items[-1]} {p}"
        else:
            items.append(p)
    return ", ".join(items)


def load_sent() -> list:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return []


def save_sent(codes: list) -> None:
    STATE_FILE.write_text(json.dumps(sorted(set(codes)), indent=2) + "\n", encoding="utf-8")


def build_payload(code: str, rewards: str, role_id: str = "") -> dict:
    mention = f"<@&{role_id}> " if role_id else ""
    return {
        "username": "Códigos WuWa",
        "content": f"{mention}Novo código de Wuthering Waves!",
        "allowed_mentions": {"roles": [role_id] if role_id else []},
        "embeds": [
            {
                "title": code,
                "description": (
                    f"**Recompensas:** {rewards or 'ver no jogo'}\n\n"
                    "Resgate no jogo: Terminal → Configurações → Outras Configurações → "
                    "Conta → Código de Resgate.\n"
                    "Os códigos diferenciam maiúsculas e minúsculas."
                ),
                "color": 0x3BA7C9,
                "footer": {"text": "Fonte: prydwen.gg"},
            }
        ],
    }


def send(webhook: str, payload: dict) -> None:
    for _ in range(3):
        r = requests.post(webhook, json=payload, timeout=30)
        if r.status_code == 429:  # limite de envio do Discord
            time.sleep(float(r.json().get("retry_after", 2)))
            continue
        r.raise_for_status()
        return
    raise RuntimeError("Discord recusou o envio várias vezes (limite de taxa).")


def main() -> int:
    dry = os.getenv("DRY_RUN") == "1"
    webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    role_id = os.getenv("DISCORD_ROLE_ID", "").strip()
    if not webhook and not dry:
        print("Falta o segredo DISCORD_WEBHOOK_URL.")
        return 1

    active = parse_active_codes(fetch_html())
    if not active:
        # O WUTHERINGGIFT é fixo; se nada foi encontrado, a página mudou de formato.
        print("Nenhum código ativo encontrado. A página pode ter mudado de formato.")
        return 1

    sent = load_sent()
    new = [c for c in active if c not in sent]
    print(f"Ativos: {list(active)} | Novos: {new}")

    for code in new:
        payload = build_payload(code, active[code], role_id)
        if dry:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            send(webhook, payload)
            sent.append(code)
            save_sent(sent)  # salva a cada envio para não repetir se algo falhar
            time.sleep(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
