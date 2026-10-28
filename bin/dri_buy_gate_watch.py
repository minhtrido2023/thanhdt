#!/usr/bin/env python3
"""dri_buy_gate_watch.py — cảnh báo CHỈ-ĐỌC khi DRI ≤ 13.100 + chạy checklist cổng G0–G5.

Đặc tả = `kb/projects/dri-triggers-20261027.md` § "CỔNG MUA THĂM DÒ DRI Ở ≤13.000" (user duyệt
28/10/2026). KHÔNG đặt/huỷ/sửa lệnh, KHÔNG ghi plan, KHÔNG gọi bot: DNSE chỉ qua `ReadOnlyDNSE`
(secdef/latest_trade/ohlc) của `intraday_price_watch`; đầu ra duy nhất = Telegram + file state.

Tự kiểm được: G3 (TSR20 ≥ 240¢ — BQ `commodity_prices` rubber, nguồn TE) · G4 (giá ≤ trần LO; phiên
tin xấu −5% & KL >2× TB20 trong 2 phiên gần nhất ⇒ chờ) · mốc ngày của G1. Còn lại (G0 duyệt user,
G1/G2 đọc BCTC, G3 phần Bobby, G5 CBTT HOSE) = THỦ CÔNG — tin nhắn nói thẳng "CHƯA ĐỦ CỔNG" trừ khi
mọi cổng PASS; không bao giờ suy PASS từ việc vắng dữ liệu (§28/§29).

Dùng:  dri_buy_gate_watch.py run [--force] [--dry] [--price N]
Cron ĐỀ XUẤT (host parse UTC; 02:15-07:45 UTC ⇔ 09:15-14:45 ICT T2-T6, mỗi 5'):
  */5 2-7 * * 1-5 cd /home/trido/thanhdt/WorkingClaude && TZ=Asia/Ho_Chi_Minh timeout 50 /home/trido/thanhdt/wc_venv/bin/python mike/bin/dri_buy_gate_watch.py run >> mike/logs/dri_buy_gate_watch.log 2>&1
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
MIKE = os.path.join(WC, "mike")
sys.path.insert(0, WC)
sys.path.insert(0, HERE)

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
TICKER = "DRI"
LEVEL1, LEVEL2 = 13_100, 11_600          # báo trước trần LO 13.000 / 11.500 một nấc (100đ)
LO1, LO2 = 13_000, 11_500
TSR_MIN = 240.0                          # ¢/kg — mốc bán 234 + đệm 6
BAD_DAY_PCT, BAD_DAY_VOLX = -5.0, 2.0
TSR_MAX_AGE_DAYS = 5
G1_A_DATE = dt.date(2026, 10, 30)        # BCTC Q3 chi tiết
G1_B_DATE = dt.date(2026, 11, 10)        # SXKD tháng 10
EXPIRY = dt.date(2027, 4, 28)            # time stop G7
SCAN_START, SCAN_END = dt.time(9, 15), dt.time(14, 45)
STATE = os.path.join(WC, "data", "dri_buy_gate_watch_state.json")
NOTIFY_TG = os.path.join(MIKE, "bin", "notify_telegram.sh")


def _atomic_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


# ------------------------------------------------------------------ logic thuần (selfcheck)
def eval_g1(today):
    if today < G1_A_DATE:
        return "WAIT", f"chưa tới BCTC Q3 chi tiết ({G1_A_DATE:%d/%m}) ⇒ tranche A chưa được mua"
    if today < G1_B_DATE:
        return "MANUAL", f"BCTC Q3 đã có thể ra: đọc checklist; tranche B chờ SXKD T10 ({G1_B_DATE:%d/%m})"
    return "MANUAL", "đọc BCTC Q3 + SXKD T10 (trigger GIẢM NỐT: bán ≥1.000 t & LNTT 10T ≥208,21 tỷ)"


def eval_g3(tsr, tsr_date, today):
    if tsr is None:
        return "UNKNOWN", "không đọc được TSR20 (BQ) — không suy PASS"
    age = (today - tsr_date).days
    if age > TSR_MAX_AGE_DAYS:
        return "UNKNOWN", f"TSR20 {tsr:.1f}¢ nhưng cũ {age} ngày ({tsr_date:%d/%m}) — không dùng"
    if tsr < TSR_MIN:
        return "FAIL", f"TSR20 {tsr:.1f}¢ < {TSR_MIN:.0f}¢ ({tsr_date:%d/%m}); mốc bán 234¢"
    return "PARTIAL", f"TSR20 {tsr:.1f}¢ ≥ {TSR_MIN:.0f}¢ ({tsr_date:%d/%m}); còn 3 chỉ báo Bobby (thủ công)"


def eval_g4(price, bars, lo):
    """bars = [(date, close, volume)] tăng dần, phiên cuối có thể là hôm nay (chưa đủ KL)."""
    if price is None:
        return "UNKNOWN", "không đọc được giá DNSE"
    notes = []
    status = "PASS" if price <= lo else "FAIL"
    notes.append(f"giá {price:,.0f} {'≤' if price <= lo else '>'} trần LO {lo:,.0f}")
    if len(bars) >= 3:
        for i in (-2, -1):
            d, c, v = bars[i]
            prev = bars[i - 1][1]
            base = [x[2] for x in bars[:i][-20:]]
            if not prev or not base:
                continue
            pct = (c / prev - 1) * 100
            volx = v / (sum(base) / len(base)) if sum(base) else 0
            if pct <= BAD_DAY_PCT and volx >= BAD_DAY_VOLX:
                status = "WAIT"
                notes.append(f"phiên {d:%d/%m} tin xấu ({pct:+.1f}%, KL {volx:.1f}×TB20) ⇒ chờ 2 phiên + đọc tin")
    else:
        status = "UNKNOWN" if status == "PASS" else status
        notes.append("thiếu lịch sử phiên để kiểm tin xấu")
    notes.append("thủ công: ex-date/ĐHCĐ; chỉ lệnh LO")
    return status, "; ".join(notes)


def verdict(gates):
    """Chỉ 'ĐỦ' khi mọi cổng PASS. Thủ công/PARTIAL/UNKNOWN/WAIT/FAIL ⇒ CHƯA ĐỦ."""
    return "ĐỦ" if all(s == "PASS" for s, _ in gates.values()) else "CHƯA ĐỦ CỔNG"


def build_message(price, level, lo, gates, today):
    icon = {"PASS": "✅", "FAIL": "❌", "WAIT": "⏳", "MANUAL": "🖐", "PARTIAL": "🟡", "UNKNOWN": "❔"}
    lines = [f"DRI {price:,.0f} ≤ {level:,.0f} — chạm vùng mua thăm dò (trần LO {lo:,.0f}). "
             f"{today:%d/%m/%Y}", ""]
    for k in ("G0", "G1", "G2", "G3", "G4", "G5"):
        s, t = gates[k]
        lines.append(f"{icon.get(s, '?')} {k} {s}: {t}")
    lines += ["", f"KẾT LUẬN: {verdict(gates)}.",
              "Tranche 1: SpaceX ~300 cp / ZaloPay ~150 cp (G5 chưa CBTT ⇒ giảm nửa). Cần user duyệt từng tranche; "
              "script này KHÔNG đặt lệnh. Chi tiết: kb/projects/dri-triggers-20261027.md (G0–G7)."]
    return "\n".join(lines)


# ------------------------------------------------------------------ I/O
def read_price_and_bars(now):
    from intraday_price_watch import LiveMarket
    m = LiveMarket()
    q = m.quote(TICKER)
    if q.get("error"):
        raise RuntimeError(q["error"])
    price = q.get("last")
    a = int((now - dt.timedelta(days=45)).timestamp())
    b = int((now + dt.timedelta(days=1)).timestamp())
    r = m.ro.ohlc(TICKER, resolution="1D", **{"from": a, "to": b})
    bars = [(dt.datetime.fromtimestamp(t, _ICT).date(), r["c"][i] * 1000, r["v"][i])
            for i, t in enumerate(r.get("t", []))]
    return price, bars


def read_tsr20():
    sql = ("SELECT observation_date, value FROM tav2_bq.commodity_prices WHERE metric_key='rubber' "
           "AND source='trading_economics' AND cadence='daily' ORDER BY observation_date DESC LIMIT 1")
    cmd = (f". {WC}/wc_env.sh && bq query --use_legacy_sql=false --format=json "
           f"--project_id=lithe-record-440915-m9 \"{sql}\"")
    try:
        out = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=40)
        row = json.loads(out.stdout)[0]
        return float(row["value"]), dt.date.fromisoformat(row["observation_date"])
    except Exception as e:  # noqa: BLE001 — thiếu nguồn ⇒ UNKNOWN, không đoán
        print(f"[dri_gate] ⚠ TSR20: {type(e).__name__}: {e}", file=sys.stderr)
        return None, None


def send_telegram(msg):
    r = subprocess.run(["bash", NOTIFY_TG, msg], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        print(f"[dri_gate] ⚠ Telegram rc={r.returncode}: {r.stderr[-300:]}", file=sys.stderr)
    return r.returncode == 0


def run(args):
    now = dt.datetime.now(_ICT)
    today = now.date()
    if today > EXPIRY:
        return 0
    if not args.force and not (now.weekday() < 5 and SCAN_START <= now.time() <= SCAN_END):
        return 0
    if args.price is not None:
        price, bars = float(args.price), []
    else:
        try:
            price, bars = read_price_and_bars(now)
        except Exception as e:  # noqa: BLE001
            print(f"[dri_gate] ⚠ DNSE: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    if price is None or price > LEVEL1:
        return 0
    level, lo = (LEVEL2, LO2) if price <= LEVEL2 else (LEVEL1, LO1)
    state = _read_json(STATE, {})
    key = f"{today}|L{1 if level == LEVEL1 else 2}"
    if state.get("sent", {}).get(key) and not args.force:
        return 0
    tsr, tsr_d = read_tsr20()
    gates = {"G0": ("MANUAL", "user duyệt từng tranche; vị thế DRI cũ+mới ≤2–4% NAV/TK (trần cứng 5%)"),
             "G1": eval_g1(today),
             "G2": ("MANUAL", "Dakruco ≤40 tỷ · TDND ≤70 tỷ & không ngoại trừ · không sự kiện Lào · không xả tồn che LN"),
             "G3": eval_g3(tsr, tsr_d, today),
             "G4": eval_g4(price, bars, lo),
             "G5": ("MANUAL", "chưa xác nhận CBTT chính thức hồ sơ HOSE ⇒ giảm tranche một nửa")}
    msg = build_message(price, level, lo, gates, today)
    print(msg)
    if args.dry:
        return 0
    if send_telegram(msg):
        state.setdefault("sent", {})[key] = now.isoformat(timespec="seconds")
        _atomic_json(STATE, state)
        return 0
    return 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("run")
    rp.add_argument("--force", action="store_true")
    rp.add_argument("--dry", action="store_true")
    rp.add_argument("--price", type=float)
    sys.exit(run(ap.parse_args()))
