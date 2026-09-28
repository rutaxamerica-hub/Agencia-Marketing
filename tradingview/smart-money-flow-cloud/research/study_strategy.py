"""Estudio a nivel de operaciones (con costes): combinaciones de entradas y salidas.

Agregacion: las metricas por operacion se agregan sobre todos los datasets del grupo; ademas se da la
mediana por dataset del retorno total y del drawdown, y el % de datasets rentables.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import backtest as bt
import common
import data
import study
import system


def window(index, symbol, tf, part):
    m = common.split_mask(index, symbol, tf, part)
    idx = np.flatnonzero(m)
    if idx.size == 0:
        return None
    return int(idx[0]), int(idx[-1]) + 1


class Runner:
    def __init__(self, part="is", tfs=None, kinds=None, symbols=None):
        self.part = part
        self.sets = [(s, tf) for s, tf in common.datasets(tfs, kinds) if not symbols or s in symbols]
        self._df = {}

    def df(self, s, tf):
        if (s, tf) not in self._df:
            self._df[(s, tf)] = data.load(s, tf)
        return self._df[(s, tf)]

    def run(self, cfg: system.Cfg, label: str, cost_mult=1.0):
        trades, per = [], []
        for s, tf in self.sets:
            df = self.df(s, tf)
            w = window(df.index, s, tf, self.part)
            if w is None or w[1] - w[0] < 500:
                continue
            base = bt.costs_for(s)
            costs = bt.Costs(base.comm * cost_mult, base.slip * cost_mult)
            tr, eq, sig = system.backtest(df, cfg, costs, start=w[0], end=w[1])
            m = bt.metrics(tr, eq.iloc[w[0]:w[1]])
            m.update({"sym": s, "tf": tf, "group": study.group_of(s, tf), "cfg": label})
            per.append(m)
            if len(tr):
                a = sig["A"]["atr"]
                sig_i = np.maximum(tr["entry_i"].to_numpy() - 1, 0)
                tr["ret_atr"] = tr["ret"] * tr["entry_px"] / a[sig_i]
                tr["group"] = study.group_of(s, tf)
                tr["sym"] = s
                tr["cfg"] = label
                trades.append(tr)
        T = pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()
        P = pd.DataFrame(per)
        return T, P


def pooled(T: pd.DataFrame, P: pd.DataFrame, by_group=False) -> pd.DataFrame:
    keys = ["cfg", "group"] if by_group else ["cfg"]
    rows = []
    for key, t in T.groupby(keys, sort=False):
        key = key if isinstance(key, tuple) else (key,)
        p = P
        for k, v in zip(keys, key):
            p = p[p[k] == v]
        w = t[t["ret"] > 0]
        lo = t[t["ret"] <= 0]
        r = dict(zip(keys, key))
        r.update({
            "trades": len(t),
            "win": len(w) / len(t),
            "pf_atr": w["ret_atr"].sum() / -lo["ret_atr"].sum() if lo["ret_atr"].sum() < 0 else np.inf,
            "exp_atr": t["ret_atr"].mean(),
            "exp_R": t["R"].replace([np.inf, -np.inf], np.nan).mean(),
            "exp_pct": 100 * t["ret"].mean(),
            "avg_win_pct": 100 * w["ret"].mean(),
            "avg_loss_pct": 100 * lo["ret"].mean(),
            "bars": t["bars"].mean(),
            "ret_med": p["return"].median(),
            "dd_med": p["max_dd"].median(),
            "pct_sets_pos": (p["return"] > 0).mean(),
        })
        rows.append(r)
    return pd.DataFrame(rows).set_index(keys)
