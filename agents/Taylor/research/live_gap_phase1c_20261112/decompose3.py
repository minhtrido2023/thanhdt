"""GĐ1 vòng 3 — phân rã phơi nhiễm CÓ PARK HAI PHÍA (job Taylor_20261112_122855).

Mỗi chuỗi, mỗi phiên t: e_park, e_sig (BAL/LAG/CAPIT), e_disc (chỉ live: DISCRETIONARY_SPECIAL + book lạ) theo /NAV.
  β_x = Σ_t e_x,t−1 · r_VNI,t (số học, không ước lượng beta);  α-dư = r − Σ_x β_x.
LIVE: từ 04/08 = park_holdings.py (sổ theo book, read-only) từng phiên → live_books/*.json (by_book mv, giá đóng cửa
đã xác minh); trước 04/08 (chưa có sổ) = lô non-PARK của bootstrap 04/08 có entry_date ≤ t × Price BQ (live_books/
july_price.csv), park := mtm_stock − sig − disc (phần dư ⇒ gồm cả over-buy 02/07) — XẤP XỈ, gắn nhãn.
ZaloPay = sleeve bot (nav_b, loại book EXCLUDED/DGC). r live = TWR GĐ0. ENGINE: e_sig = stocks_ref/nav, e_park = etf_ref/nav.
Phiên đầu (chưa có e_{t−1}): DAY1=bfill (dòng sổ đầu, như vòng 2) hoặc DAY1=zero (tiền mặt trước go-live) — chạy cả 2.
Usage: decompose3.py out_prefix"""
import sys, glob, json, os
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
R = f"{WC}/mike/agents/Taylor/research/live_gap_phase1c_20261112"
EL = f"{WC}/data/execution_logs"
VS = f"{WC}/mike/agents/Taylor/research/live_gap_phase0_20261112/vs_savings_table.csv"
TP = f"{WC}/data/trade_plans"


def one(p):
    fs = glob.glob(p); assert len(fs) == 1, (p, fs); return fs[0]


LEGS = {("SpaceX", "cold_p0"): "c3_SXcold_p0", ("SpaceX", "cold_park"): "c3_SXcold_ps",
        ("SpaceX", "warm_p0"): "c3_SXwarm_p0", ("SpaceX", "warm_park"): "c3_SXwarm_ps",
        ("ZaloPay", "cold_p0"): "c3_Zcold_p0", ("ZaloPay", "cold_park"): "c3_Zcold_ps",
        ("ZaloPay", "warm_p0"): "c3_Zwarm_p0", ("ZaloPay", "warm_park"): "c3_Zwarm_ps"}
WIN = {"SpaceX": ("2026-06-30", "2026-11-11"), "ZaloPay": ("2026-07-06", "2026-11-11")}
MONTHS = {"SpaceX": [("thang 7", "2026-06-30", "2026-07-31"), ("thang 8", "2026-07-31", "2026-08-31"),
                     ("thang 9", "2026-08-31", "2026-09-30"), ("thang 10", "2026-09-30", "2026-10-30"),
                     ("MTD Nov (->11/11)", "2026-10-30", "2026-11-11")]}
MONTHS["ZaloPay"] = [("thang 7", "2026-07-06", "2026-07-31")] + MONTHS["SpaceX"][1:]
SIG = {"BAL", "LAG", "CAPIT"}


def engine(tag):
    X = pd.read_csv(one(f"{R}/ledgers/*_exp_{tag}_univpit*.csv"), low_memory=False)
    D = X[X.record_type == "DAILY"].copy()
    D["d"] = pd.to_datetime(D["ymd"].astype(str).str[:10]); D = D.set_index("d").sort_index()
    nav = D["combined_nav"].astype(float)
    stk = D["bal_stocks_ref"].astype(float) + D["lag_stocks_ref"].astype(float)
    etf = D["bal_etf_ref"].astype(float) + D["lag_etf_ref"].astype(float)
    return pd.DataFrame({"nav": nav, "sig": stk / nav, "park": etf / nav, "disc": 0.0 * nav, "vni": D["vni_close"].astype(float)})


def live(acct, idx):
    h = pd.read_csv(f"{EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last")
    h["d"] = pd.to_datetime(h["date"]); h = h.set_index("d").sort_index()
    if acct == "SpaceX":
        nav = h["nav"].astype(float); stk = h["mtm_stock"].astype(float)
    else:
        s = pd.read_csv(f"{EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last")
        s["d"] = pd.to_datetime(s["date"]); s = s.set_index("d").sort_index()
        j = s.join(h[["mtm_stock"]], how="inner")
        nav = j["nav_b"].astype(float); stk = j["mtm_stock"].astype(float) - j["outside_mv"].astype(float)
    px = pd.read_csv(f"{R}/live_books/july_price.csv"); px["d"] = pd.to_datetime(px["d"])
    px = px.pivot(index="d", columns="ticker", values="Price")
    boot = json.load(open(f"{TP}/bootstrap_book_snapshot_{acct}_20260804.json"))["positions"]
    rows, nrec_bad = {}, 0
    for d in nav.index:
        ds = d.strftime("%Y-%m-%d"); f = f"{R}/live_books/{acct}_{ds}.json"
        if ds >= "2026-08-04" and os.path.exists(f) and os.path.getsize(f) > 0:
            H = json.load(open(f)); bb = H["by_book"]
            nrec_bad += 0 if H["reconcile"].get("ok") else 1
            p = bb.get("PARK", {}).get("mv_vnd", 0.0)
            sg = sum(v["mv_vnd"] for k, v in bb.items() if k in SIG)
            dc = sum(v["mv_vnd"] for k, v in bb.items() if k not in SIG | {"PARK", "EXCLUDED"})
            rows[d] = (p, sg, dc, "sổ")
        elif ds < "2026-08-04":
            sg = dc = 0.0
            for l in boot:
                if l["book"] in ("PARK", "EXCLUDED") or l["entry_date"] > ds: continue
                pr = px[l["ticker"]].loc[:d].dropna()
                v = l["qty"] * float(pr.iloc[-1]) if len(pr) else 0.0
                if l["book"] in SIG: sg += v
                else: dc += v
            rows[d] = (float(stk.loc[d]) - sg - dc, sg, dc, "xấp xỉ bootstrap")
    B = pd.DataFrame(rows, index=["park", "sig", "disc", "src"]).T
    out = pd.DataFrame({k: B[k].astype(float) / nav.reindex(B.index) for k in ["park", "sig", "disc"]})
    out["tot_bookcheck"] = out.sum(axis=1); out["tot_nav"] = (stk / nav).reindex(out.index)
    out["src"] = B["src"]
    return out, nrec_bad


def contrib(e, vni, a, b):
    r = vni.pct_change(); m = (vni.index > pd.Timestamp(a)) & (vni.index <= pd.Timestamp(b)); el = e.shift(1)
    return float((el[m] * r[m]).sum()), float(el[m].mean())


def main(out):
    vs = pd.read_csv(VS)
    VNI = engine("exp_gap_c3_SXwarm_p0")["vni"]
    rows = []; diag = []
    for acct in ["SpaceX", "ZaloPay"]:
        Lraw, nbad = live(acct, VNI.index)
        diag.append(f"{acct}: sổ book {sum(Lraw.src=='sổ')} phiên (reconcile!=ok {nbad}), xấp xỉ bootstrap {sum(Lraw.src!='sổ')} phiên; "
                    f"|Σbook − mtm_stock/NAV| TB {float((Lraw.tot_bookcheck-Lraw.tot_nav).abs().mean()):.2%}, max {float((Lraw.tot_bookcheck-Lraw.tot_nav).abs().max()):.2%}")
        Lraw[["park", "sig", "disc", "tot_nav", "src"]].to_csv(f"{out}_live_{acct}.csv", float_format="%.4f")
        for day1 in ["bfill", "zero"]:
            L = Lraw[["park", "sig", "disc"]].reindex(VNI.index).ffill()
            L = L.bfill() if day1 == "bfill" else L.fillna(0.0)
            series = "bot" if acct == "ZaloPay" else "account"
            for (ac, lab), tag in LEGS.items():
                if ac != acct: continue
                E = engine("exp_gap_" + tag).reindex(VNI.index)
                E["nav"] = E["nav"].bfill(); E[["sig", "park", "disc"]] = E[["sig", "park", "disc"]].fillna(0.0)
                for mlab, a, b in MONTHS[acct] + [("ky", *WIN[acct])]:
                    key = "inception->11/11" if mlab == "ky" else mlab
                    q = vs[(vs.account == acct) & (vs.series == series) & (vs.window == key)]
                    rL = float(q["live_twr_pct"].iloc[0]) / 100
                    nav = E["nav"]; nA = nav[nav.index <= pd.Timestamp(a)]
                    n0 = float(nA.iloc[-1]) if len(nA) else float(nav.iloc[0])
                    rE = float(nav[nav.index <= pd.Timestamp(b)].iloc[-1]) / n0 - 1
                    d = dict(TK=acct, engine=lab, day1=day1, ky=mlab, live_r=100 * rL, eng_r=100 * rE, gap=100 * (rL - rE))
                    for side, S, rr in (("live", L, rL), ("eng", E, rE)):
                        bt = 0.0
                        for x in ("park", "sig", "disc"):
                            bx, ex = contrib(S[x], VNI, a, b); d[f"{side}_e_{x}"] = ex; d[f"{side}_b_{x}"] = 100 * bx; bt += bx
                        d[f"{side}_b_tot"] = 100 * bt; d[f"{side}_alpha"] = 100 * (rr - bt)
                    for x in ("park", "sig", "disc", "tot"): d[f"gap_b_{x}"] = d[f"live_b_{x}"] - d[f"eng_b_{x}"]
                    d["gap_alpha"] = d["live_alpha"] - d["eng_alpha"]
                    rows.append(d)
    T = pd.DataFrame(rows); T.to_csv(out + ".csv", index=False, float_format="%.4f")
    with open(out + ".md", "w") as fh:
        fh.write("Chẩn đoán nguồn live: " + " | ".join(diag) + "\n")
        for (acct, lab, day1), g in T.groupby(["TK", "engine", "day1"], sort=False):
            fh.write(f"\n### {acct} — live vs engine {lab} (phiên đầu: {day1})\n\n| kỳ | r live | r eng | gap | e park L/E | e sig L/E | e disc L | "
                     "gap β park | gap β sig | gap β disc | gap β tổng | gap α |\n|" + "---|" * 12 + "\n")
            for _, x in g.iterrows():
                fh.write(f"| {x.ky} | {x.live_r:+.2f} | {x.eng_r:+.2f} | {x.gap:+.2f} | {x.live_e_park:.0%}/{x.eng_e_park:.0%} | "
                         f"{x.live_e_sig:.0%}/{x.eng_e_sig:.0%} | {x.live_e_disc:.0%} | {x.gap_b_park:+.2f} | {x.gap_b_sig:+.2f} | "
                         f"{x.gap_b_disc:+.2f} | {x.gap_b_tot:+.2f} | {x.gap_alpha:+.2f} |\n")
    print(open(out + ".md").read())


if __name__ == "__main__":
    main(sys.argv[1])
