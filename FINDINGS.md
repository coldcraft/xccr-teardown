# xccr.com — research dossier and automated-exploration method

Compiled 2026-10-17. Everything below was re-verified against primary sources
(live site, Wayback CDX, the restored 2006 Unfiction thread, Reddit archive
API, on-chain data) rather than copied from the fan wiki. Where the fan wiki
(craftworks.top/xccr) is wrong, it is called out.

Files in this folder:

| path | what |
|---|---|
| `xccr_probe.py` | the automation tool (stdlib only); `python -X utf8 xccr_probe.py -h` |
| `data/` | the tool's own state: `state.jsonl`, `trigger.jsonl`, `assets.manifest.json`, `wayback_home/`, `wayback_series.json`, `chain.jsonl`, `related.jsonl`, `dirs.jsonl` |
| `baseline/unfiction_thread_2006.txt` | full transcript of the 2006 Unfiction thread (230 posts) |
| `baseline/craftworks_top_xccr_2026-08-29.txt` | the fan wiki as text |
| `baseline/reddit/` | r/XCCR, r/xccrarg, r/UnresolvedMysteries, r/ARG dumps (arctic-shift API) |
| `baseline/raw/` | live HTML/JS/CSS as of 2026-10-17 plus archived 2006-2008 ASP.NET pages, readme/progress/rss/ajax handlers |
| `baseline/assets/` | every GIF/PNG in `/images/` plus archived i0-i4, x1, bunker tiles |
| `baseline/*.png` | contact sheets (`sheet1`, `sheet2`), `x1.png`, QR at 2x |
| `baseline/wayback_cdx_2026-10-17.json` | full CDX index (1212 distinct captures) |

---

## 1. What the site is

A puzzle/ARG console that has existed since 2004 and has been through three
distinct eras. It is **not** connected to Half-Life 2 beyond a coincidental
Cyrillic sign (ХССГ) in City 17, and it is **not** part of The Lost
Experience. It was built by one person as a Lost-inspired "enter the numbers
every N minutes" game. The 2006 players established all of that already; the
Half-Life theory was re-invented in 2015 by people who had not read the thread.

### Who runs it

The 2006 WHOIS (preserved in the Unfiction thread, page 1) and the owner's
other sites identify the puppet-master cluster without naming a person:

- Registrant: "xccr xccr", Batu Pahat, Johor, Malaysia. Admin/tech contact
  `xccr@palmy.net.nz`. Nameservers `ns3/ns4.kiwihosting.net.nz`. Registered
  18 Nov 2004 (RDAP confirms), now registrar Cloudflare, expires Nov 2027.
- Same IP today (103.7.11.66, Exabytes Singapore, Plesk): **palmy.nz**
  ("Palmerston North New Zealand"), **basong.my** (Johor company),
  **xmoo.net**. sg2065.com shares the Cloudflare nameservers.
- xmoo.net in 2004-2021 was "XMoo Network", a hobby network by the same
  developer: IMooU messaging, HolyMoo points, "Batu Pahat Online Portal"
  (bp.my), Auckland/Wellington/Christchurch map directories (iclod.com),
  Virtual Bet, Rock Paper Scissors, Chinese Lunar Calendar, mr2.net.nz.
- Malay in the code: `Nombor` (number), `kiri`/`tengah` (left/middle) in the
  2006 RSS feed, `#mana` (where) in push.css, `jafa/`.
- Slashdot accounts used as puppets: `foundme` (uid 897346, homepage
  xccr.com, bio "Do you readme.txt?", sig "Please stop entering code
  2,2,7,6,6,4"), `blackwater` (uid 227664), `tfeyet` (uid 974444 = "him"),
  `227664` (uid 975093), `113389363`, `3389363`, `dDwyMDYNTIwNzMOzsmUP`.
- 2006 host: hsphere.cc / vortechhosting, then spock.techservers.net
  (74.54.241.132, ThePlanet) until ~2016. MX still points at
  `webmail.techservers.net` (dead).

So: a Malaysian-Chinese hobbyist ASP.NET/PHP developer from Batu Pahat living
in New Zealand (Palmerston North, earlier Auckland), running this for 22 years
at a cost of one Plesk VPS. Domster, the best 2006 solver, was also in
Auckland and guessed "a New Zealander" at the time.

---

## 2. The three eras

### Era 1 — 2004-2006, the Lost console (ASP.NET, IIS)

Mechanics as reverse-engineered by the Unfiction team (May-June 2006):

- Enter 8-digit-max numbers. `227664` is "the code". Entering it resets a
  99-minute timer (top right), bumps the `kiri` counter (top left, decimal),
  and sometimes grants 1-4 **keys** (kw=1 west, ke=2 east, kn=3 north,
  ks=4 south). Pressing a key digit moves "you" on a 10x10 room grid; the
  binary number in the middle (`tengah`, e.g. 01001011 = 75) is the room.
  Room/timer/counter were shared per IP block, not global.
- Grid tiles are the 5x5 `a?.gif` files; gaps are doors; the "map" fills in
  column by column as the counter rises. Flooding `227664` *lowers* the
  counter (the "loss of valuable resources" in readme.txt).
- `/images/readme.txt` (rules; acrostic **tfeyet**) and
  `/images/progress.txt` (scoreboard: image, points, Y/N, timestamp, forum
  code U=Unfiction / S=sos-dan, user id).
- Puzzle images, all solved within a week:
  - **i0** 50x100, two 5px-interleaved screenshots (sos-dan + Unfiction).
  - **i1** 50x900, same trick; deliberate edits y→v, 5→s = "versus".
  - **i2** 30x40, 7 frames: "EVERYONE IS DOING IT WELL HENCE RECORD ENSURED
    DONE WITHOUT BROKEN COUNTS IF YOU HOPING OF SOME HINT TO FIND HIM THESE
    MUST LOOK PAST SKIN DEEP SMASH EACH FIVE PX YOU SHALL FIND IT". Taking
    column k of frame digit k of 227664 gives "HE IS THE CODE ON SLASHDOT".
  - **i3** 60x90, columns shifted to align blue bars: "HIM MUST BE ANSWERED
    WITH CLUE FOUND IN I2 GIF END".
  - **i4** sideways text `/./~dDwyMDYNTIwNzMOzsmUPIfvctxrGnrbRqhbJQ` = the
    page's ASP.NET `__VIEWSTATE` with digits removed; the digits point to
    Slashdot uid 113389363, which points back at 227664's friend tfeyet.
  - **q1** "ARE YOU HIM ?" shown after valid inputs.
- **The checkpoint was reached.** Entering `227664` then `974444` (tfeyet's
  uid) on 25 May 2006 produced a points-claim page (`toolate.aspx` after
  the fact) offering 0 points to a "prize pool". progress.txt added
  `Checkpoint [Are You Him?]` on 06-Jun-2006 06:06. The PM never contacted
  the winners. Era 1 then stalled.

### Era 2 — Sep 2006-2008, the bunkers

- Home page became a 21x12 grid of 252 **bunkers** (`bunker.aspx?b=1&id=N`).
  Each had an occupant, a value (~10.xx), body colour (green/black), hatch
  colour (red/green/blue/cyan/magenta/yellow), a password field for "The
  Code", a "helper bunker" dropdown, and an apply-by-email form. Codes were
  emailed; a code had to be entered within 24 h or the bunker was released.
  Entering the code in someone else's hatch as a "helper" changed both
  values by ±1.
- The target picture `/images/x1.gif` (archived 2016) is the same 21x12 grid
  and **reads "HELLO!" on rows 0-4 and "227664" on rows 7-11** in a 3x5
  pixel font, one colour per glyph (decoded in this research; nobody had
  written it down). The 2006 players guessed they were meant to recreate
  it. They never got close: the Feb 2007 capture is 90 % red hatches.
- `rss_227664.aspx`: `<title>` = seconds left on the timer (negative once
  expired), `<kiri>`, `<tengah>` mirrored the page.
- By 2008 the timer was 22 days negative; 2011-2015 captures show room
  00000000 and a dead timer; 2016-2021 the ASP.NET app threw a Runtime
  Error. Domster posted "Dead." in the thread in 2008.

### Era 3 — Jan 2022-now, the PHP "doors" console (Plesk, PHP 7.4)

Rebuilt from scratch in PHP, same GIF assets, same `jafa/` script names,
far simpler. This is the live site.

- `keys.js`: digits append to a hidden `TextBox_Numbers` (max 8, no
  backspace). Enter with `227664` → `GET t.php` then `location.reload()`.
  Enter with anything else → `GET l.php?<digits>`. Input is disabled if the
  hidden `TextBox_IP` equals `000000` (server could render that to lock an
  IP; it has only ever been seen as `127.0.0.1`).
- `countdown.js`: `SetS(N)` on load is the server's remaining seconds;
  reload at 0; `SetS(-2)` means no timer.
- Hidden text under the console (select-all to see):
  `0.00212282 / 0.00227664 = B1b`.
- Meta tags: `doorB` = BTC address `1G9rG47hF8ckTT6icgHFV3qWBDPjkj4wME`,
  `doorD` = DOGE address `DADbBq34cngE8rzyRnJv8RJjzVyKqbqYhC`, four
  `keyB*`/`keyD*` alphabet rows (`abcdefghijklm`, `nopqrstuvwxyz`,
  `ABCDEFGHIJKLM`, `NOPQRSTUVWXYZ`), `contact` = `xccr@12345.678.90`.

**Counter history, from 75 distinct archived homepages (`data/wayback_series.json`):**

| date | hidden lines | keyB1 |
|---|---|---|
| 2022-01-16 → 2023-10-03 | `0.00000000 / 0.00000227 = B1a` and `0 / 7 = D1a` | abcdefghijklm |
| 2023-10-15 | `0.00079082 / 0.00227664 = B1b`, D line gone | **D**bcdefghijklm |
| 2023-10-15 → 2024-01-21 | decays ~0.000003/h to **0.00034682** and sits there | |
| 2024-06-21 → 2024-07-31 | climbs to 0.00197882 (Flipkaboom's keepalive script) | |
| 2024-08-10 | 0.00179582 (decayed after script stopped) | |
| 2024-09-12 → today | **0.00212282**, frozen | |

What that tells us:

- Completing slot B1a replaced the first character of keyB1 (`a` → `D`) and
  removed the D line. The goal then became `0.00227664`, i.e. the code.
- `0.00034682` is exactly the BTC the doorB wallet received on 22 Nov 2022
  (one transaction, still unspent, balance verified on chain 2026-10-17).
  The counter floors at the wallet balance: the money is the "resources".
  The DOGE wallet has never received anything; the D line showed `0 / 7`.
- While the timer is alive the counter rises 0.000003 per hour; while dead it
  falls (r/XCCR, Flipkaboom, confirmed by the series). From 0.00212282 the
  goal needs 0.00015382 / 0.000003 ≈ **51 hours of unbroken timer**.
- It has not moved since 2024-09-12 although the timer has been running in
  almost every capture since. Either the hourly job died, or the rule
  changed after someone gamed it. **This is the single most important
  open question and it is directly testable (section 4).**

Other era-3 facts established today:

- `t.php` resets the timer to 6000 s **only with a same-origin Referer**
  (bare curl: no effect; `Referer: https://xccr.com/`: reset; tested
  2026-10-17 04:45Z, `data/trigger.jsonl`). There is no 10-minute lockout:
  two resets 9 s apart both took.
- `l.php`, `r.php`, `counter.php` all return 2 bytes `0x20 0x20` to any GET,
  with or without Referer/XHR headers. `r.php` returned ` 3582 ` once in a
  June 2022 capture (looks like seconds remaining); `counter.php` existed in
  2022. Other single-letter `.php` names 404 (16-byte "File not found." from
  PHP-FPM, vs the 808-byte Plesk 404 page for non-PHP paths: this
  distinguishes "PHP file missing" from "path missing").
- `b1-x.png` (318x294, top-left quarter of a QR code, version ≥3, ECC H,
  mask 6 per Dry_Spend3702's analysis) was already archived on
  **2022-04-15**. The wiki's "uploaded 11 Oct 2023" is wrong. Its PLTE chunk
  holds the printable ASCII range three times; probably just the encoder.
  Nothing has been found at `b2-x`, `b1-y`, `d1-x` etc.
- 126 distinct `l.php?N` guesses by other people are preserved in Wayback
  Save-Page-Now captures (2022-2026). None returned anything but the 2-byte
  body. The list is in `baseline/wayback_cdx_2026-10-17.json`.
- `/images/` directory listing is live (Apache-style, served by nginx), all
  files dated 17-18 Nov 2004. `readme.txt`, `progress.txt`, `i*.gif`,
  `x1.gif` are gone from the live server (404). `/icons/` is the stock
  Apache icon set and gets touched occasionally (files dated Oct 2026).
- `push.css` has `background-images: url(images/i4.gif)` (typo, never
  applied) and unused ids `#wtf`, `#mana`, `#statsright` (green Courier):
  leftovers from era 1 where the AJAX callback filled `wtf`, `mana`,
  `statsleft`, `statsmid`, `statsright`.
- Server: nginx → PHP 7.4.33 / PleskLin; Let's Encrypt cert for `xccr.com`
  only; `www.xccr.com` → 103.7.8.100 (a cPanel default page, different box).
  Plesk login on :8443. Ports 21/25/110/143/587/993/995 open (mail stack).
- `a.xccr.com` (same IP) served the single word "SPOCK" in 2018-2019 (the
  old techservers hostname) and today 303-redirects to `/login.php`, a
  webmail-style login. It is the owner's front door, not part of the
  puzzle; the probe only hashes it (`related`), never logs in.

---

## 3. Corrections to the fan wiki (craftworks.top/xccr)

- "Registered 2004, offline 2016-2022": true, but it was *broken* (ASP.NET
  Runtime Error) not offline, and the ASP.NET app was already dead by 2008.
- "b1-x.png uploaded 11/10/23, 12 days after sg2065.com was registered":
  wrong, the PNG was captured by Wayback on 2022-04-15.
- "The number on the left was slowly increasing": it only increases while the
  timer is alive; it decays otherwise, floors at the wallet balance.
- "t.php will ignore direct page request": it ignores requests without a
  Referer. A curl with the Referer header works.
- The wiki omits the 2006 checkpoint solution (227664 + 974444), the "HELLO!
  227664" content of x1.gif, the WHOIS, the XMoo Network, and the Malay.
- "Half-Life 2 billboard": the 2006 thread found it too (ХССГ in the
  opening courtyard). HL2 shipped Nov 2004, the domain was registered
  18 Nov 2004, the GIFs are dated 17 Nov 2004. The developer may well have
  taken the name from the game, but nothing points the other way.

---

## 4. Automated exploration method

The site is a tiny state machine, not a link graph. schizospider was run
(a local schizospider run) and correctly found one
page with zero links, so it only buys us a screenshot + DOM capture. The
right instrument is a state-diffing poller plus a few targeted experiments.
That is `xccr_probe.py`.

### 4.1 What the probe does

| subcommand | purpose | notes |
|---|---|---|
| `snapshot` | parse `/` (counter, goal, slot, SetS, meta keys, TextBox_IP, statsmid digits, script list, structural hash with timer removed) + hash `r.php`, `counter.php`, `l.php`, the three JS files and push.css; append to `data/state.jsonl`; print a diff vs the last snapshot | the thing to run from cron |
| `trigger --mode bare/referer/xhr` | hit `t.php` and measure SetS before/after | proves the Referer gate |
| `keepalive --every 30 --hours 60` | keep the timer alive with Referer'd `t.php`, snapshot hourly, stop the moment counter/goal/keys change | the experiment that answers the open question |
| `lphp --start --end --pad / --list` | enumerate `l.php?N`, flag any non-baseline status/length/hash/latency, re-snapshot every k probes to catch a server-side state change that the response body does not reveal | baseline is 2 bytes; latency is the only side-channel |
| `assets --save` | hash every file in `/images/`, `/icons/`, `/icons/small/`; diff vs manifest | this is how a new `b2-x.png` or `q2.gif` would be caught |
| `dirs [--wordlist]` | probe ~70 plausible paths derived from the naming scheme and the era-1/2 files | distinguishes PHP-missing (16 B) from path-missing (808 B) |
| `wayback` | pull CDX, fetch only new distinct homepage captures, rebuild the counter time series, list new non-home captures (other people's guesses, new files) | the Save-Page-Now stream is effectively a free log of the community's attempts |
| `chain` | BTC/DOGE balances and tx list | the counter floor is the wallet |
| `related` | hash palmy.nz, sg2065.com, basong.my, xmoo.net, www.xccr.com | the owner's other sites change rarely; a change there is a signal |
| `all` | everything except keepalive/lphp/trigger | |

### 4.2 Recommended schedule

1. **Hourly**: `snapshot`. Any line in "CHANGES" is worth a human look.
2. **Daily**: `all` (adds assets, dirs, wayback, chain, related).
3. **Once, now**: `keepalive --every 30 --hours 60`. If the counter still
   does not move after 60 h of continuous timer, the hourly increment is
   dead and the puzzle is frozen server-side; stop spending effort on the
   counter and the only remaining levers are the wallet (section 4.3) and
   watching for the owner to push a change. If it does move, let it run to
   `0.00227664` and watch what replaces `b` in keyB1.
4. **Opportunistic**: `lphp` over structured candidate sets, not brute force
   over 10^8. Candidates with a reason: 974444 (tfeyet, the era-1 answer),
   975093, 897346, 113389363, 3389363, 227664 reversed/permuted, 422401216364
   split, 00000227, 227, 7, the Lost numbers, the BTC amount 34682, the goal
   digits, dates (20041118, 18112004), the bunker ids. Watch latency and
   re-snapshot; a correct code most likely changes the *page*, not the
   `l.php` body.

### 4.3 The wallet lever (needs a human decision, not automated)

The B counter floors at the doorB balance and the B1a goal was
`0.00000227` BTC, i.e. 227 sat. The D line was `0 / 7` against a DOGE
address. The cheapest plausible "intended" action in era 3 is sending a
few hundred satoshi / 7 DOGE and watching whether the hidden line changes.
That is a real transfer of money and is deliberately **not** in the probe.
If you want to test it, it is a one-line decision for you, not the tool.

### 4.4 Things the probe does not do (on purpose)

- No brute force over the full 8-digit space (10^8 requests at 1/s is three
  years and the readme says not to).
- No login attempts against Plesk/:8443, FTP, mail. Out of scope and the
  r/XCCR crowd already got told off for it.
- No contacting the owner. The mail host is dead anyway (`xccr@12345.678.90`
  is a joke address; the real one in 2006 was `xccr@palmy.net.nz`).

---

## 5. Open questions, ranked by testability

1. Does the counter still increment while the timer is alive? → `keepalive`.
2. What does `r.php` return while a timer is running from *this* IP? The
   2022 capture shows a number. The probe's snapshot already records it;
   run `snapshot` a few seconds after `trigger --mode referer`.
3. Is the timer global or per-IP in era 3? Run `trigger` from the oracle box
   or via a schizospider proxy and compare SetS from two addresses.
4. Is `TextBox_IP` ever rendered as anything but `127.0.0.1`? Snapshot
   records it; a lockout would show up there.
5. What is the full QR code? Only the owner can answer that; `assets` and
   `dirs` will catch a second quadrant if one is ever uploaded.
6. Why `B` and `D` (not A/B)? Era-2 bunkers had body colours green/black
   and six hatch colours; "doors" B and D may be bunker letters. Keys
   `kw/ke/kn/ks` are still on disk, so a movement phase may be planned.

## 6. Sources

- Live site: https://xccr.com/ (index, `jafa/*.js`, `push.css`, `/images/`, `/icons/`)
- Wayback CDX for `xccr.com` (1212 captures) and `web.archive.org/web/*/xccr.com/*`
- Unfiction thread "[XCCR] Trailhead - xccr.com" (2006), restored at
  https://forums.unfiction.com/forums/viewtopic.php@t=14871.html (15 pages)
- https://craftworks.top/xccr (fan wiki, updated 2026-08-29)
- r/UnresolvedMysteries 3a4gx4 (2015), r/XCCR (64 posts, 2015-2025), r/ARG s4ys7k (2022)
- Steam HL2 forum threads 1696043263502737256 and 1728701877478457678
- Slashdot user pages ~foundme, ~blackwater, uid 227664, 113389363 (live + 2008 Wayback)
- mempool.space and blockcypher for the two addresses
- RDAP (Verisign) for the domain, APNIC for 103.7.11.66

---

## 7. Session 2 (2026-10-18): deposit result + two new findings

### 7.1 The deposit resolves the counter model (and it's not pay-to-win)

Sent 15,382 sat to doorB on 2026-10-17 (tx `43da77fc…08ae7`, confirmed block
971869, wallet now 50,064 sat). After 24 h with the timer held alive: **no page
change.** Reconstructing the floor model from the Wayback series settles why:

- During **B1a** (2022-01 → 2023-10) the wallet already held 34,682 sat (since
  Nov 2022) yet the counter read `0.00000000` the whole time. So the counter is
  **not** the live wallet balance.
- The **B1b** floor is exactly 34,682 sat = the wallet balance **at the moment of
  the Oct-2023 slot transition**. The author relaunched the slot then, seeded the
  floor from the then-current balance, and the counter has accrued/decayed around
  that seed since (then froze Sep 2024 when the accrual cron died).

**Conclusion:** the wallet balance is read **once, at a slot transition that the
author triggers manually**, not live and not on any sub-daily schedule (24 h of
10-min and hourly snapshots prove it). Our deposit raised the balance to 50,064,
which can only matter if the author ever starts a new slot, at which point 50,064
would become the new floor. There is **no player-side action that advances B1b.**
The $12 bought a clean negative result.

### 7.2 keyB is a message buffer, spelled one letter per solved slot

The four `keyB*` rows concatenate to a 52-char substitution alphabet over
plaintext `a..z A..Z`. In the B1a era it was the identity. Solving **B1a replaced
position 1: `a` → `D`.** So the slot name `B1<x>` = door B, key-row 1, character
position `x` (a=1, b=2, …), and each solved slot **overwrites one character**.
Read in slot order, the overwrites spell a message. We have letter 1: **`D`**.
`B1b` (current) will write letter 2. The door "wallet address" is doubling as the
buffer being overwritten. Nobody in 20 years of threads documented this. (keyD is
still full identity — the D-side has never cleared a slot; its line was `0 / 7`.)

### 7.3 The QR (`b1-x.png`) is a real, deliberately-cropped code — and unrecoverable from this quadrant

Clean module extraction (pitch ≈ 16.4 px; finder + timing patterns intact →
`data/qr_grid.npy`, render `baseline/qr_extracted_modules.png`). The top-left
format-info block decodes to a **valid** format: **ECC level H, mask pattern 6**
(matches Dry_Spend3702's 2022 read). A decorative fake would not carry
self-consistent format bits, so this is a genuine QR the author cropped on
purpose.

Why it can't be brute-reconstructed from what we have:
- The image is the top-left ~17×16 modules of a ≥29×29 (version ≥3) symbol — only
  about **one third** of the modules.
- QR data is placed bottom-right → up, so the **mode indicator + length header +
  start of the message sit in the missing bottom-right corner**; the top-left is
  the *tail* of the stream (largely padding).
- v3-H error correction tolerates ≤22 erased codewords per 35-codeword block;
  missing ~⅔ of the symbol is ~23+ per block, **over the limit**. RS erasure
  decoding fails. This is a hard information-theoretic ceiling, not a tooling gap.

Only three things could change this: the author uploads another quadrant
(`assets` watch would catch a `b2-x`/`b1-y`/etc.), the full code turns up
elsewhere, or a higher-res/less-cropped capture of `b1-x` surfaces. Brute force
over versions/masks doesn't help — the missing data simply isn't present.

### 7.4 Ruled out this session
- **favicon.ico "second layer"** (the 2006 thread's loose end): it's the stock
  Windows document icon (white page, folded corner, grey checkerboard). Not art.
- **Sister sites** (sg2065.com, palmy.nz, basong.my) use the identical HTML
  template (`DESCRIPTION` + `contact` meta, same casing) but carry **none** of the
  door/key/counter machinery. The game lives only on xccr.com.
- **`l.php` guesses**: the `contact` meta digits (`12345678`, `1234567890`, …) and
  the era-1 Slashdot IDs (974444, 975093, 897346) all return the 2-byte baseline.
