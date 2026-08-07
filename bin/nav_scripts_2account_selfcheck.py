#!/usr/bin/env python3
"""nav_scripts_2account_selfcheck.py [--date YYYY-MM-DD]

Selfcheck cho 3 script kế toán dùng chung file input theo ngày (`data/execution_logs/
dnse_raw_{date}.jsonl` — trộn record của MỌI account, phân biệt bằng field accountNo)
— coding_guidelines.md §12 (RETRO 2026-07-19, "Shared Multi-Account Data Files"):
`daily_nav_snapshot.py`, `verify_account_snapshot.py`, `reconcile_equity.py`.

Đây CHÍNH XÁC là lớp file đã gây 3 sự cố lẫn account trong 15 ngày (2026-07-06
daily_nav_snapshot.py, 2026-07-19 reconcile_equity.py + verify_account_snapshot.py,
2026-07-21 eod_trading_report.sh) — root cause luôn giống nhau: quên lọc `accountNo`
trước khi tính. Bài kiểm rẻ nhất theo đúng §12: chạy script cho CẢ 2 account trong
CÙNG 1 ngày có dữ liệu thật, xác nhận 2 kết quả KHÁC nhau. Script này tự động hoá
đúng bài kiểm đó, để chạy lại được (không phải làm tay 1 lần rồi quên) — trước khi
sửa 1 trong 3 script trên, chạy lại cái này.

AN TOÀN: `daily_nav_snapshot.py` ghi đè `nav_history_{account}.csv` (nguồn duy nhất
mọi báo cáo dùng chung) — selfcheck BẮT BUỘC backup 2 file này trước khi chạy và
LUÔN restore lại sau (dù pass hay fail), không bao giờ để lại thay đổi thật trên đĩa.

PASS/FAIL chỉ dựa trên 1 tiêu chí: SpaceX và ZaloPay có ra kết quả KHÁC NHAU không (đúng
mục tiêu §12). 2 phát hiện phụ dưới đây chỉ IN CẢNH BÁO, không làm fail selfcheck:
- Tái tính cho 1 ngày QUÁ KHỨ sau khi có giao dịch MỚI hơn có thể lệch khỏi lịch sử đã lưu
  (phát hiện thật 2026-07-22: SpaceX bị chính guard NAV_SANITY_MAX_PCT tự chặn khi tái tính
  07-20/07-21 sau khi CAPIT mua thêm 07-21 — recompute dường như cuốn theo vị thế HIỆN TẠI).
  Đây là giới hạn tái-tính-ngày-cũ, KHÁC hẳn bug lẫn account.
- `reconcile_equity.py --starting-capital 1000000000` dùng số PLACEHOLDER chung cho cả 2
  account (không phải vốn ban đầu THẬT của từng account) — kỳ vọng LỆCH lớn ở đẳng thức nội
  bộ của nó, không có nghĩa gì về sổ sách thật. Chỉ dùng để so sánh 2 account có RA SỐ KHÁC
  NHAU hay không (chúng phải khác — nếu giống hệt mới là dấu hiệu bug thật).

  nav_scripts_2account_selfcheck.py                 -> tự chọn ngày gần nhất có đủ 2 account
  nav_scripts_2account_selfcheck.py --date 2026-07-20  -> chỉ định ngày
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(MIKE_BIN))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
ACCOUNTS = ["SpaceX", "ZaloPay"]


def _find_shared_date():
    """Ngày gần nhất mà dnse_raw_{date}.jsonl có bản ghi balances của CẢ 2 account."""
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        date = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        seen = set()
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("kind") == "balances":
                        acct = rec.get("accountNo") or rec.get("account_no")
                        if acct:
                            seen.add(str(acct))
        except Exception:
            continue
        if len(seen) >= 2:
            return date
    return None


def _fill_dates(upto_date, max_days=90):
    """Các ngày dnse_raw CÓ record khớp lệnh (fill), <= upto_date, mới nhất trước.

    `verify_account_snapshot.py --dates` KHÔNG phải "ngày cần xem" mà là CỬA SỔ LỊCH SỬ
    KHỚP LỆNH dùng để dựng giá vốn (help của nó ghi rõ "trading dates with fills").
    Truyền đúng 1 ngày chỉ-có-balances (cái mà _find_shared_date trả về) thì MỌI vị thế
    rơi vào nhánh "legacy — no fill history" và total_mtm_value = 0.0 cho CẢ 2 account —
    tức phép so "2 account phải khác nhau" của §12 bị suy biến ở mốc 0, báo nhầm thành
    lẫn account (sự cố weekly-ops-audit 2026-08-08). Trả về danh sách để nối bằng dấu phẩy.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        date = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        if date > upto_date:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get("kind") in ("place_order", "orders"):
                        out.append(date)
                        break
        except Exception:
            continue
        if len(out) >= max_days:
            break
    return sorted(out)


def _run(cmd, cwd=WC_ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=180)
    return p.returncode, p.stdout, p.stderr


def _backup(path):
    if os.path.isfile(path):
        bak = path + ".selfcheck_bak"
        shutil.copy2(path, bak)
        return bak
    return None


def _restore(path, bak):
    if bak and os.path.isfile(bak):
        shutil.move(bak, path)
    elif os.path.isfile(path) and not bak:
        # File didn't exist before the run but exists now -> our run created it, remove it.
        os.remove(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    args = ap.parse_args()

    date = args.date or _find_shared_date()
    if not date:
        print("FAIL: không tìm được ngày nào có dữ liệu balances cho cả 2 account trong "
              f"{EXEC_DIR}/dnse_raw_*.jsonl — không thể chạy selfcheck.")
        return 1
    print(f"Selfcheck 2-account interleaved — ngày dùng: {date}")
    _fd = _fill_dates(date)
    fill_dates_arg = ",".join(_fd) if _fd else date
    print(f"  cửa sổ fill cho verify_account_snapshot: {len(_fd)} ngày "
          f"({_fd[0] if _fd else 'n/a'} → {_fd[-1] if _fd else 'n/a'})")

    balance_raw = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
    if not os.path.isfile(balance_raw):
        print(f"FAIL: {balance_raw} không tồn tại.")
        return 1

    nav_history_paths = {a: os.path.join(EXEC_DIR, f"nav_history_{a}.csv") for a in ACCOUNTS}
    nav_snapshot_json_paths = {a: os.path.join(EXEC_DIR, f"nav_snapshot_{a}_{date}.json") for a in ACCOUNTS}
    backups = {}
    snapshot_json_existed = {}
    for a in ACCOUNTS:
        backups[a] = _backup(nav_history_paths[a])
        snapshot_json_existed[a] = os.path.isfile(nav_snapshot_json_paths[a])
        if snapshot_json_existed[a]:
            backups[a + "_snap"] = _backup(nav_snapshot_json_paths[a])

    results = {}
    failures = []
    tmpdir = tempfile.mkdtemp(prefix="nav_2acct_selfcheck_")
    try:
        for account in ACCOUNTS:
            r = {}
            # 1) verify_account_snapshot.py -- safe: explicit --out to a temp path.
            out_path = os.path.join(tmpdir, f"verify_{account}.json")
            rc, stdout, stderr = _run([
                sys.executable, os.path.join(MIKE_BIN, "verify_account_snapshot.py"),
                "--account", account, "--dates", fill_dates_arg, "--asof", date, "--out", out_path,
            ])
            r["verify_rc"] = rc
            if rc != 0 or not os.path.isfile(out_path):
                failures.append(f"{account}: verify_account_snapshot.py rc={rc} stderr={stderr[-300:]}")
                r["verify_mtm"] = None
            else:
                with open(out_path, encoding="utf-8") as f:
                    verify_json = json.load(f)
                r["verify_json_path"] = out_path
                # verify_account_snapshot.py doesn't compute a total NAV itself (that's
                # daily_nav_snapshot.py's job, which adds cash/margin) — use total_mtm_value
                # (market value of positions) as the per-account differentiator instead.
                r["verify_mtm"] = verify_json.get("total_mtm_value")

            # 2) reconcile_equity.py -- safe: stdout only, no file writes.
            if r.get("verify_mtm") is not None:
                rc, stdout, stderr = _run([
                    sys.executable, os.path.join(MIKE_BIN, "reconcile_equity.py"),
                    "--account", account, "--starting-capital", "1000000000",
                    "--snapshot", out_path, "--balance-raw", balance_raw,
                ])
                r["reconcile_rc"] = rc
                r["reconcile_stdout"] = stdout
            else:
                r["reconcile_rc"] = None
                r["reconcile_stdout"] = ""

            # 3) daily_nav_snapshot.py -- MUTATES nav_history_{account}.csv, restored after.
            rc, stdout, stderr = _run([
                sys.executable, os.path.join(MIKE_BIN, "daily_nav_snapshot.py"),
                "--account", account, "--date", date,
            ])
            r["daily_nav_rc"] = rc
            r["daily_nav_stdout"] = stdout
            results[account] = r
            print(f"\n--- {account} ---")
            print(f"  verify_account_snapshot.py: rc={r['verify_rc']} mtm={r.get('verify_mtm')}")
            print(f"  reconcile_equity.py: rc={r['reconcile_rc']}")
            print(f"  daily_nav_snapshot.py: rc={r['daily_nav_rc']} out={stdout.strip()[:200]}")

        # --- So sánh: 2 account PHẢI khác nhau (bài kiểm rẻ nhất theo §12) ---
        sx, zp = results.get("SpaceX", {}), results.get("ZaloPay", {})
        if sx.get("verify_mtm") is not None and zp.get("verify_mtm") is not None:
            if sx["verify_mtm"] == zp["verify_mtm"]:
                if not sx["verify_mtm"]:
                    # Bằng nhau ở mốc 0 KHÔNG phải bằng chứng lẫn account: nghĩa là cửa sổ
                    # fill không dựng được giá vốn cho mã nào (mọi vị thế rơi vào nhánh
                    # "legacy — no fill history"), nên phép so bị suy biến, không kết luận
                    # được theo chiều nào. Nói rõ là KHÔNG KẾT LUẬN ĐƯỢC, đừng vu cho §12.
                    failures.append(
                        f"verify_account_snapshot.py: CẢ 2 account ra total_mtm_value = 0 ngày {date} "
                        f"(cửa sổ fill {len(_fd)} ngày) — phép so §12 SUY BIẾN, KHÔNG kết luận được "
                        f"có lẫn account hay không. Kiểm tra cửa sổ fill trước khi nghi ngờ code.")
                else:
                    failures.append(
                        f"verify_account_snapshot.py: SpaceX và ZaloPay ra CÙNG total_mtm_value ({sx['verify_mtm']}) "
                        f"ngày {date} — gần như chắc chắn đang đọc chung dnse_raw không lọc account.")
        if sx.get("reconcile_stdout") and zp.get("reconcile_stdout"):
            if sx["reconcile_stdout"].strip() == zp["reconcile_stdout"].strip():
                failures.append(
                    "reconcile_equity.py: SpaceX và ZaloPay ra output STDOUT giống hệt nhau — "
                    "đáng ngờ, cần kiểm tra lọc account.")
        if sx.get("daily_nav_stdout") and zp.get("daily_nav_stdout"):
            if sx["daily_nav_stdout"].strip() == zp["daily_nav_stdout"].strip():
                failures.append(
                    "daily_nav_snapshot.py: SpaceX và ZaloPay in ra STDOUT giống hệt nhau — "
                    "đáng ngờ, cần kiểm tra lọc account.")

        # --- Thông tin thêm (KHÔNG phải pass/fail gate): NAV freshly-computed có khớp giá
        # trị đã lưu trong nav_history không, nếu ngày đó đã có sẵn 1 dòng lịch sử. CHỈ IN
        # CẢNH BÁO, không fail selfcheck — phát hiện thật (2026-07-22): các script này KHÔNG
        # an toàn để tái tính cho 1 ngày TRONG QUÁ KHỨ sau khi có giao dịch MỚI xảy ra (SpaceX
        # bị chính guard NAV_SANITY_MAX_PCT của nó tự chặn khi tái tính 07-20/07-21 sau khi
        # CAPIT mua thêm ~236M ngày 07-21 — recompute dường như cuốn theo vị thế HIỆN TẠI thay
        # vì đúng point-in-time của ngày được yêu cầu). Đây là 1 giới hạn thật của cơ chế tái
        # tính-theo-ngày-cũ, KHÁC với bug lẫn account (mục tiêu thật của selfcheck này) — không
        # nhầm 2 loại vấn đề với nhau. Không fail vì lý do đó; chỉ cảnh báo để biết.
        for account in ACCOUNTS:
            hist_path = nav_history_paths[account]
            bak = backups.get(account)
            if not bak:
                continue
            existing_nav = None
            with open(bak, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if parts and parts[0] == date and len(parts) > 1:
                        try:
                            existing_nav = float(parts[1])
                        except ValueError:
                            pass
            if existing_nav is None:
                continue
            new_nav = None
            if os.path.isfile(hist_path):
                with open(hist_path, encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if parts and parts[0] == date and len(parts) > 1:
                            try:
                                new_nav = float(parts[1])
                            except ValueError:
                                pass
            if new_nav is None:
                print(f"  (info) {account}: daily_nav_snapshot.py không ghi dòng ngày {date} khi tái "
                      f"tính (rc guard hoặc lỗi khác — xem stdout ở trên; KHÔNG tính là fail của "
                      f"selfcheck này, xem ghi chú ở trên hàm này).")
            elif abs(new_nav - existing_nav) / max(existing_nav, 1) > 0.001:
                print(f"  (info) {account}: NAV tái tính ({new_nav:,.0f}) lệch so với lịch sử đã lưu "
                      f"({existing_nav:,.0f}) cho ngày {date} — nhiều khả năng do giới hạn tái-tính-"
                      f"ngày-cũ nói trên, không phải bug lẫn account. KHÔNG tính là fail.")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        for a in ACCOUNTS:
            _restore(nav_history_paths[a], backups.get(a))
            if snapshot_json_existed[a]:
                _restore(nav_snapshot_json_paths[a], backups.get(a + "_snap"))
            elif os.path.isfile(nav_snapshot_json_paths[a]):
                os.remove(nav_snapshot_json_paths[a])
        print(f"\n(Đã restore nav_history_*.csv + nav_snapshot_*.json về đúng trạng thái trước khi chạy.)")

    print()
    if failures:
        print(f"FAIL — {len(failures)} vấn đề:")
        for f_ in failures:
            print(f"  - {f_}")
        return 1
    print(f"PASS — cả 3 script cho SpaceX/ZaloPay ra kết quả KHÁC NHAU đúng như kỳ vọng (ngày "
          f"{date}), không có dấu hiệu đọc chung/lẫn account. Xem dòng (info) ở trên nếu có "
          f"cảnh báo phụ (không phải fail).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
