"""Backtester por velas que replica la semantica de strategy() de TradingView (sin bar magnifier).

- Las senales se evaluan al cierre de la vela t; las ordenes de mercado se ejecutan en la apertura de t+1
  (process_orders_on_close = false, comportamiento por defecto de Pine).
- El stop protector se coloca con la senal y ya esta activo en la vela de entrada.
- Stop: si la apertura ya esta mas alla del stop se ejecuta en la apertura (gap); si no, al precio del stop.
- Take profit parcial (limite) opcional. Si stop y objetivo caen en la misma vela se usa la regla de
  TradingView: si el maximo esta mas cerca de la apertura que el minimo, el recorrido es
  apertura -> maximo -> minimo -> cierre; si no, apertura -> minimo -> maximo -> cierre.
- El trailing se recalcula al cierre y solo se mueve a favor; queda activo desde la vela siguiente.
- Comision y slippage como fraccion del precio por lado. Sin piramidacion; senal contraria = giro.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numba import njit

REASONS = {1: "stop", 2: "senal", 3: "tp_total", 4: "tiempo", 5: "giro", 6: "fin_ventana", 7: "trailing"}


@njit(cache=True)
def _run(o, h, l, c, ent_l, ent_s, ex_l, ex_s, stop0_l, stop0_s, trail_l, trail_s, tp_l, tp_s,
         tp_frac, be_after_tp, max_bars, comm, slip, size_frac, start, end, atr, chand_k, risk_frac):
    n = c.size
    max_tr = n // 2 + 10
    t_ent = np.full(max_tr, -1, np.int64)
    t_ex = np.full(max_tr, -1, np.int64)
    t_dir = np.zeros(max_tr, np.int64)
    t_epx = np.zeros(max_tr)
    t_xpx = np.zeros(max_tr)
    t_pnl = np.zeros(max_tr)      # beneficio neto en moneda de cuenta
    t_ret = np.zeros(max_tr)      # retorno neto sobre el capital asignado a la operacion
    t_R = np.zeros(max_tr)
    t_reason = np.zeros(max_tr, np.int64)
    t_mfe = np.zeros(max_tr)
    equity = np.full(n, np.nan)
    eq = 1.0
    pos = 0
    qty = 0.0
    q0 = 0.0
    entry_px = 0.0
    init_risk = 0.0
    stop = np.nan
    tp = np.nan
    tp_done = False
    bars_in = 0
    realized = 0.0
    cost_in = 0.0
    best = 0.0
    k = 0
    pend = 0          # orden de entrada pendiente (+1/-1) para la apertura de la vela siguiente
    pend_exit = False
    pend_stop = np.nan
    pend_tp = np.nan
    be_pending = False
    ext = np.nan
    for i in range(start, min(end, n)):
        # ---------- 1) ordenes de mercado en la apertura ----------
        if pos != 0 and (pend_exit or (pend != 0 and pend != pos)):
            px = o[i] * (1.0 - slip * pos)
            gross = (px - entry_px) * qty * pos
            fee = comm * px * qty
            realized += gross - fee
            eq_before = eq
            eq += gross - fee
            t_ex[k] = i
            t_xpx[k] = px
            t_pnl[k] = realized - cost_in
            t_ret[k] = (realized - cost_in) / (q0 * entry_px) if q0 > 0 else 0.0
            t_R[k] = (realized - cost_in) / (q0 * init_risk) if init_risk > 0 else 0.0
            t_reason[k] = 5 if (pend != 0 and pend != pos) else 2
            t_mfe[k] = best
            k += 1
            pos = 0
        pend_exit = False
        if pend != 0 and pos == 0:
            px = o[i] * (1.0 + slip * pend)
            pos = pend
            qty = size_frac * eq / px
            if risk_frac > 0 and not np.isnan(pend_stop) and abs(px - pend_stop) > 0:
                # riesgo fijo: perder risk_frac del capital si salta el stop (sin apalancamiento)
                qty = min(qty, risk_frac * eq / abs(px - pend_stop))
            q0 = qty
            entry_px = px
            fee = comm * px * qty
            eq -= fee
            cost_in = fee
            realized = 0.0
            stop = pend_stop
            tp = pend_tp
            tp_done = False
            be_pending = False
            bars_in = 0
            best = 0.0
            ext = h[i] if pos == 1 else l[i]
            init_risk = abs(px - stop) if not np.isnan(stop) else np.nan
            t_ent[k] = i
            t_dir[k] = pos
            t_epx[k] = px
            if not np.isnan(stop) and (stop - px) * pos >= 0:   # stop ya superado: sale en la apertura
                stop = px
        pend = 0
        # ---------- 2) stops / objetivos dentro de la vela ----------
        if pos != 0:
            bars_in += 1
            fav = (h[i] - entry_px) if pos == 1 else (entry_px - l[i])
            if init_risk > 0 and fav / init_risk > best:
                best = fav / init_risk
            high_first = (h[i] - o[i]) < (o[i] - l[i])
            closed = False
            # orden de eventos segun el recorrido supuesto
            for step in range(2):
                if closed:
                    break
                # step 0: extremo a favor primero si el recorrido lo indica; step 1: el otro extremo
                check_tp = (step == 0) == ((pos == 1 and high_first) or (pos == -1 and not high_first))
                if check_tp:
                    if not tp_done and not np.isnan(tp):
                        hit = (h[i] >= tp) if pos == 1 else (l[i] <= tp)
                        if hit:
                            px = max(o[i], tp) if pos == 1 else min(o[i], tp)
                            cq = qty * tp_frac
                            gross = (px - entry_px) * cq * pos
                            fee = comm * px * cq
                            realized += gross - fee
                            eq += gross - fee
                            qty -= cq
                            tp_done = True
                            be_pending = be_after_tp   # en Pine el stop se mueve al recalcular al cierre
                            if qty <= 1e-12:
                                t_ex[k] = i
                                t_xpx[k] = px
                                t_pnl[k] = realized - cost_in
                                t_ret[k] = (realized - cost_in) / (q0 * entry_px)
                                t_R[k] = (realized - cost_in) / (q0 * init_risk) if init_risk > 0 else 0.0
                                t_reason[k] = 3
                                t_mfe[k] = best
                                k += 1
                                pos = 0
                                closed = True
                else:
                    if not np.isnan(stop):
                        hit = (l[i] <= stop) if pos == 1 else (h[i] >= stop)
                        if hit:
                            px = min(o[i], stop) if pos == 1 else max(o[i], stop)
                            px = px * (1.0 - slip * pos)
                            gross = (px - entry_px) * qty * pos
                            fee = comm * px * qty
                            realized += gross - fee
                            eq += gross - fee
                            t_ex[k] = i
                            t_xpx[k] = px
                            t_pnl[k] = realized - cost_in
                            t_ret[k] = (realized - cost_in) / (q0 * entry_px)
                            t_R[k] = (realized - cost_in) / (q0 * init_risk) if init_risk > 0 else 0.0
                            moved = abs(stop - (entry_px - init_risk * pos)) > 1e-12 if init_risk > 0 else False
                            t_reason[k] = 7 if moved else 1
                            t_mfe[k] = best
                            k += 1
                            pos = 0
                            closed = True
        # ---------- 3) cierre de la vela: senales para la apertura siguiente ----------
        last_bar = i == min(end, n) - 1
        if pos != 0 and last_bar:
            px = c[i] * (1.0 - slip * pos)
            gross = (px - entry_px) * qty * pos
            fee = comm * px * qty
            realized += gross - fee
            eq += gross - fee
            t_ex[k] = i
            t_xpx[k] = px
            t_pnl[k] = realized - cost_in
            t_ret[k] = (realized - cost_in) / (q0 * entry_px)
            t_R[k] = (realized - cost_in) / (q0 * init_risk) if init_risk > 0 else 0.0
            t_reason[k] = 6
            t_mfe[k] = best
            k += 1
            pos = 0
        if pos != 0 and be_pending:
            stop = entry_px if np.isnan(stop) else (max(stop, entry_px) if pos == 1 else min(stop, entry_px))
            be_pending = False
        if pos != 0:
            # trailing (solo a favor): externo y/o chandelier desde la entrada
            tr = trail_l[i] if pos == 1 else trail_s[i]
            if chand_k > 0:
                if pos == 1:
                    ext = max(ext, h[i])
                    ch = ext - chand_k * atr[i]
                    tr = ch if np.isnan(tr) else max(tr, ch)
                else:
                    ext = min(ext, l[i])
                    ch = ext + chand_k * atr[i]
                    tr = ch if np.isnan(tr) else min(tr, ch)
            if not np.isnan(tr):
                if np.isnan(stop):
                    stop = tr
                elif pos == 1 and tr > stop:
                    stop = tr
                elif pos == -1 and tr < stop:
                    stop = tr
            mark = (c[i] - entry_px) * qty * pos
            equity[i] = eq + mark
        else:
            equity[i] = eq
        if not last_bar:
            want_l = ent_l[i]
            want_s = ent_s[i]
            if pos == 1:
                if want_s:
                    pend = -1
                elif ex_l[i] and not want_l:
                    pend_exit = True
                elif max_bars > 0 and bars_in >= max_bars and not want_l:
                    pend_exit = True
            elif pos == -1:
                if want_l:
                    pend = 1
                elif ex_s[i] and not want_s:
                    pend_exit = True
                elif max_bars > 0 and bars_in >= max_bars and not want_s:
                    pend_exit = True
            else:
                if want_l and not want_s:
                    pend = 1
                elif want_s and not want_l:
                    pend = -1
            if pend != 0:
                pend_stop = stop0_l[i] if pend == 1 else stop0_s[i]
                d = tp_l[i] if pend == 1 else tp_s[i]
                pend_tp = np.nan if np.isnan(d) else (c[i] + d if pend == 1 else c[i] - d)
    return (t_ent[:k], t_ex[:k], t_dir[:k], t_epx[:k], t_xpx[:k], t_pnl[:k], t_ret[:k], t_R[:k],
            t_reason[:k], t_mfe[:k], equity)


@dataclass
class Costs:
    comm: float = 0.0005   # por lado
    slip: float = 0.0003   # por lado


def costs_for(symbol: str) -> Costs:
    if symbol.endswith("USDT"):
        return Costs(0.0005, 0.0003)      # cripto: 0.05% comision + 0.03% slippage por lado
    return Costs(0.0001, 0.0002)          # acciones/ETF/futuros: 0.01% + 0.02% por lado


def run(df: pd.DataFrame, sig: dict, costs: Costs, size_frac=1.0, start=0, end=None, tp_frac=1.0,
        be_after_tp=False, max_bars=0, atr=None, chand_k=0.0, risk_frac=0.0):
    n = len(df)
    nan = np.full(n, np.nan)
    f = np.zeros(n, dtype=np.bool_)
    get = lambda k, d: sig.get(k, d)
    out = _run(df["open"].to_numpy(float), df["high"].to_numpy(float), df["low"].to_numpy(float),
               df["close"].to_numpy(float),
               get("ent_l", f), get("ent_s", f), get("ex_l", f), get("ex_s", f),
               get("stop_l", nan), get("stop_s", nan), get("trail_l", nan), get("trail_s", nan),
               get("tp_l", nan), get("tp_s", nan), tp_frac, be_after_tp, max_bars,
               costs.comm, costs.slip, size_frac, start, n if end is None else end,
               np.zeros(n) if atr is None else np.asarray(atr, float), float(chand_k), float(risk_frac))
    ent, ex, d, epx, xpx, pnl, ret, R, reason, mfe, equity = out
    trades = pd.DataFrame({"entry_i": ent, "exit_i": ex, "dir": d, "entry_px": epx, "exit_px": xpx,
                           "pnl": pnl, "ret": ret, "R": R, "reason": [REASONS.get(int(x), "?") for x in reason],
                           "mfe_R": mfe})
    trades["bars"] = trades["exit_i"] - trades["entry_i"]
    if len(trades):
        trades["entry_time"] = df.index[trades["entry_i"].to_numpy()]
        trades["exit_time"] = df.index[trades["exit_i"].to_numpy()]
    return trades, pd.Series(equity, index=df.index)


def metrics(trades: pd.DataFrame, equity: pd.Series) -> dict:
    eq = equity.dropna()
    if len(trades) == 0 or len(eq) == 0:
        return {"trades": 0}
    wins = trades[trades["ret"] > 0]
    losses = trades[trades["ret"] <= 0]
    gp = wins["pnl"].sum()
    gl = -losses["pnl"].sum()
    peak = eq.cummax()
    dd = (eq / peak - 1).min()
    return {
        "trades": len(trades),
        "win_rate": len(wins) / len(trades),
        "profit_factor": gp / gl if gl > 0 else np.inf,
        "return": eq.iloc[-1] / eq.iloc[0] - 1,
        "max_dd": dd,
        "expectancy_pct": trades["ret"].mean(),
        "expectancy_R": trades["R"].mean(),
        "avg_win_pct": wins["ret"].mean() if len(wins) else 0.0,
        "avg_loss_pct": losses["ret"].mean() if len(losses) else 0.0,
        "avg_bars": trades["bars"].mean(),
    }
