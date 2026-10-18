#!/usr/bin/env python
"""xccr_probe.py - automated exploration / monitoring of https://xccr.com

Stdlib only. All state lives in ./data next to this file (JSONL + manifests),
so every run is a diff against the last run.

Subcommands
  snapshot            fetch / , r.php, counter.php, l.php; parse state; diff vs last
  trigger [--mode M]  hit t.php (M = bare | referer | xhr) and measure SetS before/after
  keepalive           loop: keep the 100-min timer alive, snapshot every hour,
                      stop when the counter / key / goal changes
  lphp                send l.php?<n> probes from a range or a list, record any
                      non-baseline response and re-snapshot the page every k probes
  assets              hash every file in /images/ and /icons/; diff vs manifest
  dirs                probe a small list of plausible sibling paths
  wayback             pull the CDX index, fetch new distinct homepage captures,
                      extend the counter time series
  chain               BTC (doorB) and DOGE (doorD) address balances + txs
  related             hash the homepages of the sister domains, diff vs last
  all                 snapshot + assets + dirs + wayback + chain + related
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://xccr.com/"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DATA.mkdir(exist_ok=True)

UA_BROWSER = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
UA_PROBE = "xccr-probe/0.1 (+research; contact via github issues)"

RELATED = ["https://palmy.nz/", "https://sg2065.com/", "https://basong.my/",
           "https://xmoo.net/", "https://www.xccr.com/", "https://a.xccr.com/"]
BTC_DOORB = "1G9rG47hF8ckTT6icgHFV3qWBDPjkj4wME"
DOGE_DOORD = "DADbBq34cngE8rzyRnJv8RJjzVyKqbqYhC"

# Plausible sibling files. b1-x.png is real; the rest are guesses based on
# the naming scheme (door letter, key row, -x partial) and the 2004-2008 files.
DIR_CANDIDATES = [
    "b1-x.png", "b1-y.png", "b2-x.png", "b1-2.png", "b1.png", "b.png",
    "d1-x.png", "d1.png", "d-x.png", "x1.png", "x1.gif", "x2.gif",
    "images/x1.gif", "images/x2.gif", "images/i0.gif", "images/i1.gif",
    "images/i2.gif", "images/i3.gif", "images/i4.gif", "images/i5.gif",
    "images/q1.gif", "images/q2.gif", "images/q3.gif", "images/readme.txt",
    "images/progress.txt", "images/index.html", "smiley.gif", "rss.php",
    "rss_227664.php", "rss_227664.aspx", "index.aspx", "bunker.aspx",
    "toolate.aspx", "toolate.php", "bunker.php", "bunkers/", "jafa/",
    "jafa/keys.js", "jafa/countdown.js", "jafa/addevent.js", "jafa/move.js",
    "jafa/doors.js", "push.css", "css/style.css", "r.php", "t.php", "l.php",
    "counter.php", "s.php", "k.php", "d.php", "b.php", "m.php", "q.php",
    "robots.txt", "sitemap.xml", "readme.txt", "progress.txt", "feed/",
    ".well-known/security.txt", "favicon.ico",
]


# --------------------------------------------------------------------------- http
def _req(url: str, *, ua: str = UA_BROWSER, referer: str | None = None,
         xhr: bool = False, timeout: int = 30, method: str = "GET") -> dict:
    hdrs = {"User-Agent": ua, "Accept": "*/*", "Cache-Control": "no-cache"}
    if referer:
        hdrs.update({"Referer": referer, "Sec-Fetch-Site": "same-origin",
                     "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty"})
    if xhr:
        hdrs["X-Requested-With"] = "XMLHttpRequest"
    r = urllib.request.Request(url, headers=hdrs, method=method)
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            body = resp.read()
            return {"url": url, "status": resp.status, "body": body,
                    "headers": dict(resp.headers), "ms": int((time.time() - t0) * 1000)}
    except urllib.error.HTTPError as e:
        body = e.read()
        return {"url": url, "status": e.code, "body": body,
                "headers": dict(e.headers), "ms": int((time.time() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "status": 0, "body": b"", "headers": {}, "error": repr(e),
                "ms": int((time.time() - t0) * 1000)}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def jl_append(name: str, obj: dict) -> None:
    with open(DATA / name, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def jl_last(name: str) -> dict | None:
    p = DATA / name
    if not p.exists():
        return None
    last = None
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    return last


# --------------------------------------------------------------------------- parse
def parse_index(html: str) -> dict:
    st: dict = {}
    m = re.search(r"SetS\((-?\d+)\)", html)
    st["sets"] = int(m.group(1)) if m else None
    st["timer_running"] = bool(st["sets"] and st["sets"] > 0)
    st["b_lines"] = re.findall(r"<b>([^<]{3,80})</b>", html)
    eq = re.search(r"([\d.]+)\s*/\s*([\d.]+)\s*=\s*(\w+)", " ".join(st["b_lines"]))
    if eq:
        st["counter"], st["goal"], st["slot"] = eq.group(1), eq.group(2), eq.group(3)
    st["meta"] = dict(re.findall(r'<meta name="(door\w|key\w\d|DESCRIPTION|contact)" content="([^"]*)"', html))
    sm = re.search(r"id='statsmid'>(.*?)</span>", html, re.S)
    st["statsmid"] = "".join(re.findall(r"images/d(.)\.gif", sm.group(1))) if sm else ""
    ip = re.search(r'TextBox_IP[^>]*value="([^"]*)"', html)
    st["textbox_ip"] = ip.group(1) if ip else None
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    st["title"] = t.group(1).strip() if t else None
    st["scripts"] = re.findall(r'src="([^"]+\.js)"', html)
    st["imgs"] = sorted(set(re.findall(r"src='([^']+\.gif)'", html)))
    st["html_sha"] = sha(html.encode("utf-8", "replace"))
    # structural hash: html with the volatile bits (timer) removed
    st["struct_sha"] = sha(re.sub(r"SetS\(-?\d+\)", "SetS(N)", html).encode("utf-8", "replace"))
    st["len"] = len(html)
    return st


# --------------------------------------------------------------------------- cmds
def cmd_snapshot(args) -> dict:
    idx = _req(BASE)
    html = idx["body"].decode("utf-8", "replace")
    st = parse_index(html)
    st["ts"] = now()
    st["status"] = idx["status"]
    st["server"] = {k: v for k, v in idx["headers"].items()
                    if k.lower() in ("server", "x-powered-by", "last-modified", "etag", "date")}
    for ep in ("r.php", "counter.php", "l.php", "t.php?nop"):  # t.php?nop: HEAD only, never GET here
        if ep.startswith("t.php"):
            r = _req(BASE + "t.php", method="HEAD")
        else:
            r = _req(BASE + ep, referer=BASE)
        st[ep] = {"status": r["status"], "len": len(r["body"]), "sha": sha(r["body"]),
                  "body": r["body"][:64].decode("latin-1")}
    for js in ("jafa/keys.js", "jafa/countdown.js", "jafa/addevent.js", "push.css"):
        r = _req(BASE + js)
        st[js] = {"status": r["status"], "sha": sha(r["body"]), "len": len(r["body"])}
    (DATA / "index.latest.html").write_text(html, encoding="utf-8")
    prev = jl_last("state.jsonl")
    jl_append("state.jsonl", st)
    changes = diff_state(prev, st)
    print(f"[{st['ts']}] counter={st.get('counter')} goal={st.get('goal')} slot={st.get('slot')} "
          f"SetS={st['sets']} keyB1={st['meta'].get('keyB1')} keyD1={st['meta'].get('keyD1')} "
          f"r.php={st['r.php']['body']!r} struct={st['struct_sha']}")
    if changes:
        print("  CHANGES vs previous snapshot:")
        for c in changes:
            print("   -", c)
    elif prev:
        print("  no change vs previous snapshot")
    return st


WATCH_KEYS = ["counter", "goal", "slot", "b_lines", "meta", "statsmid", "textbox_ip", "title",
              "scripts", "imgs", "struct_sha", "jafa/keys.js", "jafa/countdown.js",
              "jafa/addevent.js", "push.css", "r.php", "counter.php", "l.php"]


def diff_state(prev: dict | None, cur: dict) -> list[str]:
    if not prev:
        return []
    out = []
    for k in WATCH_KEYS:
        a, b = prev.get(k), cur.get(k)
        if isinstance(a, dict) and isinstance(b, dict):
            a = {x: y for x, y in a.items() if x != "status"}
            b = {x: y for x, y in b.items() if x != "status"}
        if a != b:
            out.append(f"{k}: {a!r} -> {b!r}")
    return out


def get_sets() -> int | None:
    html = _req(BASE)["body"].decode("utf-8", "replace")
    m = re.search(r"SetS\((-?\d+)\)", html)
    return int(m.group(1)) if m else None


def cmd_trigger(args) -> dict:
    """Hit t.php one way and report whether the server timer reset to 6000."""
    before = get_sets()
    mode = args.mode
    if mode == "bare":
        r = _req(BASE + "t.php", ua=UA_PROBE)
    elif mode == "referer":
        r = _req(BASE + "t.php", referer=BASE)
    elif mode == "xhr":
        r = _req(BASE + "t.php", referer=BASE, xhr=True)
    else:
        raise SystemExit("mode must be bare|referer|xhr")
    time.sleep(2)
    after = get_sets()
    reset = after is not None and after >= 5990
    rec = {"ts": now(), "mode": mode, "sets_before": before, "sets_after": after,
           "reset": reset, "t_status": r["status"], "t_len": len(r["body"])}
    jl_append("trigger.jsonl", rec)
    print(json.dumps(rec))
    return rec


def cmd_keepalive(args) -> None:
    """Keep the timer alive and watch the counter.

    Hypothesis under test (from r/XCCR, Jul 2024): while the timer is running the
    server adds 0.000003 to the counter every hour; while it is not, it subtracts.
    The counter has not moved since Sep 2024 even though players keep the timer up.
    """
    every = args.every * 60
    deadline = time.time() + args.hours * 3600
    last_snap = 0.0
    start = cmd_snapshot(args)
    print(f"keepalive: every {args.every} min for {args.hours} h; baseline counter={start.get('counter')}")
    while time.time() < deadline:
        s = get_sets()
        if s is None or s < 6000 - every - 120:
            r = _req(BASE + "t.php", referer=BASE)
            time.sleep(2)
            s2 = get_sets()
            print(f"[{now()}] t.php -> {r['status']} SetS {s} -> {s2}")
            jl_append("trigger.jsonl", {"ts": now(), "mode": "keepalive", "sets_before": s,
                                        "sets_after": s2, "reset": bool(s2 and s2 >= 5990)})
        if time.time() - last_snap >= 3600:
            st = cmd_snapshot(args)
            last_snap = time.time()
            if st.get("counter") != start.get("counter") or st["meta"] != start["meta"] \
                    or st.get("goal") != start.get("goal"):
                print("*** STATE CHANGED - stopping keepalive so a human can look ***")
                return
        time.sleep(every)


def cmd_lphp(args) -> None:
    """Probe l.php?<n>. Baseline response is 2 bytes "  " (0x20 0x20)."""
    nums: list[str] = []
    if args.list:
        nums = [x.strip() for x in Path(args.list).read_text().split() if x.strip()]
    else:
        nums = [str(n).zfill(args.pad) if args.pad else str(n)
                for n in range(args.start, args.end + 1, args.step)]
    base = _req(BASE + "l.php?", referer=BASE)
    base_sha = sha(base["body"])
    print(f"baseline l.php: status={base['status']} len={len(base['body'])} sha={base_sha}; probing {len(nums)} values")
    hits = 0
    for i, n in enumerate(nums, 1):
        if n == "227664":
            continue  # that one goes to t.php and is covered by trigger/keepalive
        r = _req(BASE + "l.php?" + n, referer=BASE)
        odd = r["status"] != base["status"] or sha(r["body"]) != base_sha
        rec = {"ts": now(), "n": n, "status": r["status"], "len": len(r["body"]),
               "sha": sha(r["body"]), "ms": r["ms"], "odd": odd}
        jl_append("lphp.jsonl", rec)
        if odd:
            hits += 1
            print("  ODD:", json.dumps(rec), r["body"][:200])
        if args.snap_every and i % args.snap_every == 0:
            st = cmd_snapshot(args)
        time.sleep(args.delay)
    print(f"done: {len(nums)} probes, {hits} non-baseline responses")


def _listing(path: str) -> list[str]:
    r = _req(BASE + path)
    html = r["body"].decode("utf-8", "replace")
    names = re.findall(r'<a href="([^"?/][^"]*)"', html)
    return [n for n in names if not n.startswith("?")]


def cmd_assets(args) -> None:
    manifest_p = DATA / "assets.manifest.json"
    old = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
    new: dict = {}
    for d in ("images/", "icons/", "icons/small/"):
        names = _listing(d)
        for n in names:
            if n.endswith("/"):
                continue
            url = BASE + d + n
            r = _req(url)
            if r["status"] == 200:
                new[d + n] = {"sha": sha(r["body"]), "len": len(r["body"]),
                              "lm": r["headers"].get("Last-Modified")}
                if args.save:
                    out = DATA / "assets" / d / n
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(r["body"])
            time.sleep(0.15)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(new) & set(old) if new[k]["sha"] != old[k]["sha"])
    print(f"assets: {len(new)} files; +{len(added)} -{len(removed)} ~{len(changed)}")
    for k in added:
        print("  NEW ", k, new[k])
    for k in removed:
        print("  GONE", k)
    for k in changed:
        print("  CHG ", k, old[k]["sha"], "->", new[k]["sha"])
    manifest_p.write_text(json.dumps(new, indent=1))
    jl_append("assets.jsonl", {"ts": now(), "n": len(new), "added": added, "removed": removed, "changed": changed})


def cmd_dirs(args) -> None:
    cands = list(DIR_CANDIDATES)
    if args.wordlist:
        cands += [x.strip() for x in Path(args.wordlist).read_text().splitlines() if x.strip()]
    known_404 = None
    found = []
    for p in cands:
        r = _req(BASE + p)
        body_sha = sha(r["body"])
        if r["status"] == 404 and known_404 is None:
            known_404 = body_sha
        tag = "404-page" if r["status"] == 404 else f"{r['status']}:{len(r['body'])}:{body_sha}"
        if r["status"] != 404:
            found.append((p, r["status"], len(r["body"]), r["headers"].get("Content-Type", "")))
        jl_append("dirs.jsonl", {"ts": now(), "path": p, "status": r["status"], "len": len(r["body"]), "sha": body_sha})
        time.sleep(args.delay)
    print("non-404 paths:")
    for p, s, l, ct in found:
        print(f"  {s} {l:>7}  {p}   ({ct})")


def cmd_wayback(args) -> None:
    cdx = ("http://web.archive.org/cdx/search/cdx?url=xccr.com&matchType=domain&output=json"
           "&fl=timestamp,original,statuscode,mimetype,digest&collapse=digest&limit=20000")
    r = _req(cdx, timeout=120)
    rows = json.loads(r["body"].decode())[1:]
    (DATA / "cdx.json").write_text(json.dumps(rows))
    seen_p = DATA / "wayback.seen.json"
    seen = set(json.loads(seen_p.read_text())) if seen_p.exists() else set()
    new_rows = [x for x in rows if x[0] + x[1] not in seen]
    print(f"wayback: {len(rows)} distinct captures, {len(new_rows)} new since last run")
    home = DATA / "wayback_home"
    home.mkdir(exist_ok=True)
    fetched = 0
    for ts, url, st, mt, dg in new_rows:
        u = url.rstrip("/")
        if st == "200" and u in ("https://xccr.com", "http://xccr.com", "http://www.xccr.com",
                                 "https://www.xccr.com", "http://xccr.com:80", "http://www.xccr.com:80"):
            out = home / f"{ts}.html"
            if not out.exists():
                rr = _req(f"https://web.archive.org/web/{ts}id_/{url}", timeout=60)
                if rr["status"] == 200:
                    out.write_bytes(rr["body"])
                    fetched += 1
                time.sleep(0.7)
        elif st == "200" and not url.endswith((".gif", ".png", ".css", ".js", ".ico")):
            print("  new non-home capture:", ts, url)
    seen |= {x[0] + x[1] for x in rows}
    seen_p.write_text(json.dumps(sorted(seen)))
    print(f"  fetched {fetched} new homepage captures")
    # rebuild the time series
    series = []
    for f in sorted(home.glob("*.html")):
        st = parse_index(f.read_text(encoding="utf-8", errors="replace"))
        series.append({"ts": f.stem, "sets": st["sets"], "counter": st.get("counter"), "goal": st.get("goal"),
                       "slot": st.get("slot"), "keyB1": st["meta"].get("keyB1"), "keyD1": st["meta"].get("keyD1"),
                       "b_lines": st["b_lines"], "statsmid": st["statsmid"]})
    (DATA / "wayback_series.json").write_text(json.dumps(series, indent=1))
    last = None
    for s in series:
        key = (s["counter"], s["goal"], s["slot"], s["keyB1"], s["keyD1"], tuple(s["b_lines"]))
        if key != last:
            print(f"  {s['ts']}  {s['b_lines']}  keyB1={s['keyB1']} keyD1={s['keyD1']} SetS={s['sets']}")
            last = key


def cmd_chain(args) -> None:
    r = _req(f"https://mempool.space/api/address/{BTC_DOORB}")
    btc = json.loads(r["body"] or b"{}")
    cs = btc.get("chain_stats", {})
    bal = (cs.get("funded_txo_sum", 0) - cs.get("spent_txo_sum", 0)) / 1e8
    r2 = _req(f"https://mempool.space/api/address/{BTC_DOORB}/txs")
    txs = json.loads(r2["body"] or b"[]")
    r3 = _req(f"https://api.blockcypher.com/v1/doge/main/addrs/{DOGE_DOORD}")
    doge = json.loads(r3["body"] or b"{}")
    rec = {"ts": now(), "btc_balance": bal, "btc_received": cs.get("funded_txo_sum", 0) / 1e8,
           "btc_txs": cs.get("tx_count"), "btc_last_tx": txs[0]["txid"] if txs else None,
           "doge_balance": doge.get("final_balance"), "doge_received": doge.get("total_received"),
           "doge_txs": doge.get("final_n_tx")}
    prev = jl_last("chain.jsonl")
    jl_append("chain.jsonl", rec)
    print(json.dumps(rec))
    if prev and (prev["btc_received"] != rec["btc_received"] or prev["doge_received"] != rec["doge_received"]):
        print("  *** WALLET ACTIVITY CHANGED ***")


def cmd_related(args) -> None:
    prev = jl_last("related.jsonl") or {}
    rec = {"ts": now()}
    for u in RELATED:
        r = _req(u)
        body = r["body"]
        rec[u] = {"status": r["status"], "len": len(body), "sha": sha(body),
                  "title": (re.search(rb"<title>(.*?)</title>", body, re.S) or [b"", b""])[1].decode("utf-8", "replace").strip()[:60]}
        flag = ""
        if prev.get(u) and prev[u]["sha"] != rec[u]["sha"]:
            flag = "   CHANGED"
        print(f"  {r['status']} {len(body):>7} {rec[u]['sha']}  {u}  {rec[u]['title']!r}{flag}")
    jl_append("related.jsonl", rec)


def cmd_all(args) -> None:
    print("== snapshot"); cmd_snapshot(args)
    print("== assets"); cmd_assets(args)
    print("== dirs"); cmd_dirs(args)
    print("== wayback"); cmd_wayback(args)
    print("== chain"); cmd_chain(args)
    print("== related"); cmd_related(args)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("snapshot")
    p = sub.add_parser("trigger"); p.add_argument("--mode", default="referer", choices=["bare", "referer", "xhr"])
    p = sub.add_parser("keepalive"); p.add_argument("--every", type=int, default=30, help="minutes between t.php hits")
    p.add_argument("--hours", type=float, default=60)
    p = sub.add_parser("lphp")
    p.add_argument("--start", type=int, default=0); p.add_argument("--end", type=int, default=999)
    p.add_argument("--step", type=int, default=1); p.add_argument("--pad", type=int, default=0)
    p.add_argument("--list"); p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--snap-every", type=int, default=50)
    p = sub.add_parser("assets"); p.add_argument("--save", action="store_true")
    p = sub.add_parser("dirs"); p.add_argument("--wordlist"); p.add_argument("--delay", type=float, default=0.4)
    sub.add_parser("wayback")
    sub.add_parser("chain")
    sub.add_parser("related")
    p = sub.add_parser("all"); p.add_argument("--save", action="store_true"); p.add_argument("--wordlist")
    p.add_argument("--delay", type=float, default=0.4)
    a = ap.parse_args(argv)
    {"snapshot": cmd_snapshot, "trigger": cmd_trigger, "keepalive": cmd_keepalive, "lphp": cmd_lphp,
     "assets": cmd_assets, "dirs": cmd_dirs, "wayback": cmd_wayback, "chain": cmd_chain,
     "related": cmd_related, "all": cmd_all}[a.cmd](a)


if __name__ == "__main__":
    main()
