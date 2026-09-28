"""Transliteracion literal (barra a barra) de la logica de pine/02_smf_cloud_estrategia.pine.

Sirve para verificar que el Pine produce las mismas senales que research/system.py: se generan las
ordenes siguiendo el codigo Pine linea a linea y se comparan las operaciones resultantes.
Uso: python pine_mirror.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import backtest as bt
import data
import smf
import system
import validate


def pine_signals(df: pd.DataFrame, band_mult=1.2, sq_th=1.0, atr_long_len=100, use_break=True, use_cont=True,
                 longs=True, shorts=True, stop_mode="band"):
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    n = c.size
    basis = smf.ema(smf.ema(c, 34), 3)
    atr = smf.atr(h, l, c, 14)
    atr_long = smf.atr(h, l, c, atr_long_len)
    upper = basis + atr * band_mult
    lower = basis - atr * band_mult

    go_l = np.zeros(n, bool)
    go_s = np.zeros(n, bool)
    x_l = np.zeros(n, bool)
    x_s = np.zeros(n, bool)
    new_stop_l = np.full(n, np.nan)
    new_stop_s = np.full(n, np.nan)

    regime = -1
    tested = False
    for i in range(n):
        # ta.crossover / ta.crossunder (false si hay na)
        long_cond = i > 0 and c[i] > upper[i] and c[i - 1] <= upper[i - 1]
        short_cond = i > 0 and c[i] < lower[i] and c[i - 1] >= lower[i - 1]
        prev_regime = regime
        regime = 1 if long_cond else (-1 if short_cond else regime)
        switch_up = regime == 1 and prev_regime == -1
        switch_dn = regime == -1 and prev_regime == 1
        ratio = atr[i] / atr_long[i]
        compressed = bool(ratio < sq_th) if not np.isnan(ratio) else False

        cont_up = False
        cont_dn = False
        if regime != prev_regime:
            tested = False
        elif not np.isnan(basis[i]) and i > 0 and not np.isnan(upper[i - 1]):
            if regime == 1:
                if not tested and l[i] <= basis[i]:
                    tested = True
                elif tested and long_cond:
                    cont_up = True
                    tested = False
            else:
                if not tested and h[i] >= basis[i]:
                    tested = True
                elif tested and short_cond:
                    cont_dn = True
                    tested = False

        go_l[i] = longs and compressed and ((use_break and switch_up) or (use_cont and cont_up))
        go_s[i] = shorts and compressed and ((use_break and switch_dn) or (use_cont and cont_dn))
        x_l[i] = short_cond
        x_s[i] = long_cond
        if stop_mode == "band":
            new_stop_l[i] = lower[i]
            new_stop_s[i] = upper[i]
    return {"ent_l": go_l, "ent_s": go_s, "ex_l": x_l, "ex_s": x_s, "stop_l": new_stop_l, "stop_s": new_stop_s}


def compare(symbol, tf, cfg=validate.FINAL, **kw):
    df = data.load(symbol, tf)
    costs = bt.costs_for(symbol)
    t_sys, _, _ = system.backtest(df, cfg, costs)
    sig = pine_signals(df, **kw)
    t_pine, _ = bt.run(df, sig, costs)
    cols = ["entry_i", "exit_i", "dir", "entry_px", "exit_px", "reason"]
    same = len(t_sys) == len(t_pine) and (t_sys[cols].reset_index(drop=True) == t_pine[cols].reset_index(drop=True)).all().all()
    return same, len(t_sys), len(t_pine)


if __name__ == "__main__":
    cases = [("BTCUSDT", "4h", {}), ("ETHUSDT", "1h", {}), ("SPY", "1d", {}), ("AAPL", "1h", {}),
             ("SOLUSDT", "1d", {}),
             ("SPY", "1d", {"shorts": False}), ("BTCUSDT", "4h", {"sq_th": 1.15}),
             ("QQQ", "1d", {"use_cont": False})]
    for sym, tf, kw in cases:
        cfg = validate.FINAL
        if kw.get("shorts") is False:
            cfg = cfg.but(shorts=False)
        if "sq_th" in kw:
            cfg = cfg.but(squeeze_th=kw["sq_th"])
        if kw.get("use_cont") is False:
            cfg = cfg.but(e_cont=False)
        same, a, b = compare(sym, tf, cfg, **kw)
        print(f"{sym:8s} {tf:3s} {str(kw):22s} identicas={same}  operaciones sistema={a} pine={b}")
