"""Utilidades compartidas: universo de datos, particion in-sample / out-of-sample, formato."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

import data

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")

# Particion temporal. Todas las decisiones de diseno se toman SOLO con el tramo in-sample.
IS_END = {"crypto": "2022-01-01", "stock_1d": "2015-01-01"}
# Las acciones en 1h (solo 2 anos disponibles) se reservan enteras para validacion.

WARMUP = 300  # velas descartadas al inicio (EMA/ATR/sumas sin estabilizar)


def kind(symbol: str, tf: str) -> str:
    if symbol.endswith("USDT"):
        return "crypto"
    return "stock_1d" if tf == "1d" else "stock_1h"


def datasets(tfs=None, kinds=None):
    out = []
    for s, tf in data.universe():
        if tfs and tf not in tfs:
            continue
        k = kind(s, tf)
        if kinds and k not in kinds:
            continue
        if os.path.exists(data._path(s, tf)):
            out.append((s, tf))
    return out


def split_mask(index: pd.DatetimeIndex, symbol: str, tf: str, part: str) -> np.ndarray:
    """part: 'is', 'oos' o 'all'. Las velas de calentamiento nunca cuentan."""
    n = len(index)
    m = np.ones(n, dtype=bool)
    m[:WARMUP] = False
    if part == "all":
        return m
    k = kind(symbol, tf)
    if k == "stock_1h":
        return m & (part == "oos")
    cut = pd.Timestamp(IS_END[k], tz="UTC")
    return m & ((index < cut) if part == "is" else (index >= cut))


def fmt(df: pd.DataFrame, digits=3) -> str:
    return df.to_string(float_format=lambda v: f"{v:.{digits}f}")


def save(df: pd.DataFrame, name: str, digits=3):
    os.makedirs(RESULTS, exist_ok=True)
    df.to_csv(os.path.join(RESULTS, name + ".csv"), float_format=f"%.{digits + 1}f")
    with open(os.path.join(RESULTS, name + ".md"), "w") as fh:
        fh.write(df.to_markdown(floatfmt=f".{digits}f") if hasattr(df, "to_markdown") else fmt(df, digits))
