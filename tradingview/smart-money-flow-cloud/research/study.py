"""Motor generico de estudios de senal: recorre el universo, aplica la particion IS/OOS,
evalua cada familia de senales y agrega resultados por grupo (cripto 1h/4h/1d, acciones 1d/1h)."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common
import data
import evaluate as ev
import signals
import smf


def combine(ml, ms):
    il = np.flatnonzero(ml)
    is_ = np.flatnonzero(ms)
    idx = np.concatenate([il, is_]).astype(np.int64)
    d = np.concatenate([np.ones(il.size, np.int64), -np.ones(is_.size, np.int64)])
    o = np.argsort(idx, kind="stable")
    return idx[o], d[o]


def group_of(sym, tf):
    k = common.kind(sym, tf)
    return {"crypto": f"cripto {tf}", "stock_1d": "acciones 1d", "stock_1h": "acciones 1h"}[k]


def baselines(df, ind, A):
    n = len(df)
    every = np.zeros(n, dtype=bool)
    every[::5] = True
    reg = A["regime"]
    return {
        "BASE cada 5 velas (ambos lados)": (every, every),
        "BASE cada 5 velas a favor del regimen": (every & (reg == 1), every & (reg == -1)),
    }


class Study:
    def __init__(self, part="is", tfs=None, kinds=None, cfg=None, params=None, symbols=None):
        self.part = part
        self.cfg = cfg or ev.EvalCfg()
        self.params = params
        self.sets = [(s, tf) for s, tf in common.datasets(tfs, kinds) if not symbols or s in symbols]
        self._cache = {}

    def prepared(self):
        for s, tf in self.sets:
            key = (s, tf)
            if key not in self._cache:
                df = data.load(s, tf)
                valid = common.split_mask(df.index, s, tf, self.part)
                if valid.sum() < 500:
                    self._cache[key] = None
                    continue
                ind = smf.original(df, self.params)
                A = signals.base_arrays(df, ind)
                truth = ev.Truth(df, A["atr"], self.cfg)
                self._cache[key] = (df, ind, A, truth, valid)
            if self._cache[key] is not None:
                yield (s, tf) + self._cache[key]

    def run(self, builder, with_baselines=True):
        sig_tabs, rev_recs, pb_recs = [], [], []
        bars = {}
        for s, tf, df, ind, A, truth, valid in self.prepared():
            g = group_of(s, tf)
            bars[g] = bars.get(g, 0) + int(valid.sum())
            fam = dict(builder(df, ind, A))
            if with_baselines:
                fam.update(baselines(df, ind, A))
            for name, (ml, ms) in fam.items():
                idx, d = combine(ml & valid, ms & valid)
                tab = ev.signal_table(truth, idx, d)
                tab["pbwin"] = ev.pb_window_flag(truth, tab["t"].to_numpy(), tab["dir"].to_numpy())
                tab["sig"] = name
                tab["group"] = g
                tab["sym"] = s
                tab["year"] = df.index[tab["t"].to_numpy()].year
                sig_tabs.append(tab)
                if not name.startswith("BASE"):
                    rr = ev.reversal_records(truth, idx, d, valid)
                    rr["sig"] = name
                    rr["group"] = g
                    rev_recs.append(rr)
                    pr = ev.pullback_records(truth, idx, d, valid)
                    pr["sig"] = name
                    pr["group"] = g
                    pb_recs.append(pr)
        self.tab = pd.concat(sig_tabs, ignore_index=True)
        self.rev = pd.concat(rev_recs, ignore_index=True) if rev_recs else pd.DataFrame()
        self.pb = pd.concat(pb_recs, ignore_index=True) if pb_recs else pd.DataFrame()
        self.bars = bars
        return self

    def summary(self, by_group=False):
        keys = ["sig", "group"] if by_group else ["sig"]
        rows = []
        for key, t in self.tab.groupby(keys, sort=False):
            key = key if isinstance(key, tuple) else (key,)
            nb = self.bars[key[1]] if by_group else sum(self.bars.values())
            r = dict(zip(keys, key))
            r.update(ev.summarize(t, nb))
            r["pb_precision"] = t["pbwin"].mean()
            if len(self.rev):
                sel = self.rev["sig"] == key[0]
                if by_group:
                    sel &= self.rev["group"] == key[1]
                r.update(ev.summarize_reversals(self.rev[sel]))
                selp = self.pb["sig"] == key[0]
                if by_group:
                    selp &= self.pb["group"] == key[1]
                r["pb_recall"] = self.pb.loc[selp, "hit"].mean() if selp.any() else np.nan
            rows.append(r)
        out = pd.DataFrame(rows).set_index(keys)
        return out


COLS = ["n", "per_1000", "tb_sym_win", "tb_sym_loss", "tb_asym_win", "fwd_mean", "mfe_med", "mae_med",
        "false", "delay_med", "progress_med", "remaining_med", "pb_precision", "pb_recall",
        "rev_detected", "rev_delay_med", "rev_progress_med", "rev_late_or_missed"]
