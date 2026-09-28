"""Estudio central: retroceso vs reversion.

Evento "test de base": dentro de un regimen (+1 alcista), la primera vela de un episodio en la que el
precio vuelve a la base (minimo <= base). El episodio se rearma cuando z vuelve a >= +1 (nueva extension).
Simetrico en regimen bajista.

Resultado en retrospectiva (solo para evaluar):
  CONTINUACION  el precio supera el extremo del regimen (maximo previo) antes de que el regimen cambie.
  REVERSION     el regimen cambia (cierre cruza la banda contraria) antes de marcar nuevo extremo.

Rasgos medidos EN la vela del evento (sin futuro): pendiente de la base, money flow firmado, impulso
previo (z maximo del regimen), edad del regimen, velas desde el extremo, velocidad de la caida,
profundidad (z del cierre), numero de test dentro del regimen, cuerpo de la vela, ancho de banda.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from numba import njit

import common
import study


@njit(cache=True)
def basis_events(regime, z, zl, zh, h, l, c, o, atr, slope, mf, reset_th, touch_th):
    n = z.size
    max_ev = n // 3 + 10
    ev_t = np.full(max_ev, -1, dtype=np.int64)
    ev_d = np.zeros(max_ev, dtype=np.int64)
    feat = np.full((max_ev, 12), np.nan)
    res = np.zeros(max_ev, dtype=np.int64)
    res_bars = np.full(max_ev, -1, dtype=np.int64)
    m = 0
    start = 0
    ext_px = np.nan
    ext_i = 0
    peak_z = 0.0
    armed = False
    count = 0
    for i in range(1, n):
        if np.isnan(z[i]) or np.isnan(atr[i]):
            continue
        r = regime[i]
        if r != regime[i - 1] or i == 1:
            start = i
            ext_px = h[i] if r == 1 else l[i]
            ext_i = i
            peak_z = z[i] * r
            armed = True
            count = 0
        # el evento se evalua con el extremo previo (antes de actualizarlo con esta vela)
        touch = (zl[i] <= touch_th) if r == 1 else (zh[i] >= -touch_th)
        if armed and touch and i > start:
            if m < max_ev:
                ev_t[m] = i
                ev_d[m] = r
                a = atr[i]
                feat[m, 0] = slope[i] * r                          # pendiente a favor del regimen
                feat[m, 1] = mf[i] * r                             # flujo a favor del regimen
                feat[m, 2] = peak_z                                # impulso previo (z max a favor)
                feat[m, 3] = i - start                             # edad del regimen
                feat[m, 4] = i - ext_i                             # velas desde el extremo
                dist = (ext_px - c[i]) * r / a                     # retroceso desde el extremo (ATR)
                feat[m, 5] = dist / max(1.0, i - ext_i)            # velocidad del retroceso (ATR/vela)
                feat[m, 6] = z[i] * r                              # profundidad del cierre vs base
                feat[m, 7] = count                                 # numero de test previos en el regimen
                feat[m, 8] = (c[i] - o[i]) * r / a                 # cuerpo de la vela a favor
                feat[m, 9] = dist                                  # retroceso total (ATR)
                feat[m, 10] = slope[i - 1] * r if i > 0 else np.nan
                feat[m, 11] = (h[i] - l[i]) / a                    # rango de la vela
                # resultado en retrospectiva
                outcome = 0
                for j in range(i + 1, n):
                    flip = regime[j] != r
                    newx = (h[j] > ext_px) if r == 1 else (l[j] < ext_px)
                    if flip:
                        outcome = -1
                        res_bars[m] = j - i
                        break
                    if newx:
                        outcome = 1
                        res_bars[m] = j - i
                        break
                res[m] = outcome
                m += 1
            armed = False
            count += 1
        if z[i] * r >= reset_th:
            armed = True
        if r == 1 and h[i] > ext_px:
            ext_px = h[i]
            ext_i = i
        if r == -1 and l[i] < ext_px:
            ext_px = l[i]
            ext_i = i
        if z[i] * r > peak_z:
            peak_z = z[i] * r
    return ev_t[:m], ev_d[:m], feat[:m], res[:m], res_bars[:m]


FEATS = ["pendiente", "flujo", "impulso_zmax", "edad_regimen", "velas_desde_extremo", "velocidad_retroceso",
         "z_cierre", "n_test_previos", "cuerpo_vela", "retroceso_total_atr", "pendiente_prev", "rango_vela"]


def collect(part="is", reset_th=1.0, touch_th=0.0, tfs=None, kinds=None):
    st = study.Study(part=part, tfs=tfs, kinds=kinds)
    rows = []
    for s, tf, df, ind, A, truth, valid in st.prepared():
        o = df["open"].to_numpy(float)
        t, d, f, r, rb = basis_events(A["regime"], A["z"], A["zl"], A["zh"], A["h"], A["l"], A["c"], o,
                                      A["atr"], A["slope"], A["mf"], reset_th, touch_th)
        keep = valid[t]
        ev = pd.DataFrame(f[keep], columns=FEATS)
        ev["t"] = t[keep]
        ev["dir"] = d[keep]
        ev["res"] = r[keep]
        ev["res_bars"] = rb[keep]
        ev["leg"] = truth.leg_d[t[keep]] * d[keep]      # +1 tramo mayor a favor (pullback), -1 en contra
        ev["group"] = study.group_of(s, tf)
        ev["sym"] = s
        rows.append(ev)
    return pd.concat(rows, ignore_index=True)


def conditional_table(ev: pd.DataFrame, q=5) -> pd.DataFrame:
    """P(continuacion) por quintiles de cada rasgo (eventos resueltos)."""
    ev = ev[ev["res"] != 0]
    out = []
    for f in FEATS:
        x = ev[f]
        try:
            bins = pd.qcut(x.rank(method="first"), q, labels=False)
        except ValueError:
            continue
        g = ev.groupby(bins)
        tab = pd.DataFrame({
            "rasgo": f,
            "quintil": range(q),
            "rango": [f"{x[bins == k].min():.2f}..{x[bins == k].max():.2f}" for k in range(q)],
            "n": g.size().values,
            "p_cont": g["res"].apply(lambda s: (s == 1).mean()).values,
            "p_leg_favor": g["leg"].apply(lambda s: (s == 1).mean()).values,
        })
        out.append(tab)
    return pd.concat(out, ignore_index=True)


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "is"
    ev = collect(part)
    pd.set_option("display.width", 200)
    res = ev[ev["res"] != 0]
    print("eventos", len(ev), "resueltos", len(res), "P(cont) global", round((res["res"] == 1).mean(), 3))
    print(res.groupby("group")["res"].apply(lambda s: (s == 1).mean()).round(3))
    tab = conditional_table(ev)
    print(common.fmt(tab.set_index(["rasgo", "quintil"]), 3))
    common.save(tab.set_index(["rasgo", "quintil"]), f"02_test_base_rasgos_{part}")
