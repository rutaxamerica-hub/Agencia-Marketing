"""Significancia de la ventaja: t-stat de la expectativa por operacion agregada por mes y grupo.

Agregar por mes (suma de ret_atr de las operaciones cerradas en el mes, dividida por su numero) evita
inflar la significancia por la correlacion entre activos del mismo grupo en el mismo periodo.
Uso: python study_significance.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import common
import study_strategy as ss
import system
import validate

pd.set_option("display.width", 250)

CFGS = {
    "A original": system.Cfg(),
    "FINAL umbral 1.0 (congelado)": validate.FINAL,
    "FINAL umbral 1.1": validate.FINAL.but(squeeze_th=1.1),
    "FINAL solo largos (umbral 1.0)": validate.FINAL.but(shorts=False),
    "FINAL 1.1 solo largos": validate.FINAL.but(squeeze_th=1.1, shorts=False),
}


def monthly_t(T: pd.DataFrame):
    m = T.groupby(pd.to_datetime(T["exit_time"]).dt.tz_localize(None).dt.to_period("M"))["ret_atr"].mean()
    if len(m) < 6:
        return np.nan, len(m)
    return m.mean() / (m.std(ddof=1) / np.sqrt(len(m))), len(m)


if __name__ == "__main__":
    rows = []
    for part in ("is", "oos"):
        R = ss.Runner(part)
        for k, cfg in CFGS.items():
            T, P = R.run(cfg, k)
            for g, t in T.groupby("group"):
                tt, nm = monthly_t(t)
                rows.append({"part": part, "cfg": k, "group": g, "trades": len(t),
                             "exp_atr": t["ret_atr"].mean(), "t_mensual": tt, "meses": nm})
    out = pd.DataFrame(rows).set_index(["part", "group", "cfg"]).sort_index()
    print(common.fmt(out, 2))
    common.save(out, "10_significancia")
