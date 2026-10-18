"""Build baseline/infographic.html from data/wayback_series.json (+ today's state)."""
import datetime
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
s = json.load(open(HERE / "data/wayback_series.json"))
pts = [(r["ts"][:8], float(r["counter"])) for r in s if r.get("counter") and r["ts"] >= "2022"]
pts.append(("20261017", 0.00212282))


def d(ts):
    return datetime.date(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))


t0, t1 = d("20220101"), d("20261101")
W, H, L, R, T, B = 1040, 300, 70, 30, 20, 40
goal = 0.00227664


def X(ts):
    return L + (d(ts) - t0).days / (t1 - t0).days * (W - L - R)


def Y(v):
    return T + (H - T - B) * (1 - v / 0.0024)


path = " ".join(f"{'M' if i == 0 else 'L'}{X(ts):.1f},{Y(v):.1f}" for i, (ts, v) in enumerate(pts))
ticks = "".join(
    f'<text x="{X(f"{y}0101"):.0f}" y="{H - 14}" class="ax">{y}</text>'
    f'<line x1="{X(f"{y}0101"):.0f}" y1="{T}" x2="{X(f"{y}0101"):.0f}" y2="{H - B}" class="grid"/>'
    for y in range(2022, 2027))
yt = "".join(
    f'<text x="{L - 8}" y="{Y(v) + 4:.0f}" class="ax" text-anchor="end">{v:.4f}</text>'
    f'<line x1="{L}" y1="{Y(v):.0f}" x2="{W - R}" y2="{Y(v):.0f}" class="grid"/>'
    for v in (0, 0.0008, 0.0016))
dots = "".join(f'<circle cx="{X(ts):.1f}" cy="{Y(v):.1f}" r="3" class="dot"/>' for ts, v in pts)

chart = f"""<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>.ax{{fill:#8b949e;font:12px ui-monospace,Consolas,monospace}}.grid{{stroke:#21262d;stroke-width:1}}
.ln{{fill:none;stroke:#3fb950;stroke-width:2;stroke-linejoin:round}}.dot{{fill:#0d1117;stroke:#3fb950;stroke-width:2}}
.goal{{stroke:#f0883e;stroke-width:2;stroke-dasharray:6 5}}.lab{{fill:#c9d1d9;font:12px ui-monospace,Consolas,monospace}}
.goalt{{fill:#f0883e;font:12px ui-monospace,Consolas,monospace}}</style>
{ticks}{yt}
<line x1="{L}" y1="{Y(goal):.0f}" x2="{W - R}" y2="{Y(goal):.0f}" class="goal"/>
<text x="{L + 6}" y="{Y(goal) - 6:.0f}" class="goalt">goal 0.00227664 BTC (= the code 227664)</text>
<path d="{path}" class="ln"/>{dots}
<text x="{X('20221122') - 10:.0f}" y="{Y(0.00034682) - 10:.0f}" class="lab" text-anchor="end">Nov 2022: a stranger sends 34,682 sat</text>
<text x="{X('20231015') + 8:.0f}" y="{Y(0.00079082) - 8:.0f}" class="lab">Oct 2023: B1a cleared, goal x1000</text>
<text x="{X('20240731') - 330:.0f}" y="{Y(0.00197882) - 10:.0f}" class="lab">Jul 2024: keepalive script pushes it up</text>
<text x="{X('20240912') + 10:.0f}" y="{Y(0.00212282) + 22:.0f}" class="lab">Sep 2024 to today: frozen at 0.00212282</text>
<text x="{X('20261017') - 10:.0f}" y="{Y(goal) + 44:.0f}" class="goalt" text-anchor="end">gap to goal: 15,382 sat = $12.52</text>
</svg>"""

CSS = """
body{margin:0;background:#0d1117;color:#c9d1d9;font:15px/1.45 "Segoe UI",system-ui,sans-serif;width:1100px}
.wrap{padding:34px 30px 28px}
h1{margin:0;font:700 34px/1.1 ui-monospace,Consolas,monospace;color:#3fb950;letter-spacing:.5px}
h1 small{color:#8b949e;font-weight:400;font-size:17px;margin-left:14px}
.sub{color:#8b949e;margin:8px 0 22px;font-size:15px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:18px}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px 16px}
.card h2{margin:0 0 8px;font:700 13px ui-monospace,Consolas,monospace;color:#3fb950;letter-spacing:1.5px;text-transform:uppercase}
.card ul{margin:0;padding-left:18px} .card li{margin:3px 0}
.big{font:700 30px ui-monospace,Consolas,monospace;color:#f0f6fc;margin:4px 0 2px} .big em{font-style:normal;color:#3fb950}
.tl{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:0 0 18px}
.tl div{background:#161b22;border-top:3px solid #3fb950;padding:8px 10px;border-radius:0 0 8px 8px;font-size:13px}
.tl b{display:block;color:#f0f6fc;font:700 14px ui-monospace,Consolas,monospace;margin-bottom:3px}
.tl .dead{border-top-color:#484f58;color:#8b949e} .tl .now{border-top-color:#f0883e}
.chart{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:10px 10px 4px;margin-bottom:18px}
.chart h2{margin:4px 0 2px 8px;font:700 13px ui-monospace,Consolas,monospace;color:#3fb950;letter-spacing:1.5px}
.foot{color:#8b949e;font-size:12px;margin-top:6px}
code{font:13px ui-monospace,Consolas,monospace;color:#f0f6fc;background:#0d1117;padding:1px 5px;border-radius:4px}
.status{border-color:#f0883e} .status h2{color:#f0883e}
"""

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="wrap">
<h1>ХССГ :: xccr.com <small>22 years of a $12 puzzle. What we know as of 17 Oct 2026</small></h1>
<div class="sub">A Lost-style "enter the numbers before time runs out" console, online since Nov 2004. Not Half-Life 2, not official Lost: one hobbyist's ARG, rebuilt three times, never finished.</div>
<div class="tl">
<div><b>2004</b>Domain registered 18 Nov; GIF glyphs dated 17 Nov. Registrant: Batu Pahat, Johor; email at palmy.net.nz.</div>
<div><b>May 2006</b>Slashdot sig leaks code 227664. Unfiction team solves i0 to i4 in a week and reaches the only checkpoint (227664, then 974444).</div>
<div><b>Sep 2006 to 2007</b>252 "bunkers", apply by email, codes emailed. Target image x1.gif spells HELLO! 227664. Nobody finishes it.</div>
<div class="dead"><b>2008 to 2021</b>ASP.NET app rots: dead timer, then Runtime Error. Domster: "Dead."</div>
<div><b>Jan 2022</b>PHP rebuild. Hidden line <code>balance / goal = B1a</code>, BTC + DOGE "door" addresses, 100-min timer.</div>
<div class="now"><b>17 Oct 2026</b>This run: dossier, xccr_probe.py, 60-h keepalive, and the first deliberate deposit: 15,382 sat.</div>
</div>
<div class="chart"><h2>THE HIDDEN COUNTER, FROM 75 ARCHIVED HOMEPAGES</h2>{chart}
<div class="foot" style="margin-left:8px">y axis: BTC. Every value ends in 82 (wallet 34,682 sat plus 300-sat hourly steps); the goal ends in 64, so the timer alone can never land on it.</div></div>
<div class="grid3">
<div class="card"><h2>How the live site works</h2><ul>
<li><code>227664</code> + Enter calls <code>t.php</code>, which resets a 6000-s server timer. Needs a same-origin Referer; no 10-min lockout.</li>
<li>Any other number goes to <code>l.php?N</code>; always 2 bytes back. 126 archived guesses, zero hits.</li>
<li>Counter rises 300 sat/h while the timer is alive, decays when it isn't, floors at the doorB wallet balance.</li>
<li>Clearing a slot rewrote keyB1 <code>a</code> to <code>D</code> and removed the D line (<code>0 / 7 = D1a</code>, 7 DOGE).</li>
<li>Only other file: <code>b1-x.png</code>, a quarter of a QR code, online since Apr 2022.</li></ul></div>
<div class="card"><h2>Who, and what it isn't</h2><ul>
<li>Malay in the code (<code>Nombor</code>, <code>kiri</code>, <code>tengah</code>, <code>mana</code>); 2006 WHOIS in Johor; same box hosts palmy.nz, basong.my, xmoo.net (the author's old "XMoo Network").</li>
<li>Slashdot puppets: foundme, blackwater (uid 227664), tfeyet (uid 974444 = "him").</li>
<li>The HL2 billboard ХССГ is a coincidence the 2006 players already noted. "Are you him?" is a Lost quote.</li>
<li>Total ever paid in: $5.75 (Nov 2022). Total ever asked: about $185 at today's price.</li></ul></div>
<div class="card status"><h2>Experiment in progress</h2>
<div class="big"><em>8 h</em> timer alive, counter flat</div>
<div>Keepalive runs to Sun 19 Oct; flat means the hourly meter is dead.</div>
<div class="big" style="margin-top:10px"><em>15,382</em> sat sent 13:32Z</div>
<div>Exactly goal minus counter. In mempool, txid <code>43da77fc...08ae7</code>. Page is checked every 10 min after it confirms.</div>
<div class="foot" style="margin-top:8px">Next if nothing moves: top up the balance to 227,664 sat (about $157), or accept that the server only reads the wallet when the author pokes it.</div></div>
</div>
<div class="foot">Sources: live site + jafa/*.js; Wayback CDX (1,212 captures); Unfiction thread 14871 (2006, 230 posts); r/XCCR, r/UnresolvedMysteries; Slashdot profiles; mempool.space; RDAP/APNIC. Full dossier: RESEARCH.md</div>
</div></body></html>"""

out = HERE / "baseline/infographic.html"
out.write_text(page, encoding="utf-8")
print("wrote", out)
