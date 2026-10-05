#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck funnel 8L hằng ngày (`discretionary_candidate_funnel.py`, job Taylor_20261005_180152).

Sandbox hoàn toàn (tempdir, rating/forensic/insider giả) — KHÔNG đọc/ghi data/ thật.
Phải PASS dưới `env -u TZ` VÀ TZ lạ (America/New_York, UTC): mtime giả đặt lúc 00:30 ICT để ngày
ICT khác ngày UTC/NY — code đọc giờ máy thay vì ICT sẽ ra sai asof.

    python3 mike/bin/discretionary_candidate_funnel_selfcheck.py            # 1 lượt
    python3 mike/bin/discretionary_candidate_funnel_selfcheck.py --all-tz   # 4 môi trường TZ
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd  # noqa: E402

import discretionary_candidate_funnel as F  # noqa: E402

ICT = F.ICT
N = {"ok": 0, "fail": 0}


def check(cond, msg):
    if cond:
        N["ok"] += 1
    else:
        N["fail"] += 1
        print(f"FAIL: {msg}")


def row(t, route="COMPOUNDER", rating=2, pbz=-1.5, drop=-30.0, pe=5.0, liq=1.0, roe=0.1, cfoa=1.0,
        redflag=None):
    return {"ticker": t, "route": route, "rating": rating, "ROE_Min3Y": roe, "CF_OA_3Y": cfoa,
            "redflag": redflag, "liq_bn": liq, "pb_z": pbz, "drop_pct": drop, "PE": pe,
            "PB": 1.0, "earn_yield": round(1 / pe, 4) if pe and pe > 0 else None}


def base_rating():
    rows = [
        row("AAA"),                                          # A hợp lệ
        row("BAN"),                                          # A nhưng BANNED (giả lập)
        row("HSG"),                                          # A nhưng BANNED THẬT (lag_forensic_filter)
        row("FOR"),                                          # A nhưng forensic exclude
        row("FUT"),                                          # forensic exclude NGÀY SAU asof ⇒ KHÔNG loại
        row("INS"),                                          # A nhưng insider
        row("D19", drop=-19.9),                              # drop -19,9% ⇒ KHÔNG vào A (đơn vị %)
        row("D20", drop=-20.0, pbz=-1.0),                    # biên ⇒ VÀO A
        row("PBZ", pbz=-0.99),                               # pb_z > -1 ⇒ KHÔNG A
        row("R4", rating=4),                                 # rating 4 ⇒ ngoài vũ trụ
        row("GF", roe=-0.01),                                # trượt golden floor
        row("RF", redflag="NP_TTM<0"),                       # redflag
        row("LQ", liq=0.29),                                 # thanh khoản < 0,3
        # Làn B — BANK có earn_yield rất cao (PE 2-3); COMPOUNDER PE 4-9
        row("BK1", route="BANK", pe=2.0, pbz=0.0, drop=-5.0),
        row("BK2", route="BANK", pe=2.5, pbz=0.0, drop=-5.0),
        row("BK3", route="BANK", pe=3.0, pbz=0.0, drop=-5.0),
        row("BK4", route="BANK", pe=3.5, pbz=0.0, drop=-5.0),
        row("CP1", pe=4.0, pbz=0.0, drop=-5.0),
        row("CPX", pe=3.9, pbz=0.0, drop=-5.0),              # ey cao nhất COMPOUNDER nhưng insider
        row("CP2", pe=6.0, pbz=0.0, drop=-5.0),
        row("CP3", pe=8.0, pbz=0.0, drop=-5.0),
        row("CP4", pe=9.0, pbz=0.0, drop=-5.0),
        row("NEG", pe=-3.0, pbz=0.0, drop=-5.0),             # PE<0 ⇒ không vào B
    ]
    return pd.DataFrame(rows)


# AAA..PBZ đều có PE=5 (ey 0,2) — cao hơn CP1 (0,25)? 1/5=0,2 < 1/4=0,25 ⇒ top COMPOUNDER sẽ là
# CP1 (0,25), rồi các mã PE 5 (0,2). Để làn B COMPOUNDER sạch, đặt PE lớn cho các mã thử làn A.
def rating_df():
    df = base_rating()
    lane_a_tests = ["AAA", "BAN", "HSG", "FOR", "FUT", "INS", "D19", "D20", "PBZ", "R4", "GF",
                    "RF", "LQ"]
    df.loc[df["ticker"].isin(lane_a_tests), "PE"] = 50.0
    df.loc[df["ticker"].isin(lane_a_tests), "earn_yield"] = 0.02
    return df


def write_forensic(path):
    pd.DataFrame([
        {"ticker": "FOR", "flag_type": "x", "severity": "exclude", "date": "2026-06-20",
         "source": "t", "note": "n", "review_by": "2027-01-01"},
        {"ticker": "FUT", "flag_type": "x", "severity": "exclude", "date": "2026-12-31",
         "source": "t", "note": "n", "review_by": "2027-01-01"},
        {"ticker": "AAA", "flag_type": "x", "severity": "watch", "date": "2026-06-20",
         "source": "t", "note": "watch không loại", "review_by": "2027-01-01"},
    ]).to_csv(path, index=False)


INSIDER = {"INS": {"last_alert": "2026-09-30"}, "CPX": {"last_alert": "2026-09-30"}}


def test_lanes(tmp):
    fcsv = os.path.join(tmp, "forensic.csv")
    write_forensic(fcsv)
    banned, forensic, insider, _ = F.load_exclusions(dt.date(2026, 10, 5), fcsv, INSIDER)
    banned = banned | {"BAN"}
    check("HSG" in banned, "BANNED thật phải chứa HSG (đọc từ lag_forensic_filter)")
    check("FOR" in forensic and "FUT" not in forensic, f"forensic chỉ áp cờ <= asof: {forensic}")
    check("AAA" not in forensic, "severity=watch KHÔNG được loại")
    cands, excluded = F.build_lanes(rating_df(), banned, forensic, insider)
    A = set(cands.loc[cands["lane"] == "A", "ticker"])
    check(A == {"AAA", "D20", "FUT"}, f"làn A sai: {sorted(A)}")
    for t in ("BAN", "HSG", "FOR", "INS"):
        check(t not in set(cands["ticker"]), f"{t} phải bị loại khỏi mọi làn")
    ex = dict(zip(excluded["ticker"] + "|" + excluded["lane"], excluded["excl_reason"]))
    check(ex.get("HSG|A") == "BANNED", f"HSG lý do loại: {ex.get('HSG|A')}")
    check(ex.get("FOR|A", "").startswith("forensic_exclude"), f"FOR lý do: {ex.get('FOR|A')}")
    check(ex.get("INS|A", "").startswith("insider_sell"), f"INS lý do: {ex.get('INS|A')}")
    check(ex.get("CPX|B", "").startswith("insider_sell"), "CPX phải hiện trong excluded làn B")

    B = cands[cands["lane"] == "B"]
    bank = B[B["route"] == "BANK"]["ticker"].tolist()
    comp = B[B["route"] == "COMPOUNDER"]["ticker"].tolist()
    check(bank == ["BK1", "BK2", "BK3"], f"BANK top-3 theo ey giảm dần: {bank}")
    check(comp == ["CP1", "CP2", "CP3"], f"COMPOUNDER top-3 KHÔNG bị BANK chen, CPX bị loại "
                                         f"không chiếm chỗ: {comp}")
    check(B[B["route"] == "BANK"]["lane_rank"].tolist() == [1, 2, 3], "lane_rank BANK 1..3")
    check("NEG" not in set(B["ticker"]), "PE<0 không vào làn B")
    check(set(B["route"]) == {"BANK", "COMPOUNDER"}, f"route B: {set(B['route'])}")

    # Nhãn: peer COMPOUNDER liq>=0,3 có drop -30 (x vài) và -5 ... trung vị tính ra rồi so -15
    med = cands.loc[cands["ticker"] == "AAA", "route_median_drop"].iloc[0]
    aaa_ctx = cands.loc[cands["ticker"] == "AAA", "context"].iloc[0]
    check(aaa_ctx == ("IDIO" if -30.0 <= med - 15 else "NGÀNH"), f"nhãn AAA {aaa_ctx} med={med}")
    # Ca IDIO rõ: route riêng, 4 peer -2, 1 mã -40 ⇒ IDIO; peer -30 ⇒ NGÀNH
    df2 = pd.DataFrame([row("I1", route="POWER", drop=-40.0)] +
                       [row(f"P{i}", route="POWER", drop=-2.0, pbz=0.5) for i in range(4)] +
                       [row("S1", route="SECURITIES", drop=-30.0)] +
                       [row(f"Q{i}", route="SECURITIES", drop=-28.0, pbz=0.5) for i in range(4)])
    c2, _ = F.build_lanes(df2, set(), {}, {})
    lab = dict(zip(c2.loc[c2["lane"] == "A", "ticker"], c2.loc[c2["lane"] == "A", "context"]))
    check(lab.get("I1") == "IDIO", f"I1 (-40 vs trung vị -2) phải IDIO: {lab}")
    check(lab.get("S1") == "NGÀNH", f"S1 (-30 vs trung vị -28) phải NGÀNH: {lab}")
    line = F.candidate_line(F._rec(c2[c2["ticker"] == "S1"].iloc[0]))
    check("cần Bobby trước" in line, f"nhãn NGÀNH phải ghi 'cần Bobby trước': {line}")


def cands_of(spec):
    """spec: {ticker: pb_z} ⇒ DataFrame làn A tối thiểu cho update_state."""
    return pd.DataFrame([{"ticker": t, "lane": "A", "pb_z": z} for t, z in spec.items()])


def test_state():
    d = lambda s: dt.date.fromisoformat(s)  # noqa: E731
    st, rep = F.update_state({}, cands_of({"X": -1.2, "Y": -1.1}), d("2026-10-01"))
    check({(r["ticker"], r["reason"]) for r in rep} == {("X", "NEW"), ("Y", "NEW")}, f"ngày 1: {rep}")
    st2, rep = F.update_state(st, cands_of({"X": -1.2, "Y": -1.1}), d("2026-10-01"))
    check({r["ticker"] for r in rep} == {"X", "Y"} and st2 == st,
          "chạy lại cùng asof: cùng danh sách báo + state không đổi")
    st, rep = F.update_state(st, cands_of({"X": -1.5, "Y": -1.1}), d("2026-10-02"))
    check(rep == [], f"ngày 2 liên tục, pb_z X giảm 0,3 (<0,5) ⇒ không báo: {rep}")
    st, rep = F.update_state(st, cands_of({"X": -1.7}), d("2026-10-05"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("X", "PBZ_DROP")],
          f"X giảm 0,5 so lần BÁO trước (-1,2) ⇒ PBZ_DROP dù trong cooldown: {rep}")
    check(rep[0]["prev_pb_z"] == -1.2, f"prev_pb_z = pb_z lần báo trước: {rep[0]}")
    # Y rời làn 10-05, quay lại 10-06 (5 ngày sau lần báo) ⇒ cooldown chặn
    st, rep = F.update_state(st, cands_of({"X": -1.7, "Y": -1.1}), d("2026-10-06"))
    check(rep == [], f"Y quay lại trong cooldown 30 ngày ⇒ không báo: {rep}")
    st, rep = F.update_state(st, cands_of({"X": -1.7}), d("2026-10-20"))
    st, rep = F.update_state(st, cands_of({"X": -1.7, "Y": -1.1}), d("2026-10-30"))
    check(rep == [], f"Y quay lại ngày thứ 29 ⇒ vẫn cooldown: {rep}")
    st, rep = F.update_state(st, cands_of({"X": -1.7}), d("2026-11-02"))
    st, rep = F.update_state(st, cands_of({"X": -1.7, "Y": -1.1}), d("2026-11-03"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("Y", "NEW")],
          f"Y rời rồi quay lại sau 33 ngày ⇒ NEW: {rep}")
    # Ở lì trong làn quá 30 ngày KHÔNG tự báo lại
    st, rep = F.update_state(st, cands_of({"X": -1.7, "Y": -1.1}), d("2026-12-31"))
    check(rep == [], f"ở liên tục không tự báo lại sau cooldown: {rep}")
    # Cùng ticker khác làn = khoá riêng
    c = pd.DataFrame([{"ticker": "X", "lane": "B", "pb_z": -1.7}])
    st, rep = F.update_state(st, c, d("2027-01-04"))
    check([(r["ticker"], r["lane"], r["reason"]) for r in rep] == [("X", "B", "NEW")],
          f"X vào làn B lần đầu ⇒ NEW riêng: {rep}")


def set_mtime_ict(path, y, m, dd, hh, mi):
    ts = dt.datetime(y, m, dd, hh, mi, tzinfo=ICT).timestamp()
    os.utime(path, (ts, ts))


def test_run_daily_and_files(tmp):
    base = os.path.join(tmp, "data")
    os.makedirs(base)
    rcsv = os.path.join(tmp, "rating_8l.csv")
    fcsv = os.path.join(tmp, "forensic.csv")
    write_forensic(fcsv)
    rating_df().to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 6, 0, 30)          # 00:30 ICT = 05/10 theo UTC & New York
    now = dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT)
    r1 = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    check(r1["asof"] == "2026-10-06", f"asof phải là ngày ICT của mtime, được {r1['asof']}")
    check(r1["warnings"] == [], f"rating hôm nay ⇒ không cảnh báo: {r1['warnings']}")
    check(r1["snapshot"]["status"] == "created", f"snapshot lần 1: {r1['snapshot']}")
    P = F.daily_paths(base)
    snap = os.path.join(P["snap_dir"], "rating_8l_2026-10-06.csv")
    check(os.path.exists(snap), "snapshot đúng tên rating_8l_<asof ICT>.csv")
    r2 = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    check(r2["snapshot"]["status"] == "unchanged", f"snapshot lần 2 idempotent: {r2['snapshot']}")
    check(len(os.listdir(P["snap_dir"])) == 1, f"chỉ 1 file snapshot: {os.listdir(P['snap_dir'])}")
    check(r1["reported"] == r2["reported"], "chạy lại cùng asof ⇒ cùng danh sách báo")
    log = pd.read_csv(P["log"])
    check(len(log) == len(r1["candidates"]), f"log không nhân đôi khi chạy lại: {len(log)}")
    check(set(F.LOG_COLS) <= set(log.columns), "log đủ cột")
    check(not any(".tmp" in f for f in os.listdir(base) + os.listdir(P["snap_dir"])),
          "không sót file .tmp")
    # rating đổi trong cùng ngày ⇒ snapshot replaced (bản cuối ngày thắng), vẫn 1 file
    df = rating_df()
    df.loc[df["ticker"] == "AAA", "pb_z"] = -3.0
    df.to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 6, 0, 30)
    r3 = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    check(r3["snapshot"]["status"] == "replaced" and len(os.listdir(P["snap_dir"])) == 1,
          f"snapshot cùng ngày nội dung khác ⇒ replaced: {r3['snapshot']}")
    # ngày sau, rating CŨ (pt_8l lỗi) ⇒ cảnh báo
    now2 = dt.datetime(2026, 10, 7, 19, 35, tzinfo=ICT)
    r4 = F.run_daily(rcsv, base, False, now2, fcsv, INSIDER)
    check(any("KHÔNG phải của hôm nay" in w for w in r4["warnings"]), f"cảnh báo rating cũ: {r4}")
    # dry-run (write=False) không ghi gì
    st_before = open(P["state"]).read()
    F.run_daily(rcsv, base, False, now2, fcsv, INSIDER)
    check(open(P["state"]).read() == st_before, "write=False không đụng state")

    # --- khối topic ---
    res = json.load(open(P["result"]))
    blk = F.format_topic_block(res, dt.date(2026, 10, 7))
    check("KẾT QUẢ CŨ" not in blk, f"asof 06/10, sáng 07/10 ⇒ tươi:\n{blk}")
    check("mã mới" in blk and "AAA" in blk, f"có mã mới phải liệt kê:\n{blk}")
    blk = F.format_topic_block(res, dt.date(2026, 10, 8))
    check("KẾT QUẢ CŨ" in blk, f"asof 06/10, sáng 08/10 ⇒ CŨ:\n{blk}")
    res0 = dict(res, reported=[])
    blk = F.format_topic_block(res0, dt.date(2026, 10, 7))
    check(f"0 mới ({res['n_tracking']} đang theo dõi" in blk, f"0 mới:\n{blk}")
    fri = dict(res, asof="2026-10-09")
    check("KẾT QUẢ CŨ" not in F.format_topic_block(fri, dt.date(2026, 10, 12)),
          "T2 sáng đọc kết quả T6 ⇒ tươi")
    check("KẾT QUẢ CŨ" not in F.format_topic_block(fri, dt.date(2026, 10, 11)),
          "CN sáng đọc kết quả T6 ⇒ tươi")
    hol = dict(res, asof="2026-08-28")
    check("KẾT QUẢ CŨ" not in F.format_topic_block(hol, dt.date(2026, 9, 3)),
          "03/09 sau nghỉ lễ 31/08-02/09 đọc kết quả 28/08 ⇒ tươi")
    check("CHƯA có kết quả" in F.format_topic_block(None, dt.date(2026, 10, 7)),
          "thiếu file ⇒ in cảnh báo, không im lặng")
    check(F.print_block(dt.date(2026, 10, 7), os.path.join(tmp, "nope.json")).count("CHƯA có") == 1,
          "print_block với file không tồn tại")


def run_once():
    with tempfile.TemporaryDirectory() as tmp:
        test_lanes(tmp)
        test_state()
        test_run_daily_and_files(tmp)
    tz = os.environ.get("TZ", "<unset>")
    print(f"discretionary_candidate_funnel_selfcheck TZ={tz}: {N['ok']} PASS, {N['fail']} FAIL")
    return 1 if N["fail"] else 0


def main():
    if "--all-tz" in sys.argv:
        rc = 0
        for env_tz in (None, "America/New_York", "UTC", "Asia/Ho_Chi_Minh"):
            env = {k: v for k, v in os.environ.items() if k != "TZ"}
            if env_tz:
                env["TZ"] = env_tz
            rc |= subprocess.run([sys.executable, os.path.abspath(__file__)], env=env).returncode
        return rc
    return run_once()


if __name__ == "__main__":
    sys.exit(main())
