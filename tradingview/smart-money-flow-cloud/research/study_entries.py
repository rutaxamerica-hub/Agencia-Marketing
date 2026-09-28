"""Comparacion de variantes de entrada (independiente de la salida).

Uso: python study_entries.py [is|oos|all]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common
import signals as S
import study

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 200)


def pullback(A, touch=0.0, conf=S.CONF_UPBAR, max_bars=10, slope=False, mf=False, reset=1.0):
    return S.pullback_signals(A["regime"], A["z"], A["zl"], A["zh"], A["c"], A["h"], A["l"], A["slope"], A["mf"],
                              touch, reset, conf, max_bars, slope, mf)


def builder(df, ind, A):
    fam = {"ORIG dots (retest)": (ind["bullDot"].to_numpy(), ind["bearDot"].to_numpy())}
    fam.update(S.reversal_family(A))
    for conf, name in S.CONF_NAMES.items():
        fam[f"P conf={name}"] = pullback(A, conf=conf)
    fam["P conf=z sube +pendiente"] = pullback(A, conf=S.CONF_UPBAR, slope=True)
    fam["P conf=z sube +flujo"] = pullback(A, conf=S.CONF_UPBAR, mf=True)
    fam["P conf=cierre>max[1] +pendiente"] = pullback(A, conf=S.CONF_HIGH1, slope=True)
    fam["P toque 0.5 conf=z sube"] = pullback(A, touch=0.5, conf=S.CONF_UPBAR)
    fam["P toque -0.5 conf=z sube"] = pullback(A, touch=-0.5, conf=S.CONF_UPBAR)
    for k, name in ((0, "K re-cruce banda tras test"), (1, "K nuevo extremo tras test")):
        fam[name] = S.continuation_signals(A["regime"], A["zl"], A["zh"], A["c"], A["h"], A["l"],
                                           A["upper"], A["lower"], k)
    return fam


COLS = ["n", "per_1000", "edge", "tb_sym_win", "tb_asym_win", "fwd_mean", "false", "progress_med",
        "remaining_med", "mdelay_med", "mdist_med", "pb_precision", "pb_recall", "rev_detected",
        "rev_delay_med", "rev_progress_med", "rev_late_or_missed"]

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    st = study.Study(part=part).run(builder)
    pooled = st.summary()[COLS]
    print(common.fmt(pooled, 3))
    common.save(pooled, f"03_entradas_{part}")
    byg = st.summary(by_group=True)[["n", "edge", "tb_sym_win", "tb_asym_win", "fwd_mean", "progress_med"]]
    edge = byg["edge"].unstack("group")
    print(common.fmt(edge, 3))
    common.save(byg, f"03_entradas_por_grupo_{part}")
