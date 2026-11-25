# -*- coding: utf-8 -*-
"""k_tables.py — xuất MỌI bảng số của REPORT V3 từ out/ (metrics2.csv, bt2_*.csv, null_ep.json, models_fit.json…) ⇒ report chỉ chép từ out/tables.md.
Gồm: luật chọn §5 (điểm IS + hoà), bảng mô hình chính, null E/P, backtest, delta giữa các giai đoạn chạy."""
import os, json, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); OUT = os.environ.get("OUT_DIR") or os.path.join(ROOT, "out")
m = pd.read_csv(os.path.join(OUT, "metrics2.csv")); m = m[m.scope == "ALL"].set_index(["model", "era"]); base = json.load(open(os.path.join(OUT, "base2.json")))
L = []
def pct(x, d=1): return "—" if pd.isna(x) else f"{100*x:.{d}f}"
# ---- §5 luật chọn ----
n0 = m.loc[("N0", "IS")]; b = base["ALL|IS"]; cand = ["D0", "D0B", "D0J", "DDM", "EPV", "MULT", "HEDf", "HEDr", "HEDL", "ENS1", "ENS1w", "ENS2", "META"]
rows = []
for c in cand:
    x = m.loc[(c, "IS")]
    ok = (x.ic36_lo > 0) or (x.ic36_hi < 0)
    rows.append({"model": c, "IC36_IS": x.ic36, "lo": x.ic36_lo, "hi": x.ic36_hi, "CI_loai_0": ok, "diem_pp": 100 * ((x.U_hit - n0.U_hit) + (x.O_right_rel - b["P_ex36_neg"]))})
sel = pd.DataFrame(rows); elig = sel[sel.CI_loai_0].sort_values("diem_pp", ascending=False)
top = elig.diem_pp.max(); ties = elig[elig.diem_pp >= top - 1.0].model.tolist(); pref = ["ENS1", "ENS2", "D0B"]
chosen = next((p for p in pref if p in ties), ties[0])
L.append("### Luật chọn §5 (chỉ IS)\n" + sel.sort_values("diem_pp", ascending=False).round(3).to_string(index=False) + f"\n\ntop={top:.2f}pp; hoà (<1pp)={ties}; ưu tiên không-fit ENS1>ENS2>D0B>khác ⇒ CHỌN = **{chosen}**\n")
# ---- bảng mô hình chính ----
def line(c):
    a, o = m.loc[(c, "IS")], m.loc[(c, "OOS")]
    return (f"| {c} | {pct(a.coverage,0)} / {pct(o.coverage,0)} | {a.ic36:.3f} [{a.ic36_lo:.2f}; {a.ic36_hi:.2f}] / {o.ic36:.3f} [{o.ic36_lo:.2f}; {o.ic36_hi:.2f}] | "
            f"{a.ic36_resid:.3f} / {o.ic36_resid:.3f} | {pct(a.U_hit)} / {pct(o.U_hit)} | {pct(a.U_static)} / {pct(o.U_static)} | {pct(a.O_right_rel)} / {pct(o.O_right_rel)} | {pct(a.O_false)} / {pct(o.O_false)} | n={int(a.O_n)}/{int(o.O_n)} |")
L.append("### Bảng mô hình chính (ALL = BQ + mã vắng BQ, H=−50%)\n| Mô hình | Độ phủ IS/OOS | IC36 [CI khối năm] IS / OOS | IC phần dư | U-hit | U-static | Đúng | Sai | N cảnh báo |\n|---|---|---|---|---|---|---|---|---|\n" + "\n".join(line(c) for c in ["A_pit", "A_RI", "D0", "D0B", "DDM", "EPV", "MULT", "HEDf", "ENS1", "ENS1w", "ENS2", "META", "REL", "L2_ENS1w", "N0"]))
L.append(f"\nnền vô điều kiện: U-static(+25%) {pct(b['P_max36_ge_125'])} / {pct(base['ALL|OOS']['P_max36_ge_125'])} · đúng {pct(b['P_ex36_neg'])} / {pct(base['ALL|OOS']['P_ex36_neg'])} · sai {pct(b['P_ex36_gt030'])} / {pct(base['ALL|OOS']['P_ex36_gt030'])}\n")
# ---- null E/P ----
nj = json.load(open(os.path.join(OUT, "null_ep.json"))); ne = pd.read_csv(os.path.join(OUT, "null_ep.csv"))
L.append("### Cảnh báo đắt: mô hình vs null E/P cùng tỉ lệ cờ (cùng luật 6 tháng + re-arm 36)\n| Cờ | Era | N | Đúng-tương đối | Đúng-tuyệt đối | Báo sai | Vượt trội TB (log) |\n|---|---|---|---|---|---|---|")
for r in ne.itertuples():
    L.append(f"| {r.model} | {r.era} | {r.n} | {pct(r.right_rel)} | {pct(r.right_abs)} | {pct(r.false)} | {r.ex_mean:.3f} |")
L.append("\nHiệu [điểm, CI 95% bootstrap theo năm sự kiện]:\n```\n" + json.dumps({k: nj[k] for k in nj if k.startswith("diff_")}, indent=1) + "\n```\nTrùng cờ: " + json.dumps(nj["overlap"]) + "\n")
L.append("### U-static: nền cố định +25% vs nền khớp ngưỡng\n```\n" + json.dumps(nj["ustatic_matched_baseline"], indent=1, ensure_ascii=False) + "\n```\n")
# ---- backtest ----
bt = pd.read_csv(os.path.join(OUT, "bt2_summary.csv")); P = bt.pivot(index="strategy", columns="era", values="cagr"); X = bt[bt.era == "ALL"].set_index("strategy")
dj = json.load(open(os.path.join(OUT, "bt2_dsr.json")))
L.append("### Backtest (CAGR % ALL / IS / OOS · Sharpe · MaxDD · số mã · turnover)\n| Chiến lược | ALL | IS | OOS | Sharpe | MaxDD | Số mã | TO |\n|---|---|---|---|---|---|---|---|")
for s in P.index:
    L.append(f"| {s} | {100*P.loc[s,'ALL']:.2f} | {100*P.loc[s,'IS']:.2f} | {100*P.loc[s,'OOS']:.2f} | {X.loc[s,'sharpe']:.2f} | {100*X.loc[s,'maxdd']:.1f} | {X.loc[s,'n']:.0f} | {100*X.loc[s,'turnover']:.1f} |")
L.append("\nDSR: ```\n" + json.dumps({k: dj[k] for k in dj if k.startswith("S1_")}, indent=1) + "\n```\n")
open(os.path.join(OUT, "tables.md"), "w").write("\n".join(L)); print("\n".join(L[:6]))
