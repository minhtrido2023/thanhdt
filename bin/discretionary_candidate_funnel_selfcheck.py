#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck funnel 8L hằng ngày (`discretionary_candidate_funnel.py`, job Taylor_20261005_180152,
vòng 2 Taylor_20261005_181751).

Sandbox hoàn toàn (tempdir, rating/forensic/insider giả; `anomaly_gate.WORKDIR` trỏ vào tempdir)
— KHÔNG ghi data/ thật (CLI test chỉ ĐỌC data/forensic_flags.csv thật). Phải PASS dưới
`env -u TZ` VÀ TZ lạ: mtime giả đặt lúc 00:30 và 23:30 ICT để ngày ICT khác ngày theo UTC/NY
(00:30) và theo Pacific/Kiritimati UTC+14 (23:30) — code đọc giờ máy thay vì ICT sẽ ra sai asof.

    python3 mike/bin/discretionary_candidate_funnel_selfcheck.py            # 1 lượt
    python3 mike/bin/discretionary_candidate_funnel_selfcheck.py --all-tz   # 4 môi trường TZ
"""
import contextlib
import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd  # noqa: E402

import discretionary_candidate_funnel as F  # noqa: E402
import anomaly_gate  # noqa: E402  (đường dẫn sys.path do F dựng)
import importlib.util  # noqa: E402

# Nạp daily_decision_topic CỦA CÙNG thư mục (worktree) — F chèn mike/bin repo chính vào đầu sys.path,
# `import daily_decision_topic` trơn sẽ lấy nhầm bản canonical.
_spec = importlib.util.spec_from_file_location(
    "daily_decision_topic", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "daily_decision_topic.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

assert os.path.dirname(os.path.abspath(F.__file__)) == os.path.dirname(os.path.abspath(__file__)), \
    f"selfcheck phải thử F cùng thư mục, đang nạp {F.__file__}"
ICT = F.ICT
N = {"ok": 0, "fail": 0}
F.RATING_MIN_ROWS = 10            # rating giả ~30 dòng; sàn thật (500) thử riêng ở test_sanity
FIN_REAL_FLOORS = (F.FIN_MIN_ROWS, F.FIN_MIN_TICKERS)
F.FIN_MIN_ROWS, F.FIN_MIN_TICKERS = 5, 3   # ticker_financial giả; sàn thật thử ở test_lane_c_files


def check(cond, msg):
    if cond:
        N["ok"] += 1
    else:
        N["fail"] += 1
        print(f"FAIL: {msg}")


def raises(fn, exc=Exception):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def row(t, route="COMPOUNDER", rating=2, pbz=-1.5, drop=-30.0, pe=5.0, liq=1.0, roe=0.1, cfoa=1.0,
        redflag=None, icb=9000, ey="auto"):
    return {"ticker": t, "route": route, "rating": rating, "ROE_Min3Y": roe, "CF_OA_3Y": cfoa,
            "redflag": redflag, "liq_bn": liq, "pb_z": pbz, "drop_pct": drop, "PE": pe,
            "PB": 1.0, "ICB_Code": icb,
            "earn_yield": (round(1 / pe, 4) if pe and pe > 0 else None) if ey == "auto" else ey}


LANE_A_TESTS = ["AAA", "BAN", "HSG", "FOR", "FUT", "NOD", "INS", "D19", "D20", "PBZ", "R4", "R3",
                "GF", "ROE0", "CF0", "RF", "LQ", "LQ3"]


def rating_df():
    rows = [
        row("AAA"),                                          # A hợp lệ
        row("BAN"),                                          # A nhưng BANNED (giả lập)
        row("HSG"),                                          # A nhưng BANNED THẬT (lag_forensic_filter)
        row("FOR"),                                          # A nhưng forensic exclude
        row("FUT"),                                          # forensic exclude NGÀY SAU asof ⇒ KHÔNG loại
        row("NOD"),                                          # forensic exclude ngày TRỐNG ⇒ LOẠI
        row("INS"),                                          # A nhưng insider
        row("D19", drop=-19.9),                              # drop -19,9% ⇒ KHÔNG vào A (đơn vị %)
        row("D20", drop=-20.0, pbz=-1.0),                    # biên ⇒ VÀO A
        row("PBZ", pbz=-0.99),                               # pb_z > -1 ⇒ KHÔNG A
        row("R4", rating=4),                                 # rating 4 ⇒ ngoài vũ trụ
        row("R3", rating=3),                                 # rating 3 (biên) ⇒ VÀO
        row("GF", roe=-0.01),                                # trượt golden floor
        row("ROE0", roe=0.0),                                # ROE_Min3Y = 0 (biên) ⇒ VÀO
        row("CF0", cfoa=0.0),                                # CF_OA_3Y = 0 ⇒ RA (cần > 0)
        row("RF", redflag="NP_TTM<0"),                       # redflag
        row("LQ", liq=0.29),                                 # thanh khoản < 0,3
        row("LQ3", liq=0.3),                                 # thanh khoản = 0,3 (biên) ⇒ VÀO
        # Làn B — BANK có earn_yield rất cao (PE 2-3); COMPOUNDER PE 4-9
        row("BK1", route="BANK", pe=2.0, pbz=0.0, drop=-5.0, icb=8355),
        row("BK2", route="BANK", pe=2.5, pbz=0.0, drop=-5.0, icb=8355),
        row("BK3", route="BANK", pe=3.0, pbz=0.0, drop=-5.0, icb=8355),
        row("BK4", route="BANK", pe=3.5, pbz=0.0, drop=-5.0, icb=8355),
        row("CP1", pe=4.0, pbz=0.0, drop=-5.0),
        row("CPX", pe=3.9, pbz=0.0, drop=-5.0),              # ey cao nhất COMPOUNDER nhưng insider
        row("CP2", pe=6.0, pbz=0.0, drop=-5.0),
        row("CP3", pe=8.0, pbz=0.0, drop=-5.0),
        row("CP4", pe=9.0, pbz=0.0, drop=-5.0),
        row("NEG", pe=-3.0, pbz=0.0, drop=-5.0, ey=0.9),     # PE<0 mà ey KHÔNG null ⇒ không vào B
        row("PE0", pe=0.0, pbz=0.0, drop=-5.0, ey=0.95),     # PE=0 mà ey KHÔNG null ⇒ không vào B
    ]
    df = pd.DataFrame(rows)
    # Mã thử làn A: PE lớn để không chen top-3 làn B COMPOUNDER
    df.loc[df["ticker"].isin(LANE_A_TESTS), "PE"] = 50.0
    df.loc[df["ticker"].isin(LANE_A_TESTS), "earn_yield"] = 0.02
    return df


def write_forensic(path, extra=()):
    rows = [
        {"ticker": "FOR", "flag_type": "x", "severity": "exclude", "date": "2026-06-20",
         "source": "t", "note": "n", "review_by": "2027-01-01"},
        {"ticker": "FUT", "flag_type": "x", "severity": "exclude", "date": "2026-12-31",
         "source": "t", "note": "n", "review_by": "2027-01-01"},
        {"ticker": "NOD", "flag_type": "x", "severity": "exclude", "date": "",
         "source": "t", "note": "ngày trống", "review_by": "2027-01-01"},
        {"ticker": "AAA", "flag_type": "x", "severity": "watch", "date": "2026-06-20",
         "source": "t", "note": "watch không loại", "review_by": "2027-01-01"},
    ] + list(extra)
    pd.DataFrame(rows).to_csv(path, index=False)


INSIDER = {"INS": {"last_alert": "2026-09-30"}, "CPX": {"last_alert": "2026-09-30"}}


def sandbox_insider(tmp, content):
    """Trỏ anomaly_gate.WORKDIR vào tmp/ins và ghi insider_flags.json giả (None ⇒ không có file)."""
    root = os.path.join(tmp, "ins")
    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    p = os.path.join(root, "data", "insider_flags.json")
    if os.path.exists(p):
        os.unlink(p)
    if content is not None:
        with open(p, "w", encoding="utf-8") as f:
            f.write(content if isinstance(content, str) else json.dumps(content))
    anomaly_gate.WORKDIR = root
    return p


def test_lanes(tmp):
    fcsv = os.path.join(tmp, "forensic.csv")
    write_forensic(fcsv)
    banned, forensic, insider, warn = F.load_exclusions(dt.date(2026, 10, 5), fcsv, INSIDER)
    banned = banned | {"BAN"}
    check("HSG" in banned, "BANNED thật phải chứa HSG (đọc từ lag_forensic_filter)")
    check("FOR" in forensic and "FUT" not in forensic, f"forensic chỉ áp cờ <= asof: {forensic}")
    check("NOD" in forensic and forensic["NOD"] is None,
          f"forensic exclude ngày trống ⇒ LOẠI (fail-closed): {forensic}")
    check(any("NOD" in w and "fail-closed" in w for w in warn), f"cảnh báo ngày trống: {warn}")
    check("AAA" not in forensic, "severity=watch KHÔNG được loại")
    check(raises(lambda: F.load_exclusions(dt.date(2026, 10, 5), os.path.join(tmp, "x.csv"), {}),
                 FileNotFoundError), "file forensic thiếu ⇒ raise")
    cands, excluded = F.build_lanes(rating_df(), banned, forensic, insider)
    A = set(cands.loc[cands["lane"] == "A", "ticker"])
    check(A == {"AAA", "D20", "FUT", "R3", "ROE0", "LQ3"}, f"làn A sai: {sorted(A)}")
    for t in ("BAN", "HSG", "FOR", "NOD", "INS", "CF0", "GF", "R4", "LQ", "RF", "D19", "PBZ"):
        check(t not in set(cands["ticker"]), f"{t} phải RA khỏi mọi làn")
    ex = dict(zip(excluded["ticker"] + "|" + excluded["lane"], excluded["excl_reason"]))
    check(ex.get("HSG|A") == "BANNED", f"HSG lý do loại: {ex.get('HSG|A')}")
    check(ex.get("FOR|A", "").startswith("forensic_exclude"), f"FOR lý do: {ex.get('FOR|A')}")
    check("ngày trống" in ex.get("NOD|A", ""), f"NOD lý do: {ex.get('NOD|A')}")
    check(ex.get("INS|A", "").startswith("insider_sell"), f"INS lý do: {ex.get('INS|A')}")
    check(ex.get("CPX|B", "").startswith("insider_sell"), "CPX phải hiện trong excluded làn B")

    B = cands[cands["lane"] == "B"]
    bank = B[B["route"] == "BANK"]["ticker"].tolist()
    comp = B[B["route"] == "COMPOUNDER"]["ticker"].tolist()
    check(bank == ["BK1", "BK2", "BK3"], f"BANK top-3 theo ey giảm dần: {bank}")
    check(comp == ["CP1", "CP2", "CP3"], f"COMPOUNDER top-3 KHÔNG bị BANK chen, CPX bị loại "
                                         f"không chiếm chỗ, NEG/PE0 (ey cao, PE<=0) không vào: {comp}")
    check(B[B["route"] == "BANK"]["lane_rank"].tolist() == [1, 2, 3], "lane_rank BANK 1..3")
    check(set(B["route"]) == {"BANK", "COMPOUNDER"}, f"route B: {set(B['route'])}")
    ctx = dict(zip(B["ticker"], B["context"]))
    check(ctx.get("BK1") == "KHÔNG-GIẢM", f"làn B drop -5% ⇒ KHÔNG-GIẢM: {ctx}")
    line = F.candidate_line(F._rec(B[B["ticker"] == "BK1"].iloc[0]))
    check("Bobby" not in line and "KHÔNG-GIẢM" in line, f"KHÔNG-GIẢM không đòi Bobby: {line}")


def test_insider_file(tmp):
    asof = dt.date(2026, 10, 5)
    fcsv = os.path.join(tmp, "forensic_i.csv")
    write_forensic(fcsv)
    sandbox_insider(tmp, {"INS": {"last_alert": "2026-09-30"}, "OLD": {"last_alert": "2026-01-01"},
                          "FUT": {"last_alert": "2026-12-01"}, "BAD": {"tier": "x"},
                          "BAD2": "chuỗi lạ"})
    _, _, ins, warn = F.load_exclusions(asof, fcsv, None)
    check(set(ins) == {"INS"}, f"insider=None đọc file sandbox, cửa sổ 2 đầu 90d: {sorted(ins)}")
    check(any("BAD" in w and "BAD2" in w for w in warn), f"cờ thiếu last_alert ⇒ cảnh báo: {warn}")
    cands, _ = F.build_lanes(rating_df(), set(), {}, ins)
    check("INS" not in set(cands["ticker"]), "INS bị loại qua đường insider=None")
    sandbox_insider(tmp, None)
    _, _, ins, warn = F.load_exclusions(asof, fcsv, None)
    check(ins == {} and any("KHÔNG lọc được" in w for w in warn), f"thiếu file insider: {warn}")
    sandbox_insider(tmp, "{hỏng")
    _, _, ins, warn = F.load_exclusions(asof, fcsv, None)
    check(ins == {} and any("hỏng" in w for w in warn), f"file insider hỏng ⇒ cảnh báo: {warn}")
    sandbox_insider(tmp, "[1, 2]")
    _, _, ins, warn = F.load_exclusions(asof, fcsv, None)
    check(ins == {} and any("schema lạ" in w for w in warn), f"schema lạ ⇒ cảnh báo: {warn}")
    p = sandbox_insider(tmp, {"INS": {"last_alert": "2026-09-30"}})
    check(F._insider_path() == p, "cờ và cảnh báo dùng CÙNG đường dẫn anomaly_gate.WORKDIR")


def test_context():
    cl = F.context_label
    check(cl(-9.9, -50.0) == "KHÔNG-GIẢM", "drop -9,9% ⇒ KHÔNG-GIẢM dù peer giảm sâu")
    check(cl(-10.0, 0.0) == "NGÀNH", "drop -10% (giảm đáng kể), gap 10 < 15 ⇒ NGÀNH")
    check(cl(-25.0, -10.0) == "IDIO", "gap ĐÚNG 15pp ⇒ IDIO (biên <=)")
    check(cl(-24.9, -10.0) == "NGÀNH", "gap 14,9pp ⇒ NGÀNH")
    check(cl(float("nan"), -10.0) == "NGÀNH", "drop không biết ⇒ NGÀNH (bảo thủ)")
    check(cl(-40.0, None) == "NGÀNH", "peer không biết ⇒ NGÀNH (bảo thủ)")

    rows = ([row("I1", route="POWER", drop=-40.0, icb=1111)] +
            [row(f"P{i}", route="POWER", drop=-2.0, pbz=0.5, icb=1111) for i in range(4)] +
            # Biên IDIO: trung vị ICB 2222 = -10, B0 -25 ⇒ gap đúng 15
            [row("B0", route="POWER", drop=-25.0, icb=2222)] +
            [row(f"Q{i}", route="POWER", drop=-10.0, pbz=0.5, icb=2222) for i in range(4)] +
            # gap 12 (< 15, > 10) ⇒ NGÀNH; giết đột biến 15→10
            [row("G12", route="SECURITIES", drop=-22.0, icb=3333)] +
            [row(f"R{i}", route="SECURITIES", drop=-10.0, pbz=0.5, icb=3333) for i in range(4)] +
            # Lọc liq peer: 4 peer thanh khoản -20, 6 peer KÉM thanh khoản -1 ⇒ trung vị -20 (NGÀNH);
            # bỏ lọc ⇒ trung vị -1 ⇒ IDIO (sai)
            [row("L1", route="BROKER", drop=-30.0, icb=4444)] +
            [row(f"S{i}", route="BROKER", drop=-20.0, pbz=0.5, icb=4444) for i in range(4)] +
            [row(f"U{i}", route="BROKER", drop=-1.0, pbz=0.5, liq=0.1, icb=4444) for i in range(6)] +
            # Fallback route: ICB 5555 chỉ 2 mã (<5) ⇒ dùng trung vị route REIT (5 peer -2) ⇒ IDIO;
            # nếu dùng ICB n=2 (trung vị -29,5) ⇒ NGÀNH
            [row("F1", route="REIT", drop=-30.0, icb=5555),
             row("F2", route="REIT", drop=-29.0, pbz=0.5, icb=5555)] +
            [row(f"V{i}", route="REIT", drop=-2.0, pbz=0.5, icb=6666) for i in range(5)])
    c2, _ = F.build_lanes(pd.DataFrame(rows), set(), {}, {})
    a = c2[c2["lane"] == "A"].set_index("ticker")
    lab = a["context"].to_dict()
    check(lab.get("I1") == "IDIO", f"I1 (-40 vs trung vị ICB -2) ⇒ IDIO: {lab}")
    check(lab.get("B0") == "IDIO", f"B0 gap đúng 15 ⇒ IDIO: {lab.get('B0')}")
    check(lab.get("G12") == "NGÀNH", f"G12 gap 12 ⇒ NGÀNH: {lab.get('G12')}")
    check(lab.get("L1") == "NGÀNH" and a.loc["L1", "peer_median_drop"] == -20.0,
          f"peer chỉ tính mã liq>=0,3: L1 {lab.get('L1')} med {a.loc['L1', 'peer_median_drop']}")
    check(lab.get("F1") == "IDIO" and str(a.loc["F1", "peer_basis"]).startswith("route REIT"),
          f"ICB < 5 mã ⇒ fallback route: {lab.get('F1')} {a.loc['F1', 'peer_basis']}")
    check(str(a.loc["I1", "peer_basis"]).startswith("ICB 1111"), f"peer = ICB: {a.loc['I1', 'peer_basis']}")
    line = F.candidate_line(F._rec(c2[c2["ticker"] == "G12"].iloc[0]))
    check("cần Bobby trước" in line, f"nhãn NGÀNH phải ghi 'cần Bobby trước': {line}")


def cands_of(spec):
    """spec: {ticker: pb_z} ⇒ DataFrame làn A tối thiểu cho update_state."""
    return pd.DataFrame([{"ticker": t, "lane": "A", "pb_z": z} for t, z in spec.items()])


def test_state():
    d = lambda s: dt.date.fromisoformat(s)  # noqa: E731
    # Lần đầu (state rỗng) ⇒ SEED, không phải NEW; chạy lại cùng asof vẫn SEED, state không đổi
    st, rep = F.update_state({}, cands_of({"S0": -1.2, "S1": -1.3}), d("2026-09-30"))
    check({r["reason"] for r in rep} == {"SEED"} and len(rep) == 2, f"lần đầu ⇒ SEED: {rep}")
    st_b, rep = F.update_state(st, cands_of({"S0": -1.2, "S1": -1.3}), d("2026-09-30"))
    check({r["reason"] for r in rep} == {"SEED"} and st_b == st, "chạy lại ngày seed: y hệt")
    st, rep = F.update_state(st, cands_of({"S0": -1.2, "X": -1.2, "Y": -1.1}), d("2026-10-01"))
    check({(r["ticker"], r["reason"]) for r in rep} == {("X", "NEW"), ("Y", "NEW")},
          f"sau seed, mã mới ⇒ NEW, S0 ở lì ⇒ im: {rep}")
    st2, rep = F.update_state(st, cands_of({"S0": -1.2, "X": -1.2, "Y": -1.1}), d("2026-10-01"))
    check({r["ticker"] for r in rep} == {"X", "Y"} and st2 == st,
          "chạy lại cùng asof: cùng danh sách báo + state không đổi")
    check(raises(lambda: F.update_state(st, cands_of({"X": -1.2}), d("2026-09-29")), F.AsofRegress),
          "asof đi lùi ⇒ AsofRegress")
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
    snap = json.loads(json.dumps(st))
    st_29, rep = F.update_state(snap, cands_of({"X": -1.7, "Y": -1.1}), d("2026-10-30"))
    check(rep == [], f"Y quay lại ngày thứ 29 ⇒ vẫn cooldown: {rep}")
    _, rep = F.update_state(snap, cands_of({"X": -1.7, "Y": -1.1}), d("2026-10-31"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("Y", "NEW")],
          f"Y quay lại ĐÚNG 30 ngày sau lần báo ⇒ NEW (>= 30): {rep}")
    st, rep = F.update_state(st_29, cands_of({"X": -1.7}), d("2026-11-02"))
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
    check(raises(lambda: F.run_daily(rcsv, base, False, None, fcsv, INSIDER), FileNotFoundError),
          "rating_8l.csv thiếu ⇒ raise")
    df = rating_df()
    df.to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 6, 0, 30)          # 00:30 ICT = 05/10 theo UTC & New York
    now = dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT)
    r1 = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    check(r1["asof"] == "2026-10-06", f"asof phải là ngày ICT của mtime 00:30, được {r1['asof']}")
    check(r1["warnings"] == [] or all("NOD" in w for w in r1["warnings"]),
          f"rating hôm nay ⇒ không cảnh báo ngoài forensic NOD: {r1['warnings']}")
    check(r1["seeded"] == r1["n_lane_a"] + r1["n_lane_b"] and r1["reported"] == [],
          f"lần chạy đầu ⇒ seed, KHÔNG báo hàng loạt: seeded={r1['seeded']} rep={r1['reported']}")
    check(r1["snapshot"]["status"] == "created", f"snapshot lần 1: {r1['snapshot']}")
    P = F.daily_paths(base)
    snap = os.path.join(P["snap_dir"], "rating_8l_2026-10-06.csv")
    check(os.path.exists(snap), "snapshot đúng tên rating_8l_<asof ICT>.csv")
    with open(snap, "rb") as a, open(rcsv, "rb") as b:
        check(a.read() == b.read(), "snapshot = đúng bytes rating đã đọc")
    r2 = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    check(r2["snapshot"]["status"] == "unchanged", f"snapshot lần 2 idempotent: {r2['snapshot']}")
    check(len(os.listdir(P["snap_dir"])) == 1, f"chỉ 1 file snapshot: {os.listdir(P['snap_dir'])}")
    check(r1["reported"] == r2["reported"] and r1["seeded"] == r2["seeded"],
          "chạy lại cùng asof ⇒ cùng kết quả")
    log = pd.read_csv(P["log"])
    check(len(log) == len(r1["candidates"]), f"log không nhân đôi khi chạy lại: {len(log)}")
    check(set(F.LOG_COLS) <= set(log.columns), "log đủ cột")
    check(not any(".tmp" in f for f in os.listdir(base) + os.listdir(P["snap_dir"])),
          "không sót file .tmp")
    res = json.load(open(P["result"]))
    blk = F.format_topic_block(res, dt.date(2026, 10, 7))
    check(f"Khởi tạo: {r1['seeded']} mã đang theo dõi" in blk and "0 mới" not in blk
          and "AAA" not in blk, f"khối ngày seed:\n{blk}")

    # Ngày sau (23:30 ICT = 07/10 theo UTC/NY nhưng 08/10 theo Kiritimati): thêm mã mới NEW1 vào A
    df2 = pd.concat([df, pd.DataFrame([row("NEW1", pe=50.0, ey=0.02)])], ignore_index=True)
    df2.to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 7, 23, 30)
    now2 = dt.datetime(2026, 10, 7, 23, 40, tzinfo=ICT)
    r3 = F.run_daily(rcsv, base, True, now2, fcsv, INSIDER)
    check(r3["asof"] == "2026-10-07", f"asof ngày ICT của mtime 23:30, được {r3['asof']}")
    check([(x["ticker"], x["reason"]) for x in r3["reported"]] == [("NEW1", "NEW")],
          f"ngày 2 chỉ báo mã MỚI: {r3['reported']}")
    res = json.load(open(P["result"]))
    blk = F.format_topic_block(res, dt.date(2026, 10, 8))
    check("1 mã mới/xấu đi (" in blk and "NEW1" in blk and "TỪ PHIÊN" not in blk,
          f"sáng ngay sau asof ⇒ MỚI:\n{blk}")
    blk = F.format_topic_block(res, dt.date(2026, 10, 9))
    check("TỪ PHIÊN 2026-10-07" in blk and "NEW1" in blk, f"sáng thứ 2 sau asof ⇒ 'từ phiên':\n{blk}")
    fri = dict(res, asof="2026-10-09")
    for day, first in ((10, True), (11, False), (12, False)):
        b = F.format_topic_block(fri, dt.date(2026, 10, day))
        check(("TỪ PHIÊN 2026-10-09" in b) != first and "KẾT QUẢ CŨ" not in b,
              f"kết quả T6 đọc ngày {day}/10: first={first}\n{b}")

    # Thứ tự ghi: lỗi ghi KẾT QUẢ ⇒ state KHÔNG được ghi (không đánh dấu 'đã báo' khi chưa có file)
    st_before = open(P["state"]).read()
    df3 = pd.concat([df2, pd.DataFrame([row("NEW2", pe=50.0, ey=0.02)])], ignore_index=True)
    df3.to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 8, 19, 30)
    orig = F._atomic_write_text

    def boom(path, text):
        if path == P["result"]:
            raise OSError("đĩa đầy (giả)")
        return orig(path, text)
    F._atomic_write_text = boom
    try:
        crashed = raises(lambda: F.run_daily(rcsv, base, True,
                                             dt.datetime(2026, 10, 8, 19, 35, tzinfo=ICT),
                                             fcsv, INSIDER), OSError)
    finally:
        F._atomic_write_text = orig
    check(crashed and open(P["state"]).read() == st_before,
          "ghi kết quả lỗi ⇒ state KHÔNG đổi (state ghi SAU CÙNG)")
    r4 = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 8, 19, 35, tzinfo=ICT), fcsv, INSIDER)
    check([x["ticker"] for x in r4["reported"]] == ["NEW2"], f"chạy lại sau crash vẫn báo NEW2: {r4}")

    # asof đi lùi ⇒ không ghi state, cảnh báo, khối ⛔
    st_before = open(P["state"]).read()
    log_before = open(P["log"], "rb").read() if os.path.exists(P["log"]) else None
    snaps_before = {f: open(os.path.join(P["snap_dir"], f), "rb").read()
                    for f in sorted(os.listdir(P["snap_dir"]))} if os.path.isdir(P["snap_dir"]) else {}
    set_mtime_ict(rcsv, 2026, 10, 2, 19, 30)
    r5 = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 8, 19, 40, tzinfo=ICT), fcsv, INSIDER)
    check(not r5["state_ok"] and any("đi lùi" in w for w in r5["warnings"])
          and open(P["state"]).read() == st_before, f"asof lùi ⇒ không ghi state: {r5['warnings']}")
    log_after = open(P["log"], "rb").read() if os.path.exists(P["log"]) else None
    snaps_after = {f: open(os.path.join(P["snap_dir"], f), "rb").read()
                   for f in sorted(os.listdir(P["snap_dir"]))} if os.path.isdir(P["snap_dir"]) else {}
    check(log_after == log_before and snaps_after == snaps_before,
          "asof lùi ⇒ KHÔNG ghi log forward-excess lẫn snapshot PIT của ngày cũ")
    b = F.format_topic_block(r5, dt.date(2026, 10, 9))
    check("⛔" in b and "0 mới" not in b, f"khối khi state không ghi:\n{b}")

    # rating cũ (pt_8l lỗi) ⇒ cảnh báo; dry-run không ghi gì
    set_mtime_ict(rcsv, 2026, 10, 8, 19, 30)
    st_before = open(P["state"]).read()
    files_before = {f: os.path.getmtime(os.path.join(base, f)) for f in os.listdir(base)
                    if os.path.isfile(os.path.join(base, f))}
    r6 = F.run_daily(rcsv, base, False, dt.datetime(2026, 10, 9, 19, 35, tzinfo=ICT), fcsv, INSIDER)
    check(any("KHÔNG phải của hôm nay" in w for w in r6["warnings"]), f"cảnh báo rating cũ: {r6}")
    check(open(P["state"]).read() == st_before and files_before ==
          {f: os.path.getmtime(os.path.join(base, f)) for f in os.listdir(base)
           if os.path.isfile(os.path.join(base, f))}, "write=False không đụng file nào")

    # state hỏng ⇒ raise, KHÔNG reset
    for bad in ("{hỏng", "[1,2]", '{"entries": [1]}'):
        with open(P["state"], "w") as f:
            f.write(bad)
        check(raises(lambda: F.run_daily(rcsv, base, True,
                                         dt.datetime(2026, 10, 8, 19, 35, tzinfo=ICT), fcsv, INSIDER)),
              f"state hỏng {bad!r} ⇒ raise")
        check(open(P["state"]).read() == bad, f"state hỏng {bad!r} KHÔNG bị ghi đè")

    # --- khối topic: cũ / lễ / thiếu file ---
    res = json.load(open(P["result"]))
    check("KẾT QUẢ CŨ" in F.format_topic_block(dict(res, asof="2026-10-06"), dt.date(2026, 10, 8)),
          "asof 06/10, sáng 08/10 ⇒ CŨ")
    hol = dict(res, asof="2026-08-28")
    check("KẾT QUẢ CŨ" not in F.format_topic_block(hol, dt.date(2026, 9, 3)),
          "03/09 sau nghỉ lễ 31/08-02/09 đọc kết quả 28/08 ⇒ tươi")
    check("CHƯA có kết quả" in F.format_topic_block(None, dt.date(2026, 10, 7)),
          "thiếu file ⇒ in cảnh báo, không im lặng")
    check(F.print_block(dt.date(2026, 10, 7), os.path.join(tmp, "nope.json")).count("CHƯA có") == 1,
          "print_block với file không tồn tại")


def test_sanity(tmp):
    base = os.path.join(tmp, "data_s")
    rcsv = os.path.join(tmp, "rating_s.csv")
    fcsv = os.path.join(tmp, "forensic_s.csv")
    write_forensic(fcsv)
    df = rating_df()
    df.loc[df.index[:-3], "pb_z"] = None                       # pb_z non-null ~10% < sàn 80%
    df.to_csv(rcsv, index=False)
    now = dt.datetime.now(ICT)
    r = F.run_daily(rcsv, base, True, now, fcsv, INSIDER)
    P = F.daily_paths(base)
    check(r["sanity_fail"] and not r["state_ok"] and any("pb_z non-null" in w for w in r["warnings"]),
          f"pb_z dưới sàn ⇒ sanity_fail: {r['warnings']}")
    check(not os.path.exists(P["state"]) and not os.path.exists(P["log"]),
          "dưới sàn ⇒ KHÔNG ghi state lẫn log")
    b = F.format_topic_block(r, now.date() + dt.timedelta(days=1))
    check("DƯỚI SÀN" in b and "⛔" in b and "0 mới" not in b, f"khối dưới sàn:\n{b}")
    old = F.RATING_MIN_ROWS
    F.RATING_MIN_ROWS = 500
    try:
        bad = F.rating_sanity(rating_df())
    finally:
        F.RATING_MIN_ROWS = old
    check(any("< sàn 500" in x for x in bad), f"số dòng < 500 ⇒ vi phạm: {bad}")
    check(F.rating_sanity(rating_df()) == [], "rating giả đủ sàn (đã hạ) ⇒ không vi phạm")
    df = rating_df().drop(columns=["ICB_Code"])
    df.to_csv(rcsv, index=False)
    check(raises(lambda: F.read_rating(rcsv), ValueError), "thiếu cột bắt buộc ⇒ raise")


def test_atomic(tmp):
    p = os.path.join(tmp, "atom", "x.json")
    F._atomic_write_text(p, "cũ")
    orig = os.replace

    def bad_replace(a, b):
        raise OSError("replace lỗi (giả)")
    os.replace = bad_replace
    try:
        r = raises(lambda: F._atomic_write_text(p, "mới"), OSError)
    finally:
        os.replace = orig
    check(r and open(p).read() == "cũ", "ghi lỗi ⇒ raise, file cũ nguyên vẹn")
    check(os.listdir(os.path.dirname(p)) == ["x.json"], f"ghi lỗi ⇒ dọn .tmp: {os.listdir(os.path.dirname(p))}")


class _CP:
    def __init__(self, rc, out, err):
        self.returncode, self.stdout, self.stderr = rc, out, err


def test_topic_section():
    orig = T.subprocess.run

    def fake(result=None, exc=None):
        def _run(*a, **k):
            if exc:
                raise exc
            return result
        return _run
    cases = [
        ("rc!=0", fake(_CP(1, "", "Traceback ... ValueError: state hỏng")), "rc=1", "state hỏng"),
        ("stdout rỗng", fake(_CP(0, "  \n", "")), "rc=0", "stdout rỗng"),
        ("timeout", fake(exc=subprocess.TimeoutExpired(cmd="x", timeout=120)), "không chạy được",
         "timed out"),
    ]
    try:
        for name, fn, must1, must2 in cases:
            T.subprocess.run = fn
            try:
                out = T.funnel_section()
            except Exception as e:                      # noqa: BLE001 — chính là điều đang thử
                out = f"CRASH {e!r}"
            check(out.startswith("**D. Funnel 8L**: ⚠️") and must1 in out and must2 in out,
                  f"funnel_section {name}: {out}")
        T.subprocess.run = fake(_CP(0, "**D. Funnel 8L (discretionary)** — ok\n", ""))
        check(T.funnel_section() == "**D. Funnel 8L (discretionary)** — ok", "đường thường")
    finally:
        T.subprocess.run = orig


def test_cli(tmp):
    out = os.path.join(tmp, "cli")
    rcsv = os.path.join(tmp, "rating_cli.csv")
    rating_df().to_csv(rcsv, index=False)
    sandbox_insider(tmp, {"INS": {"last_alert": dt.datetime.now(ICT).date().isoformat()}})
    jp, cp = os.path.join(tmp, "o.json"), os.path.join(tmp, "o.csv")
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        rc = F.main(["--out-dir", out, "--rating-csv", rcsv, "--json", jp, "--csv", cp])
    check(rc == 0 and json.load(open(jp))["n_tracking"] > 0 and len(pd.read_csv(cp)) > 0,
          "đường mới: --json/--csv ghi được")
    check(os.path.exists(F.daily_paths(out)["state"]), "--out-dir ghi vào sandbox")
    with contextlib.redirect_stderr(sink):
        check(raises(lambda: F.main(["--print-block", "--json", jp]), SystemExit),
              "--print-block + --json ⇒ báo lỗi rõ")
    called = []
    orig = F.legacy_main
    F.legacy_main = lambda a: called.append(a.print_block) or 0
    try:
        F.main(["--legacy-fear", "--print-block"])
    finally:
        F.legacy_main = orig
    check(called == [True], "--legacy-fear --print-block ⇒ đường legacy")


# ------------------------------------------------------------------ làn C (job Taylor_20261006_041048)
def fin_row(t, p0, p1, p4, known="2026-07-30", quarter="2026Q2", time=None, rd="same"):
    k = dt.date.fromisoformat(known)
    return {"ticker": t, "time": dt.date.fromisoformat(time) if time else k, "quarter": quarter,
            "Release_Date": k if rd == "same" else rd, "NP_P0": p0, "NP_P1": p1, "NP_P4": p4}


def write_fin(path, rows, mtime=(2026, 10, 6, 0, 0)):
    """parquet giả cùng schema thật (date object ⇒ date32). mtime cố định ⇒ cảnh báo tuổi tất định."""
    pd.DataFrame(rows, columns=F.FIN_COLS).to_parquet(path, index=False)
    set_mtime_ict(path, *mtime)


def flat_fin(tickers):
    """Mọi mã NP phẳng (YoY 0) ⇒ không vào làn C; phủ 100% vũ trụ."""
    return [fin_row(t, 100.0, 100.0, 100.0) for t in tickers]


def c_rating():
    """Route GROWTH: 3 mã PE 2 chiếm top-3 làn B ⇒ mã thử C (PE 5-12) không lọt B."""
    rows = [row(f"GB{i}", route="GROWTH", pe=2.0, pbz=0.0, drop=-5.0, icb=7777) for i in range(3)]
    spec = {"Y30": 8.0, "Y29": 8.0, "Q0": 8.0, "QN": 8.0, "PE12": 12.0, "P12X": 12.01, "PE0": 0.0,
            "PEN": -5.0, "N4": 8.0, "PIT": 8.0, "PIT1": 8.0, "RDN": 8.0, "RDF": 8.0, "RDL": 8.0,
            "CR4": 8.0, "CLQ": 8.0, "CBN": 8.0, "CIN": 8.0, "EXT": 8.0, "Z4": 8.0, "Z1": 8.0,
            "CRF": 8.0}
    for t, pe in spec.items():
        rows.append(row(t, route="GROWTH", pe=pe, pbz=0.0, drop=-5.0, icb=7777,
                        rating=4 if t == "CR4" else 2, liq=0.29 if t == "CLQ" else 1.0,
                        redflag="NP_TTM<0" if t == "CRF" else None))
    rows.append(row("MRG", route="GROWTH", pe=9.0, pbz=-1.5, drop=-30.0, icb=7777))  # A + C
    return pd.DataFrame(rows)


def c_fin():
    g = lambda t: fin_row(t, 200.0, 150.0, 100.0)  # noqa: E731 — YoY +100%, QoQ +33%
    return ([fin_row(f"GB{i}", 100.0, 100.0, 100.0) for i in range(3)] + [
        fin_row("Y30", 130.0, 100.0, 100.0),                       # YoY ĐÚNG 30% ⇒ VÀO
        fin_row("Y29", 129.9, 100.0, 100.0),                       # 29,9% ⇒ RA
        fin_row("Q0", 130.0, 130.0, 100.0),                        # QoQ = 0 ⇒ RA
        fin_row("QN", 130.0, 140.0, 50.0),                         # QoQ âm (kiểu DRI) ⇒ RA
        g("PE12"), g("P12X"), g("PE0"), g("PEN"),
        fin_row("N4", 200.0, 150.0, -10.0),                        # NP_P4 <= 0 ⇒ YoY không định nghĩa
        fin_row("PIT", 100.0, 100.0, 100.0, "2026-07-30", "2026Q2"),
        fin_row("PIT", 300.0, 200.0, 100.0, "2026-10-05", "2026Q3"),   # biết ĐÚNG ngày asof ⇒ chưa dùng
        fin_row("PIT1", 100.0, 100.0, 100.0, "2026-07-30", "2026Q2"),
        fin_row("PIT1", 300.0, 200.0, 100.0, "2026-10-04", "2026Q3"),  # biết asof−1 ⇒ dùng
        fin_row("RDN", 200.0, 150.0, 100.0, "2026-07-30", rd=None),   # Release trống ⇒ time
        fin_row("RDF", 200.0, 150.0, 100.0, "2026-10-05", rd=None),   # time = asof ⇒ RA
        fin_row("RDL", 200.0, 150.0, 100.0, "2026-10-05", time="2026-07-01"),  # Release=asof thắng time
        g("CR4"), g("CLQ"), g("CBN"), g("CIN"), g("CRF"),            # CRF: redflag ⇒ RA làn C
        # Release <= cuối quý (2026Q2 hết 30/06) = rác ⇒ ngày biết = time (=asof ⇒ RA); 01/07 hợp lệ
        fin_row("RQE", 200.0, 150.0, 100.0, "2026-10-05", rd=dt.date(2026, 6, 30)),
        fin_row("RQ1", 200.0, 150.0, 100.0, "2026-10-05", rd=dt.date(2026, 7, 1)),
        fin_row("EXT", 500.0, 400.0, 100.0),                       # YoY 400% ⇒ nhãn nghi nền thấp
        fin_row("Z4", 200.0, 150.0, 0.0),                          # NP_P4 = 0 ⇒ YoY không định nghĩa
        fin_row("Z1", 200.0, 0.0, 100.0),                          # NP_P1 = 0 ⇒ QoQ không định nghĩa
        g("MRG"),
    ])


C_IN = {"Y30", "PE12", "PIT1", "RDN", "EXT", "MRG"}
# asof 2026-10-06 (test file): quý biết 05/10 đã < asof ⇒ PIT/RDF/RDL vào; CBN chỉ BANNED ở test build
C_FILE = C_IN | {"PIT", "RDF", "RDL", "CBN"}


def test_lane_c_build(tmp):
    asof = dt.date(2026, 10, 5)
    fp = os.path.join(tmp, "fin_c.parquet")
    write_fin(fp, c_fin())
    fin, meta, warn = F.load_financials(fp, asof, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT))
    check(fin is not None and warn == [], f"fin giả hợp lệ: {warn}")
    check(fin.loc["PIT", "quarter"] == "2026Q2" and fin.loc["PIT1", "quarter"] == "2026Q3",
          f"PIT: quý biết ĐÚNG asof chưa dùng, asof−1 dùng: {fin.loc[['PIT', 'PIT1'], 'quarter'].tolist()}")
    check("RDF" not in fin.index and "RDL" not in fin.index,
          "Release trống ⇒ ngày biết = time (=asof ⇒ loại); Release=asof thắng time sớm hơn")
    check("RQE" not in fin.index and "RQ1" in fin.index and meta.get("release_le_qend") == 1,
          f"Release <= cuối quý ⇒ dùng time (asof ⇒ loại); Release = cuối quý+1 dùng được: "
          f"{meta.get('release_le_qend')}")
    cands, excluded = F.build_lanes(c_rating(), {"CBN"}, {}, {"CIN": {"last_alert": "2026-09-30"}}, fin)
    C = set(cands.loc[cands["lane"] == "C", "ticker"])
    check(C == C_IN, f"làn C sai: {sorted(C)} (mong {sorted(C_IN)})")
    for t in ("Y29", "Q0", "QN", "P12X", "PE0", "PEN", "N4", "PIT", "RDF", "RDL", "CR4", "CLQ",
              "CBN", "CIN", "Z4", "Z1", "CRF"):
        check(t not in C, f"{t} phải RA khỏi làn C")
    ex = dict(zip(excluded["ticker"] + "|" + excluded["lane"], excluded["excl_reason"]))
    check(ex.get("CBN|C") == "BANNED" and ex.get("CIN|C", "").startswith("insider_sell"),
          f"loại trừ làn C minh bạch: {ex}")
    check(set(cands.loc[cands["lane"] == "B", "ticker"]) >= {"GB0", "GB1", "GB2"}
          and not (C & set(cands.loc[cands["lane"] == "B", "ticker"])), "mã thử C không lẫn vào B")
    check(set(cands.loc[cands["ticker"] == "MRG", "lane"]) == {"A", "C"}, "MRG ở cả A và C")
    rec = {(r["ticker"], r["lane"]): F._rec(r) for _, r in cands.iterrows()}
    for t in C_IN:
        ln = F.candidate_line(rec[(t, "C")])
        check(F.LANE_C_LABEL in ln, f"nhãn bắt buộc trên dòng C {t}: {ln}")
        check((F.LANE_C_EXTREME_LABEL in ln) == (t == "EXT"), f"nhãn nền thấp chỉ khi YoY>300%: {ln}")
    ln = F.candidate_line(rec[("MRG", "A")], also_c=rec[("MRG", "C")])
    check("+làn C" in ln and F.LANE_C_LABEL in ln, f"dòng A gộp nhãn C: {ln}")
    check(abs(rec[("Y30", "C")]["g_yoy"] - 0.30) < 1e-9 and rec[("Y30", "C")]["np_quarter"] == "2026Q2",
          f"g_yoy/np_quarter mang theo: {rec[('Y30', 'C')]}")
    # Khối 08:00: MRG đã theo dõi ở A (A không báo hôm nay), C báo NEW gộp ⇒ PHẢI hiện "Làn C cũng
    # bắt" (không im lặng nuốt), và KHÔNG kèm "Làn C: 0 mới" mâu thuẫn
    res = {"asof": "2026-10-05", "warnings": [], "state_ok": True, "lane_c_ok": True, "seeded": 0,
           "seeded_by_lane": {}, "lanes_seeded_today": [], "lane_c_queued": [],
           "candidates": [rec[("MRG", "A")], rec[("MRG", "C")]],
           "n_tracking": 1, "n_lane_a": 1, "n_lane_b": 0, "n_lane_c": 1,
           "reported": [{"ticker": "MRG", "lane": "C", "reason": "NEW", "merged": True}]}
    b = F.format_topic_block(res, dt.date(2026, 10, 6))
    cm = [x for x in b.splitlines() if x.startswith("Làn C cũng bắt")]
    check(len(cm) == 1 and "MRG" in cm[0] and F.LANE_C_LABEL in cm[0] and "Làn C: 0 mới" not in b,
          f"mã C gộp (A/B không báo hôm nay) phải hiện 1 dòng 'cũng bắt', không '0 mới':\n{b}")
    res["reported"].append({"ticker": "MRG", "lane": "A", "reason": "NEW", "prev_pb_z": None})
    b = F.format_topic_block(res, dt.date(2026, 10, 6))
    check("Làn C cũng bắt" not in b and sum("MRG" in x for x in b.splitlines()) == 1
          and "+làn C" in b, f"A/B đã báo MRG ⇒ chỉ 1 dòng A gộp nhãn C:\n{b}")
    # fin None ⇒ không có làn C, A/B y nguyên
    c0, _ = F.build_lanes(c_rating(), {"CBN"}, {}, {}, None)
    check("C" not in set(c0["lane"]) and "MRG" in set(c0.loc[c0["lane"] == "A", "ticker"]),
          "fin None ⇒ không làn C, A/B vẫn chạy")
    check(F.lane_c_label(3.0) == F.LANE_C_LABEL and F.LANE_C_EXTREME_LABEL in F.lane_c_label(3.01),
          "biên YoY 300%: =300% không nhãn, >300% có")
    for g, shown, ext in ((3.004, "+300%", False), (3.006, "+301%", True)):
        check(F._pct(g) == shown and (F.LANE_C_EXTREME_LABEL in F.lane_c_label(g)) == ext
              and F._c_priority({"ticker": "X", "g_yoy": g})[1] == ext,
              f"nhãn >300% khớp SỐ HIỂN THỊ ({g}: {F._pct(g)}, {F.lane_c_label(g)})")


def c_cands(spec, a=()):
    """spec {ticker: g_yoy} làn C + a (tickers làn A)."""
    rows = [{"ticker": t, "lane": "C", "pb_z": 0.0, "g_yoy": g} for t, g in spec.items()]
    rows += [{"ticker": t, "lane": "A", "pb_z": -1.5, "g_yoy": None} for t in a]
    return pd.DataFrame(rows)


def test_lane_c_state():
    d = dt.date.fromisoformat
    st, rep = F.update_state({}, c_cands({"S1": 0.5}, a=["A0"]), d("2026-10-01"))
    check({(r["ticker"], r["reason"]) for r in rep} == {("S1", "SEED"), ("A0", "SEED")},
          f"state mới: mọi làn SEED: {rep}")
    day2 = {f"C{i}": 0.4 + 0.1 * i for i in range(1, 7)}          # 6 mã hợp lý (YoY 50%..100%)
    day2.update({"X1": 5.0, "X2": 4.0, "MRG": 0.6, "S1": 0.5})     # 2 mã cực lớn + MRG gộp A
    st2, rep = F.update_state(st, c_cands(day2, a=["A0", "MRG"]), d("2026-10-02"))
    shown = [r["ticker"] for r in rep if r["lane"] == "C" and r["reason"] == "NEW" and not r["merged"]]
    queued = sorted(r["ticker"] for r in rep if r["reason"] == "QUEUED")
    check(sorted(shown) == ["C2", "C3", "C4", "C5", "C6"],
          f"trần 5/ngày: YoY hợp lý trước, YoY giảm dần: {shown}")
    check(queued == ["C1", "X1", "X2"], f"phần dư xếp hàng (cực lớn xếp sau): {queued}")
    mrg = [r for r in rep if r["ticker"] == "MRG"]
    check(sorted((r["lane"], r["reason"], r.get("merged")) for r in mrg) ==
          [("A", "NEW", None), ("C", "NEW", True)], f"MRG: A NEW + C gộp, không chiếm trần: {mrg}")
    check(all(st2["entries"][f"{t}|C"].get("last_reported") is None for t in queued),
          "QUEUED KHÔNG được đánh dấu đã báo")
    st2b, rep_b = F.update_state(st2, c_cands(day2, a=["A0", "MRG"]), d("2026-10-02"))
    check(rep_b == rep and st2b == st2, "chạy lại cùng asof ⇒ cùng 5 mã + cùng hàng chờ, state y nguyên")
    day3 = dict(day2, C7=0.9)
    st3, rep = F.update_state(st2, c_cands(day3, a=["A0", "MRG"]), d("2026-10-05"))
    got = sorted(r["ticker"] for r in rep if r["reason"] == "NEW")
    check(got == ["C1", "C7", "X1", "X2"], f"phiên sau: hàng chờ + mã mới, không báo lại 5 mã cũ: {got}")
    # PBZ_DROP không áp cho C
    c4 = c_cands(day3, a=["A0", "MRG"])
    c4.loc[c4["lane"] == "C", "pb_z"] = -2.0
    _, rep = F.update_state(st3, c4, d("2026-10-06"))
    check(not any(r["lane"] == "C" for r in rep), f"làn C không PBZ_DROP: {rep}")
    # state cũ (trước làn C): A/B đã seed ⇒ C seed, A mới vẫn NEW
    legacy = {"seeded_on": "2026-09-30", "last_run_asof": "2026-09-30",
              "entries": {"A0|A": {"ticker": "A0", "lane": "A", "first_seen": "2026-09-30",
                                   "last_seen": "2026-09-30", "last_reported": "2026-09-30",
                                   "last_reported_pb_z": -1.5, "last_reason": "SEED"}}}
    stl, rep = F.update_state(legacy, c_cands({"P1": 0.5, "P2": 0.6}, a=["A0", "A9"]), d("2026-10-01"))
    check(sorted((r["ticker"], r["reason"]) for r in rep) == [("A9", "NEW"), ("P1", "SEED"), ("P2", "SEED")],
          f"state cũ: làn C mới thêm ⇒ SEED (không flood), A mới ⇒ NEW: {rep}")
    check(stl["seeded_lanes"] == {"A": "2026-09-30", "B": "2026-09-30", "C": "2026-10-01"},
          f"seeded_lanes: {stl.get('seeded_lanes')}")
    # Làn C lỗi giữa chừng: mã liên tục được giữ; dữ liệu về sau 40 ngày ⇒ KHÔNG báo lại là mới
    s1, _ = F.update_state({}, c_cands({"K1": 0.5}), d("2026-10-01"))
    s2, rep = F.update_state(s1, c_cands({}), d("2026-11-09"), ("C",))
    check(rep == [] and s2["entries"]["K1|C"]["last_seen"] == "2026-11-09", "phiên lỗi giữ liên tục")
    _, rep = F.update_state(s2, c_cands({"K1": 0.5}), d("2026-11-10"))
    check(rep == [], f"dữ liệu về ⇒ K1 không bị báo lại là mới: {rep}")
    s2x, _ = F.update_state(s1, c_cands({}), d("2026-11-09"))          # rời làn THẬT (không lỗi)
    _, rep = F.update_state(s2x, c_cands({"K1": 0.5}), d("2026-11-10"))
    check([r["reason"] for r in rep] == ["NEW"], f"đối chứng: rời làn thật ⇒ NEW (test có lực): {rep}")
    # Phiên C lỗi CHỈ kéo dài mục còn liên tục (last_seen == phiên trước): K1 đã rời làn 11-09 ⇒
    # phiên lỗi 11-10 KHÔNG được hồi sinh nó; 11-11 có lại ⇒ NEW
    # (từ 2026-10-06: K1 rời làn + quá cooldown ⇒ đã bị DỌN ở 11-09; phiên lỗi không dọn/không hồi sinh)
    check("K1|C" not in s2x["entries"] and [x["reason"] for x in s2x["prune_log"]] == ["STALE"],
          f"rời làn + quá cooldown ⇒ dọn STALE: {s2x['entries']} {s2x.get('prune_log')}")
    s3x, _ = F.update_state(s2x, c_cands({}), d("2026-11-10"), ("C",))
    check("K1|C" not in s3x["entries"], f"phiên lỗi không hồi sinh mục đã dọn: {s3x['entries']}")
    # Mục rời làn CHƯA hết cooldown (không bị dọn): phiên lỗi KHÔNG kéo dài last_seen của nó
    t1, _ = F.update_state({}, c_cands({"K2": 0.5}), d("2026-11-01"))
    t2, _ = F.update_state(t1, c_cands({}), d("2026-11-09"))
    t3, _ = F.update_state(t2, c_cands({}), d("2026-11-10"), ("C",))
    check(t3["entries"]["K2|C"]["last_seen"] == "2026-11-01",
          f"phiên lỗi không kéo dài mục đã rời làn: {t3['entries']['K2|C']}")
    _, rep = F.update_state(s3x, c_cands({"K1": 0.5}), d("2026-11-11"))
    check([r["reason"] for r in rep] == ["NEW"], f"rời làn → phiên lỗi → có lại ⇒ NEW: {rep}")
    # Làn C lỗi ngay phiên đầu ⇒ chưa seed; phiên sau có dữ liệu ⇒ seed (không flood)
    s1, _ = F.update_state({}, c_cands({}, a=["A0"]), d("2026-10-01"), ("C",))
    check("C" not in s1["seeded_lanes"], f"làn lỗi không seed: {s1['seeded_lanes']}")
    _, rep = F.update_state(s1, c_cands({"K1": 0.5}, a=["A0"]), d("2026-10-02"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("K1", "SEED")], f"seed khi dữ liệu về: {rep}")


def test_lane_c_files(tmp):
    base = os.path.join(tmp, "data_c")
    rcsv = os.path.join(tmp, "rating_c.csv")
    fcsv = os.path.join(tmp, "forensic_c.csv")
    fp = os.path.join(tmp, "fin_files.parquet")
    write_forensic(fcsv)
    rat = c_rating()
    rat.to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 5, 19, 25)
    now = dt.datetime(2026, 10, 5, 19, 35, tzinfo=ICT)
    ins = {"CIN": {"last_alert": "2026-09-30"}}
    # ngày 1: fin THIẾU ⇒ cảnh báo, A/B chạy, khối không nói "0 mới" cho C
    r = F.run_daily(rcsv, base, True, now, fcsv, ins, os.path.join(tmp, "khong_co.parquet"))
    check(not r["lane_c_ok"] and r["n_lane_c"] == 0 and r["n_lane_a"] > 0 and r["state_ok"],
          f"fin thiếu ⇒ làn C tắt, A/B chạy: {r['warnings']}")
    check(any("LÀN C KHÔNG CHẠY" in w for w in r["warnings"]), f"cảnh báo fin thiếu: {r['warnings']}")
    log = pd.read_csv(F.daily_paths(base)["log"], dtype={"date": str})
    check(len(log) and log["lane_c_ok"].astype(str).eq("False").all(),
          f"log ngày C không chạy: lane_c_ok=False mọi dòng: {log['lane_c_ok'].unique()}")
    b = F.format_topic_block(r, dt.date(2026, 10, 6))
    check("LÀN C (tăng trưởng LN) KHÔNG CHẠY" in b, f"khối khi fin thiếu:\n{b}")
    check("Làn C: 0 mới" not in b and "KHÔNG phải '0 mã mới'" in b, f"không im lặng thành 0 mới:\n{b}")
    # hỏng / thiếu cột / dưới sàn ⇒ cảnh báo, không raise
    with open(fp, "w") as f:
        f.write("không phải parquet")
    _, _, w = F.load_financials(fp, dt.date(2026, 10, 5), now)
    check(any("đọc lỗi" in x for x in w), f"fin hỏng ⇒ cảnh báo: {w}")
    pd.DataFrame(c_fin()).drop(columns=["NP_P1"]).to_parquet(fp, index=False)
    fin, _, w = F.load_financials(fp, dt.date(2026, 10, 5), now)
    check(fin is None and any("thiếu cột" in x and "NP_P1" in x for x in w), f"fin thiếu cột: {w}")
    write_fin(fp, c_fin())
    old = (F.FIN_MIN_ROWS, F.FIN_MIN_TICKERS)
    F.FIN_MIN_ROWS, F.FIN_MIN_TICKERS = FIN_REAL_FLOORS
    try:
        fin, meta, w = F.load_financials(fp, dt.date(2026, 10, 5), now)
    finally:
        F.FIN_MIN_ROWS, F.FIN_MIN_TICKERS = old
    check(fin is None and any("DƯỚI SÀN" in x and "dòng" in x and "mã" in x for x in w),
          f"sàn thật 50.000 dòng/1.000 mã ⇒ làn C tắt: {w}")
    # fin phủ < 80% vũ trụ chất lượng ⇒ cảnh báo (vẫn chạy)
    write_fin(fp, [fin_row(f"GB{i}", 100.0, 100.0, 100.0) for i in range(3)]
              + [fin_row(f"ZZ{i}", 100.0, 100.0, 100.0) for i in range(5)])   # đủ sàn giả, sai mã
    r = F.run_daily(rcsv, base, False, now, fcsv, ins, fp)
    check(r["lane_c_ok"] and any("chỉ phủ" in x for x in r["warnings"]), f"phủ thấp: {r['warnings']}")
    # cache cũ 5 ngày + dữ liệu cũ > 100 ngày ⇒ cảnh báo nhưng VẪN chạy
    write_fin(fp, c_fin(), mtime=(2026, 9, 30, 19, 0))
    fin, _, w = F.load_financials(fp, dt.date(2026, 10, 5), now)
    check(fin is not None and any("cũ 5" in x for x in w), f"cache cũ ⇒ cảnh báo, vẫn chạy: {w}")
    fin, _, w = F.load_financials(fp, dt.date(2027, 1, 20), dt.datetime(2027, 1, 20, 19, 35, tzinfo=ICT))
    check(fin is not None and any("ingest BCTC chết" in x for x in w), f"dữ liệu > 100 ngày: {w}")
    # ngày 2: fin về (state đã có A/B từ ngày 1) ⇒ làn C SEED, không flood
    write_fin(fp, c_fin())
    set_mtime_ict(rcsv, 2026, 10, 6, 19, 25)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT), fcsv, ins, fp)
    check(r["lane_c_ok"] and r["seeded_by_lane"]["C"] == len(C_FILE) and r["reported"] == [],
          f"làn C lần đầu ⇒ seed {len(C_FILE)}, không báo: {r['seeded_by_lane']} {r['reported']}")
    b = F.format_topic_block(r, dt.date(2026, 10, 7))
    check(f"C={len(C_FILE)}" in b and "Khởi tạo" in b and "0 mới làn A/B" in b and "Y30" not in b, f"khối ngày seed làn C:\n{b}")
    log = pd.read_csv(F.daily_paths(base)["log"])
    lc = log[log["lane"] == "C"]
    check(len(lc) == len(C_FILE) and lc["label"].str.contains(F.LANE_C_LABEL, regex=False).all()
          and set(F.LOG_COLS) == set(log.columns), "log: mọi dòng C mang nhãn bắt buộc")
    check(lc.set_index("ticker").loc["EXT", "label"].endswith(F.LANE_C_EXTREME_LABEL), "log nhãn nền thấp")
    ok_by_day = log.groupby(log["date"].astype(str))["lane_c_ok"].agg(lambda x: set(x.astype(str)))
    check(ok_by_day.get("2026-10-05") == {"False"} and ok_by_day.get("2026-10-06") == {"True"},
          f"log phân biệt ngày C không chạy / C chạy: {ok_by_day.to_dict()}")
    # ngày 3: 7 mã C mới (1 gộp với A) ⇒ 5 hiện + "còn 1 mã", gộp không báo trùng
    extra = [row(f"W{i}", route="GROWTH", pe=8.0, pbz=0.0, drop=-5.0, icb=7777) for i in range(6)]
    extra.append(row("WA", route="GROWTH", pe=9.0, pbz=-1.5, drop=-30.0, icb=7777))
    pd.concat([rat, pd.DataFrame(extra)], ignore_index=True).to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 7, 19, 25)
    write_fin(fp, c_fin() + [fin_row(f"W{i}", 100.0 + 50 * (i + 1), 100.0, 100.0) for i in range(6)]
              + [fin_row("WA", 200.0, 150.0, 100.0)])
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 7, 19, 35, tzinfo=ICT), fcsv, ins, fp)
    b = F.format_topic_block(r, dt.date(2026, 10, 8))
    c_lines = [x for x in b.splitlines() if "· làn C tăng trưởng LN ·" in x]
    check(len(c_lines) == 5 and all(F.LANE_C_LABEL in x for x in c_lines),
          f"trần 5 dòng C, dòng nào cũng có nhãn:\n{b}")
    check("còn 1 mã làn C mới" in b and r["lane_c_queued"] == ["W0"],
          f"nêu 'còn N mã' (W0 YoY thấp nhất bị cắt): {r['lane_c_queued']}\n{b}")
    na = [x for x in b.splitlines() if "WA" in x.split("·")[0]]
    check(len(na) == 1 and "làn A" in na[0] and "+làn C" in na[0] and F.LANE_C_LABEL in na[0],
          f"WA ở A+C: 1 dòng duy nhất gộp nhãn:\n{b}")
    check(f"\"{F.LANE_C_LABEL}\"" in b and "KHÔNG tự mua/size" in b, "tiêu đề làn C ghi rõ nguồn ý tưởng")
    rep = F.format_run_report(r)
    check("QUEUED" in rep and rep.count(F.LANE_C_LABEL) >= len(C_FILE) + 7, "báo cáo chạy có nhãn + QUEUED")
    # ngày 4: fin thiếu ⇒ cảnh báo; mã C liên tục không mất; ngày 5 có lại ⇒ W0 (hàng chờ) báo, không flood
    set_mtime_ict(rcsv, 2026, 10, 8, 19, 25)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 8, 19, 35, tzinfo=ICT), fcsv, ins,
                    os.path.join(tmp, "khong_co.parquet"))
    check(not r["lane_c_ok"] and r["state_ok"], "ngày 4 fin thiếu: A/B ghi state, C giữ")
    set_mtime_ict(rcsv, 2026, 10, 9, 19, 25)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 9, 19, 35, tzinfo=ICT), fcsv, ins, fp)
    check([(x["ticker"], x["lane"]) for x in r["reported"]] == [("W0", "C")],
          f"ngày 5: chỉ mã đang xếp hàng, không báo lại cả làn: {r['reported']}")


def test_lane_c_isolated(tmp):
    """Lỗi BẤT KỲ khi tính làn C (đọc fin, growth_cols, …) ⇒ C KHÔNG chạy + cảnh báo; A/B vẫn chạy."""
    rcsv = os.path.join(tmp, "rating_iso.csv")
    fcsv = os.path.join(tmp, "forensic_iso.csv")
    fp = os.path.join(tmp, "fin_iso.parquet")
    write_forensic(fcsv)
    c_rating().to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 5, 19, 25)
    write_fin(fp, c_fin())
    now = dt.datetime(2026, 10, 5, 19, 35, tzinfo=ICT)
    ok = F.run_daily(rcsv, os.path.join(tmp, "iso0"), False, now, fcsv, {}, fp)
    check(ok["lane_c_ok"] and ok["n_lane_c"] > 0 and ok["n_lane_c_seasonal"] == 0,
          f"đối chứng: fin hợp lệ ⇒ làn C chạy; fin 1 quý ⇒ 0 mã mùa vụ: {ok.get('n_lane_c_seasonal')}")

    def boom(*a, **k):
        raise KeyError("cot_la")
    for name in ("growth_cols", "load_financials"):
        orig = getattr(F, name)
        if name == "growth_cols":
            setattr(F, name, lambda df, fin: boom() if fin is not None else orig(df, fin))
        else:
            setattr(F, name, boom)
        try:
            r = F.run_daily(rcsv, os.path.join(tmp, f"iso_{name}"), True, now, fcsv, {}, fp)
        except Exception as e:                                  # noqa: BLE001
            r = None
            check(False, f"{name} lỗi làm chết cả funnel: {type(e).__name__}: {e}")
        finally:
            setattr(F, name, orig)
        if r is None:
            continue
        check(not r["lane_c_ok"] and r["n_lane_c"] == 0 and r["n_lane_a"] == ok["n_lane_a"]
              and r["n_lane_b"] == ok["n_lane_b"] and r["state_ok"],
              f"{name} lỗi ⇒ C tắt, A/B y nguyên: C={r['n_lane_c']} A={r['n_lane_a']} B={r['n_lane_b']}")
        check(any("làn C lỗi khi tính" in w and "KeyError" in w for w in r["warnings"]),
              f"{name} lỗi ⇒ cảnh báo có lỗi thật: {r['warnings']}")
        b = F.format_topic_block(r, dt.date(2026, 10, 6))
        check("LÀN C (tăng trưởng LN) KHÔNG CHẠY" in b and "Làn C: 0 mới" not in b,
              f"{name} lỗi ⇒ khối nói KHÔNG CHẠY:\n{b}")


# ------------------------------------------------------- mùa vụ / FIFO / quý mới nhất / dọn state
# (job Taylor_20261006_052500)
def _qs(start, n):
    y, q = int(start[:4]), int(start[5])
    out = []
    for _ in range(n):
        out.append(f"{y}Q{q}")
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def hist(t, vals, start="2020Q4", last_known="2026-07-30"):
    """Chuỗi NP quý liên tục từ `start`; NP_P1/NP_P4 lấy từ chính chuỗi. Ngày biết = cuối quý + 30
    ngày; quý cuối = `last_known`. None trong vals = quý thiếu NP_P0."""
    qs = _qs(start, len(vals))
    rows = []
    for i, (q, v) in enumerate(zip(qs, vals)):
        qe = F.quarter_end(pd.Series([q])).iloc[0].date()
        k = (qe + dt.timedelta(days=30)).isoformat() if i < len(vals) - 1 else last_known
        rows.append(fin_row(t, v, vals[i - 1] if i >= 1 else None, vals[i - 4] if i >= 4 else None,
                            known=k, quarter=q))
    return rows


SEAS_PAT = (1.0, 0.4, 0.8, 1.5)                      # Q1..Q4 (kiểu cao su: Q2 đáy)


def seasonal_vals(q2_qoq=0.81, q1_mult=2.0, pat=SEAS_PAT, start="2020Q4"):
    """2020Q4..2025Q4 theo mẫu mùa vụ (tăng 5%/năm, nhiễu tất định ±3%), 2026Q1 cao, 2026Q2 = Q1×q2_qoq."""
    vals = []
    for i, q in enumerate(_qs(start, 21)):
        y, qn = int(q[:4]), int(q[5])
        vals.append(100.0 * pat[qn - 1] * 1.05 ** (y - 2020) * (1 + 0.03 * ((i * 7) % 3 - 1)))
    q1 = vals[-4] * q1_mult                                    # 2026Q1 = q1_mult × 2025Q1
    return vals + [q1, q1 * q2_qoq]


DRI_REAL = [36.39, 16.34, 29.97, 14.74, 15.75, 20.93, 16.32, -5.86, 28.53, 14.78, 16.98, 10.94, 31.41,
            20.94, 9.47, 39.92, 38.43, 55.95, 21.87, 38.98, 40.6, 78.42, 63.79]      # 2020Q4..2026Q2, tỷ
PVT_REAL = [262.45, 136.41, 241.42, 94.3, 196.81, 152.52, 207.1, 270.8, 206.78, 181.87, 309.14, 249.19,
            230.16, 230.92, 288.28, 364.97, 209.06, 215.06, 294.78, 263.38, 265.9, 319.05, 552.88]


def season_fin():
    rows = [fin_row(f"GB{i}", 100.0, 100.0, 100.0) for i in range(3)]
    rows += hist("DRS", seasonal_vals())                         # mùa vụ, QoQ −19% < 0 nhưng > chuẩn ⇒ VÀO
    rows += hist("SNG", seasonal_vals(q2_qoq=0.30))              # mùa vụ, QoQ −70% tệ hơn chuẩn −60% ⇒ RA
    rows += hist("SUP", seasonal_vals(q2_qoq=1.20, q1_mult=3.0, pat=(1.0, 2.0, 1.0, 1.0)))  # chuẩn +100%, QoQ +20% ⇒ RA
    rows += hist("SHR", seasonal_vals()[-10:], start="2024Q1")   # mẫu y hệt DRS nhưng 2,5 năm ⇒ luật cũ ⇒ RA
    gap = seasonal_vals()
    rows += [r for r in hist("GAP", gap) if r["quarter"] not in ("2022Q1", "2023Q1", "2024Q1")]  # thủng ⇒ <3 năm/cặp
    rows += hist("MID", seasonal_vals(q2_qoq=0.90, pat=(1.0, 0.83, 1.0, 1.17)))  # η² ≈0,56 < 0,6 ⇒ luật cũ ⇒ RA
    rows += hist("MD6", seasonal_vals(q2_qoq=0.90, pat=(1.0, 0.80, 1.0, 1.20)))  # η² ≈0,64 ∈ [0,6; 0,7) ⇒ mùa vụ ⇒ VÀO
    rows += [r for r in hist("NQ4", seasonal_vals()) if not r["quarter"].endswith("Q4")]  # mất 2 cặp ⇒ RA
    rows += [fin_row("DUP", 200.0, 150.0, 100.0, "2026-07-30", "2026Q2"),     # Q2 bản đầu qua làn C …
             fin_row("DUP", 100.0, 100.0, 100.0, "2026-09-01", "2026Q2"),     # … bản đính chính (biết sau) thắng ⇒ RA
             fin_row("BADQ", 200.0, 150.0, 100.0, "2026-07-30", "2026-Q2")]   # quý sai dạng ⇒ bỏ dòng
    rows += hist("DRI", DRI_REAL)                                # dữ liệu THẬT: η² 0,10 ⇒ không mùa vụ ⇒ RA
    rows += hist("PVT", PVT_REAL)                                # dữ liệu THẬT: QoQ +73% ⇒ VÀO (luật cũ)
    rows += [fin_row("LQM", 200.0, 150.0, 100.0, "2026-05-01", "2026Q1"),     # Q1 qua làn C …
             fin_row("LQM", None, 200.0, 120.0, "2026-07-30", "2026Q2")]      # … nhưng Q2 thiếu NP ⇒ RA
    rows += [fin_row("LQK", 200.0, 150.0, 100.0, "2026-07-30", "2026Q2"),     # kỳ mới nhất qua làn C
             fin_row("LQK", 100.0, 100.0, 100.0, "2026-08-15", "2026Q1")]     # Q1 biết MUỘN hơn (đính chính)
    return rows


def season_rating():
    rows = [row(f"GB{i}", route="GROWTH", pe=2.0, pbz=0.0, drop=-5.0, icb=7777) for i in range(3)]
    for t in ("DRS", "SNG", "SUP", "SHR", "GAP", "MID", "MD6", "NQ4", "DUP", "BADQ", "DRI", "PVT", "LQM", "LQK"):
        rows.append(row(t, route="GROWTH", pe=8.0, pbz=0.0, drop=-5.0, icb=7777))
    return pd.DataFrame(rows)


def eta2_ref(vals_by_q):
    """η² độc lập (1 − SSW/SST) từ {qoy: [log-QoQ]} — đối chiếu seasonal_stats."""
    allv = [v for vs in vals_by_q.values() for v in vs]
    mu = sum(allv) / len(allv)
    sst = sum((v - mu) ** 2 for v in allv)
    ssw = sum((v - sum(vs) / len(vs)) ** 2 for vs in vals_by_q.values() for v in vs)
    return 1 - ssw / sst


def test_lane_c_season(tmp):
    import math
    asof = dt.date(2026, 10, 5)
    fp = os.path.join(tmp, "fin_season.parquet")
    write_fin(fp, season_fin())
    fin, meta, warn = F.load_financials(fp, asof, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT))
    check(fin is not None, f"fin mùa vụ đọc được: {warn}")
    seas = {t for t in fin.index if fin.loc[t, "seasonal"]}
    check(seas == {"DRS", "SNG", "SUP", "MD6"}, f"chỉ 4 mã mẫu mùa vụ đủ lịch sử là mùa vụ: {sorted(seas)}")
    check(F.SEASON_ETA2_MIN <= fin.loc["MD6", "season_eta2"] < 0.7, f"MD6 η² {fin.loc['MD6', 'season_eta2']:.3f}")
    nf = F.growth_cols(pd.DataFrame({"ticker": ["KHONGFIN"]}), fin)
    check(not nf["seasonal"].iloc[0] and not nf["np_missing"].iloc[0], "mã không có trong fin ⇒ không mùa vụ")
    check(0.5 < fin.loc["MID", "season_eta2"] < F.SEASON_ETA2_MIN and not fin.loc["MID", "seasonal"],
          f"MID η² sát dưới ngưỡng ⇒ KHÔNG mùa vụ: {fin.loc['MID', 'season_eta2']:.3f}")
    check(meta.get("bad_quarter") == 1 and "BADQ" not in fin.index and fin.loc["DUP", "NP_P0"] == 100.0,
          f"quý sai dạng bị bỏ + đếm; cùng kỳ 2 bản ⇒ bản biết sau thắng: {meta.get('bad_quarter')}")
    for t in ("SHR", "GAP", "NQ4"):
        check(int(fin.loc[t, "season_nmin"]) < F.SEASON_MIN_PER_PAIR and not fin.loc[t, "seasonal"],
              f"{t}: thiếu lịch sử (<3 năm/cặp) ⇒ KHÔNG mùa vụ: nmin={fin.loc[t, 'season_nmin']}")
    # η² + chuẩn mùa đối chiếu công thức độc lập trên dữ liệu THẬT DRI (cửa sổ 20 quý trước 2026Q2)
    qs = _qs("2020Q4", len(DRI_REAL))
    grp = {}
    for i in range(len(qs) - 21, len(qs) - 1):
        a, b = DRI_REAL[i - 1], DRI_REAL[i]
        if a > 0 and b > 0:
            grp.setdefault(int(qs[i][5]), []).append(math.log(b / a))
    ref = eta2_ref(grp)
    check(abs(fin.loc["DRI", "season_eta2"] - ref) < 1e-9 and 0.05 < ref < 0.2,
          f"η² DRI = công thức độc lập ({fin.loc['DRI', 'season_eta2']:.4f} vs {ref:.4f})")
    med = sorted(grp[2])[len(grp[2]) // 2]
    check(abs(fin.loc["DRI", "season_norm"] - med) < 1e-12 and len(grp[2]) == 5,
          f"chuẩn mùa DRI = trung vị log-QoQ Q1→Q2 5 năm: {fin.loc['DRI', 'season_norm']} vs {med}")
    # Quý hiện tại KHÔNG nằm trong lịch sử mùa vụ (η² không đổi khi QoQ quý hiện tại cực đoan)
    w2 = os.path.join(tmp, "fin_season2.parquet")
    write_fin(w2, hist("DRS", seasonal_vals(q2_qoq=5.0)) + flat_fin(["GB0", "GB1", "GB2"]))
    f2, _, _ = F.load_financials(w2, asof, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT))
    check(abs(f2.loc["DRS", "season_eta2"] - fin.loc["DRS", "season_eta2"]) < 1e-12,
          "η² chỉ dùng quý TRƯỚC quý hiện tại")
    # Ngưỡng η²: đúng biên VÀO, dưới biên RA (đổi hằng số quanh giá trị thật của DRS)
    e = float(fin.loc["DRS", "season_eta2"])
    old = F.SEASON_ETA2_MIN
    try:
        F.SEASON_ETA2_MIN = e
        fa, _, _ = F.load_financials(fp, asof, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT))
        F.SEASON_ETA2_MIN = e + 1e-6
        fb, _, _ = F.load_financials(fp, asof, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT))
    finally:
        F.SEASON_ETA2_MIN = old
    check(bool(fa.loc["DRS", "seasonal"]) and not bool(fb.loc["DRS", "seasonal"]),
          f"biên η²: = ngưỡng ⇒ mùa vụ, > η² ⇒ không (η²={e:.4f})")
    # Quý mới nhất THEO KỲ + thiếu NP
    check(fin.loc["LQK", "quarter"] == "2026Q2" and bool(fin.loc["LQM", "np_missing"])
          and fin.loc["LQM", "quarter"] == "2026Q2",
          f"kỳ mới nhất (không theo ngày biết); Q2 thiếu NP KHÔNG lùi về Q1: "
          f"{fin.loc[['LQK', 'LQM'], ['quarter', 'np_missing']].to_dict('index')}")
    cands, excluded = F.build_lanes(season_rating(), set(), {}, {}, fin)
    C = set(cands.loc[cands["lane"] == "C", "ticker"])
    check(C == {"DRS", "MD6", "PVT", "LQK"}, f"làn C mùa vụ: {sorted(C)} (mong DRS, MD6, PVT, LQK)")
    ex = dict(zip(excluded["ticker"] + "|" + excluded["lane"], excluded["excl_reason"]))
    check(ex.get("LQM|C") == "np_missing(2026Q2)", f"LQM ghi loại minh bạch: {ex}")
    # Đối chứng (test có lực): bỏ mùa vụ ⇒ DRS RA, SUP VÀO (QoQ +20% > 0)
    nof = fin.assign(seasonal=False)
    c0, _ = F.build_lanes(season_rating(), set(), {}, {}, nof)
    check(set(c0.loc[c0["lane"] == "C", "ticker"]) == {"SUP", "PVT", "LQK"},
          f"đối chứng luật cũ: {sorted(set(c0.loc[c0['lane'] == 'C', 'ticker']))}")
    rec = {(r["ticker"], r["lane"]): F._rec(r) for _, r in cands.iterrows()}
    d = rec[("DRS", "C")]
    check(d["seasonal"] is True and d["g_qoq"] < 0 and d["g_qoq_adj"] > 0
          and abs((1 + d["g_qoq"]) / (1 + d["season_norm_qoq"]) - 1 - d["g_qoq_adj"]) < 1e-9,
          f"DRS: QoQ âm, đ/c mùa dương, nhất quán: {d}")
    ln = F.candidate_line(d)
    check("mùa vụ η²" in ln and "QoQ chuẩn mùa" in ln and "đ/c mùa +" in ln and F.LANE_C_LABEL in ln,
          f"dòng C mùa vụ ghi nhãn + cách đ/c: {ln}")
    lp = F.candidate_line(rec[("PVT", "C")])
    check("mùa vụ" not in lp and rec[("PVT", "C")]["seasonal"] is False, f"PVT không mùa vụ: {lp}")
    res = {"asof": "2026-10-05", "warnings": [], "state_ok": True, "lane_c_ok": True, "seeded": 0,
           "seeded_by_lane": {}, "lanes_seeded_today": [], "lane_c_queued": [],
           "candidates": [rec[("DRS", "C")], rec[("PVT", "C")]], "n_tracking": 2, "n_lane_a": 0,
           "n_lane_b": 0, "n_lane_c": 2,
           "reported": [{"ticker": t, "lane": "C", "reason": "NEW", "merged": False} for t in ("DRS", "PVT")]}
    b = F.format_topic_block(res, dt.date(2026, 10, 6))
    check(b.count(F.SEASON_NOTE) == 1, f"khối 08:00 giải thích mùa vụ ĐÚNG 1 lần:\n{b}")
    res["reported"] = res["reported"][1:]
    check(F.SEASON_NOTE not in F.format_topic_block(res, dt.date(2026, 10, 6)),
          "không có dòng mùa vụ ⇒ không in giải thích")
    # Tương thích ngược: kết quả bản CŨ (không trường mùa vụ) ⇒ in bình thường, không 'mùa vụ'
    oldc = {k: v for k, v in rec[("DRS", "C")].items()
            if k not in ("seasonal", "season_eta2", "season_norm_qoq", "g_qoq_adj")}
    res["candidates"], res["reported"] = [oldc], [{"ticker": "DRS", "lane": "C", "reason": "NEW",
                                                   "merged": False}]
    b = F.format_topic_block(res, dt.date(2026, 10, 6))
    check("DRS" in b and "mùa vụ" not in b and "⚠️" not in b.split("\n", 1)[1].split("Làn C")[0],
          f"kết quả bản cũ ⇒ không cảnh báo giả:\n{b}")
    # run_daily: cảnh báo np_missing, log có cột mùa vụ, log CŨ (thiếu cột) vẫn nối được
    base = os.path.join(tmp, "data_season")
    os.makedirs(base, exist_ok=True)
    rcsv, fcsv = os.path.join(tmp, "rating_season.csv"), os.path.join(tmp, "forensic_season.csv")
    write_forensic(fcsv)
    season_rating().to_csv(rcsv, index=False)
    set_mtime_ict(rcsv, 2026, 10, 5, 19, 25)
    pd.DataFrame([{"date": "2026-10-02", "ticker": "OLD", "lane": "A", "reported": "NEW"}]).to_csv(
        F.daily_paths(base)["log"], index=False)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 5, 19, 35, tzinfo=ICT), fcsv, {}, fp)
    check(any("THIẾU NP" in w and "LQM 2026Q2" in w for w in r["warnings"]),
          f"cảnh báo quý mới nhất thiếu NP: {r['warnings']}")
    check(r["n_lane_c_seasonal"] == 2 and r["fin_meta"]["coverage"] == round(15 / 17, 3),
          f"n_lane_c_seasonal + phủ không tính mã thiếu NP: {r['n_lane_c_seasonal']} {r['fin_meta']}")
    log = pd.read_csv(F.daily_paths(base)["log"], dtype={"date": str})
    check(list(log.columns) == F.LOG_COLS and set(log["date"]) == {"2026-10-02", "2026-10-05"}
          and log.loc[log["ticker"] == "DRS", "seasonal"].astype(str).eq("True").all(),
          f"log nối bản cũ + cột mùa vụ: {list(log.columns)}")


def test_fifo():
    d = dt.date.fromisoformat
    st, _ = F.update_state({}, c_cands({"S0": 0.5}), d("2026-10-01"))
    day2 = {"X1": 5.0, "R1": 0.4, "R2": 0.5, "R3": 0.6, "R4": 0.7, "R5": 0.8, "R6": 0.9, "S0": 0.5}
    st, rep = F.update_state(st, c_cands(day2), d("2026-10-02"))
    q2 = sorted(r["ticker"] for r in rep if r["reason"] == "QUEUED")
    check(q2 == ["R1", "X1"], f"ngày 2: cắt trần, R1 (YoY thấp) + X1 (>300%) xếp hàng: {q2}")
    check(st["entries"]["X1|C"]["queued_since"] == "2026-10-02", "queued_since ghi ngày bắt đầu chờ")
    day3 = dict(day2, **{f"N{i}": 0.95 + 0.01 * i for i in range(5)})      # 5 mã mới YoY cao hơn
    st3, rep = F.update_state(st, c_cands(day3), d("2026-10-05"))
    shown = sorted(r["ticker"] for r in rep if r["reason"] == "NEW")
    check(shown == ["N2", "N3", "N4", "R1", "X1"],
          f"FIFO: mã chờ từ hôm trước (kể cả X1 >300%) trước mã mới YoY cao: {shown}")
    check(st3["entries"]["N0|C"]["queued_since"] == "2026-10-05", "mã mới xếp hàng ghi ngày hôm nay")
    check("queued_since" not in st3["entries"]["X1|C"] and not st3["entries"]["X1|C"].get("queued"),
          f"đã báo ⇒ rời hàng chờ: {st3['entries']['X1|C']}")
    st3b, rep_b = F.update_state(st3, c_cands(day3), d("2026-10-05"))
    check(rep_b == rep and st3b == st3, "FIFO: chạy lại cùng asof ⇒ y hệt")
    # rời làn rồi quay lại (chưa từng báo) ⇒ chờ lại TỪ ĐẦU (queued_since mới)
    day4 = {k: v for k, v in day3.items() if k not in ("N0",)}
    st4, _ = F.update_state(st3, c_cands(day4, a=["N0"]), d("2026-10-06"))   # còn ở A ⇒ mục C không bị dọn
    check("N0|C" in st4["entries"] and "queued_since" not in st4["entries"]["N0|C"]
          and not st4["entries"]["N0|C"].get("queued"),
          f"N0|C còn trong state (không dọn) nhưng rời làn C ⇒ gỡ chỗ chờ: {st4['entries'].get('N0|C')}")
    # B1: rời C, CHỈ còn ở A >= 30 ngày ⇒ KHÔNG được QUEUE_EXPIRED (cảnh báo nghẽn sai nguyên nhân)
    s_far, rep_far = F.update_state(st4, c_cands({k: v for k, v in day4.items()}, a=["N0"]),
                                    d("2026-11-10"))
    check(not [x for x in s_far["prune_log"] if x.get("reason") == "QUEUE_EXPIRED"]
          and "N0|C" in s_far["entries"],
          f"rời C còn ở A 35 ngày ⇒ không QUEUE_EXPIRED: {s_far['prune_log']}")
    # làn C lỗi phiên đó ⇒ không biết mã còn trong C không ⇒ GIỮ chỗ chờ
    st4u, _ = F.update_state(st3, c_cands({}, a=["N0"]), d("2026-10-06"), ("C",))
    check(st4u["entries"]["N0|C"].get("queued_since") == "2026-10-05",
          f"làn C lỗi ⇒ giữ chỗ chờ: {st4u['entries'].get('N0|C')}")
    # kể cả mục không liên tục (state ghi bởi bản trước vá B1): làn C lỗi ⇒ KHÔNG gỡ chỗ chờ
    lg = json.loads(json.dumps(st3))
    lg["entries"]["N0|C"]["last_seen"] = "2026-10-02"
    lg4, _ = F.update_state(lg, c_cands({}, a=["N0"]), d("2026-10-06"), ("C",))
    check(lg4["entries"]["N0|C"].get("queued_since") == "2026-10-05",
          f"làn C lỗi + mục không liên tục ⇒ vẫn giữ chỗ chờ: {lg4['entries'].get('N0|C')}")
    # Z* YoY cao hơn N0: nếu N0 còn giữ chỗ chờ từ 10-05 nó phải đứng đầu; reset ⇒ thua Z* cùng ngày
    st5, rep = F.update_state(st4, c_cands(dict(day4, N0=0.95, **{f"Z{i}": 0.99 for i in range(6)})),
                              d("2026-10-07"))
    shown = sorted(r["ticker"] for r in rep if r["reason"] == "NEW")
    check("N0" not in shown and st5["entries"]["N0|C"]["queued_since"] == "2026-10-07",
          f"rời làn ⇒ mất chỗ chờ, quay lại xếp cuối: {shown} {st5['entries'].get('N0|C')}")
    # state trước FIFO (queued không có queued_since) vẫn chạy
    legacy = json.loads(json.dumps(st))
    for e in legacy["entries"].values():
        e.pop("queued_since", None)
    _, rep = F.update_state(legacy, c_cands(day3), d("2026-10-05"))
    check(len([r for r in rep if r["reason"] == "NEW"]) == 5, "state cũ thiếu queued_since vẫn chạy")


def test_prune():
    d = dt.date.fromisoformat
    st, _ = F.update_state({}, c_cands({"K1": 0.5, "K2": 0.5}, a=["A1", "K3"]), d("2026-09-01"))
    st["entries"]["K3|C"] = {"ticker": "K3", "lane": "C", "first_seen": "2026-08-01",
                             "last_seen": "2026-08-01", "last_reported": "2026-08-01"}
    # 09-25: K1 rời làn (24 ngày < cooldown) ⇒ GIỮ
    s1, _ = F.update_state(st, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-09-25"))
    check("K1|C" in s1["entries"], "rời làn nhưng chưa hết cooldown ⇒ giữ")
    # 10-05: K1 hết cooldown + không còn làn nào ⇒ XOÁ; K3|C hết cooldown nhưng K3 còn ở làn A ⇒ GIỮ
    s2, rep = F.update_state(s1, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-10-05"))
    pr = [(x["key"], x["reason"]) for x in s2["prune_log"] if x["asof"] == "2026-10-05"]
    check(pr == [("K1|C", "STALE")] and "K3|C" in s2["entries"] and "K2|C" in s2["entries"],
          f"dọn STALE đúng mục (ticker-level): {pr}")
    s2b, rep_b = F.update_state(s2, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-10-05"))
    check(s2b == s2 and rep_b == rep, "dọn: chạy lại cùng asof y hệt")
    _, rep = F.update_state(s2, c_cands({"K1": 0.5, "K2": 0.5}, a=["A1", "K3"]), d("2026-10-06"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("K1", "NEW")],
          f"mã đã dọn quay lại ⇒ NEW (như khi còn mục): {rep}")
    # chưa từng báo (last_reported None) + không còn làn nào ⇒ dọn NGAY phiên đó (không đợi cooldown)
    sn = json.loads(json.dumps(s1))
    sn["entries"]["NV|C"] = {"ticker": "NV", "lane": "C", "first_seen": "2026-09-20",
                             "last_seen": "2026-09-24"}
    sn2, _ = F.update_state(sn, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-09-26"))
    check("NV|C" not in sn2["entries"] and any(x["key"] == "NV|C" and x["reason"] == "STALE"
                                               and x["last_reported"] is None for x in sn2["prune_log"]),
          f"chưa từng báo + rời mọi làn ⇒ STALE ngay: {sn2['prune_log']}")
    # phiên có làn lỗi ⇒ KHÔNG dọn
    s3, _ = F.update_state(s1, c_cands({}, a=["A1"]), d("2026-10-05"), ("C",))
    check("K1|C" in s3["entries"] and not [x for x in s3["prune_log"] if x["asof"] == "2026-10-05"],
          "làn lỗi ⇒ không dọn")
    # hàng chờ >= 30 ngày ⇒ xoá + log, không báo phiên đó; chạy lại cùng asof y hệt; phiên sau vào lại
    q = {"ticker": "QQ", "lane": "C", "first_seen": "2026-09-01", "last_seen": "2026-10-04",
         "queued": True, "queued_since": "2026-09-05"}
    s4 = json.loads(json.dumps(s2))
    s4["entries"]["QQ|C"] = q
    s4["entries"]["QY|C"] = dict(q, ticker="QY", queued_since="2026-09-06")
    s5, rep = F.update_state(s4, c_cands({"K2": 0.5, "QQ": 0.5, "QY": 0.5}, a=["A1", "K3"]),
                             d("2026-10-05"))
    pr = [(x["key"], x["reason"]) for x in s5["prune_log"] if x["asof"] == "2026-10-05"]
    check(("QQ|C", "QUEUE_EXPIRED") in pr and "QQ|C" not in s5["entries"]
          and not any(r["ticker"] == "QQ" for r in rep), f"hàng chờ 30 ngày ⇒ xoá, không báo: {pr} {rep}")
    check([r["ticker"] for r in rep if r["reason"] == "NEW"] == ["QY"] and "QY|C" in s5["entries"]
          and s5["entries"]["QY|C"].get("last_reported") == "2026-10-05",
          f"29 ngày ⇒ còn trong hàng, được báo: {rep}")
    s5b, rep_b = F.update_state(s5, c_cands({"K2": 0.5, "QQ": 0.5, "QY": 0.5}, a=["A1", "K3"]),
                                d("2026-10-05"))
    check(s5b == s5 and rep_b == rep, "hàng chờ hết hạn: chạy lại cùng asof y hệt")
    _, rep = F.update_state(s5, c_cands({"K2": 0.5, "QQ": 0.5}, a=["A1", "K3"]), d("2026-10-06"))
    check([(r["ticker"], r["reason"]) for r in rep] == [("QQ", "NEW")], f"phiên sau QQ vào lại: {rep}")
    # biên cooldown: báo 09-05 ⇒ 10-05 đúng 30 ngày ⇒ DỌN; báo 09-06 (29 ngày) ⇒ GIỮ
    sb = {"entries": {f"{t}|C": {"ticker": t, "lane": "C", "last_seen": "2026-09-30", "last_reported": lr}
                      for t, lr in (("B30", "2026-09-05"), ("B29", "2026-09-06"))},
          "seeded_lanes": {"A": "2026-09-01", "B": "2026-09-01", "C": "2026-09-01"},
          "last_run_asof": "2026-10-02"}
    sb2, _ = F.update_state(sb, c_cands({}, a=["A1"]), d("2026-10-05"))
    check("B30|C" not in sb2["entries"] and "B29|C" in sb2["entries"], f"biên cooldown 30 ngày: {sb2['entries']}")
    # phiên có làn lỗi ⇒ hàng chờ quá hạn cũng KHÔNG xoá
    s4u, _ = F.update_state(s4, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-10-05"), ("C",))
    check("QQ|C" in s4u["entries"], "làn lỗi ⇒ không xoá hàng chờ quá hạn")
    # prune_log có trần
    old = F.PRUNE_LOG_MAX
    try:
        F.PRUNE_LOG_MAX = 2
        s6 = json.loads(json.dumps(s1))
        s6["prune_log"] = [{"asof": "2026-01-01", "key": f"x{i}|C", "reason": "STALE"} for i in range(5)]
        s6, _ = F.update_state(s6, c_cands({"K2": 0.5}, a=["A1", "K3"]), d("2026-10-05"))
    finally:
        F.PRUNE_LOG_MAX = old
    check(len(s6["prune_log"]) == 2 and s6["prune_log"][-1]["key"] == "K1|C", f"trần prune_log: {s6['prune_log']}")


def test_prune_run_daily(tmp):
    """run_daily: QUEUE_EXPIRED ⇒ cảnh báo khối 08:00 + `state_pruned`; khoá kết quả bản cũ còn đủ."""
    base = os.path.join(tmp, "data_prune")
    rcsv, fcsv, fp = (os.path.join(tmp, x) for x in ("rating_pr.csv", "forensic_pr.csv", "fin_pr.parquet"))
    write_forensic(fcsv)
    c_rating().to_csv(rcsv, index=False)
    write_fin(fp, c_fin())
    set_mtime_ict(rcsv, 2026, 10, 5, 19, 25)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 5, 19, 35, tzinfo=ICT), fcsv, {}, fp)
    with open(F.daily_paths(base)["state"], encoding="utf-8") as f:
        st = json.load(f)
    st["entries"]["Y30|C"].update(queued=True, queued_since="2026-09-01", last_reported=None)
    st["entries"]["GONE|A"] = {"ticker": "GONE", "lane": "A", "last_seen": "2026-08-01",
                               "last_reported": "2026-08-01"}
    with open(F.daily_paths(base)["state"], "w", encoding="utf-8") as f:
        json.dump(st, f)
    set_mtime_ict(rcsv, 2026, 10, 6, 19, 25)
    r = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 6, 19, 35, tzinfo=ICT), fcsv, {}, fp)
    keys = sorted((x["key"], x["reason"]) for x in r["state_pruned"])
    check(keys == [("GONE|A", "STALE"), ("Y30|C", "QUEUE_EXPIRED")], f"state_pruned: {keys}")
    b = F.format_topic_block(r, dt.date(2026, 10, 7))
    check(any("xếp hàng >= 30 ngày" in x and "Y30" in x for x in b.splitlines()),
          f"khối 08:00 cảnh báo hàng chờ hết hạn:\n{b}")
    OLD_KEYS = {"asof", "run_at", "rating_csv", "warnings", "state_ok", "sanity_fail", "n_lane_a",
                "n_lane_b", "n_lane_c", "lane_c_ok", "fin_meta", "n_tracking", "seeded", "seeded_by_lane",
                "reported", "lanes_seeded_today", "lane_c_queued", "candidates", "excluded", "snapshot",
                "log_rows"}
    check(OLD_KEYS <= set(r), f"kết quả giữ ĐỦ khoá bản trước (chỉ thêm): thiếu {OLD_KEYS - set(r)}")
    OLD_CAND = {"ticker", "lane", "lane_rank", "route", "rating", "PE", "PB", "pb_z", "drop_pct", "liq_bn",
                "earn_yield", "context", "peer_median_drop", "peer_basis", "g_yoy", "g_qoq", "np_quarter"}
    check(all(OLD_CAND <= set(c) for c in r["candidates"]), "candidate giữ đủ trường bản trước")


def run_once():
    with tempfile.TemporaryDirectory() as tmp:
        fin_default = os.path.join(tmp, "fin_default.parquet")      # F.FIN_CACHE sandbox: NP phẳng
        write_fin(fin_default, flat_fin(rating_df()["ticker"].tolist() + ["NEW1", "NEW2"]))
        F.FIN_CACHE = fin_default
        test_lane_c_build(tmp)
        test_lane_c_state()
        test_lane_c_files(tmp)
        test_lane_c_isolated(tmp)
        test_lane_c_season(tmp)
        test_fifo()
        test_prune()
        test_prune_run_daily(tmp)
        test_lanes(tmp)
        test_insider_file(tmp)
        test_context()
        test_state()
        test_run_daily_and_files(tmp)
        test_sanity(tmp)
        test_atomic(tmp)
        test_topic_section()
        test_cli(tmp)
    tz = os.environ.get("TZ", "<unset>")
    print(f"discretionary_candidate_funnel_selfcheck TZ={tz}: {N['ok']} PASS, {N['fail']} FAIL")
    return 1 if N["fail"] else 0


def main():
    if "--all-tz" in sys.argv:
        rc = 0
        for env_tz in (None, "America/New_York", "Pacific/Kiritimati", "Asia/Ho_Chi_Minh"):
            env = {k: v for k, v in os.environ.items() if k != "TZ"}
            if env_tz:
                env["TZ"] = env_tz
            rc |= subprocess.run([sys.executable, os.path.abspath(__file__)], env=env).returncode
        return rc
    return run_once()


if __name__ == "__main__":
    sys.exit(main())
