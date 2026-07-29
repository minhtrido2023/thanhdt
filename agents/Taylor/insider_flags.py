#!/usr/bin/env python3
"""
insider_flags.py — writer cờ WATCH "nội bộ bán mạnh" (shadow, CHƯA wire production)
==================================================================================
Job Taylor_20260729_104614 (§5.3 của research/insider_transaction_scoping_20260729.md).
READ-ONLY với thị trường: chỉ đọc BQ + ghi data/insider_flags.json. Không đổi logic
trading, không loại mã của bất kỳ sổ nào — reader riêng
`anomaly_gate.insider_sell_flagged()` là WATCH-only, KHÔNG merge vào `anomaly_excluded`.

Điều kiện bắn cờ (pin ở §3.4, tái lập ĐÚNG công thức exp_insider/gate_analysis.py dòng
"ban >=1% CP luu hanh" — là AND của HAI vế, không chỉ vế khối lượng):
    sell_sh_90 / OShares >= 1,0%   VÀ   nsell_90 > nbuy_90
  trong đó cửa sổ 90 ngày = `asof - 90d < public_date <= asof` (giống panel2.sql),
  nsell/nbuy đếm SỐ NGƯỜI phân biệt (`trader_person_id`), không đếm số dòng.
Số đo của ngưỡng này: bắt 5,4% universe, P(fwd60 < -20%) = 19,68% vs nền 11,28%
(lift 1,745×, z=12,90), ổn định IS↔OOS. ~80% mã bị bắt KHÔNG sập ⇒ WATCH, không exclude.

3 bẫy dữ liệu bắt buộc (mike/kb/data_registry/fundamentals/insider_transaction.md):
  - chỉ `event_code IN ('DDIND','DDRP')` — KHÔNG lấy `DDINS` (flow tổ chức, không phải inside info)
  - chỉ `trade_status = 'Đã thực hiện xong'` — dòng `Đăng ký` có public_date nghĩa khác
  - `share_acquire` KHÔNG luôn có dấu (~2.500 dòng Bán dương) ⇒ TỰ áp dấu theo `action_code`

Nguồn = LIVE BQ (bảng không có trong bq_cache; và theo coding_guidelines §11 script publish
phải đọc live, không qua cache env kế thừa).

Output: data/insider_flags.json
    {ticker: {last_alert, tier, reasons, sell_pct_osh, n_sellers, window_end}}
  cùng shape với data/anomaly_flags.json (ghi atomic tmp+os.replace, guidelines §5).
  TTL = 90 ngày (khác anomaly 30) — do reader áp, file này không tự xoá cờ cũ.

Usage:
  python3 insider_flags.py                    # asof = hôm nay
  python3 insider_flags.py --asof 2026-07-24
  python3 insider_flags.py --no-flags         # chỉ in, không ghi file
  python3 insider_flags.py --selftest         # replay ca đã biết từ exp_insider/panel2.csv
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
FLAGS_PATH = os.path.join(WC, "data", "insider_flags.json")
PROJECT = "lithe-record-440915-m9"

SELL_PCT_OSH_MIN = 0.01   # §3.4: 1,0% CP lưu hành / 90 ngày (plateau với 0,5%, không phải đỉnh nhọn)
WINDOW_DAYS = 90
STALE_SESSIONS_MAX = 10   # §4.4: bảng cũ hơn ~10 phiên ⇒ WARN + KHÔNG bắn cờ mới

FLAG_SQL = """
WITH ins AS (
  SELECT i.ticker, i.public_date, i.trader_person_id AS pid,
         IF(i.action_code = "S", -ABS(i.share_acquire), ABS(i.share_acquire)) AS qty
  FROM tav2_bq.insider_transaction AS i
  WHERE i.event_code IN ("DDIND","DDRP")
    AND i.action_code IN ("B","S")
    AND i.trade_status = "Đã thực hiện xong"
    AND i.share_acquire IS NOT NULL AND ABS(i.share_acquire) > 0
    AND i.public_date <= DATE "{asof}"
    AND i.public_date > DATE_SUB(DATE "{asof}", INTERVAL {win} DAY)
),
agg AS (
  SELECT x.ticker,
         SUM(IF(x.qty < 0, -x.qty, 0)) AS sell_sh_90,
         COUNT(DISTINCT IF(x.qty < 0, x.pid, NULL)) AS nsell_90,
         COUNT(DISTINCT IF(x.qty > 0, x.pid, NULL)) AS nbuy_90,
         MAX(IF(x.qty < 0, x.public_date, NULL)) AS last_sell_date
  FROM ins x GROUP BY 1
),
osh AS (
  SELECT q.ticker, q.OShares
  FROM tav2_bq.ticker_financial AS q
  WHERE q.OShares > 0 AND q.time <= DATE "{asof}"
  QUALIFY ROW_NUMBER() OVER (PARTITION BY q.ticker ORDER BY q.time DESC) = 1
)
SELECT a.ticker, a.last_sell_date, a.nsell_90, a.nbuy_90, a.sell_sh_90, o.OShares,
       SAFE_DIVIDE(a.sell_sh_90, o.OShares) AS sell_pct_osh
FROM agg a JOIN osh o ON o.ticker = a.ticker
WHERE a.nsell_90 > a.nbuy_90
  AND SAFE_DIVIDE(a.sell_sh_90, o.OShares) >= {thr}
ORDER BY sell_pct_osh DESC
"""


def bq_csv(sql):
    """Chạy 1 query, trả về list[dict] (header + rows). Lỗi bq ⇒ raise, KHÔNG nuốt."""
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", "--format=csv",
         f"--project_id={PROJECT}", "--max_rows=100000", sql],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"bq query lỗi: {out.stderr.strip()[:500]}")
    lines = [l for l in out.stdout.strip().splitlines() if l.strip()]
    if len(lines) < 2:
        return []
    import csv as _csv
    return list(_csv.DictReader(lines))


def table_max_public_date():
    rows = bq_csv("SELECT MAX(i.public_date) AS d FROM tav2_bq.insider_transaction AS i")
    return datetime.date.fromisoformat(rows[0]["d"]) if rows and rows[0]["d"] else None


def sessions_between(d0, d1):
    """Số phiên (xấp xỉ) giữa d0 và d1 = số ngày T2-T6.

    Cố ý KHÔNG tra lịch giao dịch thật: (a) không tạo thêm phụ thuộc vào một bảng có thể
    cũng đang cũ, (b) đếm cả ngày lễ ⇒ ƯỚC LƯỢNG THỪA ⇒ dễ WARN hơn một chút, đúng hướng
    thận trọng cho một cổng "đừng bắn cờ khi nguồn có thể đã chết".
    """
    n, d = 0, d0
    while d < d1:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def scan(asof):
    sql = FLAG_SQL.format(asof=asof.isoformat(), win=WINDOW_DAYS, thr=SELL_PCT_OSH_MIN)
    recs = []
    for r in bq_csv(sql):
        recs.append({
            "ticker": r["ticker"],
            "last_alert": r["last_sell_date"],
            "tier": "W",                       # WATCH-only: cờ này KHÔNG bao giờ là hard-exclude
            "reasons": "INSIDER_SELL_1PCT",
            "sell_pct_osh": round(float(r["sell_pct_osh"]), 5),
            "n_sellers": int(r["nsell_90"]),
            "window_end": asof.isoformat(),
        })
    return recs


def write_flags(recs, path=FLAGS_PATH):
    """Merge vào file cũ + ghi atomic. Idempotent: chạy lại cùng asof cho file y hệt.

    Bản ghi cũ chỉ bị thay khi cờ mới có last_alert MỚI HƠN — tránh trường hợp cửa sổ 90d
    trượt qua giao dịch cũ rồi ghi đè last_alert cũ bằng chi tiết của một giao dịch khác
    (sẽ tạo bản ghi lai: ngày của cái này, số liệu của cái kia).
    """
    flags = {}
    if os.path.exists(path):
        try:
            flags = json.load(open(path, encoding="utf-8"))
        except Exception as ex:
            print(f"  WARNING: {path} hỏng ({ex}) — ghi lại từ đầu")
            flags = {}
    n_new = n_upd = 0
    for r in recs:
        cur = flags.get(r["ticker"])
        if cur is None:
            n_new += 1
        elif str(r["last_alert"]) > str(cur.get("last_alert", "")):
            n_upd += 1
        else:
            continue
        flags[r["ticker"]] = {k: v for k, v in r.items() if k != "ticker"}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(flags, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)
    return n_new, n_upd, len(flags)


def selftest():
    """Ca đã biết từ exp_insider/panel2.csv (cột time=2026-07-24, ngưỡng 1% + nsell>nbuy)."""
    asof = datetime.date(2026, 7, 24)
    expect = {"ITD": 0.151343, "BIG": 0.075561, "BMS": 0.028817,
              "VCI": 0.014681, "TOS": 0.013333, "DIG": 0.012155}
    recs = {r["ticker"]: r for r in scan(asof)}
    ok = True
    for tk, pct in expect.items():
        got = recs.get(tk)
        hit = got is not None and abs(got["sell_pct_osh"] - pct) < 1e-4
        print(f"  {tk}: kỳ vọng {pct:.5f} → thực tế "
              f"{got['sell_pct_osh'] if got else 'KHÔNG BẮT ĐƯỢC'} {'PASS' if hit else 'FAIL'}")
        ok &= hit
    # negative control: mã không có insider-sell KHÔNG được xuất hiện
    for tk in ("FPT", "ACB"):
        neg = tk not in recs
        print(f"  {tk} (không kỳ vọng cờ): {'PASS' if neg else 'FAIL — bị bắt nhầm'}")
        ok &= neg
    print(f"  tổng số mã bị bắt toàn thị trường asof {asof}: {len(recs)}")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", help="YYYY-MM-DD (mặc định: hôm nay)")
    ap.add_argument("--no-flags", action="store_true", help="chỉ in, không ghi JSON")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=FLAGS_PATH)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())

    asof = datetime.date.fromisoformat(args.asof) if args.asof else datetime.date.today()

    # --- fail-safe freshness (§4.4): nguồn chết ⇒ WARN + KHÔNG bắn cờ mới, KHÔNG đụng file cũ ---
    max_pub = table_max_public_date()
    if max_pub is None:
        print("WARNING: insider_transaction rỗng/không đọc được — KHÔNG ghi cờ.")
        sys.exit(2)
    stale = sessions_between(max_pub, asof)
    print(f"# insider_flags — asof {asof} | MAX(public_date)={max_pub} (~{stale} phiên trước)")
    if stale > STALE_SESSIONS_MAX:
        print(f"WARNING: bảng cũ hơn {STALE_SESSIONS_MAX} phiên ⇒ nguồn nhiều khả năng đã dừng "
              f"cập nhật. KHÔNG bắn cờ mới (cờ cũ trong file vẫn hết hạn theo TTL 90 ngày ở "
              f"reader — cố ý không đóng băng để tránh cảm giác 'sạch' giả).")
        sys.exit(3)

    recs = scan(asof)
    if not recs:
        print("Không có mã nào vượt ngưỡng nội bộ bán ≥1% CP lưu hành/90 ngày.")
    for r in sorted(recs, key=lambda x: -x["sell_pct_osh"]):
        print(f"  [{r['tier']}] {r['last_alert']} {r['ticker']}: bán "
              f"{r['sell_pct_osh']*100:.2f}% CP lưu hành/90d, {r['n_sellers']} người bán")
    if not args.no_flags:
        n_new, n_upd, n_tot = write_flags(recs, args.out)
        print(f"→ đã ghi {args.out} (mới {n_new}, cập nhật {n_upd}, tổng {n_tot} mã)")


if __name__ == "__main__":
    main()
