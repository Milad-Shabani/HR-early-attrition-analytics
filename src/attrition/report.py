"""Self-contained bilingual HTML report (no external requests: CSS, SVG and a few lines of JS inline)."""
from __future__ import annotations

import html
import math
import re

import pandas as pd

from . import analysis as A
from .i18n import CONTROLLABLE, FA_DIGITS, MAPS_FA, REASON_FA, S

LAT = re.compile(r"[A-Za-z][A-Za-z0-9_\-–]*(?: [A-Za-z][A-Za-z0-9_\-–]*)*(?:\s?[=<>≈×]\s?[0-9۰-۹٫.]+)?")
CTRL = {"en": ("Within the organisation's influence", "Other"), "fa": ("در حوزه اثر سازمان", "سایر")}

CSS = """
:root{--ink:#14202b;--mut:#5b6773;--line:#e6e9ee;--soft:#f6f8fb;--acc:#1f5eff;--risk:#e8590c;--ok:#2b8a3e;--navy:#1b2b44;--grey:#c9d0d8}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#fff;color:var(--ink);line-height:1.7}
.fa-body{font-family:"Mix","B Nazanin",Vazirmatn,Tahoma,serif;font-size:18px}.en-body{font-family:"Times New Roman",Times,serif;font-size:18px}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.hero{padding:56px 0 28px;border-bottom:1px solid var(--line)}
.hero h1{font-size:2.3rem;line-height:1.25;margin:10px 0 8px}.hero p{color:var(--mut);max-width:760px;margin:0}
.badge{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:2px 14px;font-size:.85rem;color:var(--mut);background:var(--soft)}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px}.top a{color:var(--acc);text-decoration:none;font-weight:700}
nav{position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:5}
nav .wrap{display:flex;gap:6px;overflow-x:auto;padding-top:8px;padding-bottom:8px}
nav a{white-space:nowrap;color:var(--mut);text-decoration:none;padding:4px 14px;border-radius:99px;font-size:.92rem}nav a:hover{background:var(--soft);color:var(--ink)}
section{padding:44px 0 8px}.kick{color:var(--acc);font-weight:700;font-size:.95rem;margin:0}
h2{font-size:1.65rem;line-height:1.35;margin:4px 0 18px}h4{margin:0 0 6px;font-size:1.02rem}
.grid{display:grid;gap:20px}.g3{grid-template-columns:repeat(3,1fr)}.g2{grid-template-columns:repeat(2,1fr)}
.card{border:1px solid var(--line);border-radius:16px;padding:20px 22px;background:#fff}.soft{background:var(--soft)}
.mut{color:var(--mut);font-size:.92rem}.big{font-size:3.6rem;font-weight:700;line-height:1.1;color:var(--acc)}
.formula{background:var(--soft);border-radius:12px;padding:12px 16px;margin:10px 0}
.cohort{display:flex;align-items:flex-end;gap:10px;height:210px;margin-top:8px}.cc{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;font-size:.9rem}
.cc i{display:block;width:70%;background:var(--navy);border-radius:6px 6px 0 0;transform-origin:bottom}.cc.no i{background:var(--grey)}.cc b{margin-bottom:3px}.cc span{color:var(--mut);margin-top:4px}
.yrs{display:flex;gap:10px;margin-top:2px}.yrs div{text-align:center;font-weight:700;font-size:.9rem;border-top:1px solid var(--line);padding-top:2px}
.brk{display:flex;gap:10px;margin-top:14px}.brk div{text-align:center;border-bottom:3px solid var(--navy);padding-bottom:4px;font-size:.92rem;font-weight:700}.brk .no{border-color:var(--grey);color:var(--mut)}
.waffle{display:grid;grid-template-columns:repeat(10,1fr);gap:5px;max-width:250px;margin:14px 0 8px}.waffle i{aspect-ratio:1;border-radius:50%;background:#e3e6ea;display:block}.waffle i.v{background:var(--acc)}.waffle i.n{background:var(--navy)}
.leg{display:flex;gap:14px;flex-wrap:wrap;font-size:.9rem;color:var(--mut)}.leg i{display:inline-block;width:11px;height:11px;border-radius:50%;margin-inline-end:6px;vertical-align:-1px}
.hb{display:grid;grid-template-columns:150px 1fr 64px;align-items:center;gap:10px;margin:8px 0;font-size:.95rem}.trk{direction:ltr;background:var(--soft);border-radius:8px;height:22px;position:relative}
.fill{position:absolute;left:0;top:0;height:100%;border-radius:8px;background:var(--grey);transform-origin:left}.fill.c{background:var(--acc)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:20px;border-top:1px solid var(--line);padding-top:16px}.stats b{font-size:2rem;color:var(--ink);display:block;line-height:1.2}
.seg{display:grid;grid-template-columns:150px 1fr 120px;align-items:center;gap:10px;min-height:34px;font-size:.95rem}.st{direction:ltr;position:relative;height:26px}
.st .ci{position:absolute;top:12px;height:3px;background:var(--grey);border-radius:2px}.st .dot{position:absolute;top:5px;width:16px;height:16px;margin-left:-8px;border-radius:50%;background:var(--navy)}
.st .dot.up{background:var(--risk)}.st .dot.dn{background:var(--ok)}.st .avg{position:absolute;top:-2px;bottom:-2px;border-left:2px dashed var(--acc)}.sv{font-weight:700}.sv small{color:var(--mut);font-weight:400}
.sh{margin:16px 0 2px;font-weight:700;color:var(--mut);font-size:.92rem}.axis{display:grid;grid-template-columns:150px 1fr 120px;gap:10px;margin-top:6px;color:var(--mut);font-size:.85rem}.ax{direction:ltr;position:relative;height:20px}.ax span{position:absolute;transform:translateX(-50%)}
.drv .chip{color:var(--ink);background:#eef3ff;border-radius:8px;padding:6px 10px;font-size:.9rem;margin:0 0 10px}.bars,.labs{display:flex;direction:ltr;gap:12px}.bars{height:170px;align-items:flex-end;position:relative;border-bottom:2px solid var(--grey)}
.b{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;font-weight:700;font-size:.95rem}.b span{background:#fff;padding:0 6px;border-radius:6px;position:relative;z-index:1}.b i{display:block;width:62%;background:var(--grey);border-radius:6px 6px 0 0;margin-top:3px;transform-origin:bottom}.b i.hot{background:var(--risk)}
.labs div{flex:1;text-align:center;font-size:.88rem;padding-top:6px}.labs small{display:block;color:var(--mut)}.avgl{position:absolute;left:0;right:0;border-top:2px dashed var(--acc);pointer-events:none}
.rk .b i{width:70%}.rk .b i.hot{background:var(--risk)}.rk .b i.mid{background:#f0a66b}
table{width:100%;border-collapse:collapse;font-size:.95rem}th{color:var(--mut);text-align:start;font-weight:700;border-bottom:2px solid var(--line);padding:8px}td{border-bottom:1px solid var(--line);padding:12px 8px;vertical-align:top}
td .nm{font-weight:700}.num{display:inline-flex;width:26px;height:26px;border-radius:50%;background:#eef3ff;color:var(--acc);align-items:center;justify-content:center;font-weight:700;margin-inline-end:8px}
.mini{direction:ltr;display:flex;align-items:center;gap:8px}.mini i{display:block;height:14px;background:var(--grey);border-radius:7px;transform-origin:left}.mini i.c{background:var(--risk)}
.target{margin-top:18px;background:#eef3ff;border-radius:14px;padding:16px 20px;font-weight:700}
footer{margin-top:50px;padding:26px 0 40px;border-top:1px solid var(--line);color:var(--mut);font-size:.9rem}
.reveal{opacity:0;transform:translateY(16px);transition:opacity .7s ease,transform .7s ease}.reveal.in{opacity:1;transform:none}
.reveal .cc i,.reveal .b i{transform:scaleY(0);transition:transform .9s cubic-bezier(.2,.8,.2,1) .15s}.reveal .fill,.reveal .mini i{transform:scaleX(0);transition:transform .9s cubic-bezier(.2,.8,.2,1) .15s}
.reveal.in .cc i,.reveal.in .b i{transform:scaleY(1)}.reveal.in .fill,.reveal.in .mini i{transform:scaleX(1)}
@media(max-width:860px){.g3,.g2,.stats{grid-template-columns:1fr}.hb{grid-template-columns:110px 1fr 54px}.seg,.axis{grid-template-columns:96px 1fr 84px}.hero h1{font-size:1.7rem}}
@media(prefers-reduced-motion:reduce){.reveal,.reveal *{transition:none!important;transform:none!important;opacity:1!important}}
@media print{nav{display:none}.reveal{opacity:1!important;transform:none!important}.reveal *{transform:none!important}section{break-inside:avoid}}
"""
FA_FONT = ('@font-face{font-family:"Mix";src:local("Times New Roman");unicode-range:U+0000-00FF,U+2000-206F}'
           '@font-face{font-family:"Mix";src:local("B Nazanin"),local("Vazirmatn"),local("Tahoma");unicode-range:U+0600-06FF,U+FB50-FDFF,U+FE70-FEFF,U+200C-200D}')
JS = ("const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12});"
      "document.querySelectorAll('.reveal').forEach(el=>io.observe(el));")


def build(d: pd.DataFrame, cfg: A.Config, lang: str) -> str:
    L, fa = S[lang], lang == "fa"
    m = d[d["mature"]]
    o, km = A.overall(d), A.kaplan_meier(d)

    def N(v, dec=0, pct=False):
        s = f"{v:.{dec}f}" + ("%" if pct else "")
        return s.replace(".", "٫").translate(FA_DIGITS).replace("%", "٪") if fa else s

    def T(s):
        s = html.escape(s, quote=False)
        return LAT.sub(lambda mm: f'<bdi dir="ltr">{mm.group(0)}</bdi>', s) if fa else s

    def lab(kind, key):
        return MAPS_FA.get(kind, {}).get(key, str(key)) if fa else str(key)

    def ptxt(p):
        return "p<" + N(0.001, 3) if p < 0.001 else "p=" + N(p, 3 if p < 0.1 else 2)

    avg = o["rate"]
    cut = (cfg.obs_end - pd.Timedelta(days=cfg.horizon_days)).strftime("%Y-%m-%d")
    cut_s = f'<bdi dir="ltr">{cut.translate(FA_DIGITS) if fa else cut}</bdi>'

    # ---- section 1: cohort
    rows = A.cohort_by_quarter(d, cfg)
    mx = max(r["n"] for r in rows)
    cols = "".join(f'<div class="cc {"" if r["complete"] else "no"}"><b>{N(r["n"])}</b><i style="height:{r["n"] / mx * 150:.0f}px"></i><span>{T(L["q"].format(q=N(r["q"])))}</span></div>' for r in rows)
    years = {}
    for r in rows:
        years[r["year"]] = years.get(r["year"], 0) + 1
    yrs = "".join(f'<div style="flex:{c}">{N(y)}</div>' for y, c in years.items())
    nc = sum(1 for r in rows if r["complete"])
    brk = (f'<div class="ok" style="flex:{nc}" dir="auto">{T(L["complete"].format(n=N(o["n"])))}</div>'
           f'<div class="no" style="flex:{len(rows) - nc}" dir="auto">{T(L["incomplete"].format(n=N(o["n_incomplete"])))}</div>')
    s1 = f"""<section id="s1" class="reveal"><p class="kick">{T(L['k'][0])}</p><h2>{T(L['s1h'])}</h2>
<div class="grid g2"><div class="card"><h4>{T(L['kpi_name'])}</h4><p>{T(L['kpi_def'])}</p><div class="formula">{T(L['kpi_formula'])}</div></div>
<div class="card"><p style="margin-top:0">{T(L['rule'].format(cut='◊', n_inc=N(o['n_incomplete']), naive=N(o['naive'], 1, True))).replace('◊', cut_s)}</p></div></div>
<div class="card" style="margin-top:20px"><h4>{T(L['cohort_t'])}</h4><div class="brk" dir="ltr">{brk}</div><div class="cohort" dir="ltr">{cols}</div><div class="yrs" dir="ltr">{yrs}</div></div></section>"""

    # ---- section 2: overall
    nv, ni = round(o["rate"] * o["vol_share"] / 100), round(o["rate"] * (1 - o["vol_share"] / 100))
    dots = "".join(f'<i class="{"v" if i < nv else "n" if i < nv + ni else ""}"></i>' for i in range(100))
    ymax = max(10, math.ceil(max(v["hi"] for v in km.values()) / 10) * 10)
    W, H, ml, mr, mt, mb = 560, 320, 54, 16, 20, 52
    X = lambda t: ml + t / 12 * (W - ml - mr)
    Y = lambda v: mt + (H - mt - mb) * (1 - v / ymax)
    grid = "".join(f'<line x1="{ml}" x2="{W - mr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#e6e9ee"/><text x="{ml - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="15" fill="#5b6773">{N(v)}{"٪" if fa else "%"}</text>' for v in range(0, ymax + 1, 10))
    xt = "".join(f'<text x="{X(t):.1f}" y="{H - mb + 20}" text-anchor="middle" font-size="15" fill="#5b6773">{N(t)}</text>' for t in range(0, 13, 3))
    band = " ".join(f"{X(t):.1f},{Y(km[t]['hi']):.1f}" for t in range(13)) + " " + " ".join(f"{X(t):.1f},{Y(km[t]['lo']):.1f}" for t in range(12, -1, -1))
    line = " ".join(f"{X(t):.1f},{Y(km[t]['rate']):.1f}" for t in range(13))
    pts = "".join(f'<circle cx="{X(t):.1f}" cy="{Y(km[t]["rate"]):.1f}" r="4.5" fill="#1f5eff" stroke="#fff" stroke-width="2"/><text x="{X(t):.1f}" y="{Y(km[t]["rate"]) - 10:.1f}" text-anchor="middle" font-size="15" font-weight="700" fill="#14202b">{N(km[t]["rate"], 1)}{"٪" if fa else "%"}</text>' for t in (3, 6, 9, 12))
    kmsvg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(L["km_t"])}" style="width:100%;height:auto">{grid}{xt}'
             f'<polygon points="{band}" fill="#1f5eff" opacity=".14"/><polyline points="{line}" fill="none" stroke="#1f5eff" stroke-width="3" stroke-linejoin="round"/>{pts}'
             f'<text x="{(ml + W - mr) / 2}" y="{H - 6}" text-anchor="middle" font-size="15" fill="#5b6773">{html.escape(L["km_x"])}</text></svg>')
    reasons = A.exit_reasons(m)
    rmax = max(p for _, p in reasons)
    hb = "".join(f'<div class="hb"><span>{T(REASON_FA.get(k, k) if fa else k)}</span><div class="trk"><div class="fill {"c" if k in CONTROLLABLE else ""}" style="width:{p / rmax * 100:.0f}%"></div></div><b>{N(p, 1, True)}</b></div>' for k, p in reasons)
    ex = m[m["exited12"] == 1]
    st3, st6 = 100 * (ex["tenure_days"] <= 91.3).mean(), 100 * (ex["tenure_days"] <= 182.6).mean()
    s2 = f"""<section id="s2" class="reveal"><p class="kick">{T(L['k'][1])}</p><h2>{T(L['s2h'].format(x=N(round(100 / avg))))}</h2>
<div class="grid g2"><div class="card"><p class="mut" style="margin:0">{T(L['rate_lab'])}</p><div class="big">{N(avg, 1, True)}</div><b>{T(L['of'].format(k=N(o['k']), n=N(o['n'])))}</b><p class="mut">{T(L['ci'].format(lo=N(o['lo'], 1, True), hi=N(o['hi'], 1, True)))}</p>
<div class="waffle" dir="ltr">{dots}</div><div class="leg"><span><i style="background:#1f5eff"></i>{T(L['vol'])} {N(avg * o['vol_share'] / 100, 1, True)}</span><span><i style="background:#1b2b44"></i>{T(L['invol'])} {N(avg * (1 - o['vol_share'] / 100), 1, True)}</span><span><i style="background:#e3e6ea"></i>{T(L['stay'])}</span></div></div>
<div class="card"><h4>{T(L['km_t'])}</h4><p class="mut" style="margin:0 0 4px">{T(L['km_note'])}</p>{kmsvg}</div></div>
<div class="card" style="margin-top:20px"><h4>{T(L['reasons_t'].format(k=N(o['k'])))}</h4><div class="leg" style="margin-bottom:6px"><span><i style="background:#1f5eff"></i>{CTRL[lang][0]}</span><span><i style="background:#c9d0d8"></i>{CTRL[lang][1]}</span></div>{hb}</div>
<div class="stats"><div><b>{N(o['vol_share'], 0, True)}</b><span class="mut">{T(L['stat_vol'])}</span></div><div><b>{N(st3, 1, True)}</b><span class="mut">{T(L['stat_3'])}</span></div><div><b>{N(st6, 0, True)}</b><span class="mut">{T(L['stat_6'])}</span></div></div></section>"""

    # ---- section 3: segments
    dims = ["team", "grade", "site", "contract", "manager_changed"]
    tabs = {c: A.segment_table(m, c) for c in dims}
    amx = max(10, math.ceil(max(r["hi"] for t in tabs.values() for r in t["rows"]) / 10) * 10)
    body = ""
    for c in dims:
        body += f'<div class="sh">{T(L["dims"][c])} <small>({T(ptxt(tabs[c]["p"]))})</small></div>'
        for r in tabs[c]["rows"]:
            name = L["mgr"][int(r["key"])] if c == "manager_changed" else lab(c, r["key"])
            cls = "up" if r["lo"] > avg else "dn" if r["hi"] < avg else ""
            body += (f'<div class="seg"><span dir="auto">{T(name)}</span><div class="st"><i class="ci" style="left:{r["lo"] / amx * 100:.1f}%;width:{(r["hi"] - r["lo"]) / amx * 100:.1f}%"></i>'
                     f'<i class="avg" style="left:{avg / amx * 100:.1f}%"></i><b class="dot {cls}" style="left:{r["rate"] / amx * 100:.1f}%"></b></div>'
                     f'<span class="sv">{N(r["rate"], 1, True)} <small>{T(L["people"].format(n=N(r["n"])))}</small></span></div>')
    ticks = "".join(f'<span style="left:{v / amx * 100:.0f}%">{N(v)}</span>' for v in range(0, amx + 1, 10))
    leg3 = (f'<div class="leg" style="margin-top:6px"><span><i style="background:#e8590c"></i>{L["lg"][0]}</span><span><i style="background:#2b8a3e"></i>{L["lg"][1]}</span><span><i style="background:#1b2b44"></i>{L["lg"][2]}</span></div>')
    s3 = f"""<section id="s3" class="reveal"><p class="kick">{T(L['k'][2])}</p><h2>{T(L['s3h'])}</h2>
<div class="card"><p class="mut" style="margin-top:0">{T(L['seg_note'].format(avg=N(avg, 1, True)))}</p>{leg3}{body}<div class="axis"><span></span><div class="ax">{ticks}</div><span></span></div>
<div class="axis"><span></span><div style="text-align:center;direction:ltr">{T(L['axis'])}</div><span></span></div></div></section>"""

    # ---- section 4: drivers
    dm = A.drivers_model(m)
    pay, onb, ot = N(cfg.pay_low, 2), N(cfg.onboarding_low, 1), N(cfg.overtime_high, 0)
    rng_ = lambda a, b: f'<bdi dir="ltr">{a}–{b}</bdi>'
    mg = [m[m["manager_changed"] == i] for i in (0, 1)]

    def eff(key, name, invert):
        r = dm[key]
        v = 1 / r["or"] if invert else r["or"]
        txt = L[name].format(v=N(v, 1), p=ptxt(r["p"]))
        return T(txt) + (f" · {T(L['ns'])}" if r["p"] >= 0.05 else "")
    drivers = [
        ("mgr", eff("manager_changed", "eff_mgr", False), [(L["mgr"][0], 100 * mg[0]["exited12"].mean(), len(mg[0])), (L["mgr"][1], 100 * mg[1]["exited12"].mean(), len(mg[1]))], 1),
        ("onb", eff("onboarding_score_z", "eff_onb", True), None, 0),
        ("pay", eff("pay_ratio_z", "eff_pay", True), None, 0),
        ("ot", eff("weekly_overtime_h_z", "eff_ot", False), None, 2),
    ]
    spec = {"onb": ("onboarding_score", [0, cfg.onboarding_low, 4.0, 9], [L["lvl_under"].format(x=onb), rng_(onb, N(4, 1)), L["lvl_over"].format(x=N(4, 1))]),
            "pay": ("pay_ratio", [0, cfg.pay_low, 1.0, 9], [L["lvl_under"].format(x=pay), rng_(pay, N(1, 2)), L["lvl_over"].format(x=N(1, 2))]),
            "ot": ("weekly_overtime_h", [-1, 4, cfg.overtime_high, 999], [L["lvl_under"].format(x=N(4)), rng_(N(4), ot), L["lvl_over"].format(x=ot)])}
    cards = ""
    for key, chip, data, hot in drivers:
        if data is None:
            col, edges, labels = spec[key]
            br = A.bin_rates(m, col, edges, 3)
            data = [(labels[i], br[i]["rate"], br[i]["n"]) for i in range(3)]
        top = max(10, max(x[1] for x in data) * 1.15)
        bars = "".join(f'<div class="b"><span>{N(r, 1, True)}</span><i class="{"hot" if i == hot else ""}" style="height:{r / top * 140:.0f}px"></i></div>' for i, (_, r, _) in enumerate(data))
        labs = "".join(f'<div>{lb if "<bdi" in lb else T(lb)}<small>{T(L["people"].format(n=N(n)))}</small></div>' for lb, _, n in data)
        cards += (f'<div class="card drv"><h4>{T(L["drv"][key])}</h4><p class="chip">{chip}</p><div class="bars">{bars}<div class="avgl" style="bottom:{avg / top * 140:.0f}px"></div></div><div class="labs">{labs}</div></div>')
    s4 = f"""<section id="s4" class="reveal"><p class="kick">{T(L['k'][3])}</p><h2>{T(L['s4h'])}</h2><p class="mut">{T(L['drv_note'].format(auc=N(dm['auc'], 2)))}</p><div class="grid g2">{cards}</div></section>"""

    # ---- section 5: risk stacking
    rk = A.risk_table(m)
    rmax2 = max(10, max(r["rate"] for r in rk) * 1.15)
    rbars = "".join(f'<div class="b"><span style="font-size:1.5rem">{N(r["rate"], 1, True)}</span><i class="{["", "mid", "hot"][i]}" style="height:{r["rate"] / rmax2 * 170:.0f}px"></i></div>' for i, r in enumerate(rk))
    rlabs = "".join(f'<div>{T(L["risk_n"][i])}<small>{T(L["people"].format(n=N(r["n"])))}</small></div>' for i, r in enumerate(rk))
    step = ((rk[2]["rate"] / rk[0]["rate"]) ** 0.5) if rk[0]["rate"] > 0 else float("nan")
    ctrl_share = sum(p for k, p in reasons if k in CONTROLLABLE)
    s5 = f"""<section id="s5" class="reveal"><p class="kick">{T(L['k'][4])}</p><h2>{T(L['s5h'].format(x=N(rk[2]['rate'] / rk[0]['rate'], 1)))}</h2>
<div class="grid g2"><div class="card rk"><h4>{T(L['risk_t'])}</h4><div class="bars" style="height:210px">{rbars}</div><div class="labs">{rlabs}</div><p class="mut" style="margin-top:14px">{T(L['risk_def'].format(pay=pay, onb=onb, ot=ot))}</p></div>
<div class="grid"><div class="card soft"><b style="font-size:2.2rem;color:var(--risk)">{N(rk[2]['rate'], 0, True)}</b><p style="margin:0">{T(L['ins1'].format(ph=N(rk[2]['share_hires'], 0, True), pe=N(rk[2]['share_exits'], 0, True), x=N(rk[2]['rate'] / rk[0]['rate'], 1)))}</p></div>
<div class="card soft"><b style="font-size:2.2rem;color:var(--acc)">{N(o['vol_share'], 0, True)}</b><p style="margin:0">{T(L['ins2'].format(v=N(o['vol_share'], 0, True), c=N(ctrl_share, 0, True)))}</p></div>
<div class="card soft"><p style="margin:0">{T(L['ins3'])}</p></div></div></div></section>"""

    # ---- section 6: recommendations
    ex_ = A.excess_exits(m)
    order = sorted(ex_, key=lambda f: -ex_[f])
    pr = A.priority_segments(m, cfg)
    emax = max(ex_.values())
    trs = ""
    for i, f in enumerate(order, 1):
        t, a, ow = L["rec"][f]
        start = "، ".join(f"{lab(c, k)} ({N(p, 0, True)})" for c, k, p in pr[f]) if fa else ", ".join(f"{lab(c, k)} ({N(p, 0, True)})" for c, k, p in pr[f])
        trs += (f'<tr><td><span class="num">{N(i)}</span><span class="nm">{T(t)}</span><br><span class="mut">{T(a.format(ot=ot))}</span></td><td>{T(start) if start else T(L["all_new"])}</td><td>{T(ow)}</td>'
                f'<td><div class="mini"><i class="{"c" if i == 1 else ""}" style="width:{max(ex_[f], 0) / emax * 150:.0f}px"></i><b>{N(ex_[f])}</b></div></td></tr>')
    t, a, ow = L["dash"]
    trs += f'<tr><td><span class="num">{N(len(order) + 1)}</span><span class="nm">{T(t)}</span><br><span class="mut">{T(a)}</span></td><td>{T(L["all_new"])}</td><td>{T(ow)}</td><td class="mut">{T(L["dash_i"])}</td></tr>'
    r1 = rk[1]["rate"]
    new = (o["k"] - (rk[2]["k"] - rk[2]["n"] * r1 / 100)) / o["n"] * 100
    th = "".join(f"<th>{T(x)}</th>" for x in L["th"])
    s6 = f"""<section id="s6" class="reveal"><p class="kick">{T(L['k'][5])}</p><h2>{T(L['s6h'])}</h2><div class="card" style="overflow-x:auto"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>
<div class="target">{T(L['target'].format(a=N(avg, 1, True), b=N(new, 1, True)))}</div></section>"""

    navs = "".join(f'<a href="#s{i + 1}">{T(x)}</a>' for i, x in enumerate(L["nav"]))
    font = f"<style>{FA_FONT}</style>" if fa else ""
    return f"""<!doctype html><html lang="{lang}" dir="{L['dir']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(re.sub('<[^>]+>', '', L['title']))}</title><meta name="description" content="{html.escape(L['sub'])}">{font}<style>{CSS}</style></head>
<body class="{lang}-body"><header class="hero"><div class="wrap"><div class="top"><span class="badge">{T(L['badge'])}</span><a href="{L['other_file']}">{L['other']}</a></div><h1>{T(L['title'])}</h1><p>{T(L['sub'])}</p></div></header>
<nav><div class="wrap">{navs}</div></nav><main class="wrap">{s1}{s2}{s3}{s4}{s5}{s6}</main><footer><div class="wrap">{T(L['foot'])}</div></footer><script>{JS}</script></body></html>"""
