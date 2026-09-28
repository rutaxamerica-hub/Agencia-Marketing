"""Descarga y cache de datos OHLCV.

- Cripto: API publica de Binance (data-api.binance.vision), velas spot con volumen real.
- Acciones / ETFs / futuros: Yahoo Finance via yfinance (precios ajustados por splits/dividendos).

Los CSV se guardan en research/data/ (ignorado por git). Uso:

    python data.py            # descarga todo el universo
    python data.py BTCUSDT 4h # un simbolo/intervalo concreto
"""
from __future__ import annotations

import os
import sys
import time

import pandas as pd
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

CRYPTO = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
          "DOGEUSDT", "LINKUSDT", "LTCUSDT", "AVAXUSDT", "DOTUSDT", "TRXUSDT"]
CRYPTO_TF = ["1h", "4h", "1d"]

YAHOO_DAILY = ["SPY", "QQQ", "IWM", "DIA", "EEM", "GLD", "TLT", "XLE", "XLF", "XLK",
               "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "XOM", "JNJ",
               "GC=F", "CL=F"]
YAHOO_HOURLY = ["SPY", "QQQ", "IWM", "GLD", "AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "JPM"]

BINANCE_URL = "https://data-api.binance.vision/api/v3/klines"


def _path(symbol: str, tf: str) -> str:
    safe = symbol.replace("=", "_").replace("^", "")
    return os.path.join(DATA_DIR, f"{safe}_{tf}.csv")


def download_binance(symbol: str, tf: str, start_ms: int = 1500000000000) -> pd.DataFrame:
    rows = []
    cur = start_ms
    while True:
        for attempt in range(5):
            try:
                r = requests.get(BINANCE_URL, params={"symbol": symbol, "interval": tf,
                                                      "startTime": cur, "limit": 1000}, timeout=30)
                r.raise_for_status()
                batch = r.json()
                break
            except Exception:  # red inestable: reintento con espera exponencial
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"Binance no responde para {symbol} {tf}")
        if not batch:
            break
        rows.extend(batch)
        last_open = batch[-1][0]
        if len(batch) < 1000:
            break
        cur = last_open + 1
        time.sleep(0.05)
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close", "volume", "close_time",
                                     "qv", "n", "tb", "tq", "ig"])
    df = df[["time", "open", "high", "low", "close", "volume"]].astype(float)
    df["time"] = pd.to_datetime(df["time"].astype("int64"), unit="ms", utc=True)
    df = df.drop_duplicates("time").set_index("time").sort_index()
    # la ultima vela puede estar abierta: se descarta para trabajar solo con velas cerradas
    return df.iloc[:-1]


def download_yahoo(symbol: str, tf: str) -> pd.DataFrame:
    import yfinance as yf
    if tf == "1d":
        df = yf.download(symbol, period="max", interval="1d", progress=False, auto_adjust=True)
    elif tf == "1h":
        df = yf.download(symbol, period="730d", interval="1h", progress=False, auto_adjust=True)
    else:
        raise ValueError(tf)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]].astype(float)
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "time"
    df = df[(df["high"] > 0) & (df["low"] > 0)].dropna()
    return df.iloc[:-1]


def load(symbol: str, tf: str) -> pd.DataFrame:
    p = _path(symbol, tf)
    if not os.path.exists(p):
        fetch(symbol, tf)
    df = pd.read_csv(p, index_col="time", parse_dates=["time"])
    return df


def fetch(symbol: str, tf: str) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if symbol.endswith("USDT"):
        df = download_binance(symbol, tf)
    else:
        df = download_yahoo(symbol, tf)
    df.to_csv(_path(symbol, tf))
    print(f"{symbol:10s} {tf:3s} {len(df):7d} velas  {df.index[0]} -> {df.index[-1]}", flush=True)


def universe():
    out = [(s, tf) for s in CRYPTO for tf in CRYPTO_TF]
    out += [(s, "1d") for s in YAHOO_DAILY]
    out += [(s, "1h") for s in YAHOO_HOURLY]
    return out


if __name__ == "__main__":
    if len(sys.argv) == 3:
        fetch(sys.argv[1], sys.argv[2])
    else:
        for s, tf in universe():
            if os.path.exists(_path(s, tf)):
                continue
            try:
                fetch(s, tf)
            except Exception as exc:  # un simbolo fallido no debe detener el resto
                print(f"ERROR {s} {tf}: {exc}", flush=True)
