"""Luồng E1 (job Taylor_20261112_151839) — phân rã có park HAI PHÍA cho các chân fidelity.
Tái dùng NGUYÊN hàm live()/contrib() của ../live_gap_phase1c_20261112/decompose3.py (sổ book live + bootstrap tháng 7);
engine() đọc ledger của Luồng E. Thêm cửa sổ con 07-20→07-31 (gốc = đóng cửa 07-17) và β park live cạnh engine.
Usage: decomposeE.py out_prefix"""
import sys, glob, os
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../live_gap_phase1c_20261112")))
import decompose3 as D3
R = os.path.dirname(os.path.abspath(__file__))
P1C = D3.R
LEGS = {}
for acct, k in (("SpaceX", "SX"), ("ZaloPay", "Z")):
    for reg in ("cold", "warm"):
        LEGS[(acct, f"{reg}_p1c")] = f"{P1C}/ledgers/*_exp_exp_gap_c3_{k}{reg}_ps_univpit*.csv"
        for v in ("ctlLZ", "base", "fid", "fidT", "fidJ"):
            LEGS[(acct, f"{reg}_{v}")] = f"{R}/ledgers/*_exp_exp_gapE_{k}{reg}_{v}_univpit*.csv"
LAB = {"p1c": "p1c: lịch park cũ (0,7 từ 01/07), JIT bật", "ctlLZ": "p1c + LIQ_ZERO_BLOCK=lag",
       "base": "lịch base chuẩn (1,0→0,7 07-03→0,8 08-05→0,3 09-28→0 10-02) + LZB, JIT bật = ENGINE(park mục tiêu)",
       "fid": "base + buy-only park tới 08-06 (không bán, không JIT)",
       "fidT": "base + buy-only tới 08-06, trừ trim 07-06 (= live) — FIDELITY CHÍNH",
       "fidJ": "base + chỉ tắt JIT tới 08-06 (bán về mục tiêu vẫn bật)"}
SUB = [("07-20→07-31", "2026-07-17", "2026-07-31")]


def engine(pat):
    fs = glob.glob(pat)
    if len(fs) != 1: return None
    X = pd.read_csv(fs[0], low_memory=False); Dd = X[X.record_type == "DAILY"].copy()
    Dd["d"] = pd.to_datetime(Dd["ymd"].astype(str).str[:10]); Dd = Dd.set_index("d").sort_index()
    nav = Dd["combined_nav"].astype(float)
    stk = Dd["bal_stocks_ref"].astype(float) + Dd["lag_stocks_ref"].astype(float)
    etf = Dd["bal_etf_ref"].astype(float) + Dd["lag_etf_ref"].astype(float)
    return pd.DataFrame({"nav": nav, "sig": stk / nav, "park": etf / nav, "disc": 0.0 * nav, "vni": Dd["vni_close"].astype(float)})


def live_nav(acct):
    h = pd.read_csv(f"{D3.EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last")
    h["d"] = pd.to_datetime(h["date"]); h = h.set_index("d").sort_index()
    if acct == "SpaceX": return h["nav"].astype(float)
    s = pd.read_csv(f"{D3.EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last")
    s["d"] = pd.to_datetime(s["date"]); return s.set_index("d").sort_index()["nav_b"].astype(float)


def main(out):
    vs = pd.read_csv(D3.VS)
    VNI = engine(LEGS[("SpaceX", "cold_p1c")].replace("cold", "warm"))["vni"]
    rows = []
    for acct in ["SpaceX", "ZaloPay"]:
        Lraw, _ = D3.live(acct, VNI.index)
        L = Lraw[["park", "sig", "disc"]].reindex(VNI.index).ffill().bfill()
        LN = live_nav(acct)
        series = "bot" if acct == "ZaloPay" else "account"
        for (ac, lab), pat in LEGS.items():
            if ac != acct: continue
            E = engine(pat)
            if E is None: continue
            E = E.reindex(VNI.index); E["nav"] = E["nav"].bfill(); E[["sig", "park", "disc"]] = E[["sig", "park", "disc"]].fillna(0.0)
            for mlab, a, b in D3.MONTHS[acct] + SUB + [("ky", *D3.WIN[acct])]:
                if mlab in dict((x[0], 1) for x in SUB):
                    l0 = LN[LN.index <= pd.Timestamp(a)].iloc[-1]; rL = LN[LN.index <= pd.Timestamp(b)].iloc[-1] / l0 - 1
                else:
                    key = "inception->11/11" if mlab == "ky" else mlab
                    q = vs[(vs.account == acct) & (vs.series == series) & (vs.window == key)]
                    rL = float(q["live_twr_pct"].iloc[0]) / 100
                nav = E["nav"]; nA = nav[nav.index <= pd.Timestamp(a)]
                n0 = float(nA.iloc[-1]) if len(nA) else float(nav.iloc[0])
                rE = float(nav[nav.index <= pd.Timestamp(b)].iloc[-1]) / n0 - 1
                d = dict(TK=acct, engine=lab, ky=mlab, live_r=100 * rL, eng_r=100 * rE, gap=100 * (rL - rE))
                for side, S, rr in (("live", L, rL), ("eng", E, rE)):
                    bt = 0.0
                    for x in ("park", "sig", "disc"):
                        bx, ex = D3.contrib(S[x], VNI, a, b); d[f"{side}_e_{x}"] = ex; d[f"{side}_b_{x}"] = 100 * bx; bt += bx
                    d[f"{side}_b_tot"] = 100 * bt; d[f"{side}_alpha"] = 100 * (rr - bt)
                for x in ("park", "sig", "disc", "tot"): d[f"gap_b_{x}"] = d[f"live_b_{x}"] - d[f"eng_b_{x}"]
                d["gap_alpha"] = d["live_alpha"] - d["eng_alpha"]
                rows.append(d)
    T = pd.DataFrame(rows); T.to_csv(out + ".csv", index=False, float_format="%.4f")
    with open(out + ".md", "w") as fh:
        fh.write("Phiên đầu = bfill (như vòng 2/3). β_x = Σ e_x,t−1·r_VNI,t; α = r − Σβ. Cửa sổ con 07-20→07-31: live = tỉ số NAV (không có dòng tiền tháng 7).\n")
        for (acct, lab), g in T.groupby(["TK", "engine"], sort=False):
            fh.write(f"\n### {acct} — {lab}: {LAB[lab.split('_',1)[1]]}\n\n| kỳ | r live | r eng | gap | e park L/E | e sig L/E | "
                     "β park L / E | β sig L / E | gap β tổng | α live / α eng | gap α |\n|" + "---|" * 11 + "\n")
            for _, x in g.iterrows():
                fh.write(f"| {x.ky} | {x.live_r:+.2f} | {x.eng_r:+.2f} | {x.gap:+.2f} | {x.live_e_park:.0%}/{x.eng_e_park:.0%} | "
                         f"{x.live_e_sig:.0%}/{x.eng_e_sig:.0%} | {x.live_b_park:+.2f} / {x.eng_b_park:+.2f} | {x.live_b_sig:+.2f} / {x.eng_b_sig:+.2f} | "
                         f"{x.gap_b_tot:+.2f} | {x.live_alpha:+.2f} / {x.eng_alpha:+.2f} | {x.gap_alpha:+.2f} |\n")
    print(open(out + ".md").read())


if __name__ == "__main__":
    main(sys.argv[1])
