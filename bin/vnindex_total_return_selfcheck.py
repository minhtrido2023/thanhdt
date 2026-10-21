#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `vnindex_total_return.py` (SPEC §A6) — không BQ, không mạng, không ghi
`data/` (mọi file ở thư mục tạm). Chạy dưới `env -u TZ` và một TZ lạ (§16/§19):

    env -u TZ python3 mike/bin/vnindex_total_return_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/vnindex_total_return_selfcheck.py

Lịch phiên dùng `trading_bot.vn_market` (CODE, chỉ đọc) của cây WorkingClaude chứa script.
"""
import contextlib
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vnindex_total_return as V  # noqa: E402

if V.WC_ROOT not in sys.path:
    sys.path.insert(0, V.WC_ROOT)

N_OK = 0


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def close(a, b, rel=1e-12):
    return abs(a - b) <= rel * abs(b)


def sessions(n, start=dt.date(2030, 3, 4)):
    """Phiên giả = T2–T6 (chuỗi tự là nguồn tập phiên — B3 vòng 2 — không cần lịch lễ)."""
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def rechain(rows):
    """Tính lại tr_gross/tr_net từ vnindex + y_gross (giữ chuỗi nối được — G1 kiểm điều này)."""
    rows = [dict(r) for r in rows]
    for p, r in zip(rows, rows[1:]):
        y = r["y_gross"] or 0.0
        r["tr_gross"] = p["tr_gross"] * (r["vnindex"] / p["vnindex"] + y)
        r["tr_net"] = p["tr_net"] * (r["vnindex"] / p["vnindex"] + (1 - V.DIV_TAX_RATE) * y)
    return rows


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# ───────────────────────────────────────── fixture dựng chuỗi (ca 1–4, 6)

def fixture(n=14, ca_extra=(), drop=()):
    import pandas as pd
    D = sessions(n)
    idx = [1000, 1010, 990, 995, 1000, 1005, 1000, 998, 1002, 1004, 1003, 1001, 1006, 1008, 1010, 1011]
    spec = {  # ticker: (Price, OShares, ngày có dòng)
        "AAA": (10000, 1e6, range(n)), "BBB": (20000, 2e6, range(n)), "CCC": (50000, 1e5, range(n)),
        "DDD": (30000, 1e6, range(n)), "EEE": (40000, 5e5, range(n)),
        "FFF": (15000, 1e6, [i for i in range(n) if i not in (3, 4, 5)]),
        "XXX": (10000, 1e7, range(n)),
    }
    rows = []
    for tk, (p, sh, days) in spec.items():
        for i in days:
            if (tk, i) in drop:
                continue
            px = 9600 if (tk == "AAA" and i >= 2) else p      # AAA đổi giá từ D2 (bắt mutant vốn hoá t)
            rows.append({"time": D[i].isoformat(), "ticker": tk, "Price": px, "Close": px, "OShares": sh})
    for i in range(n):
        if ("VNINDEX", i) not in drop:
            rows.append({"time": D[i].isoformat(), "ticker": "VNINDEX", "Price": idx[i], "Close": idx[i],
                         "OShares": None})

    def div(tk, i, v, stage="Đợt 1", status="executed"):
        return {"ticker": tk, "event_code": "DIV", "exright_date": D[i].isoformat(), "value_per_share": v,
                "dividend_year": 2030, "dividend_stage_vi": stage, "event_status": status}
    ca = [div("AAA", 2, 500), div("AAA", 2, 500),                          # trùng hoàn toàn ⇒ một
          div("BBB", 4, 300, "Đợt 1"), div("BBB", 4, 200, "Đợt 2"),        # hai đợt ⇒ cộng
          div("CCC", 3, 1000, status="announced"), div("CCC", 3, 2000, status="not_executed"),
          div("DDD", 5, 300), div("EEE", 7, 1000), div("FFF", 6, 1000), div("XXX", 2, 700)]
    ca += [div(*a) for a in ca_extra]
    mem = {"vintage": D[0].isoformat(), "spells": {
        "AAA": [["2000-01-01", "2100-01-01", "t"]], "BBB": [["2000-01-01", "2100-01-01", "t"]],
        "CCC": [["2000-01-01", "2100-01-01", "t"]], "DDD": [[D[5].isoformat(), "2100-01-01", "t"]],
        "EEE": [["2000-01-01", D[7].isoformat(), "t"]], "FFF": [["2000-01-01", "2100-01-01", "t"]]}}
    src2 = {D[i]: float(idx[i]) for i in range(n)}
    return D, {"panel": pd.DataFrame(rows), "ca": pd.DataFrame(ca),
               "ca_max_ingested_utc": f"{D[n - 1].isoformat()} 15:30:00"}, mem, src2


def write_mem(tmp, mem):
    p = os.path.join(tmp, "hose_membership_latest.json")
    with open(p, "w") as f:
        json.dump(mem, f)
    return p


def t_build_by_hand(tmp):
    D, inp, mem, src2 = fixture()
    sp = os.path.join(tmp, "s1.csv")
    V.update(sp, write_mem(tmp, mem), inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
             first_date=D[0].isoformat())
    r = {x["date"]: x for x in V.read_series(sp)}
    # Ca 1: D2 — rổ AAA, BBB, CCC, EEE, FFF; vốn hoá phiên D1 = 1e10+4e10+5e9+2e10+1,5e10 = 9e10
    y2 = 1e6 * 500 / 9e10
    ok(close(r[D[2]]["y_gross"], y2), f"ca1 y D2 {r[D[2]]['y_gross']} != {y2}")
    ok(r[D[2]]["n_members"] == 5, f"ca1 n D2 {r[D[2]]['n_members']}")
    ok(r[D[0]]["tr_gross"] == 1000 and r[D[1]]["tr_gross"] == 1010, "ca1 mốc + D1 không cổ tức")
    trg = 1010 * (990 / 1010 + y2)
    trn = 1010 * (990 / 1010 + 0.95 * y2)
    ok(abs(r[D[2]]["tr_gross"] - trg) < 1e-9, f"ca1 tr_gross D2 {r[D[2]]['tr_gross']} != {trg}")
    ok(abs(r[D[2]]["tr_net"] - trn) < 1e-9, f"ca1 tr_net D2 {r[D[2]]['tr_net']} != {trn}")
    rows = V.read_series(sp)
    ok(abs(V.period_return(rows, D[1], D[2], "tr_net") - (990 / 1010 + 0.95 * y2 - 1)) < 1e-12,
       "ca1 period_return tr_net")
    ok(abs(V.period_return(rows, D[0], D[2], "price") - (990 / 1000 - 1)) < 1e-12, "ca1 period price")
    # Ca 2: BBB hai đợt cùng ngày ⇒ 500 đ/cp; AAA dòng trùng ⇒ tính một lần (đã ở y2 ở trên)
    y4 = 2e6 * 500 / (9.6e9 + 4e10 + 5e9 + 2e10)
    ok(close(r[D[4]]["y_gross"], y4), f"ca2 y D4 {r[D[4]]['y_gross']} != {y4}")
    ok(r[D[3]]["y_gross"] == 0, f"ca2 CCC announced/not_executed không vào y: {r[D[3]]['y_gross']}")
    # Ca 3: DDD vào HOSE D5 (cổ tức D5 vào y), EEE rời HOSE D7 (cổ tức D7 không vào)
    y5 = 1e6 * 300 / (9.6e9 + 4e10 + 5e9 + 2e10 + 3e10)
    ok(close(r[D[5]]["y_gross"], y5), f"ca3 y D5 {r[D[5]]['y_gross']} != {y5}")
    ok(r[D[4]]["n_members"] == 4 and r[D[5]]["n_members"] == 5, "ca3 DDD vào rổ đúng phiên D5")
    ok(r[D[7]]["y_gross"] == 0, f"ca3 EEE đã rời HOSE D7 — cổ tức không vào y: {r[D[7]]['y_gross']}")
    # Ca 4: FFF ngừng D3–D5, nối lại D6 ⇒ D6 không vào rổ (cổ tức D6 bị loại), D7 vào lại
    ok(r[D[6]]["y_gross"] == 0, f"ca4 FFF phiên nối lại không vào y: {r[D[6]]['y_gross']}")
    ok(r[D[6]]["n_members"] == 5 and r[D[7]]["n_members"] == 5, "ca4 số mã D6/D7")
    ok(r[D[2]]["max_dy_ticker"] == "AAA" and abs(r[D[2]]["max_dy"] - 0.05) < 1e-12, "max_dy D2 = AAA 5%")
    st = [x["status"] for x in rows]
    ok(st == ["sealed"] * (len(rows) - V.SEAL_AFTER) + ["provisional"] * V.SEAL_AFTER, f"status {st}")
    return sp


def t_sealed(tmp):
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    sp = os.path.join(tmp, "s6.csv")
    V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
             first_date=D[0].isoformat())
    h0 = md5(sp)
    # (a) dòng sealed D8 (trong cửa sổ kiểm) đổi cổ tức ⇒ SealedChanged, file không đổi
    D2_, inp2, _, _ = fixture(ca_extra=[("BBB", 8, 100, "Đợt 3")])
    try:
        V.update(sp, mp, inputs=inp2, src2=src2)
        ok(False, "ca6 phải ném SealedChanged")
    except V.SealedChanged as exc:
        ok("y_gross" in str(exc) and D[8].isoformat() in str(exc), f"ca6 thông điệp trích giá trị: {exc}")
    ok(md5(sp) == h0, "ca6 file KHÔNG đổi sau SealedChanged")
    # (b) sát ngưỡng: Δy < 0,1 điểm cơ bản trên dòng sealed ⇒ không lỗi, phần sealed giữ nguyên byte
    # Δy = 2e6·0,3/~1e11 ≈ 6e-6; + cổ tức ở D11 (provisional, sau ranh giới) để ca6b2 bắt nối sai dòng
    _, inp3, _, _ = fixture(ca_extra=[("BBB", 8, 0.3, "Đợt 3"), ("BBB", 11, 400, "Đợt 5")])
    with open(sp, encoding="utf-8") as f:
        sealed0 = [ln for ln in f if ",sealed," in ln]
    V.update(sp, mp, inputs=inp3, src2=src2)
    with open(sp, encoding="utf-8") as f:
        sealed1 = [ln for ln in f if ",sealed," in ln]
    ok(sealed1 == sealed0, "ca6b phần sealed giữ nguyên byte khi Δy dưới ngưỡng")
    # (b2) ca thật 12-13/10/2026: Δy dưới ngưỡng ở dòng sealed trong cửa sổ kiểm ⇒ dòng provisional ĐẦU
    # TIÊN sau phần sealed phải nối từ dòng sealed GIỮ BYTE (không từ giá trị dựng lại trong bộ nhớ),
    # nếu không G1 nổ (đo thật: lệch +8,23e-06 / −8,94e-06).
    rows6b = V.read_series(sp)
    g1 = [e for e in gates(rows6b, D[0], D[-1]) if e.startswith("G1")]
    ok(not g1, f"ca6b2 G1 phải nối qua ranh giới sealed/provisional sau Δy dưới ngưỡng: {g1}")
    ok(next(x for x in rows6b if x["date"] == D[11])["y_gross"] > 0, "ca6b2 D11 có cổ tức (đuôi có y≠0)")
    # (c) dòng DIV vào muộn cho phiên PROVISIONAL ⇒ dựng lại, không lỗi
    _, inp4, _, _ = fixture(ca_extra=[("BBB", 12, 400, "Đợt 4")])
    V.update(sp, mp, inputs=inp4, src2=src2)
    r = {x["date"]: x for x in V.read_series(sp)}
    ok(r[D[12]]["y_gross"] > 0 and r[D[12]]["status"] == "provisional", "ca6c provisional dựng lại")
    # (d) CLI: rc=2, file không đổi
    cache = os.path.join(tmp, "cache6")
    os.makedirs(cache, exist_ok=True)
    inp2["panel"].to_csv(os.path.join(cache, "panel.csv"), index=False)
    inp2["ca"].to_csv(os.path.join(cache, "ca.csv"), index=False)
    s2p = os.path.join(tmp, "src2.csv")
    with open(s2p, "w") as f:
        f.write("date,close\n" + "".join(f"{d.isoformat()},{v}\n" for d, v in src2.items()))
    h1 = md5(sp)
    cp = subprocess.run([sys.executable, os.path.join(HERE, "vnindex_total_return.py"), "--update",
                         "--from-cache", cache, "--src2-csv", s2p, "--series", sp, "--membership", mp],
                        capture_output=True, text=True)
    ok(cp.returncode == 2, f"ca6d CLI rc={cp.returncode} (phải 2): {cp.stderr[-300:]}")
    ok(md5(sp) == h1, "ca6d CLI: file không đổi")
    # (e) BQ mất dòng VNINDEX của phiên đã có ⇒ BuildRefused; DNSE có phiên BQ không có ⇒ BuildRefused
    _, inp5, _, _ = fixture(drop=[("VNINDEX", 13)])
    try:
        V.update(sp, mp, inputs=inp5, src2={d: v for d, v in src2.items() if d != D[13]})
        ok(False, "ca6e phải BuildRefused (mất phiên đã có)")
    except V.BuildRefused as exc:
        ok(D[13].isoformat() in str(exc), f"ca6e thông điệp: {exc}")
    _, inp6, _, _ = fixture(drop=[("VNINDEX", 11)])
    try:
        V.update(sp, mp, inputs=inp6, src2=src2)
        ok(False, "ca6e phải BuildRefused (DNSE có phiên BQ thiếu)")
    except V.BuildRefused as exc:
        ok("DNSE" in str(exc) and D[11].isoformat() in str(exc), f"ca6e thông điệp DNSE: {exc}")
    ok(md5(sp) == h1, "ca6e file không đổi")


# ───────────────────────────────────────── cổng (ca 5) trên chuỗi dựng tay

def mk_series(n=70):
    D = sessions(n)
    rows, lvl = [], 1000.0
    for i, d in enumerate(D):
        nl = 1000.0 * (1.001 ** i)
        rows.append({"date": d, "vnindex": nl, "vnindex_src2": nl, "y_gross": 0.0 if i else None,
                     "n_members": 100 if i else None, "mc_members_vnd": 1e12 * (1.001 ** max(i - 1, 0)) if i else None,
                     "div_cash_vnd": 0.0, "tr_gross": nl, "tr_net": nl,
                     "k2_synth_pr": (nl / lvl - 1) if i else None, "status": "sealed",
                     "membership_vintage": d.isoformat(), "ca_max_ingested_at": d.isoformat() + "T22:30:00+07:00",
                     "built_at_ict": "", "max_dy": 0.0, "max_dy_ticker": "", "osh_missing_max_pct": 0.0,
                     "osh_missing_ticker": ""})
        lvl = nl
    return D, rows


def gates(rows, a, b, acks=None):
    return V.check_period(rows, a, b, acks or set())


def t_gates():
    D, base = mk_series()
    a, b = D[62], D[66]
    ok(gates(base, a, b) == [], f"chuỗi sạch phải qua: {gates(base, a, b)}")

    def mod(i, **kw):
        rows = [dict(r) for r in base]
        rows[i].update(kw)
        return rows

    def one(rows, g, must=()):
        e = [x for x in gates(rows, a, b) if x.startswith(g)]
        ok(len(e) >= 1, f"{g} phải nổ: {gates(rows, a, b)}")
        for m in must:
            ok(m in e[0], f"{g} thông điệp phải trích {m!r}: {e[0]}")

    def none(rows, g, day=None):
        # chỉ xét lỗi CỦA phiên bị sửa (sửa một dòng làm phiên kế tiếp "đổi ngược lại")
        day = (day or D[64]).isoformat()
        e = [x for x in gates(rows, a, b) if x.startswith(g) and day in x]
        ok(not e, f"{g} KHÔNG được nổ (sát ngưỡng): {e}")
    # G1 — phiên cuối thiếu / phiên giữa thiếu (B3 vòng 2: tập phiên = dòng chuỗi, không lịch lễ)
    e = gates(base[:66], a, b)
    ok(any(x.startswith("G1") and D[66].isoformat() in x for x in e), f"G1 phiên cuối: {e}")
    wy = rechain([dict(r, y_gross=0.001) if 63 <= i <= 66 else r for i, r in enumerate(base)])
    ok(gates(wy, a, b) == [], f"chuỗi có cổ tức nối đúng phải qua: {gates(wy, a, b)}")
    e = gates(wy[:64] + wy[65:], a, b)        # xoá dòng D64 ⇒ D65 không nối từ D63
    ok(any(x.startswith("G1") and D[65].isoformat() in x and D[63].isoformat() in x and "không nối" in x
           for x in e), f"G1 dòng giữa bị xoá: {e}")
    ok(not [x for x in gates(base, a, b) if x.startswith("G1")], "G1 chuỗi đủ không nổ")
    t_g1_sessions(D, base)
    t_acks(D, base, a, b)
    t_g4_acks(D, base, a, b)
    # G2 — 0,011% nổ; 0,009% không
    one(mod(64, vnindex_src2=base[64]["vnindex"] / 1.00011), "G2", (D[64].isoformat(), "+0.011%"))
    none(mod(64, vnindex_src2=base[64]["vnindex"] / 1.00009), "G2")
    one(mod(62, vnindex_src2=None), "G2", ("thiếu",))                  # cả dòng mốc
    # G3 — corporate_action nạp trước phiên của dòng
    one(mod(64, ca_max_ingested_at=(D[64] - dt.timedelta(days=1)).isoformat() + "T22:30:00+07:00"),
        "G3", (D[64].isoformat(),))
    none(mod(64, ca_max_ingested_at=D[64].isoformat() + "T00:00:01+07:00"), "G3")
    # G4 — số mã đổi > 5%; vốn hoá lệch chỉ số > 3%
    one(mod(63, n_members=94), "G4", ("100 → 94", D[63].isoformat()))    # phiên ĐẦU kỳ (ngay sau mốc D62) — mutant N11
    one(mod(64, n_members=94), "G4", ("100 → 94",))
    none(mod(64, n_members=95), "G4")
    mc_exp = base[63]["mc_members_vnd"] * base[63]["vnindex"] / base[62]["vnindex"]
    one(mod(64, mc_members_vnd=mc_exp * 1.031), "G4", ("+3.10%",))
    none(mod(64, mc_members_vnd=mc_exp * 1.029), "G4")
    # G5 — 60 phiên rổ lệch chỉ số > 0,5 điểm %
    off = base[64]["vnindex"] / base[4]["vnindex"] - 1
    k = base[64]["k2_synth_pr"]

    def g5(delta):
        return mod(64, k2_synth_pr=(1 + k) * (1 + off + delta) / (1 + off) - 1)
    one(g5(0.0051), "G5", ("+0.51",))
    none(g5(0.0049), "G5")
    # G6 — cổ tức > 30% giá; có xác nhận thì qua
    one(mod(64, max_dy=0.31, max_dy_ticker="ZZZ"), "G6", ("ZZZ", "31.0%"))
    none(mod(64, max_dy=0.29, max_dy_ticker="ZZZ"), "G6")
    ok(not [x for x in gates(mod(64, max_dy=0.31, max_dy_ticker="ZZZ"), a, b,
                             {(D[64].isoformat(), "ZZZ")}) if x.startswith("G6")], "G6 có ack thì qua")
    # G7 — bảng sàn cũ > 35 ngày so với ngày dòng
    one(mod(64, membership_vintage=(D[64] - dt.timedelta(days=36)).isoformat()), "G7")
    none(mod(64, membership_vintage=(D[64] - dt.timedelta(days=35)).isoformat()), "G7")
    # G8 — OShares thiếu ở mã > 0,5% vốn hoá
    one(mod(64, osh_missing_max_pct=0.0051, osh_missing_ticker="YYY"), "G8", ("YYY", "0.51%"))
    none(mod(64, osh_missing_max_pct=0.0049, osh_missing_ticker="YYY"), "G8")
    # benchmark_period: cổng cổ tức hỏng ⇒ ô giá có số, ô có cổ tức None + lý do; KHÔNG thay bằng giá
    bp = V.benchmark_period(a, b, series=mod(64, n_members=50), acks_path="/nonexistent/acks.json")
    ok(bp["status"] == "unavailable" and bp["vnindex_tr_net_pct"] is None
       and bp["vnindex_tr_gross_pct"] is None and bp["vnindex_price_pct"] is not None
       and "G4" in bp["reason"], f"benchmark_period khi G4 hỏng: {bp}")
    bp = V.benchmark_period(a, b, series=mod(64, vnindex_src2=1.0), acks_path="/nonexistent/acks.json")
    ok(bp["vnindex_price_pct"] is None and "G2" in bp["reason"], f"G2 hỏng cả ô giá: {bp}")
    bp = V.benchmark_period(a, b, series=base, acks_path="/nonexistent/acks.json")
    ok(bp["status"] == "ok" and bp["vnindex_tr_net_pct"] == round(100 * (base[66]["tr_net"] / base[62]["tr_net"] - 1), 3),
       f"benchmark_period sạch: {bp}")
    # Ca 7: mốc là ngày nghỉ (Thứ Bảy) ⇒ từ chối, không tự lùi
    sat = next(D[62] + dt.timedelta(days=k) for k in range(1, 8) if (D[62] + dt.timedelta(days=k)).weekday() == 5)
    try:
        V.period_return(base, sat, b, "tr_net")
        ok(False, "ca7 period_return phải từ chối mốc ngày nghỉ")
    except V.PeriodError as exc:
        ok(sat.isoformat() in str(exc) and "không tự lùi" in str(exc), f"ca7 thông điệp: {exc}")
    bp = V.benchmark_period(sat, b, series=base, acks_path="/nonexistent/acks.json")
    ok(bp["status"] == "unavailable" and bp["vnindex_price_pct"] is None, f"ca7 benchmark_period: {bp}")


def t_acks(D, base, a, b):
    """G6 (mutant N6 vòng 1): mục xác nhận PHẢI có `confirmed_by` (bằng chứng có NGƯỜI xác nhận) +
    date + ticker; thiếu ⇒ ValueError, và benchmark_period ra unavailable (không lặng lẽ bỏ qua G6)."""
    rows = [dict(r) for r in base]
    rows[64].update(max_dy=0.31, max_dy_ticker="ZZZ")
    with tempfile.TemporaryDirectory(prefix="vtr_acks_") as tmp:
        good, bad = os.path.join(tmp, "good.json"), os.path.join(tmp, "bad.json")
        with open(good, "w", encoding="utf-8") as f:
            json.dump({"G6": [{"date": D[64].isoformat(), "ticker": "ZZZ", "confirmed_by": "user 2030-06-01"}]}, f)
        ok(V.load_acks(good) == {(D[64].isoformat(), "ZZZ")}, "ack hợp lệ")
        ok(V.benchmark_period(a, b, series=rows, acks_path=good)["status"] == "ok", "G6 có ack (confirmed_by) ⇒ qua")
        for name, entry in (("thiếu confirmed_by", {"date": D[64].isoformat(), "ticker": "ZZZ"}),
                            ("confirmed_by rỗng", {"date": D[64].isoformat(), "ticker": "ZZZ", "confirmed_by": ""}),
                            ("thiếu ticker", {"date": D[64].isoformat(), "confirmed_by": "user"})):
            with open(bad, "w", encoding="utf-8") as f:
                json.dump({"G6": [entry]}, f)
            try:
                V.load_acks(bad)
                ok(False, f"ack {name} phải ValueError")
            except ValueError as exc:
                ok("confirmed_by" in str(exc), f"ack {name}: {exc}")
            bp = V.benchmark_period(a, b, series=rows, acks_path=bad)
            ok(bp["status"] == "unavailable" and bp["vnindex_tr_net_pct"] is None and "confirmed_by" in bp["reason"],
               f"ack {name} ⇒ benchmark unavailable: {bp}")


def t_g4_acks(D, base, a, b):
    """G4 ack (18/10, arch-review vòng 1): ack ràng (date, n_prev, n) — CHỈ che nhánh SỐ MÃ của đúng ngày
    và đúng số đã xem; không che nhánh vốn hoá, không che gate khác, không giả được qua mục G6; mục hỏng
    ⇒ ValueError."""
    day = D[64].isoformat()
    key = V.g4_ack_key(day, 100, 94)

    def errs(rows, acks, g="G4"):
        return [x for x in V.check_period(rows, a, b, acks) if x.startswith(g)]
    dip = [dict(r) for r in base]
    for i in (64, 65, 66):        # rổ tụt rồi GIỮ mức mới tới hết kỳ ⇒ chỉ ngày tụt (D64) cần ack
        dip[i]["n_members"] = 94
    rebound = [dict(r) for r in base]
    rebound[64]["n_members"] = 94
    ok(any(D[65].isoformat() in x for x in errs(rebound, {key})),
       "ngày bật lại >5% là một G4 RIÊNG, ack ngày tụt không che nó")
    ok(any(day in x for x in errs(dip, set())), "G4 số mã nổ khi chưa ack")
    ok(not errs(dip, {key}), f"G4 số mã có ack đúng ngày + đúng số ⇒ qua: {errs(dip, {key})}")
    ok(any(day in x for x in errs(dip, {V.g4_ack_key(D[63].isoformat(), 100, 94)})), "ack ngày khác KHÔNG cứu")
    ok(any(day in x for x in errs(dip, {(day, "ZZZ")})), "ack kiểu G6 cùng ngày KHÔNG cứu G4")
    # ràng GIÁ TRỊ: dòng provisional bị dựng lại ⇒ độ lớn/hướng khác phải nổ lại
    for name, n in (("tụt sâu hơn", 50), ("tụt rất sâu", 10), ("tăng ngược chiều", 500), ("tụt nhẹ hơn nhưng vẫn >5%", 93)):
        w = [dict(r) for r in dip]
        for i in (64, 65, 66):
            w[i]["n_members"] = n
        ok(any(day in x for x in errs(w, {key})), f"ack 100→94 KHÔNG che '{name}' (100→{n})")
    mc = [dict(r) for r in base]
    mc[64]["mc_members_vnd"] = mc[64]["mc_members_vnd"] * 1.05
    ok(any(day in x and "vốn hoá" in x for x in errs(mc, {V.g4_ack_key(day, 100, 100)})),
       "ack G4 KHÔNG che nhánh vốn hoá (cùng ngày)")
    mcdip = [dict(r) for r in dip]
    mcdip[64]["mc_members_vnd"] = mcdip[64]["mc_members_vnd"] * 1.05
    ok(any(day in x and "vốn hoá" in x for x in errs(mcdip, {key})), "ack số mã đúng ngày KHÔNG che nhánh vốn hoá")
    # ack G4 không che gate KHÁC trên cùng ngày (G3 G6 G7 G8)
    for g, kw in (("G3", {"ca_max_ingested_at": "2000-01-01"}), ("G6", {"max_dy": 0.31, "max_dy_ticker": "ZZZ"}),
                  ("G7", {"membership_vintage": "2000-01-01"}), ("G2", {"vnindex_src2": 1.0}), ("G8", {"osh_missing_max_pct": 0.5, "osh_missing_ticker": "ZZZ"})):
        w = [dict(r) for r in dip]
        w[64].update(kw)
        ok(any(day in x for x in errs(w, {key}, g)), f"ack G4 KHÔNG che {g} cùng ngày")
    # phạm vi chú thích: ack ngoài kỳ / ở mốc đầu kỳ / cặp số dưới ngưỡng KHÔNG được vào acked_g4_days
    ack_days = lambda rows, acks: V._acked_g4_days(rows, a, b, acks)           # noqa: E731
    ok(ack_days(dip, {key}) == [{"date": day, "n_prev": 100, "n": 94}], "acked_g4_days đúng ngày/cặp")
    ok(ack_days(dip, {V.g4_ack_key(D[61].isoformat(), 100, 94)}) == [], "ack ngoài kỳ không vào danh sách")
    mckey = V.g4_mc_ack_key(day, mcdip[63]["mc_members_vnd"], mcdip[64]["mc_members_vnd"])
    ok(ack_days(mcdip, {mckey}) == [{"date": day, "mc_prev": int(round(mcdip[63]["mc_members_vnd"])),
                                     "mc": int(round(mcdip[64]["mc_members_vnd"]))}],
       "acked_g4_days liệt kê ngày đã ack nhánh vốn hoá (so với chỉ số dòng TRƯỚC p, khớp _g4_errs)")
    ok(ack_days(mcdip, set()) == [], "chưa ack nhánh vốn hoá ⇒ không vào danh sách")
    # ca dòng-lệch-1: vốn hoá +0,5% nhưng chỉ số dòng TRƯỚC (p) tăng +4% so với pp ⇒ lệch -3,37% > 3% (G4 nổ);
    # nếu so p với chính nó (series[i]) tỉ số luôn =1 ⇒ dev=+0,5% ⇒ ngày đã ack bị bỏ khỏi danh sách (M1/M2)
    lag = [dict(r) for r in base]
    lag[63]["vnindex"] = lag[62]["vnindex"] * 1.04
    lag[64]["mc_members_vnd"] = lag[63]["mc_members_vnd"] * 1.005
    lagkey = V.g4_mc_ack_key(lag[64]["date"].isoformat(), lag[63]["mc_members_vnd"], lag[64]["mc_members_vnd"])
    ok([x["date"] for x in ack_days(lag, {lagkey})] == [lag[64]["date"].isoformat()],
       "acked_g4_days dùng chỉ số trễ pp→p (khớp _g4_errs), không phải p→p")
    anchor = [dict(r) for r in base]
    anchor[62]["n_members"] = 94
    ok(ack_days(anchor, {V.g4_ack_key(a.isoformat(), 100, 94)}) == [], "ngày mốc đầu kỳ (a) không thuộc kỳ (a, b]")
    small = [dict(r) for r in base]
    small[64]["n_members"] = 96
    ok(ack_days(small, {V.g4_ack_key(day, 100, 96)}) == [], "cặp dưới ngưỡng 5% không vào danh sách")
    with tempfile.TemporaryDirectory(prefix="vtr_g4acks_") as tmp:
        good, bad = os.path.join(tmp, "good.json"), os.path.join(tmp, "bad.json")
        ent = {"date": day, "n_prev": 100, "n": 94, "confirmed_by": "user 2030-06-01", "reason": "BQ thiếu 20 mã"}
        with open(good, "w", encoding="utf-8") as f:
            json.dump({"G4": [ent]}, f)
        ok(V.load_acks(good) == {key}, "ack G4 hợp lệ")
        bp = V.benchmark_period(a, b, series=dip, acks_path=good)
        ok(bp["status"] == "ok" and bp.get("acked_g4_days") == [{"date": day, "n_prev": 100, "n": 94}],
           f"benchmark ok + chú thích ngày đã ack: {bp}")
        bp = V.benchmark_period(a, b, series=base, acks_path=good)
        ok(bp["status"] == "ok" and "acked_g4_days" not in bp, "không có ngày nào cần ack ⇒ không chú thích")
        for name, e, sect in (("thiếu confirmed_by", {**ent, "confirmed_by": None}, "G4"),
                              ("confirmed_by toàn dấu cách", {**ent, "confirmed_by": "  "}, "G4"),
                              ("confirmed_by không phải chuỗi", {**ent, "confirmed_by": 1}, "G4"),
                              ("thiếu reason", {**ent, "reason": None}, "G4"),
                              ("reason rỗng", {**ent, "reason": ""}, "G4"),
                              ("reason là list", {**ent, "reason": ["x"]}, "G4"),
                              ("thiếu date", {**ent, "date": None}, "G4"),
                              ("date sai định dạng", {**ent, "date": "14/10/2026"}, "G4"),
                              ("date thừa dấu cách", {**ent, "date": day + " "}, "G4"),
                              ("date dạng liền", {**ent, "date": day.replace("-", "")}, "G4"),
                              ("thiếu n_prev", {**ent, "n_prev": None}, "G4"),
                              ("n là chuỗi", {**ent, "n": "94"}, "G4"),
                              ("n là bool", {**ent, "n": True}, "G4"),
                              ("n âm", {**ent, "n": -1}, "G4"),
                              ("giả khoá G4 qua mục G6", {"date": day, "ticker": V.G4_ACK_PREFIX + ":100>94",
                                                          "confirmed_by": "x"}, "G6")):
            with open(bad, "w", encoding="utf-8") as f:
                json.dump({sect: [e]}, f)
            try:
                V.load_acks(bad)
                ok(False, f"ack {name} phải ValueError")
            except ValueError as exc:
                ok(sect in str(exc), f"ack {name}: {exc}")
            ok(V.benchmark_period(a, b, series=dip, acks_path=bad)["status"] == "unavailable",
               f"ack {name} ⇒ benchmark unavailable")

def t_dy_corrupt(tmp):
    """DY_CORRUPT (mutant N1 vòng 1): cổ tức > 50% giá phiên trước = dữ liệu hỏng ⇒ KHÔNG vào y (vẫn ghi
    max_dy để G6 thấy); 46,7% (dưới ngưỡng) vẫn vào y."""
    for v, want_in in ((20000, False), (14000, True)):           # DDD giá 30.000 ⇒ dy 66,7% / 46,7%
        D, inp, mem, src2 = fixture(ca_extra=[("DDD", 9, v, "Đợt 9")])
        sp = os.path.join(tmp, f"s_dy_{v}.csv")
        V.update(sp, write_mem(tmp, mem), inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                 first_date=D[0].isoformat())
        r = {x["date"]: x for x in V.read_series(sp)}[D[9]]
        ok(r["max_dy_ticker"] == "DDD" and abs(r["max_dy"] - v / 30000) < 1e-7, f"dy {v}: max_dy {r}")
        if want_in:
            ok(r["y_gross"] > 0 and r["div_cash_vnd"] == 1e6 * v, f"dy {v / 300:.1f}% (< 50%) phải vào y: {r}")
        else:
            ok(r["y_gross"] == 0 and r["div_cash_vnd"] == 0, f"dy {v / 300:.1f}% (> 50%) là dữ liệu hỏng, KHÔNG "
               f"được vào y: y={r['y_gross']} div_cash={r['div_cash_vnd']}")


def t_g1_sessions(D, base):
    """B3 vòng 2 — G1/index_session_for lấy tập phiên từ chuỗi + mốc 'đã đối chiếu tới' (built_at dòng cuối)."""
    stamp = lambda d, hh: f"{d.isoformat()}T{hh}+07:00"          # noqa: E731
    # (1) nghỉ dài kiểu Tết: 10 ngày lịch không có dòng (5 ngày thường) ⇒ KHÔNG báo G1 (ca thật 2026-02-16…20)
    tet = rechain([dict(r, date=r["date"] + dt.timedelta(days=7)) if i >= 30 else r for i, r in enumerate(base)])
    gap = (tet[30]["date"] - tet[29]["date"]).days
    ok(8 <= gap <= V.G1_MAX_GAP_DAYS, f"fixture Tết {gap} ngày")
    ok(not [x for x in gates(tet, tet[25]["date"], tet[40]["date"]) if x.startswith("G1")],
       f"nghỉ Tết {gap} ngày không được báo G1: {gates(tet, tet[25]['date'], tet[40]['date'])}")
    a_ = tet[29]["date"] + dt.timedelta(days=3)             # một ngày thường trong kỳ nghỉ
    ok(V.index_session_for(tet, a_)[0] == tet[29]["date"], f"ngày thường trong kỳ nghỉ ⇒ phiên trước: "
       f"{V.index_session_for(tet, a_)}")
    # (2) khoảng trống > G1_MAX_GAP_DAYS ⇒ G1 (chuỗi mất dòng)
    big = rechain([dict(r, date=r["date"] + dt.timedelta(days=14)) if i >= 30 else r for i, r in enumerate(base)])
    e = gates(big, big[25]["date"], big[40]["date"])
    ok(any(x.startswith("G1") and big[29]["date"].isoformat() in x and "không có dòng" in x for x in e),
       f"khoảng trống {(big[30]['date'] - big[29]['date']).days} ngày phải G1: {e}")
    # (3) kỳ kết thúc SAU dòng cuối: tin khi lần dựng cuối đã đối chiếu tới hết kỳ (sau 15:00 ICT)
    s = [dict(r) for r in base[:66]]                 # dòng cuối D[65]; D[66] coi như ngày nghỉ
    s[-1]["built_at_ict"] = stamp(D[66], "23:50:00")
    ok(V.checked_through(s) == D[66], f"checked_through {V.checked_through(s)}")
    ok(not [x for x in gates(s, D[62], D[66]) if x.startswith("G1")], f"đã đối chiếu tới {D[66]}: "
       f"{gates(s, D[62], D[66])}")
    ok(V.index_session_for(s, D[66])[0] == D[65], f"ngày nghỉ sau dòng cuối ⇒ dòng cuối: {V.index_session_for(s, D[66])}")
    bm = V.report_benchmark(D[62], D[66], series=s, acks_path="/nonexistent/a.json", config_path="/nonexistent/c.json")
    ok(bm["status"] == "ok" and bm["index_end_date"] == D[65].isoformat(), f"report_benchmark ngày nghỉ cuối kỳ: {bm}")
    for st, why in ((stamp(D[66], "14:59:59"), "trước 15:00 ⇒ mới chắc tới hôm trước"),
                    (stamp(D[65], "23:50:00"), "lần dựng cuối trước ngày cuối kỳ"),
                    ("", "built_at rỗng"), ("2030-06-01T23:00:00", "thiếu múi giờ")):
        s[-1]["built_at_ict"] = st
        e = gates(s, D[62], D[66])
        ok(any(x.startswith("G1") and D[66].isoformat() in x for x in e), f"G1 phải nổ ({why}): {e}")
        ok(V.index_session_for(s, D[66])[0] is None, f"index_session_for phải None ({why})")
    ok(V.index_session_for(base, D[0] - dt.timedelta(days=3))[0] is None, "trước đầu chuỗi ⇒ None")
    # (4) không còn phụ thuộc trading_bot.vn_market
    src = open(V.__file__, encoding="utf-8").read()
    ok("import is_holiday" not in src and "_calendar_session" not in src, "vnindex_total_return không dùng lịch lễ")


def t_update_checked_through(tmp):
    """--update: DNSE phải được hỏi tới mốc built_at; DNSE có phiên BQ chưa có ⇒ BuildRefused; dựng
    offline (src2 tiêm) ⇒ built_at bị chặn ở phiên cuối của dữ liệu DNSE."""
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    sp = os.path.join(tmp, "s_ct.csv")
    last = max(src2)
    V.update(sp, mp, inputs=inp, src2=src2, built_at=f"{last.isoformat()}T23:50:00+07:00",
             first_date=D[0].isoformat())
    ok(V.checked_through(V.read_series(sp)) == last, f"checked_through = {V.checked_through(V.read_series(sp))}")
    h = md5(sp)
    nxt = last + dt.timedelta(days=1 if last.weekday() < 4 else 3)
    try:
        V.update(sp, mp, inputs=inp, src2={**src2, nxt: 1.0},
                 built_at=f"{nxt.isoformat()}T23:50:00+07:00")
        ok(False, "DNSE có phiên sau phiên cuối của BQ (BQ chưa sync) phải BuildRefused")
    except V.BuildRefused as exc:
        ok("DNSE" in str(exc) and nxt.isoformat() in str(exc), f"thông điệp: {exc}")
    ok(md5(sp) == h, "BuildRefused ⇒ file không đổi")
    far = last + dt.timedelta(days=30)
    V.update(sp, mp, inputs=inp, src2=src2, built_at=f"{far.isoformat()}T23:50:00+07:00")
    ct = V.checked_through(V.read_series(sp))
    ok(ct == last, f"offline: built_at phải chặn ở phiên cuối của DNSE {last}, không phải {far}: {ct}")
    try:
        V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01 23:50")
        ok(False, "built_at thiếu múi giờ phải BuildRefused")
    except V.BuildRefused as exc:
        ok("múi giờ" in str(exc), f"{exc}")


# ───────────────────────────────────────── C: seal-guard + A: đính chính dòng sealed (vòng 2, 21/10)

@contextlib.contextmanager
def g4_loose(n=True, mc=True):
    """Fixture 5–7 mã: đổi rổ 1 mã đã > 5% và vốn hoá lệch > 3% ⇒ seal-guard (C) giữ gần hết fixture ở
    provisional. Ca 1–6 (không kiểm cổng) nới G4 để kiểm đúng thứ chúng kiểm; seal-guard có ca riêng
    với ngưỡng THẬT (t_seal_guard). Chỉ đổi hằng số module trong selfcheck — production không có công tắc."""
    a, b = V.G4_MAX_N_CHANGE_FRAC, V.G4_MC_TOL
    if n:
        V.G4_MAX_N_CHANGE_FRAC = 1e9
    if mc:
        V.G4_MC_TOL = 1e9
    try:
        yield
    finally:
        V.G4_MAX_N_CHANGE_FRAC, V.G4_MC_TOL = a, b


def write_acks(tmp, name, g4=()):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"G4": [{"date": d.isoformat(), "n_prev": a, "n": b, "confirmed_by": "user selfcheck",
                           "reason": "selfcheck"} for d, a, b in g4]}, f)
    return p


def statuses(sp):
    return [x["status"] for x in V.read_series(sp)]


def t_seal_guard(tmp):
    """C: --update KHÔNG seal dòng mà G1/G4 của chính nó nổ chưa ack; dòng đó + mọi dòng sau ở provisional.
    Fixture (n=14 ⇒ D0..D8 đủ SEAL_AFTER): số mã D2=5, D3=4 (FFF ngừng), D4=4, D5=5 (DDD vào)."""
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    noack = os.path.join(tmp, "noack.json")
    sealed_n = lambda sp: sum(1 for x in statuses(sp) if x == "sealed")                 # noqa: E731
    with g4_loose(n=False, mc=True):                      # chỉ nhánh SỐ MÃ (nhánh có ack)
        sp = os.path.join(tmp, "sg1.csv")
        res = V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                       first_date=D[0].isoformat(), acks_path=noack)
        st = statuses(sp)
        ok(st[:3] == ["sealed"] * 3 and st[3:] == ["provisional"] * (len(st) - 3),
           f"sg1 G4 nổ ở D3 chưa ack ⇒ D3 + mọi dòng sau provisional (sealed = tiền tố): {st}")
        ok(res.get("seal_blocked") and res["seal_blocked"][0]["date"] == D[3].isoformat()
           and "G4" in res["seal_blocked"][0]["errors"][0], f"sg1 kết quả nêu dòng bị chặn + lỗi: {res}")
        # ack SAI giá trị (5>3) không mở khoá; ack đúng D3 ⇒ chặn tiếp ở D5; ack cả D5 ⇒ seal hết D0..D8
        V.update(sp, mp, inputs=inp, src2=src2, acks_path=write_acks(tmp, "a0.json", [(D[3], 5, 3)]))
        ok(sealed_n(sp) == 3, f"sg2 ack sai (n_prev,n) không mở khoá: {statuses(sp)}")
        V.update(sp, mp, inputs=inp, src2=src2, acks_path=write_acks(tmp, "a1.json", [(D[3], 5, 4)]))
        ok(sealed_n(sp) == 5, f"sg3 ack D3 ⇒ seal tới D4, chặn ở D5 (4→5): {statuses(sp)}")
        V.update(sp, mp, inputs=inp, src2=src2,
                 acks_path=write_acks(tmp, "a2.json", [(D[3], 5, 4), (D[5], 4, 5)]))
        ok(sealed_n(sp) == len(D) - V.SEAL_AFTER, f"sg4 ack D3+D5 ⇒ seal đủ: {statuses(sp)}")
        # sổ ack hỏng ⇒ BuildRefused, file không đổi (không seal theo giả định)
        bad = os.path.join(tmp, "abad.json")
        with open(bad, "w") as f:
            f.write("{không phải json")
        h = md5(sp)
        try:
            V.update(sp, mp, inputs=inp, src2=src2, acks_path=bad)
            ok(False, "sg5 sổ ack hỏng phải BuildRefused")
        except V.BuildRefused as exc:
            ok("ack" in str(exc), f"sg5 {exc}")
        ok(md5(sp) == h, "sg5 file không đổi")
    # nhánh VỐN HOÁ (không có ack) với ngưỡng thật: D3 vẫn bị chặn dù có ack nhánh số mã
    sp = os.path.join(tmp, "sg6.csv")
    res = V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                   first_date=D[0].isoformat(), acks_path=write_acks(tmp, "a3.json", [(D[3], 5, 4)]))
    ok(sealed_n(sp) == 3 and any("vốn hoá" in e for e in res["seal_blocked"][0]["errors"]),
       f"sg6 G4 vốn hoá nổ ⇒ chặn seal (không ack được): {res.get('seal_blocked')}")
    # ack nhánh vốn hoá ràng GIÁ TRỊ (date, mc_prev, mc): đúng ⇒ mở khoá D3; sai giá trị ⇒ vẫn chặn
    rows = V.read_series(sp)
    mc_prev, mc_cur = rows[2]["mc_members_vnd"], rows[3]["mc_members_vnd"]

    def mc_acks(name, mp_, m_):
        pa = os.path.join(tmp, name)
        with open(pa, "w", encoding="utf-8") as f:
            json.dump({"G4": [{"date": D[3].isoformat(), "n_prev": 5, "n": 4, "confirmed_by": "u", "reason": "r"}],
                       "G4_MC": [{"date": D[3].isoformat(), "mc_prev": mp_, "mc": m_, "confirmed_by": "u",
                                  "reason": "r"}]}, f)
        return pa
    spm = os.path.join(tmp, "sg6b.csv")
    res = V.update(spm, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                   first_date=D[0].isoformat(), acks_path=mc_acks("a4.json", mc_prev, mc_cur))
    ok(sealed_n(spm) > 3 and not any(b["date"] == D[3].isoformat() for b in res.get("seal_blocked", [])),
       f"sg6b ack MC đúng giá trị ⇒ D3 hết bị chặn: {statuses(spm)} {res.get('seal_blocked')}")
    for tag, (a_, b_) in (("mc_prev lệch", (mc_prev + 1e6, mc_cur)), ("mc lệch", (mc_prev, mc_cur + 1e6))):
        spw = os.path.join(tmp, "sg6c.csv")
        if os.path.exists(spw):
            os.remove(spw)
        res = V.update(spw, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                       first_date=D[0].isoformat(), acks_path=mc_acks("a5.json", a_, b_))
        ok(sealed_n(spw) == 3 and any("vốn hoá" in e for e in res["seal_blocked"][0]["errors"]),
           f"sg6c ack MC {tag} KHÔNG mở khoá: {res.get('seal_blocked')}")
    # ack ĐÚNG mc_prev/mc nhưng SAI NGÀY (D[4] thay vì D[3]) KHÔNG mở khoá — khoá ràng cả ngày
    pa = os.path.join(tmp, "a5d.json")
    with open(pa, "w", encoding="utf-8") as f:
        json.dump({"G4": [{"date": D[3].isoformat(), "n_prev": 5, "n": 4, "confirmed_by": "u", "reason": "r"}],
                   "G4_MC": [{"date": D[4].isoformat(), "mc_prev": mc_prev, "mc": mc_cur, "confirmed_by": "u",
                              "reason": "r"}]}, f)
    spd = os.path.join(tmp, "sg6d.csv")
    res = V.update(spd, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                   first_date=D[0].isoformat(), acks_path=pa)
    ok(sealed_n(spd) == 3 and any("vốn hoá" in e for e in res["seal_blocked"][0]["errors"]),
       f"sg6e ack MC đúng giá trị SAI NGÀY KHÔNG mở khoá: {res.get('seal_blocked')}")
    ok(V.g4_mc_ack_key(D[3], mc_prev, mc_cur) != V.g4_mc_ack_key(D[4], mc_prev, mc_cur)
       and V.g4_ack_key(D[3], 5, 4) != V.g4_ack_key(D[4], 5, 4), "sg6e khoá ack G4/G4_MC chứa NGÀY")
    ok(any("mục G4_MC" in e and f"mc_prev={int(round(mc_prev))}" in e and f"mc={int(round(mc_cur))}" in e
           for e in res["seal_blocked"][0]["errors"]), "sg6c thông báo lỗi nêu đúng số cần ack")
    for tag, bad in (("thiếu confirmed_by", {"date": D[3].isoformat(), "mc_prev": 1.0, "mc": 2.0, "reason": "r"}),
                     ("mc <= 0", {"date": D[3].isoformat(), "mc_prev": 1.0, "mc": 0, "confirmed_by": "u", "reason": "r"}),
                     ("mc là chuỗi", {"date": D[3].isoformat(), "mc_prev": 1.0, "mc": "2", "confirmed_by": "u", "reason": "r"}),
                     ("thiếu reason", {"date": D[3].isoformat(), "mc_prev": 1.0, "mc": 2.0, "confirmed_by": "u"})):
        pa = os.path.join(tmp, "a6.json")
        with open(pa, "w", encoding="utf-8") as f:
            json.dump({"G4_MC": [bad]}, f)
        try:
            V.load_acks(pa)
            ok(False, f"sg6d mục G4_MC {tag} phải ValueError")
        except ValueError:
            ok(True, f"sg6d {tag}")
    # mục G4 / G4_MC / G6 không phải list (dict, chuỗi, phần tử không phải object) ⇒ ValueError RÕ RÀNG
    for sect in ("G4", "G4_MC", "G6"):
        for tag, val in (("dict", {"date": "2030-01-01"}), ("dict rỗng", {}), ("chuỗi", "x"),
                         ("chuỗi rỗng", ""), ("phần tử chuỗi", ["x"])):
            pa = os.path.join(tmp, "a7.json")
            with open(pa, "w", encoding="utf-8") as f:
                json.dump({sect: val}, f)
            try:
                V.load_acks(pa)
                ok(False, f"sg6f mục {sect} {tag} phải ValueError")
            except ValueError as exc:
                ok(sect in str(exc) and "phải là list" in str(exc) or "không phải object" in str(exc),
                   f"sg6f {sect} {tag}: {exc}")
    pa = os.path.join(tmp, "a7.json")
    with open(pa, "w", encoding="utf-8") as f:
        json.dump([1], f)
    try:
        V.load_acks(pa)
        ok(False, "sg6f gốc là list phải ValueError")
    except ValueError as exc:
        ok("object" in str(exc), f"sg6f gốc list: {exc}")
    # G1 là blocker: seal_blockers trên hai dòng không nối được
    rows = V.read_series(sp)
    r = dict(rows[2]); r["tr_gross"] *= 1.001
    ok(any(e.startswith("G1") for e in V.seal_blockers(rows[0], rows[1], r, set())), "sg7 G1 là blocker")
    ok(V.seal_blockers(rows[0], rows[1], rows[2], set()) == [], "sg7 dòng sạch không bị chặn")


def t_restate(tmp):
    """A: --restate-sealed = đường DUY NHẤT sửa dòng sealed — dựng lại, nối lại đuôi, sổ chỉ-thêm."""
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    sp, log = os.path.join(tmp, "rs.csv"), os.path.join(tmp, "rs_log.jsonl")
    noack = os.path.join(tmp, "noack.json")
    kw = dict(membership_path=mp, src2=src2, acks_path=noack, log_path=log)
    with g4_loose():
        V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                 first_date=D[0].isoformat(), acks_path=noack)
        # cổ tức vào muộn cho dòng SEALED D6 (Δy ≈ 2e6·100/~1e11 = 2e-3 > ngưỡng) ⇒ --update rc=2
        _, inp2, _, _ = fixture(ca_extra=[("BBB", 6, 100, "Đợt 3")])
        try:
            V.update(sp, mp, inputs=inp2, src2=src2, acks_path=noack)
            ok(False, "rs0 phải SealedChanged")
        except V.SealedChanged:
            ok(True, "rs0")
        h0 = md5(sp)
        with open(sp, encoding="utf-8") as f:
            lines0 = f.readlines()
        i6 = 1 + [x["date"] for x in V.read_series(sp)].index(D[6])
        # (1) thiếu lý do / người xác nhận ⇒ từ chối, file + sổ không đổi
        for reason, conf, word in (("", "u", "reason"), ("   ", "u", "reason"), (None, "u", "reason"),
                                   ("r", "", "confirmed-by"), ("r", None, "confirmed-by")):
            try:
                V.restate_sealed([D[6]], reason, conf, sp, inputs=inp2, **kw)
                ok(False, f"rs1 thiếu {word} phải RestateRefused")
            except V.RestateRefused as exc:
                ok(word in str(exc), f"rs1 {exc}")
        ok(md5(sp) == h0 and not os.path.exists(log), "rs1 file + sổ không đổi")
        # (2) dòng provisional / dòng mốc / không có ⇒ từ chối
        for d in (D[12], D[0], dt.date(2030, 1, 1)):
            try:
                V.restate_sealed([d], "r", "u", sp, inputs=inp2, **kw)
                ok(False, f"rs2 {d} phải RestateRefused")
            except V.RestateRefused as exc:
                ok(True, f"rs2 {exc}")
        # (3) nêu D5 nhưng D6 (sealed, trong vùng dựng lại) cũng lệch ⇒ từ chối, phải nêu tên D6
        try:
            V.restate_sealed([D[5]], "r", "u", sp, inputs=inp2, **kw)
            ok(False, "rs3 phải RestateRefused (D6 lệch không được nêu)")
        except V.RestateRefused as exc:
            ok(D[6].isoformat() in str(exc), f"rs3 {exc}")
        ok(md5(sp) == h0 and not os.path.exists(log), "rs3 file + sổ không đổi")
        # (4) dry-run ⇒ không ghi gì nhưng trả dòng mới
        res = V.restate_sealed([D[6]], "r", "u", sp, inputs=inp2, write=False, **kw)
        ok(md5(sp) == h0 and not os.path.exists(log) and res["written"] is False, "rs4 dry-run không ghi")
        ok("seal_blocked" not in res, f"rs4 --restate-sealed KHÔNG xuất khoá seal_blocked (chỉ --update): {sorted(res)}")
        ok(res["md5_before"] == h0 and D[6].isoformat() in res["rows_after"], f"rs4 {res}")
        # (5) đính chính thật
        res = V.restate_sealed([D[6]], "cổ tức BBB 100đ vào muộn", "user selfcheck", sp, inputs=inp2, **kw)
        with open(sp, encoding="utf-8") as f:
            lines1 = f.readlines()
        ent = [json.loads(x) for x in open(log, encoding="utf-8")] if os.path.exists(log) else []
        ok(len(ent) == 1 and ent[0]["md5_before"] == h0 and ent[0]["md5_after"] == md5(sp),
           f"rs5 sổ ghi md5 trước/sau khớp file: {ent} vs {md5(sp)}")
        ok(ent[0]["reason"] == "cổ tức BBB 100đ vào muộn" and ent[0]["confirmed_by"] == "user selfcheck"
           and ent[0]["dates"] == [D[6].isoformat()] and ent[0]["ts_ict"].endswith("+07:00"), f"rs5 {ent[0]}")
        ok(ent[0]["rows_before"][D[6].isoformat()] == lines0[i6]
           and ent[0]["rows_after"][D[6].isoformat()] == lines1[i6], "rs5 sổ giữ dòng cũ/mới nguyên byte")
        ok(lines1[:i6] == lines0[:i6], "rs5 mọi dòng TRƯỚC dòng đính chính giữ nguyên byte")
        # sổ giữ BYTE CŨ của dòng sealed bị nối lại + đuôi provisional cũ ⇒ hoàn tác byte-exact không cần backup
        i7 = 1 + [x["date"] for x in V.read_series(sp)].index(D[7])
        ok(ent[0]["rechained_sealed_before"].get(D[7].isoformat()) == lines0[i7]
           and set(ent[0]["rechained_sealed_before"]) == set(ent[0]["rechained_sealed"]),
           "rs5 sổ giữ byte cũ của MỌI dòng sealed bị nối lại")
        ok(ent[0]["tail_before"] and ent[0]["tail_before"] == lines0[1 + len(
            [1 for x in V._parse_lines(lines0, "l0") if x["status"] == "sealed"]):],
           "rs5 sổ giữ đuôi provisional cũ")
        ok(V.undo_restatement(ent[0], "".join(lines1).encode("utf-8")) == "".join(lines0).encode("utf-8"),
           "rs5 undo_restatement dựng lại ĐÚNG byte file trước đính chính (md5_before)")
        try:
            V.undo_restatement(ent[0], "".join(lines1).encode("utf-8") + b"x")
            ok(False, "rs5 undo trên file đã đổi phải ValueError")
        except ValueError:
            ok(True, "rs5 undo từ chối file không khớp md5_after")
        rows1 = V.read_series(sp)
        r6 = rows1[i6 - 1]
        ok(r6["status"] == "sealed" and r6["y_gross"] > V._parse_lines(lines0, "lines0")[i6 - 1]["y_gross"],
           f"rs5 D6 sealed + y mới: {r6}")
        g1 = [e for e in gates(rows1, D[0], D[-1]) if e.startswith("G1")]
        ok(not g1, f"rs5 cả chuỗi (sealed sau + provisional) nối lại từ dòng đính chính: {g1}")
        ok(D[7].isoformat() in res["rechained_sealed"] and D[8].isoformat() in res["rechained_sealed"],
           f"rs5 dòng sealed sau được nối lại + nêu trong sổ: {res['rechained_sealed']}")
        # sau đính chính --update chạy lại được, phần sealed giữ byte
        sealed1 = [x for x in lines1 if ",sealed," in x]
        V.update(sp, mp, inputs=inp2, src2=src2, acks_path=noack)
        with open(sp, encoding="utf-8") as f:
            ok([x for x in f if ",sealed," in x] == sealed1, "rs5 --update sau đính chính giữ byte sealed")
        # (6) đính chính lại y hệt ⇒ không có gì đổi ⇒ từ chối, sổ không thêm dòng. built_at CỐ Ý khác lần
        # trước (ca flaky thật 21/10: hai lần chạy khác giây ⇒ dòng khác byte chỉ ở built_at_ict)
        try:
            V.restate_sealed([D[6]], "r", "u", sp, inputs=inp2, built_at="2030-01-02T01:02:03+07:00", **kw)
            ok(False, "rs6 không đổi gì phải RestateRefused")
        except V.RestateRefused as exc:
            ok("không có gì" in str(exc), f"rs6 {exc}")
        # (7) sổ CHỈ-THÊM: lần đính chính thứ hai thêm dòng, dòng cũ giữ byte
        with open(log, encoding="utf-8") as f:
            log1 = f.read()
        _, inp3, _, _ = fixture(ca_extra=[("BBB", 6, 100, "Đợt 3"), ("CCC", 7, 2000, "Đợt 4")])
        h1 = md5(sp)
        V.restate_sealed([D[7]], "r2", "u2", sp, inputs=inp3, **kw)
        with open(log, encoding="utf-8") as f:
            log2 = f.read()
        ok(log2.startswith(log1) and len(log2.splitlines()) == 2, "rs7 sổ chỉ-thêm")
        e2 = json.loads(log2.splitlines()[1])
        ok("retry_of" not in e2, f"rs7 đính chính độc lập thứ hai KHÔNG bị đánh dấu retry: {e2.get('retry_of')}")
        ok(e2["md5_before"] == h1 and e2["md5_after"] == md5(sp), f"rs7 md5 lần 2: {e2['md5_before']} vs {h1}")
        ok(not [e for e in gates(V.read_series(sp), D[0], D[-1]) if e.startswith("G1")], "rs7 G1 sạch")
    # (8) bất biến C cho đính chính: dòng đính chính vẫn nổ G4 chưa ack (ngưỡng thật) ⇒ từ chối
    h = md5(sp)
    try:
        V.restate_sealed([D[3]], "r", "u", sp, inputs=inp3, **kw)
        ok(False, "rs8 dòng đính chính nổ G4 phải RestateRefused")
    except V.RestateRefused as exc:
        ok("G4" in str(exc), f"rs8 {exc}")
    ok(md5(sp) == h and len(open(log).read().splitlines()) == 2, "rs8 file + sổ không đổi")
    # X7: đính chính NHIỀU ngày, dòng nổ G4 ở NGÀY ĐẦU (D3) — kiểm bất biến phải quét từ want[0], không từ want[-1]
    try:
        V.restate_sealed([D[3], D[6]], "r", "u", sp, inputs=inp3, **kw)
        ok(False, "x7 nhiều ngày, G4 nổ ở ngày đầu phải RestateRefused")
    except V.RestateRefused as exc:
        ok("G4" in str(exc) and D[3].isoformat() in str(exc), f"x7 {exc}")
    ok(md5(sp) == h and len(open(log).read().splitlines()) == 2, "x7 file + sổ không đổi")
    # (9) CLI: thiếu --reason ⇒ rc=4, file không đổi
    cp = subprocess.run([sys.executable, os.path.join(HERE, "vnindex_total_return.py"), "--restate-sealed",
                         D[6].isoformat(), "--confirmed-by", "u", "--series", sp, "--membership", mp,
                         "--acks", noack, "--restate-log", log], capture_output=True, text=True)
    ok(cp.returncode == 4 and "reason" in cp.stderr, f"rs9 CLI rc={cp.returncode}: {cp.stderr[-300:]}")
    ok(md5(sp) == h, "rs9 CLI file không đổi")
    t_restate_crash_noise(tmp)


def t_restate_crash_noise(tmp):
    """X9 (chết giữa ghi sổ và thay file) + mục 5 (chạy lại ⇒ retry_of) + X11 (dòng chỉ-nối-lại không phải đổi)."""
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    noack = os.path.join(tmp, "noack.json")
    _, inp2, _, _ = fixture(ca_extra=[("BBB", 6, 100, "Đợt 3")])
    with g4_loose():
        sp, log = os.path.join(tmp, "x9.csv"), os.path.join(tmp, "x9_log.jsonl")
        kw = dict(membership_path=mp, src2=src2, acks_path=noack, log_path=log)
        V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                 first_date=D[0].isoformat(), acks_path=noack)
        b0 = open(sp, "rb").read()
        h0 = md5(sp)

        def boom(path, data):
            raise OSError("selfcheck: chết giữa ghi sổ và thay file")
        real = V._write_atomic
        V._write_atomic = boom
        try:
            V.restate_sealed([D[6]], "r", "u", sp, inputs=inp2, **kw)
            ok(False, "x9 _write_atomic hỏng phải nổ lên")
        except OSError:
            ok(True, "x9")
        finally:
            V._write_atomic = real
        ent = [json.loads(x) for x in open(log, encoding="utf-8")]
        ok(md5(sp) == h0 and open(sp, "rb").read() == b0, "x9 file KHÔNG đổi khi chết trước khi thay")
        ok(len(ent) == 1 and ent[0]["md5_before"] == h0 and ent[0]["md5_after"] != h0 and "retry_of" not in ent[0],
           f"x9 sổ ĐÃ có dòng (sổ trước, file sau), md5_after ≠ file hiện tại: {ent}")
        # chạy lại ⇒ dòng sổ mới đánh dấu retry_of dòng trước, không trông như đính chính độc lập
        V.restate_sealed([D[6]], "r", "u", sp, inputs=inp2, **kw)
        ent = [json.loads(x) for x in open(log, encoding="utf-8")]
        ok(len(ent) == 2 and ent[1]["retry_of"] == {"ts_ict": ent[0]["ts_ict"], "md5_after": ent[0]["md5_after"]}
           and ent[1]["md5_before"] == h0 and ent[1]["md5_after"] == md5(sp),
           f"mục5 chạy lại sau crash ⇒ retry_of dòng trước: {ent[1:]}")
        ok(V.undo_restatement(ent[1], open(sp, "rb").read()) == b0, "mục5 undo từ dòng retry ra đúng byte gốc")
        # X11: dòng KHÔNG được nêu chỉ lệch do nối lại (nhiễu float trong G1_CHAIN_TOL) không phải đính chính
        sp2, log2 = os.path.join(tmp, "x11.csv"), os.path.join(tmp, "x11_log.jsonl")
        kw2 = dict(membership_path=mp, src2=src2, acks_path=noack, log_path=log2)
        V.update(sp2, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                 first_date=D[0].isoformat(), acks_path=noack)
        with open(sp2, encoding="utf-8") as f:
            ls = f.readlines()
        i7 = 1 + [x["date"] for x in V.read_series(sp2)].index(D[7])
        rr = dict(zip(V.COLUMNS, next(__import__("csv").reader([ls[i7]]))))
        rr["tr_gross"] = V._fmt(float(rr["tr_gross"]) * (1 + 1e-13), 15)
        ls[i7] = V._row_line(rr)
        with open(sp2, "w", encoding="utf-8") as f:
            f.writelines(ls)
        ok(not [e for e in gates(V.read_series(sp2), D[0], D[-1]) if e.startswith("G1")], "x11 nhiễu 1e-13 chưa nổ G1")
        h2 = md5(sp2)
        try:
            V.restate_sealed([D[6]], "r", "u", sp2, inputs=inp, **kw2)
            ok(False, "x11 chỉ có dòng bị nối lại ⇒ phải RestateRefused")
        except V.RestateRefused as exc:
            ok("không có gì" in str(exc), f"x11 {exc}")
        ok(md5(sp2) == h2 and not os.path.exists(log2), "x11 file + sổ không đổi")


def t_undo_polish(tmp):
    """Mục 1 (retry_of chỉ khi cùng dates+reason+confirmed_by) + mục 2 (undo có sổ, fail-closed, dòng sổ cũ
    thiếu byte cũ ⇒ ValueError rõ ràng)."""
    D, inp, mem, src2 = fixture()
    mp = write_mem(tmp, mem)
    noack = os.path.join(tmp, "noack.json")
    _, inp2, _, _ = fixture(ca_extra=[("BBB", 6, 100, "Đợt 3")])
    with g4_loose():
        sp, log = os.path.join(tmp, "u.csv"), os.path.join(tmp, "u_log.jsonl")
        kw = dict(membership_path=mp, src2=src2, acks_path=noack, log_path=log)
        V.update(sp, mp, inputs=inp, src2=src2, built_at="2030-01-01T00:00:00+07:00",
                 first_date=D[0].isoformat(), acks_path=noack)
        b0 = open(sp, "rb").read()
        h0 = md5(sp)
        rd = lambda: [json.loads(x) for x in open(log, encoding="utf-8")]               # noqa: E731

        def restore():
            with open(sp, "wb") as f:
                f.write(b0)
        # (1) retry_of: đính chính ĐỘC LẬP (lý do khác) sau khi khôi phục file KHÔNG bị gắn retry_of
        V.restate_sealed([D[6]], "lần đầu", "u1", sp, inputs=inp2, **kw)
        restore()
        V.restate_sealed([D[6]], "độc lập, lý do khác", "u1", sp, inputs=inp2, **kw)
        ent = rd()
        ok(ent[1]["md5_before"] == ent[0]["md5_before"] == h0 and "retry_of" not in ent[1],
           f"u1 cùng md5_before nhưng KHÁC lý do ⇒ không phải retry: {ent[1].get('retry_of')}")
        restore()
        V.restate_sealed([D[6]], "độc lập, lý do khác", "u2", sp, inputs=inp2, **kw)
        ok("retry_of" not in rd()[2], "u1 khác người xác nhận ⇒ không phải retry")
        restore()
        V.restate_sealed([D[6]], "độc lập, lý do khác", "u2", sp, inputs=inp2, **kw)
        ok("retry_of" in rd()[3], "u1 cùng dates+lý do+người ⇒ vẫn là retry")
        # (2) undo: thiếu lý do/người ⇒ từ chối, không đổi gì
        h1, n_log = md5(sp), len(rd())
        for r_, c_, word in ((None, "u", "reason"), ("  ", "u", "reason"), ("r", None, "confirmed-by"), ("r", "", "confirmed-by")):
            try:
                V.undo_last_restatement(r_, c_, sp, log_path=log)
                ok(False, f"u2 thiếu {word} phải RestateRefused")
            except V.RestateRefused as exc:
                ok(word in str(exc), f"u2 {exc}")
        ok(md5(sp) == h1 and len(rd()) == n_log, "u2 file + sổ không đổi")
        # file đã đổi sau đính chính (md5 ≠ md5_after) ⇒ từ chối
        with open(sp, "ab") as f:
            f.write(b"x")
        try:
            V.undo_last_restatement("r", "u", sp, log_path=log)
            ok(False, "u3 file đã đổi phải RestateRefused")
        except V.RestateRefused as exc:
            ok("md5_after" in str(exc), f"u3 {exc}")
        cur = open(sp, "rb").read()[:-1]
        with open(sp, "wb") as f:
            f.write(cur)
        ok(md5(sp) == h1 and len(rd()) == n_log, "u3 file + sổ không đổi")
        # dry-run ⇒ không ghi
        res = V.undo_last_restatement("r", "u", sp, write=False, log_path=log)
        ok(res["written"] is False and md5(sp) == h1 and len(rd()) == n_log and res["md5_after"] == h0, "u4 dry-run")
        # sổ TRƯỚC, file SAU: chết giữa chừng ⇒ có dòng undo mà file chưa đổi
        real = V._write_atomic

        def boom(path, data):
            raise OSError("selfcheck: chết giữa ghi sổ và thay file")
        V._write_atomic = boom
        snap = open(log, "rb").read()
        try:
            V.undo_last_restatement("r", "u", sp, log_path=log)
            ok(False, "u5 phải nổ")
        except OSError:
            ok(True, "u5")
        finally:
            V._write_atomic = real
        ok(md5(sp) == h1 and len(rd()) == n_log + 1 and rd()[-1]["kind"] == "undo" and rd()[-1]["md5_after"] == h0,
           "u5 sổ ĐÃ có dòng undo trước khi thay file")
        with open(log, "wb") as f:                                   # bỏ dòng undo của ca chết giữa chừng
            f.write(snap)
        # undo thật
        last_before = rd()[-1]
        res = V.undo_last_restatement("sai số cổ tức BBB", "user selfcheck", sp, log_path=log)
        ent = rd()
        ok(open(sp, "rb").read() == b0 and md5(sp) == h0, "u6 undo dựng lại ĐÚNG byte file gốc")
        u = ent[-1]
        ok(len(ent) == n_log + 1 and u["kind"] == "undo" and u["md5_before"] == h1 and u["md5_after"] == h0
           and u["undoes"] == last_before["md5_after"] == h1 and u["confirmed_by"] == "user selfcheck"
           and u["reason"] == "sai số cổ tức BBB" and u["ts_ict"].endswith("+07:00")
           and ent[:-1] == [json.loads(x) for x in snap.decode("utf-8").splitlines()], f"u6 dòng sổ undo: {u}")
        ok(res["md5_after"] == h0 and res["kind"] == "undo", f"u6 {res}")
        # undo chồng: dòng cuối đã là undo ⇒ từ chối
        try:
            V.undo_last_restatement("r", "u", sp, log_path=log)
            ok(False, "u7 undo chồng phải RestateRefused")
        except V.RestateRefused as exc:
            ok("đã là một undo" in str(exc), f"u7 {exc}")
        # N1: undo ĐÃ GHI SỔ nhưng file CHƯA thay (md5 file == md5_before của dòng undo) ⇒ thông báo nói đúng, không "đã là undo"
        sp_n1 = os.path.join(os.path.dirname(sp), "n1_series.csv")
        with open(sp_n1, "wb") as f:
            f.write(b0)
        log_n1 = os.path.join(os.path.dirname(sp), "n1_log.jsonl")
        with open(log_n1, "w", encoding="utf-8") as f:
            f.write(json.dumps({"series": os.path.abspath(sp_n1), "kind": "undo", "ts_ict": "2030-01-01T00:00:00+07:00",
                                "md5_before": md5(sp_n1), "md5_after": "0" * 32}) + "\n")
        try:
            V.undo_last_restatement("r", "u", sp_n1, log_path=log_n1)
            ok(False, "n1 phải RestateRefused")
        except V.RestateRefused as exc:
            ok("CHƯA được thay" in str(exc) and "đã là một undo" not in str(exc), f"n1 {exc}")
        # N2: đính chính CHƯA từng được áp (md5 file == md5_before của dòng sổ cuối) ⇒ thông báo nói đúng, không đoán --update
        with open(log_n1, "w", encoding="utf-8") as f:
            f.write(json.dumps({"series": os.path.abspath(sp_n1), "kind": "restate", "ts_ict": "2030-01-01T00:00:00+07:00",
                                "md5_before": md5(sp_n1), "md5_after": "0" * 32}) + "\n")
        try:
            V.undo_last_restatement("r", "u", sp_n1, log_path=log_n1)
            ok(False, "n2 phải RestateRefused")
        except V.RestateRefused as exc:
            ok("CHƯA từng được áp" in str(exc) and "--update?" not in str(exc), f"n2 {exc}")
        # sau undo, đính chính độc lập không bị gắn retry_of vào dòng undo
        V.restate_sealed([D[6]], "r", "u", sp, inputs=inp2, **kw)
        ok("retry_of" not in rd()[-1], "u8 prior là undo ⇒ không retry_of")
        # (3) dòng sổ CŨ thiếu byte cũ (dạng dòng 12:34 21/10) ⇒ ValueError/RestateRefused rõ ràng, KHÔNG KeyError
        old = {k: v for k, v in rd()[-1].items() if k not in ("rechained_sealed_before", "tail_before")}
        try:
            V.undo_restatement(old, open(sp, "rb").read())
            ok(False, "u9 dòng sổ thiếu byte cũ phải ValueError")
        except ValueError as exc:
            ok("rechained_sealed_before" in str(exc) and "tail_before" in str(exc), f"u9 {exc}")
        log2 = os.path.join(tmp, "u_log_old.jsonl")
        with open(log2, "w", encoding="utf-8") as f:
            f.write(json.dumps(old, ensure_ascii=False) + "\n")
        h2 = md5(sp)
        try:
            V.undo_last_restatement("r", "u", sp, log_path=log2)
            ok(False, "u10 phải RestateRefused")
        except V.RestateRefused as exc:
            ok("thiếu" in str(exc), f"u10 {exc}")
        ok(md5(sp) == h2 and len(open(log2).read().splitlines()) == 1, "u10 file + sổ không đổi")
        # CLI: thiếu --reason ⇒ rc=4; đủ ⇒ rc=0 + file về byte gốc
        base = [sys.executable, os.path.join(HERE, "vnindex_total_return.py"), "--undo-last-restatement",
                "--series", sp, "--restate-log", log]
        cp = subprocess.run(base + ["--confirmed-by", "u"], capture_output=True, text=True)
        ok(cp.returncode == 4 and "reason" in cp.stderr and md5(sp) == h2, f"u11 CLI thiếu reason rc={cp.returncode}")
        cp = subprocess.run(base + ["--confirmed-by", "u", "--reason", "r"], capture_output=True, text=True)
        ok(cp.returncode == 0 and md5(sp) == h0 and json.loads(cp.stdout)["kind"] == "undo",
           f"u11 CLI undo rc={cp.returncode}: {cp.stderr[-200:]}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vtr_sc_") as tmp:
        V.ACKS_PATH = os.path.join(tmp, "khong_co_acks.json")    # không đọc sổ ack thật của data/
        with g4_loose():
            t_update_checked_through(tmp)
            t_dy_corrupt(tmp)
            t_build_by_hand(tmp)
            t_sealed(tmp)
        t_seal_guard(tmp)
        t_restate(tmp)
        t_undo_polish(tmp)
    t_gates()
    print(f"OK — {N_OK} assertion PASS (vnindex_total_return_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
