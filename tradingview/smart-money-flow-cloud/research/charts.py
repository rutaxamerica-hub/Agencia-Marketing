"""Figuras del informe (PNG, modo claro). Paleta validada con el script de la guia de visualizacion:
azul/rojo = alcista/bajista (par opuesto), violeta = salidas y stops, gris apagado = senal tardia.
Todos los marcadores llevan texto, asi que el color nunca es el unico codigo.
Uso: python charts.py
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import backtest as bt  # noqa: E402
import common  # noqa: E402
import data  # noqa: E402
import smf  # noqa: E402
import study_conditions as sc  # noqa: E402
import system  # noqa: E402
import validate  # noqa: E402

OUT = os.path.join(common.RESULTS, "figuras")
SURF = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BULL = "#2a78d6"
BEAR = "#e34948"
EXIT = "#4a3aa7"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6, "font.size": 9,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False,
    "font.family": "DejaVu Sans",
})


def _bars(ax, x, o, h, l, c, colors):
    ax.vlines(x, l, h, colors=colors, linewidth=0.7)
    ax.hlines(o, x - 0.35, x, colors=colors, linewidth=0.7)
    ax.hlines(c, x, x + 0.35, colors=colors, linewidth=0.7)


_STACK = {}


def _mark(ax, xs, ys, marker, color, text, dy, size=9, filled=True, label=None):
    """Marcador + texto. Si ya hay marcas en la misma zona (vela cercana y mismo lado) se apilan."""
    if len(xs) == 0:
        return
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    side = 1 if dy >= 0 else -1
    step = ax.get_ylim()  # se recalcula con los datos al final; se usa un paso relativo al rango de precio
    out_y = []
    for x, y in zip(xs, ys):
        key = (id(ax), int(round(x / 3.0)), side)
        k = _STACK.get(key, 0)
        _STACK[key] = k + 1
        out_y.append((x, y, k))
    rng = _RANGE.get(id(ax), 1.0)
    for x, y, k in out_y:
        yy = y + side * k * 0.065 * rng
        ax.scatter([x], [yy], marker=marker, s=size ** 2, color=color if filled else SURF, edgecolors=color,
                   linewidths=1.2, zorder=5, label=label)
        label = None
        if text:
            ax.annotate(text, (x, yy), xytext=(0, dy), textcoords="offset points", ha="center",
                        va="bottom" if dy > 0 else "top", fontsize=7, color=INK2)


_RANGE = {}


def price_panels(symbol, tf, start, end, fname):
    df = data.load(symbol, tf)
    ind = smf.original(df)
    cfg = validate.FINAL
    sig = system.build(df, cfg)
    A = sig["A"]
    trades, _ = bt.run(df, sig, bt.costs_for(symbol))
    m = (df.index >= pd.Timestamp(start, tz="UTC")) & (df.index < pd.Timestamp(end, tz="UTC"))
    idx = np.flatnonzero(m)
    x = np.arange(idx.size)
    o, h, l, c = (df[k].to_numpy()[idx] for k in ("open", "high", "low", "close"))
    atr = A["atr"][idx]
    pad = 0.6 * np.nanmedian(atr)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 8.6), sharex=True, gridspec_kw={"hspace": 0.32})
    _STACK.clear()
    _RANGE[id(a1)] = _RANGE[id(a2)] = float(np.nanmax(h) - np.nanmin(l))
    # ---- original
    reg0 = ind["regime"].to_numpy()[idx]
    _bars(a1, x, o, h, l, c, np.where(reg0 == 1, BULL, BEAR))
    a1.plot(x, ind["bC"].to_numpy()[idx], color=INK2, linewidth=1.4, label="Base")
    a1.plot(x, ind["upper"].to_numpy()[idx], color=MUTED, linewidth=0.8, linestyle="--", label="Bandas adaptativas")
    a1.plot(x, ind["lower"].to_numpy()[idx], color=MUTED, linewidth=0.8, linestyle="--")
    b = ind["buy"].to_numpy()[idx]
    s = ind["sell"].to_numpy()[idx]
    bd = ind["bullDot"].to_numpy()[idx]
    sd = ind["bearDot"].to_numpy()[idx]
    _mark(a1, x[b], l[b] - pad, "^", BULL, "Buy", -8, label="Buy / Sell original")
    _mark(a1, x[s], h[s] + pad, "v", BEAR, "Sell", 8)
    _mark(a1, x[bd], l[bd] - pad, "o", BULL, "", 0, size=6, filled=False, label="Retest (original)")
    _mark(a1, x[sd], h[sd] + pad, "o", BEAR, "", 0, size=6, filled=False)
    a1.set_title(f"{symbol} {tf} — indicador ORIGINAL (todas las rupturas + retests)", loc="left", pad=24)
    a1.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, fontsize=8, borderaxespad=0.2)

    # ---- nuevo
    reg = A["regime"][idx]
    _bars(a2, x, o, h, l, c, np.where(reg == 1, BULL, BEAR))
    a2.plot(x, A["bc"][idx], color=INK2, linewidth=1.4, label="Base")
    a2.plot(x, A["upper"][idx], color=MUTED, linewidth=0.8, linestyle="--", label="Bandas fijas ±1.2 ATR")
    a2.plot(x, A["lower"][idx], color=MUTED, linewidth=0.8, linestyle="--")
    kind = sig["kind"][idx]
    el, es = sig["ent_l"][idx], sig["ent_s"][idx]
    brk_l, brk_s = el & (kind == 1), es & (kind == 1)
    cnt_l, cnt_s = el & (kind == 2), es & (kind == 2)
    sq = A["atr_ratio"][idx] < cfg.squeeze_th
    late_u = A["buy"][idx] & ~sq
    late_d = A["sell"][idx] & ~sq
    _mark(a2, x[brk_l], l[brk_l] - pad, "^", BULL, "Long", -8, size=10, label="Entrada (ruptura en compresión)")
    _mark(a2, x[brk_s], h[brk_s] + pad, "v", BEAR, "Short", 8, size=10)
    _mark(a2, x[cnt_l], l[cnt_l] - pad, "^", BULL, "Cont", -8, size=8, filled=False, label="Continuación")
    _mark(a2, x[cnt_s], h[cnt_s] + pad, "v", BEAR, "Cont", 8, size=8, filled=False)
    _mark(a2, x[late_u], l[late_u] - pad, "o", MUTED, "tarde", -8, size=7, label="Cambio tardío (descartado)")
    _mark(a2, x[late_d], h[late_d] + pad, "o", MUTED, "tarde", 8, size=7)
    # salidas y stops de la estrategia dentro de la ventana
    pos_to_x = {int(i): k for k, i in enumerate(idx)}
    stop_line = np.full(idx.size, np.nan)
    first_exit = True
    for t in trades.itertuples():
        e_sig = t.entry_i - 1
        if e_sig < idx[0] or e_sig > idx[-1]:
            continue   # solo operaciones que empiezan dentro de la ventana
        if t.reason in ("stop", "trailing"):
            xb = t.exit_i
            txt = "Stop"
        else:
            xb = t.exit_i - 1
            txt = "Salida"
        if xb in pos_to_x and t.reason not in ("giro", "fin_ventana"):
            k = pos_to_x[xb]
            y = h[k] + pad if t.dir == 1 else l[k] - pad
            _mark(a2, [k], [y], "X", EXIT, txt, 8 if t.dir == 1 else -8, size=8,
                  label="Salida / stop" if first_exit else None)
            first_exit = False
        st = sig["stop_l"][e_sig] if t.dir == 1 else sig["stop_s"][e_sig]
        for i in range(t.entry_i, t.exit_i + 1):
            if i in pos_to_x:
                stop_line[pos_to_x[i]] = st
    a2.plot(x, stop_line, color=EXIT, linewidth=1.1, linestyle=(0, (3, 2)), label="Stop activo")
    a2.set_title(f"{symbol} {tf} — versión NUEVA (solo rupturas con volatilidad comprimida, continuación y salida por régimen)",
                 loc="left", pad=38)
    a2.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, fontsize=8, borderaxespad=0.2)
    ticks = np.linspace(0, idx.size - 1, 8).astype(int)
    a2.set_xticks(ticks)
    a2.set_xticklabels([df.index[idx[t]].strftime("%Y-%m-%d") for t in ticks])
    for a in (a1, a2):
        a.margins(x=0.01)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, fname), dpi=130, bbox_inches="tight")
    plt.close(fig)


def compression_effect(fname):
    def ev_builder(df, ind, A):
        return {"R0": (ind["buy"].to_numpy(), ind["sell"].to_numpy())}
    labels = ["<0.8", "0.8–0.9", "0.9–1.0", "1.0–1.15", ">1.15"]
    res = {}
    for part in ("is", "oos"):
        ev = sc.collect(part, ev_builder)
        ev["vol"] = pd.cut(ev["atr_ratio"], [0, 0.8, 0.9, 1.0, 1.15, 99], labels=labels)
        res[part] = ev.groupby("vol", observed=False)["tb2_40"].apply(lambda s: (s == 1).mean() - (s == -1).mean())
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    w = 0.38
    xx = np.arange(len(labels))
    b1 = ax.bar(xx - w / 2 - 0.01, res["is"].values, w, color=S1, label="In-sample (desarrollo)")
    b2 = ax.bar(xx + w / 2 + 0.01, res["oos"].values, w, color=S2, label="Fuera de muestra (validación)")
    for bars in (b1, b2):
        for r in bars:
            v = r.get_height()
            ax.annotate(f"{v:+.3f}", (r.get_x() + r.get_width() / 2, v), xytext=(0, 3 if v >= 0 else -3),
                        textcoords="offset points", ha="center", va="bottom" if v >= 0 else "top", fontsize=8, color=INK2)
    ax.axhline(0, color="#c3c2b7", linewidth=1)
    ax.set_xticks(xx)
    ax.set_xticklabels(labels)
    ax.set_xlabel("ATR(14) / ATR(100) en la vela de la señal  (compresión ←  → expansión)")
    ax.set_ylabel("Ventaja: P(+2 ATR antes) − P(−2 ATR antes)")
    ax.set_title("Buy/Sell original según la volatilidad: las rupturas en expansión no tienen ventaja", loc="left")
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(OUT, fname), dpi=130, bbox_inches="tight")
    plt.close(fig)
    return res


def oos_sharpe(fname):
    port = pd.read_csv(os.path.join(common.RESULTS, "09_validacion_cartera_oos.csv"), index_col=[0, 1])
    cfgs = [("A original (SAR, banda adaptativa)", "Original", S1), ("E FINAL (+ stop en banda)", "Final", S2),
            ("E' FINAL solo largos", "Final solo largos", S3)]
    groups = ["acciones 1d", "acciones 1h", "cripto 1d", "cripto 4h", "cripto 1h"]
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    w = 0.26
    xx = np.arange(len(groups))
    for k, (cfg, lab, col) in enumerate(cfgs):
        vals = [port.loc[(cfg, g), "sharpe"] for g in groups]
        bars = ax.bar(xx + (k - 1) * (w + 0.02), vals, w, color=col, label=lab)
        for r in bars:
            v = r.get_height()
            ax.annotate(f"{v:.2f}", (r.get_x() + r.get_width() / 2, v), xytext=(0, 3 if v >= 0 else -3),
                        textcoords="offset points", ha="center", va="bottom" if v >= 0 else "top", fontsize=7.5,
                        color=INK2)
    ax.axhline(0, color="#c3c2b7", linewidth=1)
    ax.set_xticks(xx)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Sharpe anual de la cartera equiponderada")
    ax.set_title("Fuera de muestra: mejora clara en acciones, empate en cripto 1d, peor en cripto 4h, nada en 1h", loc="left")
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(OUT, fname), dpi=130, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    price_panels("BTCUSDT", "4h", "2024-01-15", "2024-04-20", "01_btc_4h_original_vs_nuevo.png")
    price_panels("SPY", "1d", "2021-11-01", "2023-08-01", "02_spy_1d_original_vs_nuevo.png")
    price_panels("ETHUSDT", "1d", "2022-06-01", "2024-01-01", "03_eth_1d_original_vs_nuevo.png")
    r = compression_effect("04_efecto_compresion_is_vs_oos.png")
    print(pd.DataFrame(r).round(3))
    oos_sharpe("05_sharpe_oos_por_grupo.png")
    print("ok")
