"""Sensibilidad de parametros: se busca una meseta amplia, no un optimo aislado.

Uso: python study_robustness.py [is|oos]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common
import study_strategy as ss
import system

pd.set_option("display.width", 250)


def run_grid(R, grid):
    TT, PP = [], []
    for k, cfg in grid.items():
        T, P = R.run(cfg, k)
        TT.append(T)
        PP.append(P)
    T = pd.concat(TT)
    P = pd.concat(PP)
    return ss.pooled(T, P, by_group=True)


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    R = ss.Runner(part)
    base = system.Cfg(adaptive=False, fixed_mult=1.2, squeeze=True, squeeze_th=1.0, atr_long=100,
                      stop_mode="band")
    out = {}
    # 1) multiplicador de banda x longitud de base
    g = {}
    for L in (21, 34, 55):
        for m in (0.8, 1.0, 1.2, 1.5, 2.0):
            g[f"len={L} mult={m}"] = base.but(len=L, fixed_mult=m)
    out["banda_x_len"] = run_grid(R, g)
    # 2) umbral de compresion x longitud del ATR largo
    g = {"sin filtro": base.but(squeeze=False)}
    for AL in (50, 100, 200):
        for th in (0.8, 0.9, 1.0, 1.1, 1.2):
            g[f"atrLargo={AL} umbral={th}"] = base.but(atr_long=AL, squeeze_th=th)
    out["compresion"] = run_grid(R, g)
    # 3) longitud del ATR corto
    g = {f"atr={a}": base.but(atr_len=a) for a in (7, 14, 21, 28)}
    out["atr_corto"] = run_grid(R, g)
    for name, tab in out.items():
        print(f"\n===== {name}: expectativa por operacion (ATR) =====")
        print(common.fmt(tab["exp_atr"].unstack("group"), 3))
        print(f"===== {name}: % de datasets rentables =====")
        print(common.fmt(tab["pct_sets_pos"].unstack("group"), 2))
        print(f"===== {name}: operaciones =====")
        print(tab["trades"].unstack("group"))
        common.save(tab, f"07_robustez_{name}_{part}")
