#!/usr/bin/env python3
"""Selfcheck PREREG-5 sổ heo/DBC. Không chạm BQ, không ghi ngoài thư mục tạm. Chạy dưới env -u TZ và TZ=Asia/Tokyo.
  $DNA_PYEXE prereg5_hog_ledger_selfcheck.py"""
import os, sys, tempfile, filecmp, shutil, contextlib, io
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["PREREG5_SELFCHECK"] = "1"
import prereg5_hog_ledger as L

A4 = os.path.join(HERE, "..", "nowcast_kqkd_12fam_20261119")
WC = "/home/trido/thanhdt/WorkingClaude"
N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        print("FAIL:", msg); sys.exit(1)


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = L.main(argv)
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
            print(e.code)
    return rc, buf.getvalue()


# 1) ĐỐI CHỨNG: công thức đóng băng tái lập c của A4 cho đủ 27 quý DBC (dữ liệu chụp 19/11)
hog = L.load_hog(type("a", (), {"hog_csv": None})())
C, M = L.load_feed_inputs(type("a", (), {"comm_parquet": f"{A4}/commodity_snapshot_20261119.parquet",
                                         "macro_parquet": f"{A4}/macro_snapshot_20261119.parquet"})())
S, _ = L.signal(hog, C, M)
P = pd.read_csv(f"{A4}/a4_panel.csv"); P = P[(P.fam == 2) & (P.ticker == "DBC")]
ok(len(P) == 27, f"A4 DBC 27 quý, thấy {len(P)}")
d = max(abs(S.at[pd.Timestamp(r.qend), "c"] - r.c) for r in P.itertuples())
ok(d < 1e-9, f"c tái lập A4 lệch {d}")
# cắt dữ liệu tại qend (như nowcast làm) không đổi c lịch sử
for r in P.tail(4).itertuples():
    qe = pd.Timestamp(r.qend)
    S2, _ = L.signal(hog[hog.index <= qe], C[C.index <= qe], M[M.index <= qe])
    ok(abs(S2.at[qe, "c"] - r.c) < 1e-9, f"cắt tại qend đổi c {r.quarter}")
# np_d_hat đóng băng = OLS trên đúng 27 quý
b, a = np.polyfit(P.c, P.np_d, 1)
ok(abs(a - L.NP_A) < 5e-7 and abs(b - L.NP_B) < 5e-7, f"hệ số np_d_hat lệch OLS ({a},{b})")
# định nghĩa sue2/np_d trùng tracker PREREG-4 (LAG live)
sys.path.insert(0, f"{WC}/mike/bin")
import commodity_sue_decomp_forward_tracker as T
for vals in [(5e10, 4e10, 3e10, 2e10, 1e10, 2e11), (-1e9, np.nan, 2e9, np.nan, 3e9, 5e10), (1e8, 1e8, 1e8, 1e8, 1e8, 0)]:
    r = pd.Series(dict(zip(["NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4", "Revenue_P4"], vals)))
    ok(np.allclose(L.sue2(r), T.sue2(r), equal_nan=True), f"sue2 khác tracker {vals}")
    ok(np.allclose(L.np_d(r), T.sue1(r), equal_nan=True), f"np_d khác sue1 tracker {vals}")

# 2) Dòng chảy sổ trên dữ liệu tổng hợp 2025-01 → 2027-06
tmp = tempfile.mkdtemp(prefix="prereg5_sc_")
try:
    days = pd.date_range("2025-01-01", "2027-06-30", freq="D")
    hogp = np.where(days < "2026-01-01", 50000.0, 60000.0)
    pd.DataFrame({"date": days, "region": "Nam", "price_vnd_kg": hogp}).to_csv(f"{tmp}/hog.csv", index=False)
    pd.concat([pd.DataFrame({"metric_key": "corn", "source": "trading_economics", "observation_date": days, "value": 450.0}),
               pd.DataFrame({"metric_key": "soybean_meal_cny", "source": "sunsirs", "observation_date": days, "value": 3000.0})]
              ).to_parquet(f"{tmp}/c.parquet", index=False)
    pd.concat([pd.DataFrame({"series_key": "vn_usdvnd", "observation_date": days, "value": 25000.0}),
               pd.DataFrame({"series_key": "cn_usdcny", "observation_date": days, "value": 7.0})]).to_parquet(f"{tmp}/m.parquet", index=False)
    fin = pd.DataFrame(dict(quarter=["2026Q4", "2026Q4"], Release_Date=["2027-01-25", "2027-03-01"],  # bản restate sau bị bỏ
                            NP_P0=[3e11, 9e11], NP_P1=[1e11] * 2, NP_P2=[1e11] * 2, NP_P3=[1e11] * 2, NP_P4=[1e11] * 2,
                            Revenue_P4=[4e12] * 2))
    fin.to_csv(f"{tmp}/fin.csv", index=False)
    bd = pd.bdate_range("2027-01-04", "2027-06-30")
    pd.concat([pd.DataFrame({"time": bd, "ticker": "DBC", "Close": 30.0 * 1.001 ** np.arange(len(bd))}),
               pd.DataFrame({"time": bd, "ticker": "VNINDEX", "Close": 1500.0})]).to_csv(f"{tmp}/px.csv", index=False)
    dd = f"{tmp}/led"
    base = ["--data-dir", dd, "--hog-csv", f"{tmp}/hog.csv", "--comm-parquet", f"{tmp}/c.parquet",
            "--macro-parquet", f"{tmp}/m.parquet", "--fin-csv", f"{tmp}/fin.csv", "--px-csv", f"{tmp}/px.csv"]
    # --now bị cấm ngoài selfcheck
    os.environ.pop("PREREG5_SELFCHECK")
    rc, o = run(["nowcast", "--now", "2027-01-06T03:00:00Z"] + base)
    ok(rc != 0 and "chống ghi lùi" in o, "--now phải bị chặn ngoài selfcheck")
    os.environ["PREREG5_SELFCHECK"] = "1"
    # quý lịch sử (< 2026Q4) bị từ chối
    rc, o = run(["nowcast", "--quarter", "2026Q3", "--now", "2026-10-05T03:00:00Z"] + base)
    ok(rc != 0 and not os.path.exists(f"{dd}/nowcast.csv"), "quý lịch sử phải bị từ chối")
    # ranh giới TZ: 2026-12-31T18:00Z = 01/01/2027 01:00 ICT ⇒ quý 2026Q4 ĐÃ kết thúc theo ICT nhưng dữ liệu phải phủ
    rc, o = run(["nowcast", "--now", "2026-12-31T16:30:00Z"] + base)  # 23:30 ICT 31/12 ⇒ quý mặc định = 2026Q3 ⇒ từ chối
    ok(rc != 0 and "2026Q3" in o, f"mốc quý phải theo ICT: {o}")
    # thiếu dữ liệu cuối quý ⇒ WAIT, không ghi
    h = pd.read_csv(f"{tmp}/hog.csv"); h[h.date < "2026-12-20"].to_csv(f"{tmp}/hog_short.csv", index=False)
    b2 = base.copy(); b2[b2.index("--hog-csv") + 1] = f"{tmp}/hog_short.csv"
    rc, o = run(["nowcast", "--now", "2027-01-06T03:00:00Z"] + b2)
    ok(rc == 3 and not os.path.exists(f"{dd}/nowcast.csv"), "thiếu dữ liệu phải WAIT")
    # ghi đúng hạn
    rc, o = run(["nowcast", "--now", "2027-01-06T03:00:00Z"] + base)
    ok(rc == 0, f"nowcast rc {rc} {o}")
    n = pd.read_csv(f"{dd}/nowcast.csv")
    ok(len(n) == 1 and n.status[0] == "ON_TIME" and bool(n.counts[0]), "dòng ON_TIME")
    feed = 0.65 * 450 / 100 / 25.4 * 25000 + 0.25 * 3000 / 1000 * 25000 / 7.0
    exp_c = ((60000 - 2.8 * feed) - (50000 - 2.8 * feed)) / 50000
    ok(abs(n.c[0] - exp_c) < 1e-9, f"c tổng hợp {n.c[0]} vs {exp_c}")
    ok(pd.isna(n.struct_flag[0]), f"struct_flag trong dải: {n.struct_flag[0]}")
    ok(L.struct_flag(pd.Series(dict(feed_q=10000.0, hog_q=40000.0))) == "RATIO_OUT(0.700);HOG_OUT(40000)", "struct_flag ngoài dải")
    ok(abs(n.np_d_hat[0] - (L.NP_A + L.NP_B * exp_c)) < 1e-12, "np_d_hat")
    ok(n.prereg_md5[0] == L.md5(os.path.join(HERE, "PREREG5.md")) and len(n.inputs_sha256[0]) == 64, "md5/sha")
    ok("c=" not in o and f"{exp_c:.3f}" not in o, "nowcast không in giá trị c")
    # append-only: chạy lại (kể cả dữ liệu đổi) không đổi file
    shutil.copy(f"{dd}/nowcast.csv", f"{tmp}/n0.csv")
    rc, o = run(["nowcast", "--now", "2027-01-07T03:00:00Z"] + b2)
    ok(rc == 0 and filecmp.cmp(f"{dd}/nowcast.csv", f"{tmp}/n0.csv", shallow=False), "append-only nowcast")
    # outcome trước ngày công bố: không ghi
    rc, o = run(["outcome", "--now", "2027-01-20T03:00:00Z"] + base)
    ok(not os.path.exists(f"{dd}/outcomes.csv"), "outcome trước công bố không ghi")
    # sau công bố + 20 phiên: ghi outcome bản ĐẦU (NP_P0 3e11) + drift H20, chưa H60
    rc, o = run(["outcome", "--now", "2027-02-24T03:00:00Z"] + base)
    out = pd.read_csv(f"{dd}/outcomes.csv"); dr = pd.read_csv(f"{dd}/drift.csv")
    ok(len(out) == 1 and out.NP_P0[0] == 3e11 and abs(out.np_d[0] - 0.05) < 1e-12, "outcome = bản công bố đầu")
    ok(abs(out.sue2[0] - 2.0) < 1e-12 and bool(out.hit[0]), "sue2/hit")
    ok(list(dr.H) == [20] and str(dr.t0[0]) == "2027-01-25", f"drift H20 t0 {dr.t0.tolist()}")
    ok(abs(dr.ret_dbc[0] - 20 * np.log(1.001)) < 1e-9 and abs(dr.excess[0] - dr.ret_dbc[0]) < 1e-12, "drift số")
    rc, o = run(["outcome", "--now", "2027-05-01T03:00:00Z"] + base)
    dr = pd.read_csv(f"{dd}/drift.csv"); out2 = pd.read_csv(f"{dd}/outcomes.csv")
    ok(sorted(dr.H) == [20, 60] and len(out2) == 1, "H60 thêm, outcome không lặp")
    # nowcast muộn (đã công bố) ⇒ LATE counts False
    fin2 = fin.copy(); fin2.loc[len(fin2)] = ["2027Q1", "2027-04-10", 1e11, 1e11, 1e11, 1e11, 1e11, 4e12]
    fin2.to_csv(f"{tmp}/fin.csv", index=False)
    rc, o = run(["nowcast", "--now", "2027-04-20T03:00:00Z"] + base)
    n = pd.read_csv(f"{dd}/nowcast.csv")
    ok(n.status.iloc[-1] == "LATE" and not bool(n.counts.iloc[-1]), "LATE counts False")
    # review bị từ chối khi chưa đủ mốc, có ghi audit
    rc, o = run(["review", "--k", "8", "--now", "2027-05-01T03:00:00Z"] + base)
    au = pd.read_csv(f"{dd}/review_audit.csv")
    ok(rc != 0 and len(au) == 1 and not bool(au.allowed[0]), "review từ chối + audit")
    rc, o = run(["review", "--k", "5", "--now", "2027-05-01T03:00:00Z"] + base)
    ok(rc != 0, "K ngoài mốc bị từ chối")
finally:
    shutil.rmtree(tmp)

# 3) Luật quyết định khai trước (PREREG5 §3)
def mk(signs, mags=None):
    k = len(signs); mags = mags if mags is not None else np.arange(1, k + 1, dtype=float)
    c = mags * 0.01; y = np.where(np.array(signs) > 0, 1, -1) * mags * 0.001
    return pd.DataFrame({"quarter": [f"q{i:02d}" for i in range(k)], "c": c, "np_d": y})
ok(L.decide(mk([1] * 8), 8)[2] == "CONTINUE_ELIGIBLE", "8/8 đơn điệu ⇒ ELIGIBLE")
ok(L.decide(mk([1, 1, 1, 1, -1, -1, -1, -1]), 8)[2] == "CLOSE", "4/8 ⇒ CLOSE")
ok(L.decide(mk([-1, -1, 1, 1, 1, 1, 1, 1]), 8)[2] == "CONTINUE", "6/8 trượt ở |c| nhỏ ⇒ CONTINUE")
ok(L.decide(mk([1, 1, 1, 1, 1, 1, -1, -1]), 8)[2] == "CLOSE", "6/8 nhưng Spearman ≤0 ⇒ CLOSE")
ok(L.decide(mk([1] * 10 + [-1] * 2), 12)[0] == 10, "đếm trùng dấu 12")
ok(L.decide(mk([1] * 7 + [-1] * 5), 12)[2] == "CLOSE", "7/12 ⇒ CLOSE")
ok(L.decide(mk([1] * 11 + [-1] * 5), 16)[2] == "CLOSE", "11/16 ⇒ CLOSE (mốc cuối)")
ok(L.decide(mk([1] * 16), 16)[2] == "CONTINUE_ELIGIBLE", "16/16 ⇒ ELIGIBLE")
led = pd.DataFrame({"quarter": ["a", "b", "c", "d"], "counts": ["True"] * 4, "c": ["0.1", "0.1", "0.1", "0.1"]})
out = pd.DataFrame({"quarter": ["a", "b", "c", "d"], "np_d": ["0.1", "-0.1", "-0.1", "-0.1"]})
ok("EARLY_STOP" in L.early_stop(led, out), "3 trượt liên tiếp ⇒ cờ")
out.loc[3, "np_d"] = "0.1"
ok(L.early_stop(led, out) == "", "không cờ khi chuỗi đứt")
print(f"PASS {N[0]} assertion (TZ={os.environ.get('TZ', '<unset>')})")
