import math

import pandas as pd
import pytest

from attrition import analysis as A, report, synth


@pytest.fixture(scope="module")
def prepared():
    cfg = A.Config(obs_end=pd.Timestamp("2026-06-30"))
    df = synth.generate(n=900, seed=3)
    return A.prepare(df, cfg), cfg


def test_wilson_interval_contains_point_estimate():
    lo, hi = A.wilson(30, 100)
    assert 0 < lo < 0.30 < hi < 1
    assert all(math.isnan(x) for x in A.wilson(0, 0))


def test_mature_cohort_has_full_follow_up(prepared):
    d, cfg = prepared
    m = d[d["mature"]]
    assert (m["hire_date"] <= cfg.obs_end - pd.Timedelta(days=cfg.horizon_days)).all()
    assert len(m) < len(d)


def test_naive_rate_understates_when_recent_hires_are_included(prepared):
    d, _ = prepared
    o = A.overall(d)
    assert o["naive"] < o["rate"]          # right-censoring bias
    assert o["lo"] < o["rate"] < o["hi"]


def test_kaplan_meier_is_monotone_and_bounded(prepared):
    d, _ = prepared
    km = A.kaplan_meier(d)
    rates = [km[i]["rate"] for i in range(13)]
    assert rates[0] == 0 and rates == sorted(rates) and rates[-1] <= 100
    assert all(km[i]["lo"] <= km[i]["rate"] <= km[i]["hi"] for i in range(13))


def test_km_agrees_with_cohort_rate_within_sampling_noise(prepared):
    d, _ = prepared
    assert abs(A.kaplan_meier(d)[12]["rate"] - A.overall(d)["rate"]) < 4


def test_risk_groups_partition_the_cohort(prepared):
    d, _ = prepared
    m = d[d["mature"]]
    rt = A.risk_table(m)
    assert sum(r["n"] for r in rt) == len(m)
    assert rt[2]["rate"] > rt[0]["rate"]   # risk stacks in the synthetic data


def test_segment_table_covers_all_rows(prepared):
    d, _ = prepared
    m = d[d["mature"]]
    t = A.segment_table(m, "team")
    assert sum(r["n"] for r in t["rows"]) == len(m)
    assert 0 <= t["p"] <= 1


def test_drivers_model_recovers_manager_effect(prepared):
    d, _ = prepared
    r = A.drivers_model(d[d["mature"]])
    assert r["manager_changed"]["or"] > 1 and r["manager_changed"]["p"] < 0.05
    assert 0.5 < r["auc"] < 1


@pytest.mark.parametrize("lang", ["en", "fa"])
def test_reports_build_and_are_self_contained(prepared, lang):
    d, cfg = prepared
    html = report.build(d, cfg, lang)
    assert "<!doctype html>" in html and "http://" not in html.replace("http://www.w3.org", "")
    assert 'dir="rtl"' in html if lang == "fa" else 'dir="ltr"' in html
    if lang == "fa":
        assert "۲" in html            # Persian digits
        assert "◊" not in html        # no leftover placeholders
