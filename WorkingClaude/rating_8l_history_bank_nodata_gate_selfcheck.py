#!/usr/bin/env python3
"""rating_8l_history_bank_nodata_gate_selfcheck.py — selfcheck phương án B bank-nodata (user duyệt 2026-11-19
21:5x ICT, job Taylor_20261119_145312): rating_8l_history.override_current_bank_aq hạ hạng (CHỈ hạ) dòng
mới nhất của mã ngân hàng thiếu lens = max(proxy, live, 4), có cổng chặn G1-G4.

BẤT BIẾN:
  T1 proxy 3/2/5 + live nodata 4 ⇒ 4/4/5 (max); live nodata 3 (rating_8l.py cũ) vẫn ⇒ 4 (sàn).
  T2 lens đọc lỗi / rỗng ⇒ KHÔNG hạ + cảnh báo (G1).
  T3 tỉ lệ nodata > ngưỡng ⇒ KHÔNG hạ + cảnh báo (G3).
  T4 mã nhãn nodata có trong lens ⇒ KHÔNG hạ (G2).
  T5 mã có lens ở snapshot kỳ trước nay nodata / snapshot hỏng ⇒ KHÔNG hạ (G4).
  T6 mọi dòng KHÁC dòng mới nhất của mã nodata giống từng byte trước/sau.
  T7 live_run: cảnh báo gọi notify (giả) + snapshot chỉ ghi khi cổng không bật; run thí nghiệm không gửi/ghi.
  T8 ĐẦU-CUỐI: history canonical thật + rating_8l.csv thật + lens thật ⇒ dedup kiểu fa_ratings_8l
     (ROW_NUMBER ticker,eff_date ORDER BY q_time DESC) + đọc as-of mới nhất ⇒ mọi mã bank-nodata >3.
  T9 ĐỘT BIẾN: (a) max→proxy-only, (b) bỏ cổng chặn ⇒ các test tương ứng PHẢI FAIL.

PHỤ THUỘC MÔI TRƯỜNG: TZ — chỉ _write_lens_snapshot gọi now(ZoneInfo ICT) (neo tường minh); vẫn chạy
env -u TZ và TZ=Asia/Tokyo. WORKDIR_8L — T8 đọc data/ canonical (CHỈ ĐỌC); mọi test khác dùng thư mục tạm.
Notify luôn trỏ script giả (R8L_BANK_GATE_NOTIFY) ⇒ không bao giờ gửi Discord thật.
Usage: python3 rating_8l_history_bank_nodata_gate_selfcheck.py
"""
import os, sys, tempfile, importlib.util, json, stat
os.environ.setdefault("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
CANON = os.environ["WORKDIR_8L"]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import warnings; warnings.filterwarnings("ignore")
import pandas as pd
import rating_8l_history as H

N_OK, FAILS = 0, []
def ok(cond, label, detail=""):
    global N_OK
    if cond: N_OK += 1
    else: FAILS.append(label + (f" -- {detail}" if detail else ""))

TMP = tempfile.mkdtemp(prefix="r8l_bnd_gate_")
NOTIFY_LOG = os.path.join(TMP, "notify_calls.log")
FAKE_NOTIFY = os.path.join(TMP, "fake_notify.sh")
with open(FAKE_NOTIFY, "w") as f:
    f.write(f'#!/bin/sh\nprintf "%s|%s\\n" "$2" "$1" >> "{NOTIFY_LOG}"\n')
os.chmod(FAKE_NOTIFY, os.stat(FAKE_NOTIFY).st_mode | stat.S_IEXEC)
os.environ["R8L_BANK_GATE_NOTIFY"] = FAKE_NOTIFY          # KHÔNG BAO GIỜ notify thật


def hist(rows):
    return pd.DataFrame([dict(ticker=t, eff_date=e, q_time=e, route="BANK", rating=r, core_score=0,
                              tier={1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}[r]) for t, e, r in rows])


def run(M, h, live, lens=("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9"), snapshot=None,
        live_run=False, lens_raw=None):
    """Chạy M.override_current_bank_aq trên WORKDIR tạm. Trả (out, alert_text, notify_calls, snap_after)."""
    wd = tempfile.mkdtemp(dir=TMP); d = os.path.join(wd, "data"); os.makedirs(d)
    pd.DataFrame(live, columns=["ticker", "route", "rating", "note"]).to_csv(os.path.join(d, "rating_8l.csv"), index=False)
    if lens_raw is not None:
        open(os.path.join(d, "bank_lens_v3.csv"), "w").write(lens_raw)
    elif lens is not None:
        pd.DataFrame({"ticker": list(lens), "ROE": 0.15}).to_csv(os.path.join(d, "bank_lens_v3.csv"), index=False)
    snap = os.path.join(d, "bank_lens_ticker_snapshot.json")
    if snapshot is not None:
        open(snap, "w").write(snapshot if isinstance(snapshot, str) else json.dumps({"lens_tickers": snapshot}))
    sink = os.path.join(wd, "alert.txt")
    if os.path.exists(NOTIFY_LOG): os.unlink(NOTIFY_LOG)
    env_keep = {k: os.environ.get(k) for k in ("R8L_BANK_GATE_ALERT_SINK", "R8L_BANK_LENS_SNAPSHOT", "MIKE_BOT_TEST_MODE")}
    os.environ["R8L_BANK_GATE_ALERT_SINK"] = sink; os.environ["R8L_BANK_LENS_SNAPSHOT"] = snap
    os.environ.pop("MIKE_BOT_TEST_MODE", None)
    old = M.WORKDIR
    try:
        M.WORKDIR = wd
        out = M.override_current_bank_aq(h.copy(), live_run=live_run)
    finally:
        M.WORKDIR = old
        for k, v in env_keep.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    alert = open(sink).read() if os.path.exists(sink) else ""
    calls = open(NOTIFY_LOG).read() if os.path.exists(NOTIFY_LOG) else ""
    snap_after = json.load(open(snap)) if os.path.exists(snap) and snapshot is None else None
    return out, alert, calls, snap_after


def latest(out, tk):
    s = out[out["ticker"] == tk].sort_values("eff_date")
    return int(s["rating"].iloc[-1])


H3 = [("PX3", "2026-01-01", 3), ("PX3", "2026-10-01", 3), ("PX2", "2026-10-01", 2), ("PX5", "2026-10-01", 5),
      ("RL", "2026-10-01", 1)]
# 3 nodata / 4 bank = 75% ⇒ cần thêm mã lens để KHÔNG vượt ngưỡng 45%: L1..L5 có lens & live thật
LENS_LIVE = [(f"L{i}", "BANK", 3, "profitable (AQ-modulated)") for i in range(1, 6)]


def t1_max(M):
    live = [("PX3", "BANK", 4, "bank-nodata"), ("PX2", "BANK", 4, "bank-nodata"), ("PX5", "BANK", 4, "bank-nodata"),
            ("RL", "BANK", 2, "strong asset-quality")] + LENS_LIVE
    out, alert, _, _ = run(M, hist(H3), live, lens=("RL", "L1", "L2", "L3", "L4", "L5"))
    got = [latest(out, t) for t in ("PX3", "PX2", "PX5")]
    ok(got == [4, 4, 5], "T1 proxy 3/2/5 + live nodata 4 ⇒ 4/4/5 (max)", str(got))
    ok(latest(out, "RL") == 2, "T1 mã có lens thật vẫn nhận hạng live (2)", str(latest(out, "RL")))
    ok(alert == "", "T1 cổng KHÔNG bật khi dữ liệu lành", alert[:200])
    live3 = [(t, b, 3, n) if n == "bank-nodata" else (t, b, r, n) for t, b, r, n in live]
    out, _, _, _ = run(M, hist(H3), live3, lens=("RL", "L1", "L2", "L3", "L4", "L5"))
    got = [latest(out, t) for t in ("PX3", "PX2", "PX5")]
    ok(got == [4, 4, 5], "T1 live nodata=3 (rating_8l.py chưa đổi) vẫn ⇒ 4/4/5 nhờ sàn 4", str(got))
    live_nr = [("PX2", "BANK", 3, "bank-noROE")] + LENS_LIVE
    out, _, _, _ = run(M, hist(H3), live_nr, lens=("PX2", "L1", "L2", "L3", "L4", "L5"))
    ok(latest(out, "PX2") == 4, "T1 bank-noROE live (lens có mã, ROE trống) ⇒ sàn 4", str(latest(out, "PX2")))
    return got


def _gate_case(M, label, code, **kw):
    live = [("PX3", "BANK", 4, "bank-nodata"), ("PX2", "BANK", 4, "bank-nodata")] + LENS_LIVE
    out, alert, _, _ = run(M, hist(H3), live, **kw)
    ok([latest(out, "PX3"), latest(out, "PX2")] == [3, 2], f"{label} ⇒ KHÔNG hạ (giữ proxy 3/2)",
       str([latest(out, "PX3"), latest(out, "PX2")]))
    ok(code in alert, f"{label} ⇒ có cảnh báo chứa '{code}'", alert[:300])


def t2_lens_fail(M):
    _gate_case(M, "T2 lens file vắng", "G1", lens=None)
    _gate_case(M, "T2 lens rỗng (chỉ header)", "G1", lens_raw="ticker,ROE\n")
    _gate_case(M, "T2 lens hỏng (không cột ticker)", "G1", lens_raw="foo,bar\n1,2\n")


def t3_ratio(M):
    # 4 nodata / 7 bank = 57% > 45%; không mã nào có trong lens (G2 không bật) ⇒ chỉ G3
    live = [(t, "BANK", 4, "bank-nodata") for t in ("PX3", "PX2", "N1", "N2")] + LENS_LIVE[:3]
    out, alert, _, _ = run(M, hist(H3), live, lens=("L1", "L2", "L3"))
    ok([latest(out, "PX3"), latest(out, "PX2")] == [3, 2], "T3 tỉ lệ nodata 57% > ngưỡng ⇒ KHÔNG hạ")
    ok("G3" in alert and "G2" not in alert and "G1" not in alert, "T3 cảnh báo đúng nhánh G3", alert[:300])
    # ngay dưới ngưỡng: 4/9 = 44,4% ⇒ hạ bình thường
    live = [(t, "BANK", 4, "bank-nodata") for t in ("PX3", "PX2", "N1", "N2")] + LENS_LIVE
    out, alert, _, _ = run(M, hist(H3), live, lens=("L1", "L2", "L3", "L4", "L5"))
    ok([latest(out, "PX3"), latest(out, "PX2")] == [4, 4] and alert == "", "T3 4/9=44,4% ≤ 45% ⇒ hạ bình thường",
       alert[:200])
    ok(H.BANK_NODATA_MAX_FRAC == 0.45 and 10 / 28 <= H.BANK_NODATA_MAX_FRAC < 13 / 28,
       "T3 ngưỡng 45%: hiện trạng 10/28 qua, mất 3 mã lens (13/28) bật")


def t4_inconsistent(M):
    _gate_case(M, "T4 mã nhãn nodata có trong lens (PX3)", "G2", lens=("PX3", "L1", "L2", "L3", "L4", "L5"))


def t5_snapshot(M):
    _gate_case(M, "T5 PX2 có lens kỳ trước nay nodata", "G4", lens=("L1", "L2", "L3", "L4", "L5"),
               snapshot=["PX2", "L1", "L2", "L3", "L4", "L5"])
    _gate_case(M, "T5 snapshot hỏng", "G4", lens=("L1", "L2", "L3", "L4", "L5"), snapshot="{not json")


def t6_history_bytes(M):
    rows = [(t, f"20{y:02d}-0{q}-15", r) for t in ("PX3", "PX2", "AA", "BB") for y in range(14, 27)
            for q, r in ((2, 2), (5, 3), (8, 5))]
    h = hist(rows)
    live = [("PX3", "BANK", 4, "bank-nodata"), ("PX2", "BANK", 3, "bank-nodata"),
            ("AA", "BANK", 1, "elite asset-quality")] + LENS_LIVE
    out, _, _, _ = run(M, h, live, lens=("AA", "L1", "L2", "L3", "L4", "L5"))
    lat = {h[h.ticker == t].sort_values("eff_date").index[-1] for t in ("PX3", "PX2", "AA")}
    keep = [i for i in h.index if i not in lat]
    ok(h.loc[keep].to_csv(index=False) == out.loc[keep].to_csv(index=False),
       f"T6 {len(keep)} dòng lịch sử (ngoài dòng mới nhất) giống từng byte")
    ok(len(out) == len(h), "T6 không thêm/bớt dòng")
    ok(latest(out, "PX3") == 5 and latest(out, "PX2") == 5, "T6 proxy 5 + nodata ⇒ vẫn 5 (không bao giờ nâng)")


def t7_live_run(M):
    live = [("PX3", "BANK", 4, "bank-nodata")] + LENS_LIVE
    _, alert, calls, snap = run(M, hist(H3), live, lens=("L1", "L2", "L3", "L4", "L5"), live_run=True)
    ok(snap is not None and snap.get("lens_tickers") == ["L1", "L2", "L3", "L4", "L5"],
       "T7 live_run + cổng không bật ⇒ ghi snapshot lens", str(snap))
    ok(calls == "", "T7 không bật cổng ⇒ không notify", calls)
    _, alert, calls, snap = run(M, hist(H3), live, lens=None, live_run=True)
    ok(calls.startswith("trading_daily|") and "G1" in calls, "T7 live_run + G1 ⇒ notify Trading Daily kèm bằng chứng",
       calls[:200])
    ok(snap is None, "T7 cổng bật ⇒ KHÔNG ghi snapshot", str(snap))
    _, alert, calls, snap = run(M, hist(H3), live, lens=None, live_run=False)
    ok(calls == "" and "G1" in alert and snap is None, "T7 run thí nghiệm ⇒ chỉ log/sink, không notify, không snapshot")


def t8_end_to_end():
    """Dữ liệu THẬT (chỉ đọc): history canonical + rating_8l.csv + bank_lens_v3.csv ⇒ fa_ratings_8l-style."""
    hpath = os.path.join(CANON, "data", "rating_8l_history.csv")
    h = pd.read_csv(hpath)
    live = pd.read_csv(os.path.join(CANON, "data", "rating_8l.csv"))
    nod = sorted(live[(live["route"] == "BANK") & live["note"].astype(str).str.contains("bank-nodata")]["ticker"])
    keep = {k: os.environ.get(k) for k in ("R8L_BANK_GATE_ALERT_SINK", "R8L_BANK_LENS_SNAPSHOT")}
    os.environ["R8L_BANK_GATE_ALERT_SINK"] = os.path.join(TMP, "e2e_alert.txt")
    os.environ["R8L_BANK_LENS_SNAPSHOT"] = os.path.join(TMP, "e2e_nosnap.json")   # không có ⇒ G4 bỏ qua
    old = H.WORKDIR
    try:
        H.WORKDIR = CANON
        out = H.override_current_bank_aq(h.copy(), live_run=False)   # live_run=False: không ghi/gửi gì
    finally:
        H.WORKDIR = old
        for k, v in keep.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    # fa_ratings_8l = dedup (ticker,eff_date) giữ q_time lớn nhất; consumer đọc dòng eff_date mới nhất ≤ ngày
    fa = (out.sort_values(["ticker", "eff_date", "q_time"]).drop_duplicates(["ticker", "eff_date"], keep="last"))
    asof = fa.sort_values("eff_date").groupby("ticker").tail(1).set_index("ticker")["rating"]
    bad = {t: int(asof[t]) for t in nod if t in asof and int(asof[t]) <= 3}
    ok(len(nod) > 0, "T8 dữ liệu thật có mã bank-nodata (test không rỗng)", str(nod))
    ok(not bad, f"T8 ĐẦU-CUỐI: {len(nod)} mã bank-nodata thật ⇒ fa_ratings_8l-style as-of rating >3", str(bad))
    print(f"  [T8] e2e: " + ", ".join(f"{t}={int(asof[t])}" for t in nod if t in asof))
    return bad


def mutant(src_old, src_new, name):
    src = open(H.__file__, encoding="utf-8").read()
    assert src_old in src, f"mutation anchor missing: {src_old}"
    spec = importlib.util.spec_from_loader(name, loader=None); m = importlib.util.module_from_spec(spec)
    m.__file__ = H.__file__
    exec(compile(src.replace(src_old, src_new), H.__file__, "exec"), m.__dict__)
    return m


def t9_mutations():
    for label, a, b, tests in (
        ("max→proxy-only", "new_r = max(cur, nodata_map[tk][0], BANK_NODATA_FLOOR)", "new_r = cur", (t1_max, t6_history_bytes)),
        ("bỏ cổng chặn", "reasons, lens = bank_nodata_gate(lb)", "_r_, lens = bank_nodata_gate(lb); reasons = []",
         (t2_lens_fail, t3_ratio, t4_inconsistent, t5_snapshot))):
        m = mutant(a, b, "mut_" + str(abs(hash(label))))
        n0 = len(FAILS); n_ok0 = N_OK
        for t in tests: t(m)
        caught = len(FAILS) - n0
        del FAILS[n0:]
        globals()["N_OK"] = n_ok0
        ok(caught >= 1, f"T9 ĐỘT BIẾN '{label}' BỊ bắt ({caught} assertion fail)", f"caught={caught}")
        print(f"  [T9] mutation {label}: {caught} assertion(s) FAIL như mong đợi")


if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '<unset>')}  WORKDIR_8L={CANON}")
    t1_max(H); t2_lens_fail(H); t3_ratio(H); t4_inconsistent(H); t5_snapshot(H); t6_history_bytes(H); t7_live_run(H)
    t8_end_to_end()
    t9_mutations()
    import shutil; shutil.rmtree(TMP, ignore_errors=True)
    for f in FAILS: print("FAIL:", f)
    print(f"{'PASS' if not FAILS else 'FAIL'}: {N_OK} ok, {len(FAILS)} fail")
    sys.exit(1 if FAILS else 0)
