"""Metricas de calidad de senal, independientes de la logica de salida.

Para cada senal (vela t, direccion d) con entrada en la apertura de t+1:
- Tramo mayor en retrospectiva (zigzag k_major*ATR): si la senal va a favor del tramo se mide
  retraso (velas desde el giro real), fraccion del movimiento ya recorrida y movimiento restante (ATR).
  Si va contra el tramo es una senal "temprana" (el giro llega pronto y con poco retroceso) o "falsa".
- Triple barrera simetrica y asimetrica, MFE/MAE a horizonte fijo, retorno a horizonte.
- Pullbacks: pivotes menores (zigzag k_minor*ATR) dentro de un tramo mayor.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

import labels


@dataclass
class EvalCfg:
    k_major: float = 5.0
    k_minor: float = 2.0
    horizon: int = 40
    tb_sym: float = 2.0         # barrera simetrica +-2 ATR
    tb_up: float = 3.0          # asimetrica: +3 ATR antes que -1.5 ATR
    tb_dn: float = 1.5
    early_bars: int = 10        # una senal contra-tramo es "temprana" si el giro llega en <= N velas
    early_adverse: float = 1.0  # ... y con un retroceso adverso <= X ATR


class Truth:
    """Verdad de campo en retrospectiva para un DataFrame de precios."""

    def __init__(self, df: pd.DataFrame, atr: np.ndarray, cfg: EvalCfg):
        self.cfg = cfg
        self.o = df["open"].to_numpy(float)
        self.h = df["high"].to_numpy(float)
        self.l = df["low"].to_numpy(float)
        self.c = df["close"].to_numpy(float)
        self.atr = atr
        n = self.c.size
        self.M_idx, self.M_typ = labels.zigzag(self.h, self.l, atr, cfg.k_major)
        self.m_idx, self.m_typ = labels.zigzag(self.h, self.l, atr, cfg.k_minor)
        self.leg_d, self.leg_s, self.leg_e = labels.leg_map(n, self.M_idx, self.M_typ)
        self.mleg_d, self.mleg_s, self.mleg_e = labels.leg_map(n, self.m_idx, self.m_typ)

    def pivot_price(self, i, typ):
        return self.h[i] if typ == 1 else self.l[i]

    def pullback_ends(self):
        """Pivotes menores que son final de pullback: minimos menores dentro de un tramo mayor alcista
        (sin ser el inicio del tramo) y maximos menores dentro de un tramo mayor bajista."""
        out = []
        major_set = set(self.M_idx.tolist())
        for i, t in zip(self.m_idx, self.m_typ):
            if i in major_set:
                continue
            d = self.leg_d[i]
            if d == 1 and t == -1:
                out.append((i, 1))
            elif d == -1 and t == 1:
                out.append((i, -1))
        return out


def signal_table(truth: Truth, idx: np.ndarray, dirs: np.ndarray) -> pd.DataFrame:
    cfg = truth.cfg
    n = truth.c.size
    keep = idx + 1 < n
    idx = idx[keep]
    dirs = dirs[keep]
    o, h, l, c, a = truth.o, truth.h, truth.l, truth.c, truth.atr
    res_s, bars_s, mfe, mae, fin = labels.triple_barrier(o, h, l, c, a, idx, dirs, cfg.tb_sym, cfg.tb_sym, cfg.horizon)
    res_a, _, _, _, _ = labels.triple_barrier(o, h, l, c, a, idx, dirs, cfg.tb_up, cfg.tb_dn, cfg.horizon)
    rows = {
        "t": idx, "dir": dirs, "entry": o[idx + 1], "atr": a[idx],
        "tb_sym": res_s, "tb_asym": res_a, "mfe": mfe, "mae": mae, "fwd": fin,
    }
    df = pd.DataFrame(rows)
    leg_d = truth.leg_d[idx]
    s = truth.leg_s[idx]
    e = truth.leg_e[idx]
    with_leg = leg_d == dirs
    against = (leg_d == -dirs) & (leg_d != 0)
    df["leg"] = np.where(leg_d == 0, "none", np.where(with_leg, "with", "against"))

    # a favor del tramo: retraso, progreso, restante
    start_px = np.where(dirs == 1, l[np.maximum(s, 0)], h[np.maximum(s, 0)])
    end_px = np.where(dirs == 1, h[np.maximum(e, 0)], l[np.maximum(e, 0)])
    span = np.abs(end_px - start_px)
    entry = df["entry"].to_numpy()
    prog = np.where(dirs == 1, entry - start_px, start_px - entry) / np.where(span == 0, np.nan, span)
    rem = np.where(dirs == 1, end_px - entry, entry - end_px) / a[idx]
    df["delay"] = np.where(with_leg, idx - s, np.nan)
    df["progress"] = np.where(with_leg, prog, np.nan)
    df["remaining"] = np.where(with_leg, rem, np.nan)
    df["leg_atr"] = np.where(with_leg, span / a[idx], np.nan)

    # contra el tramo: temprana (giro cercano y poco adverso) o falsa
    turn_px = np.where(dirs == 1, l[np.maximum(e, 0)], h[np.maximum(e, 0)])
    adverse = np.where(dirs == 1, entry - turn_px, turn_px - entry) / a[idx]
    bars_to_turn = e - idx
    early = against & (bars_to_turn <= cfg.early_bars) & (adverse <= cfg.early_adverse)
    df["class"] = np.where(with_leg, "on_trend", np.where(early, "early", np.where(against, "false", "none")))
    df["adverse_to_turn"] = np.where(against, adverse, np.nan)

    # cercania al giro local: pivote menor del tipo relevante (minimo para largos) mas cercano en el tiempo
    mdelay = np.full(idx.size, np.nan)
    mdist = np.full(idx.size, np.nan)
    lows = truth.m_idx[truth.m_typ == -1]
    highs = truth.m_idx[truth.m_typ == 1]
    for j in range(idx.size):
        arr = lows if dirs[j] == 1 else highs
        if arr.size == 0:
            continue
        k = np.searchsorted(arr, idx[j])
        best = None
        for kk in (k - 1, k):
            if 0 <= kk < arr.size and (best is None or abs(arr[kk] - idx[j]) < abs(best - idx[j])):
                best = arr[kk]
        if best is None or abs(best - idx[j]) > 30:
            continue
        mdelay[j] = idx[j] - best
        piv = l[best] if dirs[j] == 1 else h[best]
        mdist[j] = (entry[j] - piv) / a[idx[j]] if dirs[j] == 1 else (piv - entry[j]) / a[idx[j]]
    df["mdelay"] = mdelay
    df["mdist"] = mdist
    return df


def summarize(tab: pd.DataFrame, n_bars: int | None = None) -> dict:
    if len(tab) == 0:
        return {"n": 0}
    valid = tab[tab["class"] != "none"]
    out = {
        "n": len(tab),
        "per_1000": (1000.0 * len(tab) / n_bars) if n_bars else np.nan,
        "tb_sym_win": (tab["tb_sym"] == 1).mean(),
        "tb_sym_loss": (tab["tb_sym"] == -1).mean(),
        "tb_asym_win": (tab["tb_asym"] == 1).mean(),
        "mfe_med": tab["mfe"].median(),
        "mae_med": tab["mae"].median(),
        "fwd_mean": tab["fwd"].mean(),
        "on_trend": (valid["class"] == "on_trend").mean() if len(valid) else np.nan,
        "early": (valid["class"] == "early").mean() if len(valid) else np.nan,
        "false": (valid["class"] == "false").mean() if len(valid) else np.nan,
        "delay_med": valid["delay"].median(),
        "progress_med": valid["progress"].median(),
        "remaining_med": valid["remaining"].median(),
        "mdelay_med": tab["mdelay"].median(),
        "mdist_med": tab["mdist"].median(),
        "edge": (tab["tb_sym"] == 1).mean() - (tab["tb_sym"] == -1).mean(),
    }
    return out


def reversal_records(truth: Truth, idx: np.ndarray, dirs: np.ndarray, valid=None) -> pd.DataFrame:
    """Una fila por giro mayor real: si hubo senal en la nueva direccion antes de que acabara el tramo,
    cuantas velas tardo y que fraccion del nuevo tramo ya se habia recorrido al entrar."""
    h, l = truth.h, truth.l
    M_idx, M_typ = truth.M_idx, truth.M_typ
    order = np.argsort(idx, kind="stable")
    idx = idx[order]
    dirs = dirs[order]
    rows = []
    for j in range(M_idx.size - 1):
        p = M_idx[j]
        q = M_idx[j + 1]
        if valid is not None and not (valid[p] and valid[q]):
            continue
        d = 1 if M_typ[j] == -1 else -1
        lo = np.searchsorted(idx, p, side="left")
        hi = np.searchsorted(idx, q, side="left")
        t = -1
        for k in range(lo, hi):
            if dirs[k] == d:
                t = idx[k]
                break
        if t < 0 or t + 1 >= truth.o.size:
            rows.append((False, np.nan, np.nan))
            continue
        entry = truth.o[t + 1]
        sp = l[p] if d == 1 else h[p]
        ep = h[q] if d == 1 else l[q]
        rows.append((True, float(t - p), (entry - sp) / (ep - sp) if ep != sp else np.nan))
    return pd.DataFrame(rows, columns=["detected", "delay", "progress"])


def summarize_reversals(rec: pd.DataFrame) -> dict:
    if len(rec) == 0:
        return {}
    det = rec[rec["detected"]]
    return {
        "turns": len(rec),
        "rev_detected": rec["detected"].mean(),
        "rev_delay_med": det["delay"].median(),
        "rev_progress_med": det["progress"].median(),
        "rev_late_or_missed": ((~rec["detected"]) | (rec["progress"] > 0.5)).mean(),
    }


def pullback_ends_array(truth: Truth, valid=None):
    ends = truth.pullback_ends()
    if valid is not None:
        ends = [(i, d) for i, d in ends if valid[i]]
    return ends


def pullback_records(truth: Truth, idx: np.ndarray, dirs: np.ndarray, valid=None, window: int = 8,
                     max_run: float = 1.5) -> pd.DataFrame:
    """Una fila por final de pullback real: acierto si hubo senal a favor del tramo mayor en
    [pivote, pivote+window] antes de que el cierre se alejara mas de max_run ATR del pivote."""
    ends = pullback_ends_array(truth, valid)
    by_d = {}
    for t, d in zip(idx, dirs):
        by_d.setdefault(int(d), []).append(int(t))
    for d in by_d:
        by_d[d] = np.array(sorted(by_d[d]))
    hits = []
    for i, d in ends:
        arr = by_d.get(d)
        ok = False
        if arr is not None and arr.size:
            lo = np.searchsorted(arr, i, side="left")
            hi = np.searchsorted(arr, i + window, side="right")
            piv = truth.l[i] if d == 1 else truth.h[i]
            for k in range(lo, hi):
                t = arr[k]
                run = (truth.c[t] - piv) / truth.atr[i] if d == 1 else (piv - truth.c[t]) / truth.atr[i]
                if run <= max_run:
                    ok = True
                    break
        hits.append(ok)
    return pd.DataFrame({"hit": hits})


def pb_window_flag(truth: Truth, idx: np.ndarray, dirs: np.ndarray, window: int = 8) -> np.ndarray:
    """True si la senal cae en [final de pullback real, +window] con la misma direccion."""
    ends = truth.pullback_ends()
    by_d = {1: np.array(sorted([i for i, d in ends if d == 1]), dtype=np.int64),
            -1: np.array(sorted([i for i, d in ends if d == -1]), dtype=np.int64)}
    out = np.zeros(idx.size, dtype=bool)
    for j, (t, d) in enumerate(zip(idx, dirs)):
        arr = by_d[int(d)]
        if arr.size == 0:
            continue
        k = np.searchsorted(arr, t, side="right") - 1
        out[j] = k >= 0 and t - arr[k] <= window
    return out
