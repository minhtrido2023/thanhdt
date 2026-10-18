#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `vnindex_total_return.py` (SPEC §A6) — không BQ, không mạng, không ghi
`data/` (mọi file ở thư mục tạm). Chạy dưới `env -u TZ` và một TZ lạ (§16/§19):

    env -u TZ python3 mike/bin/vnindex_total_return_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/vnindex_total_return_selfcheck.py

Lịch phiên dùng `trading_bot.vn_market` (CODE, chỉ đọc) của cây WorkingClaude chứa script.
"""
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
    _, inp3, _, _ = fixture(ca_extra=[("BBB", 8, 0.3, "Đợt 3")])         # Δy = 2e6·0,3/~1e11 ≈ 6e-6
    with open(sp, encoding="utf-8") as f:
        sealed0 = [ln for ln in f if ",sealed," in ln]
    V.update(sp, mp, inputs=inp3, src2=src2)
    with open(sp, encoding="utf-8") as f:
        sealed1 = [ln for ln in f if ",sealed," in ln]
    ok(sealed1 == sealed0, "ca6b phần sealed giữ nguyên byte khi Δy dưới ngưỡng")
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
    """G4 ack (18/10): ngày rổ tụt vì BQ thiếu dòng có NGƯỜI xác nhận ⇒ nhánh SỐ MÃ qua đúng ngày đó;
    ngày khác, nhánh vốn hoá, và mục thiếu confirmed_by/reason KHÔNG được qua."""
    day = D[64].isoformat()

    def g4(rows, acks):
        return [x for x in V.check_period(rows, a, b, acks) if x.startswith("G4")]
    dip = [dict(r) for r in base]
    for i in (64, 65, 66):        # rổ tụt rồi GIỮ mức mới tới hết kỳ ⇒ chỉ ngày tụt (D64) cần ack
        dip[i]["n_members"] = 94
    rebound = [dict(r) for r in base]
    rebound[64]["n_members"] = 94
    ok(any(D[65].isoformat() in x for x in g4(rebound, {(day, V.G4_ACK_KEY)})),
       "ngày bật lại >5% là một G4 RIÊNG, ack ngày tụt không che nó")
    ok(any(day in x for x in g4(dip, set())), "G4 số mã nổ khi chưa ack")
    ok(not any(day in x for x in g4(dip, {(day, V.G4_ACK_KEY)})), "G4 số mã có ack đúng ngày ⇒ qua")
    ok(any(day in x for x in g4(dip, {(D[63].isoformat(), V.G4_ACK_KEY)})), "ack ngày khác KHÔNG cứu")
    ok(any(day in x for x in g4(dip, {(day, "ZZZ")})), "ack kiểu G6 cùng ngày KHÔNG cứu G4")
    mc = [dict(r) for r in base]
    mc[64]["mc_members_vnd"] = mc[64]["mc_members_vnd"] * 1.05
    ok(any("vốn hoá" in x for x in g4(mc, {(day, V.G4_ACK_KEY)})), "ack G4 KHÔNG che nhánh vốn hoá")
    with tempfile.TemporaryDirectory(prefix="vtr_g4acks_") as tmp:
        good, bad = os.path.join(tmp, "good.json"), os.path.join(tmp, "bad.json")
        with open(good, "w", encoding="utf-8") as f:
            json.dump({"G4": [{"date": day, "confirmed_by": "user 2030-06-01", "reason": "BQ thiếu 20 mã"}]}, f)
        ok(V.load_acks(good) == {(day, V.G4_ACK_KEY)}, "ack G4 hợp lệ")
        ok(V.benchmark_period(a, b, series=dip, acks_path=good)["status"] == "ok", "benchmark ok khi có ack G4")
        for name, entry in (("thiếu confirmed_by", {"date": day, "reason": "x"}),
                            ("thiếu reason", {"date": day, "confirmed_by": "user"}),
                            ("reason rỗng", {"date": day, "confirmed_by": "user", "reason": ""}),
                            ("thiếu date", {"confirmed_by": "user", "reason": "x"})):
            with open(bad, "w", encoding="utf-8") as f:
                json.dump({"G4": [entry]}, f)
            try:
                V.load_acks(bad)
                ok(False, f"ack G4 {name} phải ValueError")
            except ValueError as exc:
                ok("G4" in str(exc), f"ack G4 {name}: {exc}")
            ok(V.benchmark_period(a, b, series=dip, acks_path=bad)["status"] == "unavailable",
               f"ack G4 {name} ⇒ benchmark unavailable")


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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vtr_sc_") as tmp:
        t_update_checked_through(tmp)
        t_dy_corrupt(tmp)
        t_build_by_hand(tmp)
        t_sealed(tmp)
    t_gates()
    print(f"OK — {N_OK} assertion PASS (vnindex_total_return_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
