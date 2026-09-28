"""Que informacion interna del indicador mejora la direccion futura de una entrada?

Para un conjunto de eventos (vela t, direccion d) calcula rasgos en t (sin futuro) y resultados
con varias lentes: triple barrera +-2 ATR / 40 velas, +-4 ATR / 120 velas y retorno a 40 / 120 velas.
Uso: python study_conditions.py [is|oos]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common
import labels
import signals as S
import smf
import study

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", 300)


def features(df, ind, A):
    c = A["c"]
    a = A["atr"]
    atr_long = smf.rma(smf.true_range(A["h"], A["l"], c), 100)
    f = pd.DataFrame(index=np.arange(len(c)))
    f["pendiente"] = A["slope"]
    f["aceleracion"] = A["slope"] - smf.shift(A["slope"], 5)
    f["z"] = A["z"]
    f["dz5"] = A["z"] - smf.shift(A["z"], 5)
    f["flujo"] = A["mf"]
    f["flujo_abs"] = np.abs(A["mf"])
    f["atr_ratio"] = a / atr_long                        # compresion (<1) / expansion (>1)
    f["ancho_banda"] = ind["mult"].to_numpy()
    rng = A["h"] - A["l"]
    f["cuerpo"] = (c - df["open"].to_numpy(float)) / a
    f["rango"] = rng / a
    # edad del regimen y recorrido del regimen previo
    reg = A["regime"]
    age = np.zeros(len(c))
    for i in range(1, len(c)):
        age[i] = 0 if reg[i] != reg[i - 1] else age[i - 1] + 1
    f["edad_regimen"] = age
    return f


SIGNED = {"pendiente", "aceleracion", "z", "dz5", "flujo", "cuerpo"}   # se orientan a favor de la entrada


def outcomes(df, A, t, d):
    o = df["open"].to_numpy(float)
    out = {}
    for name, (up, dn, hz) in {"tb2_40": (2, 2, 40), "tb4_120": (4, 4, 120)}.items():
        r, _, _, _, fin = labels.triple_barrier(o, A["h"], A["l"], A["c"], A["atr"], t, d, up, dn, hz)
        out[name] = r
        out["fwd" + str(hz)] = fin
    return out


def collect(part, make_events):
    st = study.Study(part=part)
    rows = []
    for s, tf, df, ind, A, truth, valid in st.prepared():
        evs = make_events(df, ind, A)
        F = features(df, ind, A)
        for name, (ml, ms) in evs.items():
            idx, d = study.combine(ml & valid, ms & valid)
            idx_ok = idx + 1 < len(df)
            idx, d = idx[idx_ok], d[idx_ok]
            if idx.size == 0:
                continue
            fe = F.iloc[idx].reset_index(drop=True)
            for col in SIGNED:
                fe[col] = fe[col] * d
            oc = outcomes(df, A, idx, d)
            for k, v in oc.items():
                fe[k] = v
            fe["sig"] = name
            fe["group"] = study.group_of(s, tf)
            rows.append(fe)
    return pd.concat(rows, ignore_index=True)


def table(ev, feats, q=5):
    out = []
    for sig, e in ev.groupby("sig"):
        for f in feats:
            b = pd.qcut(e[f].rank(method="first"), q, labels=False)
            g = e.groupby(b)
            out.append(pd.DataFrame({
                "sig": sig, "rasgo": f, "q": range(q),
                "desde": g[f].min().values, "hasta": g[f].max().values,
                "edge2_40": g["tb2_40"].apply(lambda s: (s == 1).mean() - (s == -1).mean()).values,
                "edge4_120": g["tb4_120"].apply(lambda s: (s == 1).mean() - (s == -1).mean()).values,
                "fwd40_med": g["fwd40"].median().values,
                "fwd120_med": g["fwd120"].median().values,
            }))
    return pd.concat(out, ignore_index=True)


def events(df, ind, A):
    n = len(df)
    every = np.zeros(n, dtype=bool)
    every[::5] = True
    reg = A["regime"]
    return {
        "R0 banda (original)": (ind["buy"].to_numpy(), ind["sell"].to_numpy()),
        "BASE regimen": (every & (reg == 1), every & (reg == -1)),
    }


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    ev = collect(part, events)
    feats = ["pendiente", "aceleracion", "z", "dz5", "flujo", "flujo_abs", "atr_ratio", "ancho_banda", "cuerpo",
             "rango", "edad_regimen"]
    tab = table(ev, feats)
    summary = ev.groupby("sig").apply(lambda e: pd.Series({
        "n": len(e), "edge2_40": (e.tb2_40 == 1).mean() - (e.tb2_40 == -1).mean(),
        "edge4_120": (e.tb4_120 == 1).mean() - (e.tb4_120 == -1).mean(),
        "fwd40_med": e.fwd40.median(), "fwd120_med": e.fwd120.median()}))
    print(common.fmt(summary, 3))
    print(common.fmt(tab.set_index(["sig", "rasgo", "q"]), 3))
    common.save(tab.set_index(["sig", "rasgo", "q"]), f"04_condicionantes_{part}")
