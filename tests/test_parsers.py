"""Testes dos leitores de página. Rodar com:  python -m pytest -q

O HTML abaixo reproduz a estrutura real de cada site (capturada em 13/11/2026),
só sem menus, imagens e scripts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import wuwa_codes as w  # noqa: E402

PRYDWEN = """
<h1>Wuthering Waves Codes</h1>
<section class="section-group"><h2>ACTIVE WUWA CODES</h2>
 <div class="banner-grid"><article class="code-card">
  <div class="code-card-heading"><h3><code>WUTHERINGGIFT</code></h3></div>
  <ul><li>Astrite <span>×50</span></li><li>Shell Credit <span>×10,000</span></li></ul>
  <span>Active</span><button>Copy code</button>
 </article></div></section>
<section class="section-group"><h2>WUWA 3.7 LIVESTREAM CODES</h2>
 <div class="codes-grid"><article class="code-card">
  <div class="code-card-heading"><h3><code>FALLINGSANCTUM</code></h3></div>
  <ul><li>Astrite <span>×100</span></li></ul><span>Expired</span>
 </article></div></section>
<h2>EXPIRED WUWA CODES</h2>
<details class="codes-archive-disclosure"><table class="codes-archive"><tbody>
 <tr><th><code>BLOOMINGFLOWERS</code></th></tr><tr><th><code>BLACKSHORES</code></th></tr>
</tbody></table></details>
"""

GAME8 = """
<h2>What can you do as a free member?</h2>
<h2>Wuthering Waves Active Codes</h2>
<h3>Permanent Redeem Codes</h3>
<table class="a-table"><tr><th>All Active Code(s)</th></tr><tr><td>
 <div class="a-clipboard__container"><input type="text" class="a-clipboard__textInput"
  value="WUTHERINGGIFT" readonly><div class="a-clipboard__copyMessage">Copied</div></div>
 <div class="align"><a>Astrite</a> x50</div></td></tr></table>
<h2>How to Redeem Wuthering Waves Codes</h2>
<h2>List of Past Redeem Codes</h2>
<h3>All Past Redeem Codes</h3>
<table class="a-table"><tr><th>Expired Codes and Past Rewards</th></tr>
 <tr><td><b class="a-bold">STARRYSTAGE2</b><div>Astrite <b class="a-bold">x80</b></div></td></tr>
 <tr><td><b class="a-bold">FALLINGSANCTUM</b></td></tr></table>
"""

GAMEMARKET_NOW = """
<h1>Wuthering Waves Redeem Codes That Still Work and How to Redeem Them</h1>
<h2>Active Wuthering Waves Codes</h2>
<ul><li><strong>WUTHERINGGIFT</strong>: Astrite x50, Shell Credit x10,000</li></ul>
<p><strong>WUTHERINGGIFT</strong> is permanent. The 3.8 codes <strong>TRAINOFSOULS</strong>,
<strong>BLOOMINGFLOWERS</strong> and <strong>SCHOOLLIFE</strong> expired on November 8.</p>
<h2>How to Redeem Wuthering Waves Codes</h2>
<ol><li>Select Redeem, then type the code, such as the permanent code WUTHERINGGIFT</li></ol>
<h2>Why a Code Is Not Working</h2>
<h2>Expired Wuthering Waves Codes</h2>
<ul><li>TRAINOFSOULS</li><li>BLOOMINGFLOWERS</li><li>SCHOOLLIFE</li>
<li>F5F4D3B2A2 (Escape from Duckov livery)</li><li>2NDANNIVERSARY</li></ul>
"""

TIMESAVER_NOW = """
<h1>Wuthering Waves Codes (November 13, 2026): Active Redeem Codes and Free Astrite</h1>
<p><strong>one active in-game redeem code right now: WUTHERINGGIFT</strong></p>
<p><strong>TRAINOFSOULS, BLOOMINGFLOWERS and SCHOOLLIFE, expired on 8 November</strong></p>
<h2>What Wuthering Waves codes are active right now?</h2>
<table><tr><td>WUTHERINGGIFT</td><td>50 Astrite</td></tr></table>
<h2>How much free Astrite can you get in Version 3.8?</h2>
<table><tr><td>WUTHERINGGIFT (if never claimed)</td></tr></table>
<h2>Which Wuthering Waves codes have expired?</h2>
<table><tr><td>TRAINOFSOULS</td></tr><tr><td>BLOOMINGFLOWERS</td></tr>
<tr><td>SCHOOLLIFE</td></tr></table>
<h2>FAQ</h2><p><strong>Do TRAINOFSOULS, BLOOMINGFLOWERS and SCHOOLLIFE still work?</strong></p>
<h3>Wuthering Waves 3.8 Livestream Codes (Expired November 8) and Everything Announced</h3>
"""

LEVVVEL = """
<ul><li><a>RIVALS codes</a></li></ul>
<h1>Wuthering Waves codes November 2026</h1>
<aside><h2>Quick answer</h2><h3>Active code</h3></aside>
<section><h2>Working Wuthering Waves codes</h2>
 <article><code>WUTHERINGGIFT</code><p>50 Astrite, 10,000 Shell Credits</p></article></section>
<details><summary>Expired codes (40)</summary>
 <article><code>TRAINOFSOULS</code></article><article><code>SCHOOLLIFE</code></article></details>
<h2>How to redeem Wuthering Waves codes</h2><ol><li>Reach Union Level 2.</li></ol>
"""

# Como as páginas estavam em 7/11, durante a live da 3.8 (Prydwen e Game8 atrasados)
GAMEMARKET_LIVE = """
<h2>Active Wuthering Waves Codes</h2>
<ul><li><strong>WUTHERINGGIFT</strong>: Astrite x50</li>
<li><strong>TRAINOFSOULS</strong>: 100 Astrite, 3 Premium Resonance Potion</li>
<li><strong>BLOOMINGFLOWERS</strong>: 100 Astrite, 40,000 Shell Credit</li>
<li><strong>SCHOOLLIFE</strong>: 100 Astrite, 20 Premium Tuner</li></ul>
<h2>Expired Wuthering Waves Codes</h2><ul><li>FALLINGSANCTUM</li></ul>
"""
TIMESAVER_LIVE = """
<h2>What Wuthering Waves codes are active right now?</h2>
<table><tr><td>WUTHERINGGIFT</td></tr><tr><td>TRAINOFSOULS</td></tr>
<tr><td>BLOOMINGFLOWERS</td></tr><tr><td>SCHOOLLIFE</td></tr></table>
<h2>Which Wuthering Waves codes have expired?</h2><table><tr><td>FALLINGSANCTUM</td></tr></table>
"""


def test_prydwen():
    f = w.parse_prydwen(PRYDWEN)
    assert list(f.active) == ["WUTHERINGGIFT"]
    assert "Astrite ×50" in f.active["WUTHERINGGIFT"]
    assert {"FALLINGSANCTUM", "BLOOMINGFLOWERS", "BLACKSHORES"} <= f.expired


def test_game8():
    f = w.parse_game8(GAME8)
    assert list(f.active) == ["WUTHERINGGIFT"]
    assert "Astrite" in f.active["WUTHERINGGIFT"]
    assert f.expired == {"STARRYSTAGE2", "FALLINGSANCTUM"}


def test_gamemarket_now():
    f = w.parse_generic(GAMEMARKET_NOW)
    # os da 3.8 aparecem no texto da seção "Active", mas também na lista de expirados
    assert "WUTHERINGGIFT" in f.active
    assert {"TRAINOFSOULS", "SCHOOLLIFE", "F5F4D3B2A2", "2NDANNIVERSARY"} <= f.expired


def test_timesaver_now():
    f = w.parse_generic(TIMESAVER_NOW)
    assert list(f.active) == ["WUTHERINGGIFT"]
    assert {"TRAINOFSOULS", "BLOOMINGFLOWERS", "SCHOOLLIFE"} <= f.expired


def test_levvvel_details_count_as_expired():
    f = w.parse_generic(LEVVVEL)
    assert list(f.active) == ["WUTHERINGGIFT"]
    assert {"TRAINOFSOULS", "SCHOOLLIFE"} <= f.expired


def test_combine_today_only_permanent_code():
    res = w.combine({
        "Prydwen": w.parse_prydwen(PRYDWEN),
        "Game8": w.parse_game8(GAME8),
        "GameMarket": w.parse_generic(GAMEMARKET_NOW),
        "Timesaver": w.parse_generic(TIMESAVER_NOW),
        "Levvvel": w.parse_generic(LEVVVEL),
    })
    assert set(res.confirmed) == {"WUTHERINGGIFT"}
    assert res.pending == {}


def test_combine_livestream_window_catches_new_codes():
    """Cenário de 7/11: só os sites menores tinham os códigos da 3.8."""
    res = w.combine({
        "Prydwen": w.parse_prydwen(PRYDWEN),
        "Game8": w.parse_game8(GAME8),
        "GameMarket": w.parse_generic(GAMEMARKET_LIVE),
        "Timesaver": w.parse_generic(TIMESAVER_LIVE),
    })
    assert {"TRAINOFSOULS", "BLOOMINGFLOWERS", "SCHOOLLIFE"} <= set(res.confirmed)
    rewards, srcs = res.confirmed["TRAINOFSOULS"]
    assert "100 Astrite" in rewards and set(srcs) == {"GameMarket", "Timesaver"}


def test_single_small_source_is_not_enough():
    res = w.combine({
        "Prydwen": w.parse_prydwen(PRYDWEN),
        "GameMarket": w.parse_generic(GAMEMARKET_LIVE),
    })
    # só 1 voto -> ficam aguardando, não são enviados
    assert {"TRAINOFSOULS", "BLOOMINGFLOWERS", "SCHOOLLIFE"} <= set(res.pending)
    assert "TRAINOFSOULS" not in res.confirmed


def test_trusted_source_alone_is_enough():
    res = w.combine({"Prydwen": w.parse_prydwen(PRYDWEN)})
    assert "WUTHERINGGIFT" in res.confirmed
