"""Command line: `python -m attrition build` generates data (or reads a CSV) and writes both reports."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import analysis as A, report, synth


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="attrition", description="Early attrition analytics")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="generate/read data and write the EN + FA HTML reports")
    b.add_argument("--csv", help="read this CSV instead of generating synthetic data")
    b.add_argument("--n", type=int, default=1200)
    b.add_argument("--seed", type=int, default=11)
    b.add_argument("--obs-end", default="2026-06-30", help="end of the observation window (YYYY-MM-DD)")
    b.add_argument("--data-out", default="data/synthetic_hires.csv")
    b.add_argument("--out", default="docs")
    a = ap.parse_args(argv)

    cfg = A.Config(obs_end=pd.Timestamp(a.obs_end))
    if a.csv:
        df = A.load(a.csv)
    else:
        df = synth.generate(n=a.n, obs_end=a.obs_end, seed=a.seed)
        Path(a.data_out).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(a.data_out, index=False)
        print(f"wrote {a.data_out} ({len(df)} rows)")
    d = A.prepare(df, cfg)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for lang in ("en", "fa"):
        p = out / f"early_attrition_{lang}.html"
        p.write_text(report.build(d, cfg, lang), encoding="utf-8")
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
