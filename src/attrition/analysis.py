"""Core analytics: censoring-aware KPI, Kaplan-Meier, segment intervals, drivers, risk stacking."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

DPM = 30.4375  # days per month


@dataclass(frozen=True)
class Config:
    obs_end: pd.Timestamp
    horizon_days: int = 365
    pay_low: float = 0.90          # pay ratio vs band midpoint
    onboarding_low: float = 3.0    # onboarding score (1-5)
    overtime_high: float = 8.0     # weekly overtime hours
    min_segment: int = 40


def load(path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["hire_date", "exit_date"])


def prepare(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    d = df.copy()
    end = d["exit_date"].fillna(cfg.obs_end)
    d["tenure_days"] = (end - d["hire_date"]).dt.days
    d["exited12"] = (d["exit_date"].notna() & (d["tenure_days"] <= cfg.horizon_days)).astype(int)
    d["mature"] = d["hire_date"] <= cfg.obs_end - pd.Timedelta(days=cfg.horizon_days)
    d["voluntary"] = ((d["exit_type"] == "Voluntary") & (d["exited12"] == 1)).astype(int)
    d["f_pay"] = d["pay_ratio"] < cfg.pay_low
    d["f_onb"] = d["onboarding_score"] < cfg.onboarding_low
    d["f_mgr"] = d["manager_changed"] == 1
    d["f_ot"] = d["weekly_overtime_h"] >= cfg.overtime_high
    d["n_flags"] = d[["f_pay", "f_onb", "f_mgr", "f_ot"]].sum(axis=1)
    return d


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / den, (c + h) / den


def overall(d: pd.DataFrame) -> dict:
    m = d[d["mature"]]
    n, k = len(m), int(m["exited12"].sum())
    lo, hi = wilson(k, n)
    return {"n": n, "k": k, "rate": 100 * k / n, "lo": 100 * lo, "hi": 100 * hi,
            "naive": 100 * d["exited12"].mean(), "n_all": len(d), "n_incomplete": int((~d["mature"]).sum()),
            "vol_share": 100 * m["voluntary"].sum() / max(k, 1)}


def kaplan_meier(d: pd.DataFrame, horizon_months: int = 12) -> dict:
    """Cumulative exit % at whole months with a 95% log-transformed Greenwood interval."""
    t = np.minimum(d["tenure_days"].to_numpy() / DPM, horizon_months)
    e = d["exited12"].to_numpy().astype(bool)
    steps, s, var = [], 1.0, 0.0
    for u in np.unique(t[e]):
        n_at = int((t >= u).sum())
        dd = int(((t == u) & e).sum())
        s *= 1 - dd / n_at
        var += dd / (n_at * (n_at - dd)) if n_at > dd else 0.0
        steps.append((u, s, var))
    out = {}
    for mth in range(horizon_months + 1):
        last = [x for x in steps if x[0] <= mth]
        s_, v_ = (last[-1][1], last[-1][2]) if last else (1.0, 0.0)
        if 0 < s_ < 1:
            half = 1.96 * math.sqrt(v_) / max(abs(math.log(s_)), 1e-9)
            lo_s, hi_s = s_ ** math.exp(half), s_ ** math.exp(-half)
        else:
            lo_s = hi_s = s_
        out[mth] = {"rate": 100 * (1 - s_), "lo": 100 * (1 - hi_s), "hi": 100 * (1 - lo_s)}
    return out


def segment_table(m: pd.DataFrame, col: str) -> dict:
    rows = []
    for key, g in m.groupby(col):
        n, k = len(g), int(g["exited12"].sum())
        lo, hi = wilson(k, n)
        rows.append({"key": key, "n": n, "k": k, "rate": 100 * k / n, "lo": 100 * lo, "hi": 100 * hi})
    ct = pd.crosstab(m[col], m["exited12"])
    p = float(stats.chi2_contingency(ct)[1]) if ct.shape[0] > 1 and ct.shape[1] > 1 else float("nan")
    return {"rows": sorted(rows, key=lambda r: -r["rate"]), "p": p}


def bin_rates(m: pd.DataFrame, col: str, edges, n_bins: int) -> list[dict]:
    c = pd.cut(m[col], edges, labels=False, right=False)
    out = []
    for i in range(n_bins):
        g = m[c == i]
        out.append({"n": len(g), "rate": 100 * g["exited12"].mean() if len(g) else float("nan")})
    return out


def drivers_model(m: pd.DataFrame) -> dict:
    d = m.dropna(subset=["onboarding_score"]).copy()
    for c in ("onboarding_score", "pay_ratio", "weekly_overtime_h"):
        d[c + "_z"] = (d[c] - d[c].mean()) / d[c].std()
    d["fixed_term"] = (d["contract"] == "Fixed-term").astype(int)
    f = ("exited12 ~ manager_changed + onboarding_score_z + pay_ratio_z + weekly_overtime_h_z"
         " + fixed_term + C(grade) + C(team) + C(site)")
    res = smf.logit(f, d).fit(disp=0)
    ci = res.conf_int()
    out = {k: {"or": float(np.exp(res.params[k])), "lo": float(np.exp(ci.loc[k, 0])),
               "hi": float(np.exp(ci.loc[k, 1])), "p": float(res.pvalues[k])}
           for k in ("manager_changed", "onboarding_score_z", "pay_ratio_z", "weekly_overtime_h_z", "fixed_term")}
    pred, y = res.predict(), d["exited12"].to_numpy()
    r = stats.rankdata(pred)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    out["auc"] = float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))
    out["n"] = len(d)
    return out


def risk_table(m: pd.DataFrame) -> list[dict]:
    g = m["n_flags"].clip(upper=2)
    total_exits = int(m["exited12"].sum())
    rows = []
    for i in range(3):
        sub = m[g == i]
        k = int(sub["exited12"].sum())
        rows.append({"n": len(sub), "k": k, "rate": 100 * k / len(sub) if len(sub) else float("nan"),
                     "share_hires": 100 * len(sub) / len(m), "share_exits": 100 * k / max(total_exits, 1)})
    return rows


FLAGS = ("f_pay", "f_onb", "f_mgr", "f_ot")


def excess_exits(m: pd.DataFrame) -> dict:
    out = {}
    for f in FLAGS:
        a, b = m[m[f]], m[~m[f]]
        out[f] = len(a) * (a["exited12"].mean() - b["exited12"].mean()) if len(a) and len(b) else 0.0
    return out


def priority_segments(m: pd.DataFrame, cfg: Config, k: int = 3, mult: float = 1.15) -> dict:
    out = {}
    for f in FLAGS:
        base = m[f].mean()
        rows = []
        for col in ("team", "grade", "site"):
            for key, g in m.groupby(col):
                if len(g) >= cfg.min_segment:
                    rows.append((col, key, 100 * g[f].mean(), len(g)))
        rows = sorted(rows, key=lambda r: (-round(r[2]), -r[3]))
        out[f] = [(c, key, p) for c, key, p, _ in rows if p >= 100 * base * mult][:k]
    return out


def exit_reasons(m: pd.DataFrame) -> list[tuple[str, float]]:
    ex = m[m["exited12"] == 1]
    vc = ex["exit_reason"].value_counts()
    return [(k, 100 * v / len(ex)) for k, v in vc.items()]


def cohort_by_quarter(d: pd.DataFrame, cfg: Config) -> list[dict]:
    q = d["hire_date"].dt.to_period("Q")
    cutoff = cfg.obs_end - pd.Timedelta(days=cfg.horizon_days)
    rows = []
    for per, g in d.groupby(q):
        rows.append({"q": per.quarter, "year": per.year, "n": len(g), "complete": per.end_time.normalize() <= cutoff})
    return rows
