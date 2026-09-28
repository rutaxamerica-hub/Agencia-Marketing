"""Familias de senales candidatas construidas SOLO con informacion disponible al cierre de cada vela.

Notacion (todas en unidades de ATR):
  z   = (close - base) / ATR        distancia del cierre a la base
  zl  = (low   - base) / ATR        distancia del minimo a la base
  zh  = (high  - base) / ATR
  slope = (base - base[1]) / ATR    pendiente de la base (en 24/7 es identica a la "nube")
  regime: +1/-1 regimen con histeresis del indicador original (cruce de banda superior / inferior)
"""
from __future__ import annotations

import numpy as np
from numba import njit

import smf

# tipos de confirmacion para el final de un pullback
CONF_TOUCH = 0      # entra en la vela del toque (sin confirmacion)
CONF_UPBAR = 1      # z sube respecto a la vela anterior (confirmacion minima)
CONF_HIGH1 = 2      # cierre por encima del maximo de la vela anterior
CONF_BASIS = 3      # cierre de nuevo por encima de la base
CONF_HIGH2 = 4      # cierre por encima del maximo de las dos velas anteriores
CONF_NAMES = {0: "toque", 1: "z sube", 2: "cierre>max[1]", 3: "cierre>base", 4: "cierre>max[1,2]"}


@njit(cache=True)
def pullback_signals(regime, z, zl, zh, c, h, l, slope, mf, touch_th, reset_th, conf, max_bars,
                     need_slope, need_mf):
    """Senales de final de pullback a favor del regimen.

    Episodio largo: en regimen alcista, se "arma" cuando zl <= touch_th (el minimo entra en la zona
    de valor alrededor de la base). Dispara con la confirmacion elegida dentro de max_bars velas.
    Un episodio produce como mucho una senal; se rearma solo cuando z >= reset_th (nueva extension)
    o al empezar un regimen nuevo. Simetrico para cortos.
    """
    n = z.size
    out_l = np.zeros(n, dtype=np.bool_)
    out_s = np.zeros(n, dtype=np.bool_)
    arm_l = False
    arm_s = False
    used_l = False
    used_s = False
    t_l = -1
    t_s = -1
    for i in range(2, n):
        if np.isnan(z[i]) or np.isnan(z[i - 1]):
            continue
        if regime[i] != regime[i - 1]:
            arm_l = False
            arm_s = False
            used_l = False
            used_s = False
        # ---- largos
        if regime[i] == 1:
            if z[i] >= reset_th:
                used_l = False
                arm_l = False
            if not arm_l and not used_l and zl[i] <= touch_th:
                arm_l = True
                t_l = i
            if arm_l:
                if i - t_l > max_bars:
                    arm_l = False
                    used_l = True
                else:
                    ok = False
                    if conf == 0:
                        ok = i == t_l
                    elif conf == 1:
                        ok = z[i] > z[i - 1]
                    elif conf == 2:
                        ok = c[i] > h[i - 1]
                    elif conf == 3:
                        ok = z[i] > 0.0 and (z[i - 1] <= 0.0 or i == t_l)
                    elif conf == 4:
                        ok = c[i] > max(h[i - 1], h[i - 2])
                    if ok and need_slope and slope[i] <= 0.0:
                        ok = False
                    if ok and need_mf and mf[i] <= 0.0:
                        ok = False
                    if ok:
                        out_l[i] = True
                        arm_l = False
                        used_l = True
        # ---- cortos
        if regime[i] == -1:
            if z[i] <= -reset_th:
                used_s = False
                arm_s = False
            if not arm_s and not used_s and zh[i] >= -touch_th:
                arm_s = True
                t_s = i
            if arm_s:
                if i - t_s > max_bars:
                    arm_s = False
                    used_s = True
                else:
                    ok = False
                    if conf == 0:
                        ok = i == t_s
                    elif conf == 1:
                        ok = z[i] < z[i - 1]
                    elif conf == 2:
                        ok = c[i] < l[i - 1]
                    elif conf == 3:
                        ok = z[i] < 0.0 and (z[i - 1] >= 0.0 or i == t_s)
                    elif conf == 4:
                        ok = c[i] < min(l[i - 1], l[i - 2])
                    if ok and need_slope and slope[i] >= 0.0:
                        ok = False
                    if ok and need_mf and mf[i] >= 0.0:
                        ok = False
                    if ok:
                        out_s[i] = True
                        arm_s = False
                        used_s = True
    return out_l, out_s


@njit(cache=True)
def first_per_regime(ev, regime, direction):
    """Conserva solo el primer evento dentro de cada tramo de regimen contrario (regime == -direction)."""
    out = np.zeros(ev.size, dtype=np.bool_)
    done = False
    for i in range(ev.size):
        if i > 0 and regime[i] != regime[i - 1]:
            done = False
        if ev[i] and regime[i] == -direction and not done:
            out[i] = True
            done = True
    return out


@njit(cache=True)
def exhaustion(z, c, h, l, stretch, lookback):
    """Vela de giro tras estiramiento: el minimo de z en las ultimas `lookback` velas fue <= -stretch
    y el cierre supera el maximo de la vela anterior (simetrico para cortos)."""
    n = z.size
    out_l = np.zeros(n, dtype=np.bool_)
    out_s = np.zeros(n, dtype=np.bool_)
    for i in range(lookback + 1, n):
        mn = 1e9
        mx = -1e9
        for k in range(i - lookback, i + 1):
            if z[k] < mn:
                mn = z[k]
            if z[k] > mx:
                mx = z[k]
        if mn <= -stretch and c[i] > h[i - 1]:
            out_l[i] = True
        if mx >= stretch and c[i] < l[i - 1]:
            out_s[i] = True
    return out_l, out_s


def base_arrays(df, ind):
    c = df["close"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    bc = ind["bC"].to_numpy(float)
    a = ind["atr"].to_numpy(float)
    return dict(
        c=c, h=h, l=l, bc=bc, atr=a,
        z=(c - bc) / a, zl=(l - bc) / a, zh=(h - bc) / a,
        slope=ind["slope"].to_numpy(float),
        mf=ind["mfSm"].to_numpy(float),
        regime=ind["regime"].to_numpy(np.int64),
        upper=ind["upper"].to_numpy(float), lower=ind["lower"].to_numpy(float),
    )


def reversal_family(A):
    """Senales de reversion (a contra-regimen). Devuelve dict nombre -> (long_mask, short_mask)."""
    z, reg, slope, mf = A["z"], A["regime"], A["slope"], A["mf"]
    zero = np.zeros_like(z)
    out = {}
    # original: cruce de banda que cambia el regimen
    up = smf.crossover(A["c"], A["upper"]) & (np.roll(reg, 1) == -1)
    dn = smf.crossunder(A["c"], A["lower"]) & (np.roll(reg, 1) == 1)
    out["R0 banda (original)"] = (up, dn)
    # recuperacion de la base: cierre cruza la base en contra del regimen (primer cruce del regimen)
    cu = smf.crossover(z, zero)
    cd = smf.crossunder(z, zero)
    out["R1 cruce base (1o)"] = (first_per_regime(cu, reg, 1), first_per_regime(cd, reg, -1))
    # giro de pendiente de la base (primer giro del regimen)
    su = smf.crossover(slope, zero)
    sd = smf.crossunder(slope, zero)
    out["R2 giro pendiente (1o)"] = (first_per_regime(su, reg, 1), first_per_regime(sd, reg, -1))
    # cruce de base con pendiente ya girada
    out["R3 base+pendiente"] = (first_per_regime(cu & (slope > 0) | su & (z > 0), reg, 1),
                                first_per_regime(cd & (slope < 0) | sd & (z < 0), reg, -1))
    # flujo: cambio de signo del money flow suavizado
    mu = smf.crossover(mf, zero)
    md = smf.crossunder(mf, zero)
    out["R4 flujo cambia signo (1o)"] = (first_per_regime(mu, reg, 1), first_per_regime(md, reg, -1))
    # agotamiento: vela de giro tras estiramiento >= 2 ATR (primer evento del regimen)
    el, es = exhaustion(z, A["c"], A["h"], A["l"], 2.0, 5)
    out["R5 agotamiento z<=-2 + cierre>max[1]"] = (first_per_regime(el, reg, 1), first_per_regime(es, reg, -1))
    return out


@njit(cache=True)
def continuation_signals(regime, zl, zh, c, h, l, upper, lower, kind):
    """Continuacion tras un test de base dentro del mismo regimen.
    kind 0: el cierre vuelve a cruzar la banda del regimen (re-cruce de banda superior en alcista).
    kind 1: el cierre supera el extremo del regimen previo al test (nuevo maximo en alcista)."""
    n = c.size
    out_l = np.zeros(n, dtype=np.bool_)
    out_s = np.zeros(n, dtype=np.bool_)
    tested = False
    ext = np.nan
    ext_at_test = np.nan
    for i in range(1, n):
        r = regime[i]
        if r != regime[i - 1]:
            tested = False
            ext = h[i] if r == 1 else l[i]
            continue
        if np.isnan(zl[i]) or np.isnan(upper[i - 1]):
            continue
        if r == 1:
            if not tested and zl[i] <= 0.0:
                tested = True
                ext_at_test = ext
            elif tested:
                if kind == 0 and c[i] > upper[i] and c[i - 1] <= upper[i - 1]:
                    out_l[i] = True
                    tested = False
                elif kind == 1 and c[i] > ext_at_test:
                    out_l[i] = True
                    tested = False
            if h[i] > ext:
                ext = h[i]
        else:
            if not tested and zh[i] >= 0.0:
                tested = True
                ext_at_test = ext
            elif tested:
                if kind == 0 and c[i] < lower[i] and c[i - 1] >= lower[i - 1]:
                    out_s[i] = True
                    tested = False
                elif kind == 1 and c[i] < ext_at_test:
                    out_s[i] = True
                    tested = False
            if l[i] < ext:
                ext = l[i]
    return out_l, out_s
