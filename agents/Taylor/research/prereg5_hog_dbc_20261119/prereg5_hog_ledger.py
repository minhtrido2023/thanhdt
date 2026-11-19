#!/usr/bin/env python3
"""PREREG-5 — sổ PAPER FORWARD nowcast KQKD DBC từ biên heo (họ 2). PAPER-ONLY: không lệnh/plan/trading_rules/LAG/BAL.

Thiết kế đóng băng: PREREG5.md cùng thư mục (md5 ghi vào mỗi dòng sổ). Công thức tín hiệu = NGUYÊN VĂN
`nowcast_kqkd_12fam_20261119/a4_nowcast.py` họ 2 + PREREG_ADDENDUM A1 (giá heo ≥10 quan sát/quý).

Lệnh con:
  nowcast  — quý Q vừa đóng (mặc định: quý gần nhất đã kết thúc). Ghi 1 dòng vào nowcast.csv TRƯỚC khi DBC công bố
             BCTC Q. Đã có dòng Q ⇒ không làm gì (append-only). DBC đã công bố ⇒ ghi status=LATE, counts=False.
  outcome  — với mỗi quý trong nowcast.csv: BCTC đã ra ⇒ ghi np_d thực + sue2 (định nghĩa LAG live) vào outcomes.csv
             (giá trị lần thấy ĐẦU được giữ); đủ 20/60 phiên sau công bố ⇒ ghi drift vào drift.csv. In cờ dừng sớm.
  review   — CHỈ chạy được khi số quý counts=True có outcome ≥ mốc K ∈ {8,12,16}; tính trên ĐÚNG K quý đầu.
             Mọi lần gọi (kể cả bị từ chối) ghi 1 dòng review_audit.csv.
Không lệnh con nào in IC/CI/p ngoài `review` tại mốc.

Chạy: . wc_env.sh; $DNA_PYEXE <thư mục>/prereg5_hog_ledger.py nowcast|outcome|review [--k 8] [--data-dir DIR]
Selfcheck: prereg5_hog_ledger_selfcheck.py (env -u TZ và TZ=Asia/Tokyo).
"""
import argparse, datetime as dt, hashlib, io, json, os, subprocess, sys
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
PROJ = "lithe-record-440915-m9"
# ---- ĐÓNG BĂNG (PREREG5 §2) — không sửa; đổi = chương trình mới + trial mới
FCR, W_CORN, W_SBM = 2.8, 0.65, 0.25
MIN_HOG, MIN_FEED = 10, 40            # quan sát/quý (A4 + addendum A1)
NP_A, NP_B = -0.000367, 0.257436       # np_d_hat = A + B·c, OLS DBC 27 quý 2020Q1–2026Q3 (mô tả, không dùng cho cổng)
FIRST_Q = "2026Q4"
CHECKPOINTS = (8, 12, 16)
# Dải lịch sử 2020Q1–2026Q3 (đo 19/11 trên snapshot A4): ngoài dải ⇒ struct_flag (quý VẪN tính; báo user — PREREG5 §3.4)
RATIO_RANGE = (0.159, 0.432)          # FCR·feed_q / hog_q
HOG_RANGE = (46154.0, 80032.0)        # hog_q VND/kg
HORIZONS = (20, 60)

NOW_COLS = ["quarter", "qend", "run_ts_utc", "run_date_ict", "status", "counts", "release_seen", "hog_q", "hog_q4", "n_hog",
            "feed_q", "feed_q4", "n_feed", "margin_q", "margin_q4", "c", "np_d_hat", "struct_flag", "hog_max_date", "feed_max_date",
            "inputs_sha256", "script_md5", "prereg_md5"]
OUT_COLS = ["quarter", "release_date", "first_seen_utc", "NP_P0", "NP_P4", "Revenue_P4", "np_d", "sue2", "hit"]
DRIFT_COLS = ["quarter", "H", "t0", "tH", "ret_dbc", "ret_vni", "excess", "first_seen_utc"]


def md5(path):
    try:
        return hashlib.md5(open(path, "rb").read()).hexdigest()
    except OSError:
        return "missing"


def now_utc(args):
    if args.now:
        if os.environ.get("PREREG5_SELFCHECK") != "1":
            sys.exit("--now chỉ dùng trong selfcheck (PREREG5_SELFCHECK=1) — chống ghi lùi ngày")
        return pd.Timestamp(args.now).tz_convert("UTC") if pd.Timestamp(args.now).tzinfo else pd.Timestamp(args.now, tz="UTC")
    return pd.Timestamp(dt.datetime.now(dt.timezone.utc))


def bq(sql):
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJ}", "--format=csv",
                          "--max_rows=1000000", sql], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"bq lỗi (rc={out.returncode}): {out.stderr.strip()[-800:]}")
    return pd.read_csv(io.StringIO(out.stdout))


# ---------------- dữ liệu (mặc định BQ/CSV thật; selfcheck truyền file)
def load_hog(a):
    h = pd.read_csv(a.hog_csv or f"{WC}/data/hog_price_vn.csv")
    h["date"] = pd.to_datetime(h.date)
    return h.groupby("date").price_vnd_kg.mean().sort_index()


def load_feed_inputs(a):
    if a.comm_parquet:
        C, M = pd.read_parquet(a.comm_parquet), pd.read_parquet(a.macro_parquet)
    else:  # cùng bộ lọc với nowcast_kqkd_12fam_20261119/fetch_data.py
        # NGUYÊN VĂN bộ lọc fetch_data.py (đủ 11 mã): chỉ mục ngày của bảng pivot = hợp mọi mã ⇒ ffill(limit=7) và
        # trung bình quý của feed phụ thuộc tập mã này — đổi tập mã là đổi c (đo: lệch tới 0,0014 khi chỉ lấy 2 mã).
        C = bq("""SELECT metric_key,source,observation_date,value FROM tav2_bq.commodity_prices WHERE cadence='daily' AND (
 (source='trading_economics' AND metric_key IN ('steel','iron_ore_cny','corn','polyvinyl')) OR
 (source='sunsirs' AND metric_key IN ('coke','soybean_meal_cny','yellow_phosphorus','caustic_soda','polyester_staple_fiber','pta','ethylene_glycol')))""")
        M = bq("SELECT series_key,observation_date,value FROM tav2_bq.macro_indicator WHERE series_key IN ('vn_usdvnd','cn_usdcny')")
    C = C.copy()
    C["observation_date"] = pd.to_datetime(C.observation_date)
    C = C.pivot_table(index="observation_date", columns="metric_key", values="value").sort_index()
    M = M[M.series_key.isin(["vn_usdvnd", "cn_usdcny"])].copy()
    M["observation_date"] = pd.to_datetime(M.observation_date)
    M = M.pivot_table(index="observation_date", columns="series_key", values="value").sort_index()
    return C, M


def load_fin(a):
    if a.fin_csv:
        f = pd.read_csv(a.fin_csv)
    else:
        f = bq("SELECT quarter,Release_Date,NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,Revenue_P4 FROM tav2_bq.ticker_financial WHERE ticker='DBC'")
    f["Release_Date"] = pd.to_datetime(f.Release_Date)
    return f.sort_values("Release_Date").drop_duplicates("quarter", keep="first")  # bản công bố ĐẦU TIÊN


def load_px(a, since):
    if a.px_csv:
        p = pd.read_csv(a.px_csv)
    else:
        p = bq(f"SELECT time,ticker,Close FROM tav2_bq.ticker WHERE ticker IN ('DBC','VNINDEX') AND time>='{since}'")
    p["time"] = pd.to_datetime(p.time)
    return p.pivot_table(index="time", columns="ticker", values="Close").sort_index().dropna()


# ---------------- công thức đóng băng (nguyên văn a4_nowcast.py họ 2)
def qmean(s, minn):
    s = s.dropna(); m = s.resample("QE").mean(); n = s.resample("QE").count()
    return m.where(n >= minn), n


def signal(hog, C, M):
    fx = M[["vn_usdvnd", "cn_usdcny"]].dropna(how="all").ffill(limit=7)
    d = pd.DataFrame({"corn": C.corn, "sbm": C.soybean_meal_cny}).join(fx, how="outer").ffill(limit=7)
    feed = W_CORN * d.corn / 100 / 25.4 * d.vn_usdvnd + W_SBM * d.sbm / 1000 * d.vn_usdvnd / d.cn_usdcny
    hq, nh = qmean(hog, MIN_HOG); fq, nf = qmean(feed, MIN_FEED)
    Mg = hq - FCR * fq
    c = (Mg - Mg.shift(4)) / hq.shift(4)
    return pd.DataFrame({"hog_q": hq, "hog_q4": hq.shift(4), "n_hog": nh, "feed_q": fq, "feed_q4": fq.shift(4),
                         "n_feed": nf, "margin_q": Mg, "margin_q4": Mg.shift(4), "c": c}), feed


def struct_flag(r):
    f = []
    ratio = FCR * r.feed_q / r.hog_q
    if not RATIO_RANGE[0] <= ratio <= RATIO_RANGE[1]:
        f.append(f"RATIO_OUT({ratio:.3f})")
    if not HOG_RANGE[0] <= r.hog_q <= HOG_RANGE[1]:
        f.append(f"HOG_OUT({r.hog_q:.0f})")
    return ";".join(f)


def sue2(r):  # = commodity_sue_decomp_forward_tracker.sue2 = surprise_B_MA của lag_live_schedule.py
    v = [r.NP_P1, r.NP_P2, r.NP_P3, r.NP_P4]
    if pd.isna(r.NP_P0) or all(pd.isna(x) for x in v):
        return np.nan
    e = np.nanmean(v)
    return float(np.clip((r.NP_P0 - e) / max(abs(e), 1e9), -5, 5))


def np_d(r):  # = đích A4 = sue1 của PREREG-4
    if not (pd.notna(r.Revenue_P4) and r.Revenue_P4 > 0 and pd.notna(r.NP_P0) and pd.notna(r.NP_P4)):
        return np.nan
    return float(np.clip((r.NP_P0 - r.NP_P4) / r.Revenue_P4, -0.5, 0.5))


# ---------------- sổ
def read(path, cols):
    return pd.read_csv(path, dtype=str) if os.path.exists(path) else pd.DataFrame(columns=cols)


def append(path, row, cols):
    new = not os.path.exists(path)
    line = pd.DataFrame([row], columns=cols).to_csv(index=False, header=new)
    with open(path, "a") as fh:
        fh.write(line); fh.flush(); os.fsync(fh.fileno())


def cmd_nowcast(a, D):
    nu = now_utc(a); today = nu.tz_convert(ICT).date()
    q = pd.Period(a.quarter, "Q") if a.quarter else pd.Period(pd.Timestamp(today), "Q") - 1
    if q < pd.Period(FIRST_Q, "Q"):
        sys.exit(f"{q} < {FIRST_Q}: ngoài phạm vi forward (lịch sử đã thấy trong A4)")
    qend = q.end_time.normalize()
    if pd.Timestamp(today) <= qend:
        sys.exit(f"{q} chưa kết thúc (hôm nay ICT {today})")
    led = read(D["now"], NOW_COLS)
    if str(q) in set(led.quarter):
        print(f"{q}: đã có dòng nowcast — append-only, không làm gì"); return 0
    hog = load_hog(a); C, M = load_feed_inputs(a)
    hog_max = hog.index.max(); feed_max = min(C.corn.dropna().index.max(), C.soybean_meal_cny.dropna().index.max())
    if hog_max < qend - pd.Timedelta(days=3) or feed_max < qend - pd.Timedelta(days=5):
        print(f"{q}: WAIT — dữ liệu chưa phủ cuối quý (heo tới {hog_max.date()}, TACN tới {feed_max.date()}); không ghi")
        return 3
    S, _ = signal(hog[hog.index <= qend], C[C.index <= qend], M[M.index <= qend])
    if qend not in S.index or pd.isna(S.at[qend, "c"]):
        print(f"{q}: WAIT — thiếu quan sát (n_hog/n_feed dưới ngưỡng); không ghi"); return 3
    r = S.loc[qend]
    F = load_fin(a); rel = F[F.quarter == str(q)]
    seen = bool(len(rel)) and rel.Release_Date.iloc[0].date() <= today
    payload = json.dumps({k: (None if pd.isna(r[k]) else round(float(r[k]), 10)) for k in S.columns}, sort_keys=True)
    row = dict(quarter=str(q), qend=qend.date(), run_ts_utc=nu.strftime("%Y-%m-%dT%H:%M:%SZ"), run_date_ict=today,
               status="LATE" if seen else "ON_TIME", counts=not seen, release_seen=seen,
               **{k: r[k] for k in ["hog_q", "hog_q4", "n_hog", "feed_q", "feed_q4", "n_feed", "margin_q", "margin_q4", "c"]},
               np_d_hat=NP_A + NP_B * r.c, struct_flag=struct_flag(r), hog_max_date=hog_max.date(), feed_max_date=feed_max.date(),
               inputs_sha256=hashlib.sha256(payload.encode()).hexdigest(), script_md5=md5(os.path.abspath(__file__)),
               prereg_md5=md5(os.path.join(HERE, "PREREG5.md")))
    append(D["now"], row, NOW_COLS)
    print(f"{q}: ghi nowcast status={row['status']} counts={row['counts']} (KHÔNG in giá trị c — xem sổ). "
          "Bước tiếp: git commit sổ TRƯỚC ngày DBC công bố (PREREG5 §6).")
    return 0


def cmd_outcome(a, D):
    nu = now_utc(a); today = pd.Timestamp(nu.tz_convert(ICT).date())
    led = read(D["now"], NOW_COLS)
    if led.empty:
        print("chưa có nowcast nào"); return 0
    F = load_fin(a); out = read(D["out"], OUT_COLS); dr = read(D["drift"], DRIFT_COLS)
    px = None; added = 0
    for _, n in led.iterrows():
        rel = F[(F.quarter == n.quarter) & (F.Release_Date <= today)]
        if not len(rel):
            continue
        r = rel.iloc[0]
        if n.quarter not in set(out.quarter):
            y = np_d(r); c = float(n.c)
            row = dict(quarter=n.quarter, release_date=r.Release_Date.date(), first_seen_utc=nu.strftime("%Y-%m-%dT%H:%M:%SZ"),
                       NP_P0=r.NP_P0, NP_P4=r.NP_P4, Revenue_P4=r.Revenue_P4, np_d=y, sue2=sue2(r),
                       hit=(c * y > 0) if pd.notna(y) else "")
            append(D["out"], row, OUT_COLS); out = read(D["out"], OUT_COLS); added += 1
        for H in HORIZONS:
            if ((dr.quarter == n.quarter) & (dr.H == str(H))).any():
                continue
            if px is None:
                px = load_px(a, (r.Release_Date - pd.Timedelta(days=10)).date())
            px_t = px[px.index <= today]
            i0 = px_t.index.searchsorted(r.Release_Date, side="right") - 1  # t0 = phiên cuối ≤ ngày công bố
            if i0 < 0 or i0 + H >= len(px_t):
                continue
            p0, pH = px_t.iloc[i0], px_t.iloc[i0 + H]
            rd, rv = np.log(pH.DBC / p0.DBC), np.log(pH.VNINDEX / p0.VNINDEX)
            append(D["drift"], dict(quarter=n.quarter, H=H, t0=px_t.index[i0].date(), tH=px_t.index[i0 + H].date(),
                                    ret_dbc=rd, ret_vni=rv, excess=rd - rv, first_seen_utc=nu.strftime("%Y-%m-%dT%H:%M:%SZ")),
                   DRIFT_COLS)
            dr = read(D["drift"], DRIFT_COLS); added += 1
    flag = early_stop(led, out)
    print(f"outcome: thêm {added} dòng; cờ dừng sớm: {flag or 'không'}")
    return 0


def counted(led, out):
    m = led[led.counts.astype(str) == "True"].merge(out, on="quarter")
    m = m.assign(c=pd.to_numeric(m.c, errors="coerce"), np_d=pd.to_numeric(m.np_d, errors="coerce")).dropna(subset=["c", "np_d"])
    return m.sort_values("quarter").reset_index(drop=True)


def early_stop(led, out):
    m = counted(led, out)
    if len(m) >= 3 and ((m.c * m.np_d).tail(3) <= 0).all():
        return "EARLY_STOP_3_MISS (3 quý liên tiếp nowcast trượt dấu) ⇒ PREREG5 §3.3: báo user, đề xuất ĐÓNG"
    return ""


def decide(m, K):
    x = m.head(K); S = int((x.c * x.np_d > 0).sum()); rho = float(spearmanr(x.c, x.np_d)[0])
    if K == 8:
        dec = "CLOSE" if (S <= 4 or rho <= 0) else ("CONTINUE_ELIGIBLE" if (S >= 7 and rho >= 0.69) else "CONTINUE")
    elif K == 12:
        dec = "CLOSE" if (S <= 7 or rho <= 0) else ("CONTINUE_ELIGIBLE" if (S >= 10 and rho >= 0.61) else "CONTINUE")
    else:
        dec = "CONTINUE_ELIGIBLE" if (S >= 12 and rho >= 0.53) else "CLOSE"
    return S, rho, dec


def cmd_review(a, D):
    nu = now_utc(a); K = a.k
    m = counted(read(D["now"], NOW_COLS), read(D["out"], OUT_COLS))
    ok = K in CHECKPOINTS and len(m) >= K
    append(D["audit"], dict(ts_utc=nu.strftime("%Y-%m-%dT%H:%M:%SZ"), k=K, n_counted=len(m), allowed=ok),
           ["ts_utc", "k", "n_counted", "allowed"])
    if not ok:
        sys.exit(f"TỪ CHỐI: review chỉ tại mốc {CHECKPOINTS} khi đủ quý (hiện {len(m)} quý counted) — PREREG5 §3")
    S, rho, dec = decide(m, K)
    print(f"mốc K={K} ({m.quarter.iloc[0]}→{m.quarter.iloc[K-1]}): trùng dấu {S}/{K}, Spearman {rho:.3f} ⇒ {dec}")
    print("CONTINUE_ELIGIBLE KHÔNG phải GO wire: chỉ được xin quant-skeptic + user cho một PREREG sử dụng riêng (PREREG5 §4).")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["nowcast", "outcome", "review"])
    p.add_argument("--quarter"); p.add_argument("--k", type=int, default=8)
    p.add_argument("--data-dir", default=os.path.join(HERE, "ledger"))
    p.add_argument("--now"); p.add_argument("--hog-csv"); p.add_argument("--comm-parquet"); p.add_argument("--macro-parquet")
    p.add_argument("--fin-csv"); p.add_argument("--px-csv")
    a = p.parse_args(argv)
    os.makedirs(a.data_dir, exist_ok=True)
    D = {k: os.path.join(a.data_dir, f) for k, f in
         dict(now="nowcast.csv", out="outcomes.csv", drift="drift.csv", audit="review_audit.csv").items()}
    return dict(nowcast=cmd_nowcast, outcome=cmd_outcome, review=cmd_review)[a.cmd](a, D)


if __name__ == "__main__":
    sys.exit(main())
