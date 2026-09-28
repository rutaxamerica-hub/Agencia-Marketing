"""Etiquetas de evaluacion (usan informacion futura A PROPOSITO; nunca se usan para generar senales).

- zigzag(k): pivotes confirmados cuando el precio se mueve k*ATR contra el extremo vigente.
  Nivel mayor (k grande) = tramos de tendencia; sus pivotes son las "reversiones reales".
  Nivel menor (k pequeno) = oscilaciones; sus pivotes dentro de un tramo mayor son "finales de pullback".
- triple barrera: desde la entrada, +P*ATR antes que -S*ATR dentro de H velas.
- MFE / MAE en unidades de ATR.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True)
def zigzag(h, l, atr, k):
    """Devuelve (idx, tipo) de pivotes: tipo +1 = maximo, -1 = minimo. El ultimo tramo queda abierto."""
    n = h.size
    idx = np.empty(n, dtype=np.int64)
    typ = np.empty(n, dtype=np.int64)
    m = 0
    start = 0
    while start < n and np.isnan(atr[start]):
        start += 1
    if start >= n:
        return idx[:0], typ[:0]
    d = 0
    hi = h[start]
    hi_i = start
    lo = l[start]
    lo_i = start
    for i in range(start + 1, n):
        if d == 0:
            if h[i] > hi:
                hi = h[i]
                hi_i = i
            if l[i] < lo:
                lo = l[i]
                lo_i = i
            if hi - lo >= k * atr[i]:
                if hi_i > lo_i:
                    idx[m] = lo_i
                    typ[m] = -1
                    m += 1
                    d = 1
                else:
                    idx[m] = hi_i
                    typ[m] = 1
                    m += 1
                    d = -1
        elif d == 1:
            if h[i] > hi:
                hi = h[i]
                hi_i = i
            elif hi - l[i] >= k * atr[hi_i]:
                idx[m] = hi_i
                typ[m] = 1
                m += 1
                d = -1
                lo = l[i]
                lo_i = i
        else:
            if l[i] < lo:
                lo = l[i]
                lo_i = i
            elif h[i] - lo >= k * atr[lo_i]:
                idx[m] = lo_i
                typ[m] = -1
                m += 1
                d = 1
                hi = h[i]
                hi_i = i
    return idx[:m], typ[:m]


@njit(cache=True)
def leg_map(n, piv_idx, piv_typ):
    """Para cada vela: direccion del tramo (en retrospectiva), indice de inicio y de fin del tramo.
    Las velas fuera de tramos cerrados quedan con dir=0."""
    d = np.zeros(n, dtype=np.int64)
    s = np.full(n, -1, dtype=np.int64)
    e = np.full(n, -1, dtype=np.int64)
    for j in range(piv_idx.size - 1):
        a = piv_idx[j]
        b = piv_idx[j + 1]
        direction = 1 if piv_typ[j] == -1 else -1
        for t in range(a, b):
            d[t] = direction
            s[t] = a
            e[t] = b
    return d, s, e


@njit(cache=True)
def triple_barrier(o, h, l, c, atr, sig_idx, sig_dir, up_k, dn_k, horizon):
    """Entrada en la apertura de la vela siguiente a la senal. Devuelve resultado (+1/-1/0),
    velas hasta tocar, MFE y MAE (en ATR de la vela de senal) y retorno final a horizonte."""
    n = c.size
    k = sig_idx.size
    res = np.zeros(k, dtype=np.int64)
    bars = np.full(k, -1, dtype=np.int64)
    mfe = np.full(k, np.nan)
    mae = np.full(k, np.nan)
    fin = np.full(k, np.nan)
    for j in range(k):
        t = sig_idx[j]
        if t + 1 >= n or np.isnan(atr[t]):
            continue
        dr = sig_dir[j]
        a = atr[t]
        entry = o[t + 1]
        best = 0.0
        worst = 0.0
        done = False
        last = min(n - 1, t + horizon)
        for i in range(t + 1, last + 1):
            fav = (h[i] - entry) / a if dr == 1 else (entry - l[i]) / a
            adv = (entry - l[i]) / a if dr == 1 else (h[i] - entry) / a
            if fav > best:
                best = fav
            if adv > worst:
                worst = adv
            if not done:
                hit_dn = adv >= dn_k
                hit_up = fav >= up_k
                if hit_dn:  # si ambas en la misma vela se asume lo peor
                    res[j] = -1
                    bars[j] = i - t
                    done = True
                elif hit_up:
                    res[j] = 1
                    bars[j] = i - t
                    done = True
        mfe[j] = best
        mae[j] = worst
        fin[j] = ((c[last] - entry) / a) * dr
    return res, bars, mfe, mae, fin
