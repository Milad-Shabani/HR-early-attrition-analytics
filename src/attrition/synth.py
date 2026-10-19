"""Synthetic hiring cohort for a *fictional* retail & logistics company.

Every value is generated; nothing here comes from a real employer. Exit risk follows a
logistic model driven by pay position, onboarding experience, manager change and overtime,
so the analysis has real structure to recover.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TEAMS = ["Customer Care", "Fulfilment", "Logistics", "Store Ops", "Sales", "Finance", "People & Culture"]
TEAM_P = [0.20, 0.22, 0.16, 0.16, 0.12, 0.07, 0.07]
GRADES = ["G1", "G2", "G3", "G4"]
GRADE_P = [0.30, 0.38, 0.22, 0.10]
SITES = ["Hub North", "Hub South", "HQ", "Remote"]
SITE_P = [0.22, 0.18, 0.42, 0.18]
OT_MEAN = {"Customer Care": 6.5, "Fulfilment": 8.5, "Logistics": 9.0, "Store Ops": 7.0,
           "Sales": 5.0, "Finance": 3.5, "People & Culture": 3.0}
VOL_REASONS = ["Pay", "Workload", "Manager/Team", "Career growth", "Better offer", "Personal"]
INVOL_REASONS = ["Performance", "Restructuring"]


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def generate(n: int = 1200, start: str = "2023-01-01", last_hire: str = "2025-12-31",
             obs_end: str = "2026-06-30", seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start_d, last_d, obs = pd.Timestamp(start), pd.Timestamp(last_hire), pd.Timestamp(obs_end)
    span = (last_d - start_d).days
    hire = start_d + pd.to_timedelta(rng.integers(0, span + 1, n), unit="D")
    team = rng.choice(TEAMS, n, p=TEAM_P)
    grade = rng.choice(GRADES, n, p=GRADE_P)
    site = rng.choice(SITES, n, p=SITE_P)
    fixed = rng.random(n) < 0.20
    g1, hi = grade == "G1", np.isin(grade, ["G3", "G4"])
    pay = np.clip(rng.normal(0.98 - 0.05 * g1 + 0.03 * hi, 0.07), 0.70, 1.30)
    ot = np.array([rng.gamma(4.0, OT_MEAN[t] / 4.0) for t in team])
    onb = np.clip(rng.normal(3.8, 0.65, n), 1.0, 5.0)
    onb_obs = np.where(rng.random(n) < 0.05, np.nan, onb)
    mgr = (rng.random(n) < 0.16).astype(int)

    z = (-1.95 + 0.60 * (pay < 0.90) + 0.80 * (onb < 3.0) + 0.85 * mgr + 0.60 * (ot >= 8.0)
         + 0.25 * fixed + 0.15 * (team == "Customer Care"))
    leaves = rng.random(n) < _sigmoid(z)
    days = (30 + 335 * rng.beta(1.3, 1.1, n)).astype(int)
    exit_dt = hire + pd.to_timedelta(days, unit="D")
    observed = leaves & (exit_dt <= obs)

    voluntary = rng.random(n) < 0.82
    reason = []
    for i in range(n):
        if not observed[i]:
            reason.append(None)
        elif voluntary[i]:
            w = np.array([1.0 + 2.0 * (pay[i] < 0.90), 1.0 + 2.0 * (ot[i] >= 8), 1.0 + 2.5 * mgr[i], 1.2, 1.2, 0.8])
            reason.append(rng.choice(VOL_REASONS, p=w / w.sum()))
        else:
            reason.append(rng.choice(INVOL_REASONS, p=[0.7, 0.3]))
    df = pd.DataFrame({
        "hire_id": [f"H{i + 1:04d}" for i in range(n)],
        "hire_date": hire.normalize(),
        "team": team, "grade": grade, "site": site,
        "contract": np.where(fixed, "Fixed-term", "Permanent"),
        "pay_ratio": pay.round(3), "weekly_overtime_h": ot.round(1),
        "onboarding_score": np.round(onb_obs, 2), "manager_changed": mgr,
        "exit_date": pd.Series(exit_dt.normalize()).where(observed),
        "exit_type": np.where(observed, np.where(voluntary, "Voluntary", "Involuntary"), None),
        "exit_reason": reason,
    })
    return df.sort_values("hire_date").reset_index(drop=True)
