"""Metricas de senal (tiempos, falsas, restante) del sistema nuevo frente al original."""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common
import signals as S
import study
import system

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)


def make_builder(mult):
    def builder(df, ind, A0):
        cfg = system.Cfg(adaptive=False, fixed_mult=mult, squeeze=True, squeeze_th=1.0, e_cont=True)
        A = system.core(df, cfg)
        sq = A["atr_ratio"] < 1.0
        cl, cs = S.continuation_signals(A["regime"], A["zl"], A["zh"], A["c"], A["h"], A["l"],
                                        A["upper"], A["lower"], 0)
        return {
            f"NUEVA entrada: ruptura en compresion (banda {mult})": (A["buy"] & sq, A["sell"] & sq),
            f"NUEVA descartada: ruptura en expansion (banda {mult})": (A["buy"] & ~sq, A["sell"] & ~sq),
            f"NUEVA continuacion en compresion (banda {mult})": (cl & sq, cs & sq),
        }
    return builder


def builder(df, ind, A):
    out = {"ORIGINAL Buy/Sell": (ind["buy"].to_numpy(), ind["sell"].to_numpy()),
           "ORIGINAL dots": (ind["bullDot"].to_numpy(), ind["bearDot"].to_numpy())}
    out.update(make_builder(1.2)(df, ind, A))
    out.update(make_builder(1.5)(df, ind, A))
    return out


COLS = ["n", "per_1000", "edge", "tb_asym_win", "false", "delay_med", "progress_med", "remaining_med",
        "mdelay_med", "mdist_med", "rev_detected", "rev_delay_med", "rev_progress_med", "rev_late_or_missed"]

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    st = study.Study(part=part).run(builder, with_baselines=True)
    s = st.summary()[COLS]
    print(common.fmt(s, 3))
    common.save(s, f"08_tiempos_senal_{part}")
    g = st.summary(by_group=True)[["edge", "progress_med", "false"]]
    print(common.fmt(g["edge"].unstack("group"), 3))
    print(common.fmt(g["progress_med"].unstack("group"), 3))
    common.save(g, f"08_tiempos_senal_por_grupo_{part}")
