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
    set_mtime_ict(rcsv, 2026, 10, 2, 19, 30)
    r5 = F.run_daily(rcsv, base, True, dt.datetime(2026, 10, 8, 19, 40, tzinfo=ICT), fcsv, INSIDER)
    check(not r5["state_ok"] and any("đi lùi" in w for w in r5["warnings"])
          and open(P["state"]).read() == st_before, f"asof lùi ⇒ không ghi state: {r5['warnings']}")
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


def run_once():
    with tempfile.TemporaryDirectory() as tmp:
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
