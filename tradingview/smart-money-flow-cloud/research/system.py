"""Constructor configurable del sistema de senales (entradas, stops, trailing, salidas).

Es la fuente de verdad de la logica que replica el Pine mejorado. Todo se calcula al cierre de cada
vela con informacion pasada; el backtester ejecuta en la apertura siguiente.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

import backtest as bt
import signals as S
import smf


@dataclass
class Cfg:
    # ---- nucleo (igual que el original salvo 'adaptive') ----
    len: int = 34
    basis_smooth: int = 3
    atr_len: int = 14
    adaptive: bool = True          # banda adaptativa por |flujo| (original) o multiplicador fijo
    fixed_mult: float = 1.2
    mf_skew: float = 0.0           # banda asimetrica: el flujo a favor acerca la banda de ese lado
    min_mult: float = 0.9
    max_mult: float = 2.2
    # ---- filtro de compresion de volatilidad ----
    squeeze: bool = False
    atr_long: int = 100
    squeeze_th: float = 1.0
    # ---- entradas ----
    e_switch: bool = True          # ruptura que cambia el regimen (original)
    e_cont: bool = False           # re-cruce de la banda del regimen tras un test de base
    e_pullback: bool = False       # final de pullback
    pb_conf: int = S.CONF_UPBAR
    pb_touch: float = 0.0
    e_early: str = ""              # "", "basis", "slope": reversion temprana a contra-regimen
    squeeze_on_pullback: bool = False
    mf_filter: bool = False        # exigir money flow a favor en las entradas
    longs: bool = True
    shorts: bool = True
    # ---- salidas ----
    exit_flip: bool = True         # salir cuando el cierre cruza la banda contraria (cambio de regimen)
    exit_basis: bool = False       # salir cuando el cierre cruza la base en contra
    exit_slope: bool = False       # salir cuando la pendiente de la base gira en contra
    stop_mode: str = "none"        # none | band | atr | struct
    stop_atr: float = 2.0
    struct_len: int = 10
    band_trail: bool = False       # stop que sigue a la banda contraria (se ejecuta intrabarra)
    basis_trail: float = np.nan    # stop = base -/+ x*ATR (solo a favor)
    chand_k: float = 0.0           # chandelier desde la entrada: extremo - k*ATR
    tp_atr: float = np.nan         # toma parcial a +x ATR desde el cierre de senal
    tp_frac: float = 0.5
    be_after_tp: bool = False
    max_bars: int = 0
    extra: dict = field(default_factory=dict)

    def but(self, **kw):
        return replace(self, **kw)


def core(df: pd.DataFrame, cfg: Cfg) -> dict:
    p = smf.Params(len=cfg.len, basis_smooth=cfg.basis_smooth, atr_len=cfg.atr_len,
                   min_mult=cfg.min_mult, max_mult=cfg.max_mult)
    ind = smf.original(df, p)
    A = S.base_arrays(df, ind)
    if not cfg.adaptive:
        sk = cfg.mf_skew * np.nan_to_num(A["mf"])
        up = A["bc"] + A["atr"] * (cfg.fixed_mult - sk)
        lo = A["bc"] - A["atr"] * (cfg.fixed_mult + sk)
        lc = smf.crossover(A["c"], up) & ~np.isnan(smf.shift(up))
        sc = smf.crossunder(A["c"], lo) & ~np.isnan(smf.shift(lo))
        reg, bu, se = smf._regime(lc, sc, A["c"], A["bc"])
        A["upper"], A["lower"], A["regime"] = up, lo, reg
        A["buy"], A["sell"] = bu, se
        A["longCond"], A["shortCond"] = lc, sc
    else:
        A["buy"], A["sell"] = ind["buy"].to_numpy(), ind["sell"].to_numpy()
        A["longCond"], A["shortCond"] = ind["longCond"].to_numpy(), ind["shortCond"].to_numpy()
    A["atr_long"] = smf.atr(A["h"], A["l"], A["c"], cfg.atr_long)
    A["atr_ratio"] = A["atr"] / A["atr_long"]
    A["bo"] = ind["bO"].to_numpy()
    A["open"] = df["open"].to_numpy(float)
    return A


def build(df: pd.DataFrame, cfg: Cfg, A: dict | None = None) -> dict:
    A = A or core(df, cfg)
    n = len(df)
    c, h, l, a = A["c"], A["h"], A["l"], A["atr"]
    reg = A["regime"]
    sq = A["atr_ratio"] < cfg.squeeze_th if cfg.squeeze else np.ones(n, dtype=bool)
    el = np.zeros(n, dtype=bool)
    es = np.zeros(n, dtype=bool)
    kind = np.zeros(n, dtype=np.int64)   # 1 ruptura, 2 continuacion, 3 pullback, 4 temprana
    if cfg.e_switch:
        el |= A["buy"] & sq
        es |= A["sell"] & sq
        kind[A["buy"] & sq] = 1
        kind[A["sell"] & sq] = 1
    if cfg.e_cont:
        cl, cs = S.continuation_signals(reg, A["zl"], A["zh"], c, h, l, A["upper"], A["lower"], 0)
        cl &= sq
        cs &= sq
        kind[(cl | cs) & (kind == 0)] = 2
        el |= cl
        es |= cs
    if cfg.e_pullback:
        pl, ps = S.pullback_signals(reg, A["z"], A["zl"], A["zh"], c, h, l, A["slope"], A["mf"],
                                    cfg.pb_touch, 1.0, cfg.pb_conf, 10, False, False)
        if cfg.squeeze_on_pullback:
            pl &= sq
            ps &= sq
        kind[(pl | ps) & (kind == 0)] = 3
        el |= pl
        es |= ps
    if cfg.e_early:
        zero = np.zeros(n)
        if cfg.e_early == "basis":
            ul, us = smf.crossover(A["z"], zero), smf.crossunder(A["z"], zero)
        else:
            ul, us = smf.crossover(A["slope"], zero), smf.crossunder(A["slope"], zero)
        ul = S.first_per_regime(ul, reg, 1)
        us = S.first_per_regime(us, reg, -1)
        kind[(ul | us) & (kind == 0)] = 4
        el |= ul
        es |= us
    if cfg.mf_filter:
        el &= A["mf"] > 0
        es &= A["mf"] < 0
    if not cfg.longs:
        el[:] = False
    if not cfg.shorts:
        es[:] = False

    # ---- salidas por senal (al cierre -> apertura siguiente) ----
    xl = np.zeros(n, dtype=bool)
    xs = np.zeros(n, dtype=bool)
    if cfg.exit_flip:
        # el cierre cruza la banda contraria (cambio de regimen, o fallo de una entrada temprana)
        xl |= A["shortCond"]
        xs |= A["longCond"]
    if cfg.exit_basis:
        xl |= smf.crossunder(c, A["bc"])
        xs |= smf.crossover(c, A["bc"])
    if cfg.exit_slope:
        zero = np.zeros(n)
        xl |= smf.crossunder(A["slope"], zero)
        xs |= smf.crossover(A["slope"], zero)

    # ---- stop inicial (calculado en la vela de senal) ----
    nan = np.full(n, np.nan)
    if cfg.stop_mode == "band":
        sl, ss = A["lower"].copy(), A["upper"].copy()
    elif cfg.stop_mode == "atr":
        sl, ss = c - cfg.stop_atr * a, c + cfg.stop_atr * a
    elif cfg.stop_mode == "struct":
        lo = pd.Series(l).rolling(cfg.struct_len, min_periods=1).min().to_numpy()
        hi = pd.Series(h).rolling(cfg.struct_len, min_periods=1).max().to_numpy()
        sl, ss = lo - 0.25 * a, hi + 0.25 * a
    else:
        sl, ss = nan.copy(), nan.copy()

    tl, ts = nan.copy(), nan.copy()
    if cfg.band_trail:
        tl, ts = A["lower"].copy(), A["upper"].copy()
    if not np.isnan(cfg.basis_trail):
        bl = A["bc"] - cfg.basis_trail * a
        bs = A["bc"] + cfg.basis_trail * a
        tl = np.where(np.isnan(tl), bl, np.fmax(tl, bl))
        ts = np.where(np.isnan(ts), bs, np.fmin(ts, bs))
    tp = cfg.tp_atr * a if not np.isnan(cfg.tp_atr) else nan
    return {"ent_l": el, "ent_s": es, "ex_l": xl, "ex_s": xs, "stop_l": sl, "stop_s": ss,
            "trail_l": tl, "trail_s": ts, "tp_l": tp, "tp_s": tp, "kind": kind, "A": A}


def backtest(df: pd.DataFrame, cfg: Cfg, costs: bt.Costs, start=0, end=None, A=None, size_frac=1.0,
             risk_frac=0.0):
    sig = build(df, cfg, A)
    trades, eq = bt.run(df, sig, costs, size_frac=size_frac, start=start, end=end,
                        tp_frac=cfg.tp_frac if not np.isnan(cfg.tp_atr) else 1.0,
                        be_after_tp=cfg.be_after_tp, max_bars=cfg.max_bars,
                        atr=sig["A"]["atr"], chand_k=cfg.chand_k, risk_frac=risk_frac)
    if len(trades):
        sk = sig["kind"]
        trades["kind"] = [int(sk[i - 1]) if i >= 1 else 0 for i in trades["entry_i"]]
    return trades, eq, sig
