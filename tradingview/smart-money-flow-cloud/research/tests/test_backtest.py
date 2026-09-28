"""Pruebas de semantica del backtester (python -m pytest tests o python tests/test_backtest.py)."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import backtest as bt  # noqa: E402

NOCOST = bt.Costs(0.0, 0.0)


def frame(rows):
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
    df["volume"] = 1.0
    df.index = pd.date_range("2020-01-01", periods=len(df), freq="h", tz="UTC")
    return df


def arr(n, idx, val=True, dtype=bool):
    a = np.zeros(n, dtype=dtype) if dtype is bool else np.full(n, np.nan)
    for i in np.atleast_1d(idx):
        a[i] = val
    return a


def test_entry_next_open_and_stop():
    df = frame([(100, 101, 99, 100), (100, 102, 99, 101), (101, 101, 94, 95), (95, 96, 94, 95)])
    n = len(df)
    sig = {"ent_l": arr(n, 0), "stop_l": arr(n, 0, 96.0, float)}
    tr, eq = bt.run(df, sig, NOCOST)
    assert len(tr) == 1
    t = tr.iloc[0]
    assert t.entry_i == 1 and t.entry_px == 100      # apertura de la vela siguiente
    assert t.exit_i == 2 and t.exit_px == 96          # stop intrabarra al precio del stop
    assert t.reason == "stop"
    assert abs(t.R + 1.0) < 1e-9


def test_gap_through_stop_fills_at_open():
    df = frame([(100, 101, 99, 100), (100, 102, 99, 101), (93, 94, 90, 92), (92, 93, 91, 92)])
    n = len(df)
    tr, _ = bt.run(df, {"ent_l": arr(n, 0), "stop_l": arr(n, 0, 96.0, float)}, NOCOST)
    assert tr.iloc[0].exit_px == 93                  # gap: se ejecuta en la apertura, peor que el stop


def test_signal_exit_and_reverse():
    df = frame([(100, 101, 99, 100), (100, 102, 99, 101), (101, 104, 100, 103), (103, 104, 102, 103), (103, 103, 101, 102)])
    n = len(df)
    sig = {"ent_l": arr(n, 0), "ent_s": arr(n, 2)}
    tr, _ = bt.run(df, sig, NOCOST)
    assert tr.iloc[0].exit_i == 3 and tr.iloc[0].exit_px == 103 and tr.iloc[0].reason == "giro"
    assert tr.iloc[1].dir == -1 and tr.iloc[1].entry_px == 103
    assert tr.iloc[1].reason == "fin_ventana"


def test_partial_tp_path_rule():
    # vela 2: apertura 101, maximo 106 (a 5), minimo 97 (a 4) -> el minimo esta mas cerca: primero el stop
    df = frame([(100, 101, 99, 100), (100, 101, 99, 101), (101, 106, 97, 100), (100, 101, 99, 100)])
    n = len(df)
    sig = {"ent_l": arr(n, 0), "stop_l": arr(n, 0, 98.0, float), "tp_l": arr(n, 0, 4.0, float)}
    tr, _ = bt.run(df, sig, NOCOST, tp_frac=0.5)
    assert tr.iloc[0].reason == "stop" and tr.iloc[0].exit_px == 98
    # ahora el maximo mas cerca de la apertura: primero el objetivo parcial (104), luego el stop (98)
    df2 = frame([(100, 101, 99, 100), (100, 101, 99, 101), (101, 104.5, 97, 100), (100, 101, 99, 100)])
    tr2, _ = bt.run(df2, sig, NOCOST, tp_frac=0.5)
    t = tr2.iloc[0]
    # R: la mitad gana 4 y la otra mitad pierde 2 respecto a 100 -> (0.5*4 - 0.5*2) / 2 = 0.5 R
    assert abs(t.R - 0.5) < 1e-9, t.R


def test_costs():
    df = frame([(100, 101, 99, 100), (100, 102, 99, 101), (110, 111, 109, 110), (110, 111, 109, 110)])
    n = len(df)
    c = bt.Costs(0.001, 0.0)
    tr, eq = bt.run(df, {"ent_l": arr(n, 0), "ex_l": arr(n, 1)}, c)
    t = tr.iloc[0]
    expected = (110 - 100) / 100 - 0.001 - 0.001 * 110 / 100
    assert abs(t.ret - expected) < 1e-9, (t.ret, expected)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
