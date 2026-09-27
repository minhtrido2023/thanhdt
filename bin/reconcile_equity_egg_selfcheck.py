#!/usr/bin/env python3
"""Selfcheck cho bản vá 2026-09-27 của `reconcile_equity.py`: vế phải PHẢI cộng Trứng vàng
(`egg.totalValue`, §25 chiều thứ ba). Chạy trên dữ liệu broker THẬT (`dnse_raw_*.jsonl`) chứ
không phải fixture tự bịa — đó là điều kiện duy nhất chứng minh được residual giả đã hết.

    python3 bin/reconcile_equity_egg_selfcheck.py [--mutations]

4 nhóm assertion:
  A. Sau sửa, `unexplained_pct_of_rhs` của CẢ 2 account ≤ 0,05% NAV (trước sửa: 9,58% / 11,96%).
  B. §12 — 2 account cho kết quả KHÁC nhau (cùng file dnse_raw dùng chung ⇒ giống nhau = không lọc).
  C. Raw KHÔNG có key `egg` (trước 2026-08-18) ⇒ `egg_assets` = 0 VÀ vế phải đúng hệt công thức
     cũ `mtm + cash − debt` ⇒ bản vá không đổi hành vi lịch sử.
  D. `--mutations`: bỏ `+ egg_value` khỏi vế phải ⇒ assertion nhóm A PHẢI chết (nếu vẫn xanh thì
     test không đo cái nó tuyên bố đo).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(BIN, "reconcile_equity.py")
sys.path.insert(0, BIN)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
EXEC = os.path.join(WC_ROOT, "data", "execution_logs")

# Fixture ngày cố định (KHÔNG dùng datetime.now — §16: selfcheck không được phụ thuộc TZ/hôm nay).
EGG_DATE = "2026-09-25"      # raw CÓ egg
NOEGG_DATE = "2026-08-01"    # raw TRƯỚC khi DNSE expose egg
ACCOUNTS = {"SpaceX": ["--starting-capital", "1000000000"], "ZaloPay": []}
MAX_UNEXPLAINED_PCT = 0.05   # cổng đối soát muốn dùng được để bắt dòng tiền nhỏ


def run(script, account, date, extra=(), tmpdir=None):
    """Chạy reconcile và trả dict JSON nó ghi ra. Snapshot được COPY sang tmpdir để output
    KHÔNG ghi đè artifact canonical `data/execution_logs/reconcile_equity_*.json`."""
    src = os.path.join(EXEC, f"verified_snapshot_{account}_{date}.json")
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    snap = os.path.join(tmpdir, f"verified_snapshot_{account}_{date}.json")
    with open(src, "rb") as fi, open(snap, "wb") as fo:
        fo.write(fi.read())
    cmd = [sys.executable, script, "--account", account, "--snapshot", snap,
           "--balance-raw", os.path.join(EXEC, f"dnse_raw_{date}.jsonl")] + \
        ACCOUNTS[account] + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = snap.replace("verified_snapshot", "reconcile_equity")
    if not os.path.exists(out):
        raise RuntimeError(f"{script} không ghi được {out}\nrc={p.returncode}\n{p.stdout}\n{p.stderr}")
    return json.load(open(out, encoding="utf-8")), p.stdout


def egg_from_raw(date, account_no):
    """egg.totalValue của bản ghi balances CUỐI CÙNG cho ĐÚNG account (§12)."""
    val = None
    for line in open(os.path.join(EXEC, f"dnse_raw_{date}.jsonl"), encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("kind") != "balances" or rec.get("account_no") not in (None, account_no):
            continue
        val = float((rec.get("payload", {}).get("egg") or {}).get("totalValue") or 0)
    return val


def account_no_of(account):
    sys.path.insert(0, WC_ROOT)
    from trading_bot.config import load_config, load_accounts
    m = next((p for p in load_accounts(load_config()) if p["label"] == account), None)
    return m.get("account_id") if m else None


def checks(script, tmpdir, fails, n):
    res = {}
    # A — residual thật sau sửa
    for acc in ACCOUNTS:
        r, _ = run(script, acc, EGG_DATE, tmpdir=tmpdir)
        res[acc] = r
        egg_raw = egg_from_raw(EGG_DATE, account_no_of(acc))
        n[0] += 1
        if abs(r["egg_assets"] - egg_raw) > 1:
            fails.append(f"A/{acc}: egg_assets {r['egg_assets']:,.0f} != egg.totalValue trong raw {egg_raw:,.0f}")
        n[0] += 1
        if abs(r["unexplained_pct_of_rhs"]) > MAX_UNEXPLAINED_PCT:
            fails.append(f"A/{acc}: unexplained {r['unexplained_pct_of_rhs']:+.4f}% NAV "
                         f"> ngưỡng {MAX_UNEXPLAINED_PCT}% (residual giả do bỏ sót egg chưa hết)")
        n[0] += 1
        if not r["within_tolerance"]:
            fails.append(f"A/{acc}: đẳng thức chính vẫn LỆCH VƯỢT NGƯỠNG sau sửa")
        n[0] += 1
        if not r["egg_assets_auto"]:
            fails.append(f"A/{acc}: egg_assets_auto=False dù không truyền --no-egg")
    # B — §12: 2 account phải khác nhau
    a, b = res["SpaceX"], res["ZaloPay"]
    for k in ("cash", "mtm_stock", "egg_assets", "rhs_balance_sheet_path"):
        n[0] += 1
        if a[k] == b[k]:
            fails.append(f"B: SpaceX và ZaloPay cùng {k}={a[k]:,.0f} — dấu hiệu đọc "
                         f"dnse_raw dùng chung mà KHÔNG lọc account_no (§12)")
    # C — raw trước khi có egg: egg=0 và vế phải đúng công thức cũ
    for acc in ACCOUNTS:
        r, _ = run(script, acc, NOEGG_DATE, tmpdir=tmpdir)
        n[0] += 1
        if r["egg_assets"] != 0:
            fails.append(f"C/{acc}: raw {NOEGG_DATE} không có key egg mà egg_assets={r['egg_assets']}")
        expect = r["mtm_stock"] + r["cash"] - r["margin_debt"] + r["offbook_assets_used"]
        n[0] += 1
        if abs(r["rhs_balance_sheet_path"] - expect) > 1:
            fails.append(f"C/{acc}: vế phải {r['rhs_balance_sheet_path']:,.0f} != công thức cũ {expect:,.0f}")
    return res


MUTATIONS = {
    "bo-egg-khoi-ve-phai": (
        "rhs = mtm_stock + cash - debt + egg_value + args.offbook_assets",
        "rhs = mtm_stock + cash - debt + args.offbook_assets"),
    "egg-luon-0": (
        'egg_value = 0.0 if args.no_egg else float(',
        'egg_value = 0.0 if True else float('),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutations", action="store_true", help="chạy thêm mutation test")
    args = ap.parse_args()
    rc = 0
    with tempfile.TemporaryDirectory() as tmp:
        fails, n = [], [0]
        res = checks(SCRIPT, tmp, fails, n)
        for acc, r in res.items():
            print(f"  {acc}: egg {r['egg_assets']:>14,.0f} | residual {r['residual']:>+14,.0f} "
                  f"| dư sau diễn giải {r['unexplained_after_estimates']:>+12,.0f} "
                  f"({r['unexplained_pct_of_rhs']:+.4f}% NAV)")
        print(f"{'✅' if not fails else '❌'} {n[0] - len(fails)}/{n[0]} assertion PASS")
        for f in fails:
            print(f"   ❌ {f}")
        rc = 1 if fails else 0

        if args.mutations:
            src = open(SCRIPT, encoding="utf-8").read()
            killed = 0
            for name, (old, new) in MUTATIONS.items():
                if old not in src:
                    print(f"   ❌ mutation {name}: KHÔNG tìm thấy đoạn cần đổi — test đã mốc")
                    rc = 1
                    continue
                mpath = os.path.join(BIN, f"_mut_reconcile_equity_{name.replace('-', '_')}.py")
                open(mpath, "w", encoding="utf-8").write(src.replace(old, new, 1))
                try:
                    mf, mn = [], [0]
                    try:
                        checks(mpath, tmp, mf, mn)
                    except Exception as e:      # mutation làm script chết hẳn cũng là bị GIẾT
                        mf.append(f"crash: {e}")
                    if mf:
                        killed += 1
                        print(f"   ✅ mutation {name} BỊ GIẾT ({len(mf)} assertion fail, "
                              f"vd: {mf[0][:110]})")
                    else:
                        print(f"   ❌ mutation {name} SỐNG SÓT — selfcheck không đo egg thật")
                        rc = 1
                finally:
                    os.remove(mpath)
            print(f"{'✅' if killed == len(MUTATIONS) else '❌'} mutation: {killed}/{len(MUTATIONS)} bị giết")
    return rc


if __name__ == "__main__":
    sys.exit(main())
