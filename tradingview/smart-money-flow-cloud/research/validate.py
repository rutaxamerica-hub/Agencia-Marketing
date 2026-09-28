"""Validacion del sistema congelado (decidido solo con in-sample) frente al original.

- Ablacion: original -> banda fija -> + compresion -> + continuacion -> + stop en banda.
- Metricas de trading por grupo (por operacion agregadas y cartera equiponderada por grupo).
- Resultados por ano.
Uso: python validate.py [is|oos|all] [cost_mult]
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import backtest as bt
import common
import study
import study_strategy as ss
import system

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

FINAL = system.Cfg(adaptive=False, fixed_mult=1.2, squeeze=True, squeeze_th=1.0, atr_long=100,
                   e_switch=True, e_cont=True, exit_flip=True, stop_mode="band")

LADDER = {
    "A original (SAR, banda adaptativa)": system.Cfg(),
    "B banda fija 1.2": system.Cfg(adaptive=False, fixed_mult=1.2),
    "C + filtro compresion": system.Cfg(adaptive=False, fixed_mult=1.2, squeeze=True, squeeze_th=1.0),
    "D + continuacion": system.Cfg(adaptive=False, fixed_mult=1.2, squeeze=True, squeeze_th=1.0, e_cont=True),
    "E FINAL (+ stop en banda)": FINAL,
    "E' FINAL solo largos": FINAL.but(shorts=False),
}


def portfolio(R: ss.Runner, cfg: system.Cfg, part: str, cost_mult=1.0, risk_frac=0.0) -> dict:
    """Cartera equiponderada por grupo con rebalanceo diario de las curvas de cada dataset."""
    curves = {}
    for s, tf in R.sets:
        df = R.df(s, tf)
        w = ss.window(df.index, s, tf, part)
        if w is None or w[1] - w[0] < 500:
            continue
        base = bt.costs_for(s)
        tr, eq, _ = system.backtest(df, cfg, bt.Costs(base.comm * cost_mult, base.slip * cost_mult),
                                    start=w[0], end=w[1], risk_frac=risk_frac)
        e = eq.iloc[w[0]:w[1]].dropna()
        d = e.resample("1D").last().dropna()
        curves.setdefault(study.group_of(s, tf), []).append(d.pct_change().fillna(0.0))
    out = {}
    for g, lst in curves.items():
        # promedio solo sobre los activos que existen en cada fecha (skipna)
        rets = pd.concat(lst, axis=1, sort=True).mean(axis=1).fillna(0.0)
        eq = (1 + rets).cumprod()
        years = (eq.index[-1] - eq.index[0]).days / 365.25
        dd = (eq / eq.cummax() - 1).min()
        per_year = 365 if g.startswith("cripto") else 252
        sharpe = rets.mean() / rets.std() * np.sqrt(per_year) if rets.std() > 0 else np.nan
        yearly = eq.resample("YE").last().pct_change()
        yearly.iloc[0] = eq.resample("YE").last().iloc[0] - 1
        out[g] = {"cagr": eq.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan, "max_dd": dd,
                  "sharpe": sharpe, "total": eq.iloc[-1] - 1, "yearly": yearly}
    return out


def buy_hold(R: ss.Runner, part: str) -> dict:
    curves = {}
    for s, tf in R.sets:
        df = R.df(s, tf)
        w = ss.window(df.index, s, tf, part)
        if w is None or w[1] - w[0] < 500:
            continue
        c = df["close"].iloc[w[0]:w[1]].resample("1D").last().dropna()
        curves.setdefault(study.group_of(s, tf), []).append(c.pct_change().fillna(0.0))
    out = {}
    for g, lst in curves.items():
        rets = pd.concat(lst, axis=1, sort=True).mean(axis=1).fillna(0.0)
        eq = (1 + rets).cumprod()
        years = (eq.index[-1] - eq.index[0]).days / 365.25
        per_year = 365 if g.startswith("cripto") else 252
        out[g] = {"cagr": eq.iloc[-1] ** (1 / years) - 1, "max_dd": (eq / eq.cummax() - 1).min(),
                  "sharpe": rets.mean() / rets.std() * np.sqrt(per_year), "total": eq.iloc[-1] - 1}
    return out


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "oos"
    cost_mult = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    R = ss.Runner(part)
    TT, PP = [], []
    for k, cfg in LADDER.items():
        T, P = R.run(cfg, k, cost_mult=cost_mult)
        TT.append(T)
        PP.append(P)
    T = pd.concat(TT)
    P = pd.concat(PP)
    g = ss.pooled(T, P, by_group=True)
    g["tot_atr"] = g["exp_atr"] * g["trades"]
    tag = f"{part}" + (f"_costesx{cost_mult:g}" if cost_mult != 1.0 else "")
    common.save(g, f"09_validacion_escalera_{tag}")
    for col in ["trades", "win", "pf_atr", "exp_atr", "tot_atr", "avg_win_pct", "avg_loss_pct", "bars",
                "ret_med", "dd_med", "pct_sets_pos"]:
        print(f"== {col}")
        print(common.fmt(g[col].unstack("group"), 3))

    rows = []
    yearly = []
    for k, cfg in LADDER.items():
        pf = portfolio(R, cfg, part, cost_mult)
        for grp, m in pf.items():
            rows.append({"cfg": k, "group": grp, "cagr": m["cagr"], "max_dd": m["max_dd"], "sharpe": m["sharpe"],
                         "total": m["total"]})
            y = m["yearly"].rename(lambda t: t.year)
            yearly.append(pd.DataFrame({"cfg": k, "group": grp, "year": y.index, "ret": y.values}))
    for grp, m in buy_hold(R, part).items():
        rows.append({"cfg": "Z comprar y mantener", "group": grp, **m})
    port = pd.DataFrame(rows).set_index(["cfg", "group"])
    print("== cartera equiponderada por grupo")
    print(common.fmt(port.unstack("group"), 3))
    common.save(port, f"09_validacion_cartera_{tag}")
    Y = pd.concat(yearly).pivot_table(index=["group", "year"], columns="cfg", values="ret")
    print(common.fmt(Y, 3))
    common.save(Y, f"09_validacion_por_ano_{tag}")
