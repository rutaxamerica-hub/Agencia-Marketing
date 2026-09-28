"""Port fiel a Python del indicador "Smart Money Flow Cloud [BOSWaves]".

Reproduce la semantica de Pine v6:
- ta.ema: alpha = 2/(n+1), sembrada con la SMA de los primeros n valores validos (na antes).
- ta.atr: RMA (alpha = 1/n) del true range, sembrada con SMA.
- math.sum: suma movil, na hasta tener n valores.
- ta.alma: pesos gaussianos, offset hacia la vela mas reciente (sin lookahead).
- ta.crossover(a, b): a > b and a[1] <= b[1].

Todas las series se calculan solo con informacion disponible al cierre de cada vela.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numba import njit


# ─────────────────────────── primitivas estilo Pine ───────────────────────────
@njit(cache=True)
def ema(x, n):
    out = np.full(x.size, np.nan)
    alpha = 2.0 / (n + 1.0)
    run = 0
    acc = 0.0
    prev = np.nan
    for i in range(x.size):
        v = x[i]
        if np.isnan(prev):
            if np.isnan(v):
                run = 0
                acc = 0.0
                continue
            run += 1
            acc += v
            if run > n:
                acc -= x[i - n]
            if run >= n:
                prev = acc / n
                out[i] = prev
        else:
            if np.isnan(v):
                out[i] = prev
                continue
            prev = alpha * v + (1.0 - alpha) * prev
            out[i] = prev
    return out


@njit(cache=True)
def rma(x, n):
    out = np.full(x.size, np.nan)
    alpha = 1.0 / n
    run = 0
    acc = 0.0
    prev = np.nan
    for i in range(x.size):
        v = x[i]
        if np.isnan(prev):
            if np.isnan(v):
                run = 0
                acc = 0.0
                continue
            run += 1
            acc += v
            if run > n:
                acc -= x[i - n]
            if run >= n:
                prev = acc / n
                out[i] = prev
        else:
            if np.isnan(v):
                out[i] = prev
                continue
            prev = alpha * v + (1.0 - alpha) * prev
            out[i] = prev
    return out


@njit(cache=True)
def rolling_sum(x, n):
    out = np.full(x.size, np.nan)
    acc = 0.0
    cnt = 0
    for i in range(x.size):
        v = x[i]
        if np.isnan(v):
            acc = 0.0
            cnt = 0
            continue
        acc += v
        cnt += 1
        if cnt > n:
            acc -= x[i - n]
            cnt = n
        if cnt == n:
            out[i] = acc
    return out


@njit(cache=True)
def alma(x, n, offset, sigma):
    out = np.full(x.size, np.nan)
    m = offset * (n - 1)
    s = n / sigma
    w = np.empty(n)
    for i in range(n):
        w[i] = np.exp(-((i - m) ** 2) / (2 * s * s))
    w /= w.sum()
    for t in range(n - 1, x.size):
        acc = 0.0
        ok = True
        for i in range(n):
            v = x[t - (n - 1) + i]  # i=0 es la vela mas antigua de la ventana
            if np.isnan(v):
                ok = False
                break
            acc += v * w[i]
        if ok:
            out[t] = acc
    return out


def true_range(h, l, c):
    c1 = np.roll(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - c1), np.abs(l - c1)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h, l, c, n):
    return rma(true_range(h, l, c), n)


def crossover(a, b):
    a1 = np.roll(a, 1)
    b1 = np.roll(b, 1)
    out = (a > b) & (a1 <= b1)
    out[0] = False
    return out


def crossunder(a, b):
    a1 = np.roll(a, 1)
    b1 = np.roll(b, 1)
    out = (a < b) & (a1 >= b1)
    out[0] = False
    return out


def shift(x, k=1, fill=np.nan):
    out = np.empty_like(x, dtype=float)
    if k > 0:
        out[:k] = fill
        out[k:] = x[:-k]
    elif k == 0:
        out[:] = x
    return out


# ─────────────────────────── indicador original ───────────────────────────
@dataclass
class Params:
    len: int = 34
    basis_type: str = "EMA"
    alma_offset: float = 0.85
    alma_sigma: float = 6.0
    basis_smooth: int = 3
    mf_len: int = 24
    mf_smooth: int = 5
    mf_power: float = 1.2
    atr_len: int = 14
    min_mult: float = 0.9
    max_mult: float = 2.2
    dot_cooldown: int = 12


def _basis(x, p: Params):
    raw = alma(x, p.len, p.alma_offset, p.alma_sigma) if p.basis_type == "ALMA" else ema(x, p.len)
    return ema(raw, p.basis_smooth) if p.basis_smooth > 1 else raw


@njit(cache=True)
def _regime(long_c, short_c, close, basis):
    n = close.size
    last = np.zeros(n, dtype=np.int64)
    sw_up = np.zeros(n, dtype=np.bool_)
    sw_dn = np.zeros(n, dtype=np.bool_)
    prev = 0
    for i in range(n):
        if i == 0:
            # en Pine "close >= na" es false, asi que con la base aun sin calcular arranca en -1
            prev_ls = 1 if (not np.isnan(basis[i]) and close[i] >= basis[i]) else -1
            prev_ls2 = 0
        else:
            prev_ls = prev
            prev_ls2 = prev
        cur = 1 if long_c[i] else (-1 if short_c[i] else prev_ls)
        last[i] = cur
        sw_up[i] = cur == 1 and prev_ls2 == -1
        sw_dn[i] = cur == -1 and prev_ls2 == 1
        prev = cur
    return last, sw_up, sw_dn


@njit(cache=True)
def _dots(cond, cooldown):
    out = np.zeros(cond.size, dtype=np.bool_)
    last = -1
    for i in range(cond.size):
        if cond[i] and (cooldown == 0 or last < 0 or (i - last) >= cooldown):
            out[i] = True
            last = i
    return out


def original(df: pd.DataFrame, p: Params | None = None) -> pd.DataFrame:
    """Calcula todas las series del indicador original. Devuelve un DataFrame alineado con df."""
    p = p or Params()
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)

    rng = h - l
    clv = np.where(rng == 0, 0.0, ((c - l) - (h - c)) / np.where(rng == 0, 1.0, rng))
    raw = clv * v
    num = rolling_sum(raw, p.mf_len)
    den = rolling_sum(np.abs(raw), p.mf_len)
    mf = np.where(den == 0.0, 0.0, num / np.where(den == 0.0, 1.0, den))
    mf = np.where(np.isnan(den), np.nan, mf)
    mf_sm = ema(mf, p.mf_smooth) if p.mf_smooth > 1 else mf
    strength = np.clip(np.abs(mf_sm) ** p.mf_power, 0.0, 1.0)
    mult = p.min_mult + (p.max_mult - p.min_mult) * strength

    b_o = _basis(o, p)
    b_c = _basis(c, p)
    a = atr(h, l, c, p.atr_len)
    upper = b_c + a * mult
    lower = b_c - a * mult

    long_c = crossover(c, upper)
    short_c = crossunder(c, lower)
    # los cruces con na son falsos en Pine
    long_c &= ~np.isnan(upper) & ~np.isnan(shift(upper))
    short_c &= ~np.isnan(lower) & ~np.isnan(shift(lower))
    last, sw_up, sw_dn = _regime(long_c, short_c, c, b_c)

    bull_dot = _dots((last == 1) & (l < b_c), p.dot_cooldown)
    bear_dot = _dots((last == -1) & (h > b_c), p.dot_cooldown)

    out = pd.DataFrame(index=df.index)
    out["bO"] = b_o
    out["bC"] = b_c
    out["atr"] = a
    out["clv"] = clv
    out["mf"] = mf
    out["mfSm"] = mf_sm
    out["strength"] = strength
    out["mult"] = mult
    out["upper"] = upper
    out["lower"] = lower
    out["longCond"] = long_c
    out["shortCond"] = short_c
    out["regime"] = last
    out["buy"] = sw_up
    out["sell"] = sw_dn
    out["bullDot"] = bull_dot
    out["bearDot"] = bear_dot
    # oscilador implicito: distancia del precio a la base en ATR (el "gauge" es tanh de esto)
    out["z"] = (c - b_c) / a
    out["slope"] = (b_c - shift(b_c)) / a
    out["cloud"] = (b_c - b_o) / a
    return out
