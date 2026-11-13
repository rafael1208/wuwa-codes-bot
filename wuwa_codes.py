"""
Robô de códigos do Wuthering Waves para Discord.

- Lê várias páginas de códigos (Prydwen, GameMarket, Timesaver, Levvvel).
- Um código só é enviado quando as fontes concordam que ele está ativo:
    * Prydwen vale 2 votos (marca o status de cada código);
    * as outras valem 1 voto (o status vem dos títulos das seções).
  Basta 2 votos. Um site que lista o código como ativo e também como expirado
  não vota nele.
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

try:  # imita o navegador Chrome (TLS), o que costuma passar pelo Cloudflare
    from curl_cffi import requests as cffi_requests
except ImportError:  # pragma: no cover
    cffi_requests = None

STATE_FILE = Path(__file__).with_name("sent_codes.json")
CODE_RE = re.compile(r"^[A-Z0-9]{6,24}$")
# código no começo do texto, seguido de fim ou de um separador ("CODIGO: recompensas")
LEADING_CODE_RE = re.compile(r"^([A-Z0-9]{6,24})(?:\s*$|\s*[:(–—-]\s*(.*))", re.S)
PERMANENT_CODE = "WUTHERINGGIFT"
VOTES_NEEDED = 2

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class Found:
    active: dict = field(default_factory=dict)  # {CODIGO: "recompensas"}
    expired: set = field(default_factory=set)


@dataclass
class Source:
    name: str
    url: str
    parser: Callable[[str], Found]
    weight: int


# --------------------------------------------------------------------------- download

def fetch_html(url: str, attempts: int = 3) -> str:
    """Baixa a página fingindo ser o Chrome; tenta algumas vezes antes de desistir."""
    last_err = None
    for i in range(attempts):
        try:
            if cffi_requests is not None:
                resp = cffi_requests.get(url, headers=HEADERS, impersonate="chrome", timeout=30)
            else:
                ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
                resp = requests.get(url, headers={**HEADERS, **ua}, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:  # 403 do Cloudflare, timeout etc.
            last_err = e
            print(f"  tentativa {i + 1}/{attempts} falhou: {e}")
            if i < attempts - 1:
                time.sleep(5 * (i + 1))
    raise last_err


def make_soup(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return soup


def is_code(text: str) -> bool:
    # precisa ter pelo menos uma letra (evita números soltos como 100000)
    return bool(CODE_RE.match(text)) and any(c.isalpha() for c in text)


# --------------------------------------------------------------------------- Prydwen

def parse_prydwen(html: str) -> Found:
    """Cada código fica num <code>, seguido das recompensas e de um selo
    "Active" ou "Expired". Os códigos dentro de tabelas são o arquivo de expirados."""
    soup = make_soup(html)
    found = Found()
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
        if parent == "code" and is_code(text):
            if node.find_parent("table"):
                found.expired.add(text)
                current = None
            else:
                current = text
            parts = []
            continue
        if current is None:
            continue

        if text == "Active":
            found.active[current] = format_rewards(parts)
            current = None
        elif text == "Expired":
            found.expired.add(current)
            current = None
        else:
            parts.append(text)
            if len(parts) > 60:  # segurança: nunca achou o selo
                current = None

    return found


def format_rewards(parts: list) -> str:
    """Junta pedaços como ['Astrite', '×50', 'Shell Credit', '×10,000']."""
    items = []
    for p in parts:
        if p.startswith("×") and items:
            items[-1] = f"{items[-1]} {p}"
        else:
            items.append(p)
    return ", ".join(items)


# --------------------------------------------------------------------------- genérico

EXPIRED_WORDS = re.compile(r"expired|past|no longer|inactive|not working|old codes", re.I)
ACTIVE_WORDS = re.compile(r"\bactive\b|working|livestream|new codes?|current|valid", re.I)
CANDIDATE_TAGS = ["code", "strong", "b", "td", "li", "input"]


def classify_heading(text: str):
    if EXPIRED_WORDS.search(text):
        return "expired"
    if ACTIVE_WORDS.search(text):
        return "active"
    return None


def parse_generic(html: str) -> Found:
    """Para sites em formato de artigo: o status de cada código vem do título da seção
    em que ele aparece (ex.: "Active codes" / "Expired codes"). Subtítulos sem palavra-chave
    herdam o status do título acima. Códigos dentro de <details> (listas recolhidas)
    contam como expirados."""
    soup = make_soup(html)
    found = Found()
    levels = {}  # nível do título -> status

    for el in soup.find_all(["h2", "h3", "h4"] + CANDIDATE_TAGS):
        if el.name in ("h2", "h3", "h4"):
            lvl = int(el.name[1])
            for k in [k for k in levels if k >= lvl]:
                del levels[k]
            levels[lvl] = classify_heading(el.get_text(" ", strip=True))
            continue

        status = next((levels[k] for k in sorted(levels, reverse=True) if levels[k]), None)
        if el.find_parent("details"):
            status = "expired"
        if status is None:
            continue

        if el.name == "input":
            text = (el.get("value") or "").strip()
        else:
            text = " ".join(el.get_text(" ", strip=True).split())
        m = LEADING_CODE_RE.match(text)
        if not m or not is_code(m.group(1)):
            continue
        code = m.group(1)
        if status == "expired":
            found.expired.add(code)
        elif code not in found.active or not found.active[code]:
            found.active[code] = (m.group(2) or "").strip()

    return found


SOURCES = [
    Source("Prydwen", "https://www.prydwen.gg/wuthering-waves/codes", parse_prydwen, 2),
    Source("GameMarket",
           "https://gamemarket.gg/news/wuthering-waves/"
           "wuthering-waves-redeem-codes-that-still-work-and-how-to-redeem-them",
           parse_generic, 1),
    Source("Timesaver", "https://timesaver.gg/blog/wuthering-waves-codes", parse_generic, 1),
    Source("Levvvel", "https://levvvel.com/wuthering-waves-codes/", parse_generic, 1),
]


# --------------------------------------------------------------------------- junção

@dataclass
class Result:
    confirmed: dict  # {CODIGO: (recompensas, [fontes])}
    pending: dict    # códigos vistos como ativos, mas sem votos suficientes
    ok_sources: list
    failed_sources: list


def combine(results: dict) -> Result:
    """results = {nome_da_fonte: Found}; só usa as fontes que responderam."""
    weights = {s.name: s.weight for s in SOURCES}
    votes, seen_by, rewards = {}, {}, {}

    for name, found in results.items():
        for code, rew in found.active.items():
            # Cada site só invalida os próprios códigos: se ele mesmo lista o código
            # como expirado, não vota. Não usamos o "expirado" de um site para anular
            # outro porque a Kuro às vezes reaproveita códigos antigos.
            if code in found.expired:
                continue
            votes[code] = votes.get(code, 0) + weights.get(name, 1)
            seen_by.setdefault(code, []).append(name)
            # prefere a descrição de recompensas mais completa
            if len(rew) > len(rewards.get(code, "")):
                rewards[code] = rew

    confirmed, pending = {}, {}
    for code, v in votes.items():
        target = confirmed if v >= VOTES_NEEDED else pending
        target[code] = (rewards.get(code, ""), seen_by[code])
    return Result(confirmed, pending, list(results), [])


def collect() -> Result:
    results, failed = {}, []
    for src in SOURCES:
        print(f"[{src.name}] {src.url}")
        try:
            html = fetch_html(src.url)
            found = src.parser(html)
        except Exception as e:
            print(f"::warning::{src.name}: não consegui ler a página ({e})")
            failed.append(src.name)
            continue
        valid = sorted(c for c in found.active if c not in found.expired)
        print(f"  ativos: {valid} | expirados: {len(found.expired)}")
        if not valid:
            title = make_soup(html).title
            title = title.get_text(strip=True) if title else "?"
            print(f"::warning::{src.name}: nenhum código ativo encontrado "
                  f"(página: {len(html)} bytes, título: {title!r}); "
                  "o site pode ter mudado de formato ou bloqueado o acesso.")
            if not found.expired:  # página sem nada útil: não conta como fonte válida
                failed.append(src.name)
                continue
        results[src.name] = found
    res = combine(results)
    res.failed_sources = failed
    return res


# --------------------------------------------------------------------------- Discord

def load_sent() -> list:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return []


def save_sent(codes: list) -> None:
    STATE_FILE.write_text(json.dumps(sorted(set(codes)), indent=2) + "\n", encoding="utf-8")


def build_payload(code: str, rewards: str, sources: list, role_id: str = "") -> dict:
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
                "footer": {"text": "Fontes: " + ", ".join(sources)},
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

    res = collect()
    if not res.ok_sources:
        # Todas bloquearam/caíram: tenta de novo na próxima execução sem marcar falha.
        print("::warning::Nenhuma fonte respondeu. Tento de novo na próxima execução.")
        return 0

    for code, (_, srcs) in sorted(res.pending.items()):
        print(f"::warning::{code} aparece como ativo só em {', '.join(srcs)}; "
              f"aguardando confirmação de outra fonte.")
    if PERMANENT_CODE not in res.confirmed and len(res.ok_sources) >= 2:
        print(f"::warning::{PERMANENT_CODE} (código fixo) não foi confirmado; "
              "alguma página pode ter mudado de formato.")

    sent = load_sent()
    new = [c for c in res.confirmed if c not in sent]
    print(f"Confirmados: {sorted(res.confirmed)} | Novos: {new}")

    for code in new:
        rewards, srcs = res.confirmed[code]
        payload = build_payload(code, rewards, srcs, role_id)
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
