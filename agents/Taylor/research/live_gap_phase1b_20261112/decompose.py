"""GĐ1 vòng 2 — việc 3: phân rã phơi nhiễm theo tháng, live vs engine (job Taylor_20261112_112708).

Mỗi chuỗi (live / engine) mỗi tháng:
  e_mean   = tỷ trọng cổ phiếu/NAV TB các phiên trong tháng (e_{t-1} dùng cho phiên t)
  r        = lợi suất tháng (live: TWR GĐ0 vs_savings_table.csv — đã khử dòng tiền; engine: NAV cuối tháng)
  beta_c   = Σ_t e_{t-1}·r_VNI,t   (phần "phơi nhiễm × thị trường", số học, không ước lượng beta)
  alpha_c  = r − beta_c            (dư: chọn mã + thực thi + lãi phần không-cổ-phiếu)
Gap live−engine = Δbeta_c + Δalpha_c (cộng tính theo tháng; tổng kỳ = tổng tháng, sai số gộp lãi kép ghi riêng).
e của live: SpaceX = mtm_stock/nav (nav_history_SpaceX.csv); ZaloPay bot = (mtm_stock − outside_mv)/nav_b
(nav_history_ZaloPay.csv ⨝ nav_sleeve_history_ZaloPay.csv). Phiên đầu (01/07 SpaceX, 07/07 ZaloPay) chưa có dòng
sổ của ngày trước ⇒ e_{t-1} := e của dòng sổ đầu tiên (bot khớp lệnh ngay sáng phiên đầu) — gắn nhãn xấp xỉ.
VN-Index đóng cửa: cột cuối DAILY của ledger engine (cùng cache bq_cache_asof20261111).
Usage: decompose.py out_prefix  (đọc legs từ LEGS bên dưới)"""
import sys, glob, json
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
R = f"{WC}/mike/agents/Taylor/research/live_gap_phase1b_20261112"
P1 = f"{WC}/mike/agents/Taylor/research/live_gap_phase1_20261112"
EL = f"{WC}/data/execution_logs"
VS = f"{WC}/mike/agents/Taylor/research/live_gap_phase0_20261112/vs_savings_table.csv"


def one(pattern):
    fs = glob.glob(pattern)
    assert len(fs) == 1, (pattern, fs)
    return fs[0]


LEGS = {  # (account, label) -> ledger
    ("SpaceX", "eng_cold_1B"): one(f"{P1}/ledgers/*_exp_gap_W1_adj_univpit_nav1B_from20260701.csv"),
    ("SpaceX", "eng_warm_live"): one(f"{R}/ledgers/*_exp_gap_WL2warm_SX_adj_univpit*.csv"),
    ("ZaloPay", "eng_cold_live"): one(f"{R}/ledgers/*_exp_gap_Z1cold_live_adj_univpit*.csv"),
    ("ZaloPay", "eng_warm_live"): one(f"{R}/ledgers/*_exp_gap_WL2warm_Z_adj_univpit*.csv"),
}
WIN = {"SpaceX": ("2026-06-30", "2026-11-11"), "ZaloPay": ("2026-07-06", "2026-11-11")}
MONTHS = {"SpaceX": [("thang 7", "2026-06-30", "2026-07-31"), ("thang 8", "2026-07-31", "2026-08-31"),
                     ("thang 9", "2026-08-31", "2026-09-30"), ("thang 10", "2026-09-30", "2026-10-30"),
                     ("MTD Nov (->11/11)", "2026-10-30", "2026-11-11")]}
MONTHS["ZaloPay"] = [("thang 7", "2026-07-06", "2026-07-31")] + MONTHS["SpaceX"][1:]


def engine(path):
    X = pd.read_csv(path, low_memory=False)
    D = X[X.record_type == "DAILY"].copy()
    D["d"] = pd.to_datetime(D["ymd"].astype(str).str[:10])
    D = D.set_index("d").sort_index()
    nav = D["combined_nav"].astype(float)
    stk = D["bal_stocks_ref"].astype(float) + D["lag_stocks_ref"].astype(float)
    etf = D["bal_etf_ref"].astype(float) + D["lag_etf_ref"].astype(float)
    vni = D.iloc[:, -1].astype(float)
    return pd.DataFrame({"nav": nav, "e": stk / nav, "etf": etf / nav, "vni": vni})


def live_e(acct, idx):
    h = pd.read_csv(f"{EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last")
    h["d"] = pd.to_datetime(h["date"]); h = h.set_index("d").sort_index()
    if acct == "SpaceX":
        e = h["mtm_stock"].astype(float) / h["nav"].astype(float)
    else:
        s = pd.read_csv(f"{EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last")
        s["d"] = pd.to_datetime(s["date"]); s = s.set_index("d").sort_index()
        j = s.join(h[["mtm_stock"]], how="inner")
        e = (j["mtm_stock"].astype(float) - j["outside_mv"].astype(float)) / j["nav_b"].astype(float)
    e = e.reindex(idx).ffill().bfill()  # phiên đầu: bfill = xấp xỉ đã gắn nhãn
    return e


def contrib(e, vni, a, b):
    """Σ_{t∈(a,b]} e_{t-1}·r_VNI,t và e TB, trên lưới phiên của vni."""
    r = vni.pct_change()
    m = (vni.index > pd.Timestamp(a)) & (vni.index <= pd.Timestamp(b))
    el = e.shift(1)
    return float((el[m] * r[m]).sum()), float(el[m].mean()), float(vni[vni.index <= pd.Timestamp(b)].iloc[-1]
                                                                     / vni[vni.index <= pd.Timestamp(a)].iloc[-1] - 1)


def main(out):
    vs = pd.read_csv(VS)
    VNI = engine(one(f"{R}/ledgers/*_exp_gap_WL2warm_SX_adj_univpit*.csv"))["vni"]  # lưới phiên + VNI chung (có 30/06)
    rows = []
    for (acct, lab), path in LEGS.items():
        E = engine(path).reindex(VNI.index)
        E["nav"] = E["nav"].bfill()          # chân cold: trước phiên đầu = vốn tiền mặt ban đầu (lệnh đầu 21/07)
        E["e"] = E["e"].fillna(0.0)
        vni = VNI
        series = "bot" if acct == "ZaloPay" else "account"
        eL = live_e(acct, vni.index)
        for mlab, a, b in MONTHS[acct] + [("ky", *WIN[acct])]:
            # live TWR: GĐ0 table (đã khử dòng tiền). Kỳ = inception->11/11.
            key = "inception->11/11" if mlab == "ky" else mlab
            q = vs[(vs.account == acct) & (vs.series == series) & (vs.window == key)]
            rL = float(q["live_twr_pct"].iloc[0]) / 100
            bL, eLm, rV = contrib(eL, vni, a, b)
            nav = E["nav"]
            nA = nav[nav.index <= pd.Timestamp(a)]
            n0 = float(nA.iloc[-1]) if len(nA) else float(nav.iloc[0])  # cold leg: NAV đầu = vốn tiền mặt
            rE = float(nav[nav.index <= pd.Timestamp(b)].iloc[-1]) / n0 - 1
            bE, eEm, _ = contrib(E["e"], vni, a, b)
            rows.append(dict(TK=acct, engine=lab, ky=mlab, tu=a, den=b, vni_pct=100 * rV,
                             live_e=eLm, eng_e=eEm, live_r=100 * rL, eng_r=100 * rE,
                             live_beta=100 * bL, live_alpha=100 * (rL - bL),
                             eng_beta=100 * bE, eng_alpha=100 * (rE - bE),
                             gap=100 * (rL - rE), gap_beta=100 * (bL - bE), gap_alpha=100 * ((rL - bL) - (rE - bE)),
                             eng_nav_start=n0))
    T = pd.DataFrame(rows)
    T.to_csv(out + ".csv", index=False, float_format="%.4f")
    with open(out + ".md", "w") as fh:
        for (acct, lab), g in T.groupby(["TK", "engine"], sort=False):
            fh.write(f"\n### {acct} — live vs {lab} (NAV engine đầu kỳ {g.eng_nav_start.iloc[-1]:,.0f})\n\n")
            fh.write("| kỳ | VNI% | e live | e eng | r live% | r eng% | β·mkt live | β·mkt eng | α-dư live | α-dư eng | gap pp | gap β | gap α |\n|"
                     + "---|" * 13 + "\n")
            for _, x in g.iterrows():
                fh.write(f"| {x.ky} | {x.vni_pct:+.2f} | {x.live_e:.0%} | {x.eng_e:.0%} | {x.live_r:+.2f} | {x.eng_r:+.2f} | "
                         f"{x.live_beta:+.2f} | {x.eng_beta:+.2f} | {x.live_alpha:+.2f} | {x.eng_alpha:+.2f} | "
                         f"{x.gap:+.2f} | {x.gap_beta:+.2f} | {x.gap_alpha:+.2f} |\n")
            m = g[g.ky != "ky"]
            k = g[g.ky == "ky"].iloc[0]
            fh.write(f"\nTổng tháng (cộng) gap {m.gap.sum():+.2f} = β {m.gap_beta.sum():+.2f} + α {m.gap_alpha.sum():+.2f}; "
                     f"kỳ (gộp lãi kép) gap {k.gap:+.2f} = β {k.gap_beta:+.2f} + α {k.gap_alpha:+.2f}.\n")
    print(open(out + ".md").read())


if __name__ == "__main__":
    main(sys.argv[1])
