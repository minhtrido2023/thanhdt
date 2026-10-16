#!/usr/bin/env python3
"""sprint2_plots.py — three figures for SPRINT2_CASH_DIVIDEND.md. Reads out2/ only."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprint2_analyze import Index, YIELD_LABELS, block_bootstrap_mean  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out2")
INK, POS, NEG, GREY = "#1f2933", "#0b7285", "#c92a2a", "#adb5bd"


def style(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=10, color=INK, loc="left", pad=8)
    ax.set_xlabel(xlabel, fontsize=8.5, color=INK)
    ax.set_ylabel(ylabel, fontsize=8.5, color=INK)
    ax.tick_params(labelsize=8, colors=INK)
    ax.grid(axis="y", color="#e9ecef", lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#ced4da")


def main() -> int:
    ev = pd.read_csv(os.path.join(OUT, "event_features.csv"))
    ewu = pd.read_csv(os.path.join(OUT, "ew_universe.csv"))
    res = json.load(open(os.path.join(OUT, "results.json")))
    bm = Index.from_returns(ewu, "ew_ret")

    core = ev[(ev["in_universe_pit"] == 1) & (ev["n_iss_adj_21"] == 0)
              & (ev["n_other_div_21"] == 0)].dropna(subset=["BHAR_20"]).copy()

    # ---------------- Fig 1: event-time CAAR path, anchored at k = -21 -------------------
    anchors = [(-21, "c_m21", "d_m21"), (-1, "c_m1", "d_m1"), (0, "c_0", "d_0"),
               (5, "c_5", "d_5"), (10, "c_10", "d_10"), (20, "c_20", "d_20"),
               (60, "c_60", "d_60")]
    ks, mus, los, his = [], [], [], []
    for k, cc, dd in anchors:
        v = (core[cc] / core["c_m21"] - 1.0) - bm.ret(core["d_m21"], core[dd])
        b = block_bootstrap_mean(v.to_numpy(), core["ex_month"].to_numpy(), n_boot=2000)
        ks.append(k); mus.append(100 * b["mean"]); los.append(100 * b["lo"]); his.append(100 * b["hi"])

    fig, ax = plt.subplots(figsize=(7.4, 4.0), dpi=170)
    ax.fill_between(ks, los, his, color=POS, alpha=0.13, lw=0)
    ax.plot(ks, mus, "-o", color=POS, lw=1.8, ms=4.5)
    ax.axvline(0, color=NEG, lw=1.1, ls="--")
    ax.axhline(0, color=GREY, lw=0.9)
    ax.annotate("ex-date", xy=(0, ax.get_ylim()[1]), xytext=(1.5, mus[-1] * 0.9 + 1.4),
                fontsize=8, color=NEG)
    for x, y in zip(ks, mus):
        ax.annotate(f"{y:+.2f}%", (x, y), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=7.2, color=INK)
    style(ax, f"CAAR quanh ngày GDKHQ cổ tức tiền mặt — P-CORE (universe_pit), "
              f"N={len(core)} sự kiện / {core['ticker'].nunique()} mã",
          "phiên tính từ ngày GDKHQ (k = 0)", "CAAR vs EW universe_pit (%), neo tại k = −21")
    fig.text(0.01, 0.015, "Dải = CI 95% block bootstrap theo tháng lịch của ex-date. "
                          "Đo trên Close hồi tố; KHÔNG đọc ticker.Price dòng ex-date.",
             fontsize=6.8, color="#6c757d")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(os.path.join(OUT, "fig1_caar_path.png"))
    plt.close(fig)

    # ---------------- Fig 2: module A — drop ratio + AR_ex ------------------------------
    A = pd.read_csv(os.path.join(OUT, "module_A_events.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), dpi=170)
    dr = A["DR"].clip(-1, 3)
    axes[0].hist(dr, bins=80, color=POS, alpha=0.8)
    axes[0].axvline(1.0, color=NEG, lw=1.3, ls="--")
    axes[0].axvline(float(A["DR"].median()), color=INK, lw=1.2)
    axes[0].annotate(f"trung vị {A['DR'].median():.3f}", (A['DR'].median(), 0),
                     xytext=(6, 6), textcoords="offset points", fontsize=8, color=INK)
    axes[0].annotate("lý thuyết = 1", (1.0, 0), xytext=(6, 22), textcoords="offset points",
                     fontsize=8, color=NEG)
    style(axes[0], f"A-S1 · Drop ratio (P_cum − P̂_ex)/D   n={len(A)}",
          "drop ratio (cắt [−1,3])", "số sự kiện")

    bins = res["module_A"]["by_yield_bin"]
    x = np.arange(len(bins))
    mu = [100 * b["AR_ex_mean"] for b in bins]
    err = [[100 * (b["AR_ex_mean"] - b["lo"]) for b in bins],
           [100 * (b["hi"] - b["AR_ex_mean"]) for b in bins]]
    axes[1].bar(x, mu, color=[POS if m > 0 else NEG for m in mu], alpha=0.85, width=0.62)
    axes[1].errorbar(x, mu, yerr=err, fmt="none", ecolor=INK, elinewidth=1.1, capsize=3)
    axes[1].axhline(0, color=GREY, lw=0.9)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([b["bin"].split()[0] for b in bins], fontsize=8)
    for i, (m, b) in enumerate(zip(mu, bins)):
        axes[1].annotate(f"n={b['n']}", (i, 0), xytext=(0, -14), textcoords="offset points",
                         ha="center", fontsize=7, color="#6c757d")
    style(axes[1], "A-P · Lợi suất ex-day điều chỉnh thị trường theo bin tỉ suất",
          "bin tỉ suất cổ tức gộp", "AR_ex (%)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_module_A.png"))
    plt.close(fig)

    # ---------------- Fig 3: BHAR_20 by yield bin, raw vs paired ------------------------
    raw = {b["bin"]: b for b in res["module_B"]["by_yield_bin"]}
    pr = {b["bin"]: b for b in res["module_B"]["paired_by_yield_bin"]}
    labs = [l for l in YIELD_LABELS if l in raw]
    x = np.arange(len(labs))
    fig, ax = plt.subplots(figsize=(7.6, 4.0), dpi=170)
    for off, src, col, name in ((-0.19, raw, POS, "thô (vs EW universe)"),
                                (0.19, pr, "#e8590c", "trừ baseline xa (ghép cặp cùng mã)")):
        m = [100 * src[l]["mean"] for l in labs]
        e = [[100 * (src[l]["mean"] - src[l]["lo"]) for l in labs],
             [100 * (src[l]["hi"] - src[l]["mean"]) for l in labs]]
        ax.bar(x + off, m, width=0.36, color=col, alpha=0.85, label=name)
        ax.errorbar(x + off, m, yerr=e, fmt="none", ecolor=INK, elinewidth=1.0, capsize=2.5)
    ax.axhline(0, color=GREY, lw=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8)
    ax.legend(fontsize=8, frameon=False)
    for i, l in enumerate(labs):
        ax.annotate(f"n={raw[l]['n']}", (i, 0), xytext=(0, -15), textcoords="offset points",
                    ha="center", fontsize=7, color="#6c757d")
    style(ax, "B · BHAR_20 sau ngày GDKHQ theo bin tỉ suất cổ tức — P-CORE",
          "bin tỉ suất cổ tức gộp", "BHAR_20 (%)")
    fig.text(0.01, 0.015, "Thanh lỗi = CI 95% block bootstrap theo tháng. Bin Y1 lệch mạnh ở "
                          "bản ghép cặp vì chính baseline xa của Y1 cao bất thường (+2,26%) — "
                          "đọc hệ số hồi quy theo tỉ suất, không đọc từng bin ghép cặp.",
             fontsize=6.6, color="#6c757d")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(os.path.join(OUT, "fig3_bhar_by_yield.png"))
    plt.close(fig)

    caar = [{"k": k, "caar_mean": m / 100, "lo": lo / 100, "hi": hi / 100}
            for k, m, lo, hi in zip(ks, mus, los, his)]
    json.dump(caar, open(os.path.join(OUT, "caar_path.json"), "w"), indent=2)
    print("wrote fig1_caar_path.png, fig2_module_A.png, fig3_bhar_by_yield.png, caar_path.json")
    print(json.dumps(caar, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
