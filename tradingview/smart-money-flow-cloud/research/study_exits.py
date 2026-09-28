"""Salidas estudiadas por separado: misma entrada, distintas logicas de salida (in-sample)."""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common
import study_strategy as ss
import system

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)


def exits(base: system.Cfg):
    b = base
    return {
        "X0 cambio de regimen (SAR)": b,
        "X1 stop que sigue a la banda contraria": b.but(stop_mode="band", band_trail=True),
        "X2 cierre cruza la base": b.but(exit_basis=True),
        "X3 pendiente gira": b.but(exit_slope=True),
        "X4 chandelier 2 ATR": b.but(chand_k=2.0),
        "X5 chandelier 3 ATR": b.but(chand_k=3.0),
        "X6 chandelier 4 ATR": b.but(chand_k=4.0),
        "X7 stop en base -0.5 ATR": b.but(basis_trail=0.5),
        "X8 stop inicial 2 ATR": b.but(stop_mode="atr", stop_atr=2.0),
        "X9 stop estructura + chandelier 3": b.but(stop_mode="struct", chand_k=3.0),
        "X10 parcial 50% a 2 ATR + BE + chand 3": b.but(stop_mode="atr", stop_atr=2.0, tp_atr=2.0, tp_frac=0.5,
                                                        be_after_tp=True, chand_k=3.0),
        "X11 tiempo 40 velas": b.but(max_bars=40),
    }


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    bases = {
        "E1": system.Cfg(adaptive=False, squeeze=True, squeeze_th=1.0),
        "E3": system.Cfg(adaptive=False, squeeze=True, squeeze_th=1.0, e_cont=True),
    }
    R = ss.Runner(part)
    out = []
    for bname, base in bases.items():
        TT, PP = [], []
        for k, cfg in exits(base).items():
            T, P = R.run(cfg, f"{bname} | {k}")
            TT.append(T)
            PP.append(P)
        T = pd.concat(TT)
        P = pd.concat(PP)
        pooled = ss.pooled(T, P)
        print(common.fmt(pooled, 3))
        g = ss.pooled(T, P, by_group=True)
        print(common.fmt(g["exp_atr"].unstack("group"), 3))
        print(common.fmt(g["pct_sets_pos"].unstack("group"), 2))
        print(common.fmt(g["dd_med"].unstack("group"), 2))
        out.append(g)
    common.save(pd.concat(out), f"06_salidas_{part}")
