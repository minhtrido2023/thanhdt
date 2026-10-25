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

AN TOÀN (sandbox hoá 2026-10-25, prevention (a) retro 2026-10-24): mặc định selfcheck chạy
3 script trên MỘT BẢN SAO `data/execution_logs` trong thư mục tạm (WC_ROOT giả có marker
`wc_env.sh`, mọi entry khác symlink về cây thật) và `daily_nav_snapshot.py --from-raw` (KHÔNG
gọi broker) ⇒ không bao giờ chạm `data/` thật, kể cả khi chạy từ worktree. Sau khi chạy, so md5
`nav_history_*.csv` + danh sách file của execution_logs THẬT trước/sau — đổi là FAIL. Cờ
`--no-sandbox` giữ cơ chế cũ (gọi broker thật, ghi `data/` thật, backup/restore) — chỉ để
tái hiện bug; backup mang tên DUY NHẤT (pid+uuid) và cả lượt chạy giữ flock độc quyền, hai
selfcheck đồng thời không giẫm lên backup của nhau. Cần `--date` < hôm nay (ICT): `--from-raw`
từ chối ngày hôm nay.

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
import fcntl
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

# Dùng CHÍNH hàm mà 3 script bị kiểm dùng (`wc_paths.find_wc_root`), KHÔNG đếm cấp thư mục.
# Trước 2026-09-27 dòng này là `dirname(dirname(MIKE_BIN))` ⇒ backup/restore của selfcheck và file
# mà `daily_nav_snapshot.py` GHI có thể là HAI cây khác nhau, và lời hứa "không bao giờ để lại
# thay đổi thật trên đĩa" ở đầu file bị VI PHẠM IM LẶNG.
# Đo thật (2026-09-27, job Taylor_20260927_103434): chạy selfcheck này từ một checkout KHÔNG nằm ở
# `<gốc>/WorkingClaude/mike` trong khi env có `WC_ROOT=/home/trido/thanhdt/WorkingClaude` (chính
# `bin/dispatch.sh` export biến này vào MỌI phiên agent) ⇒ selfcheck backup/restore bản
# `<checkout>/../data/...`, còn `daily_nav_snapshot.py` (dùng find_wc_root — env override thắng)
# GHI vào `/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_history_*.csv` THẬT. Quan sát
# được: 1 dòng NAV ngày 2026-09-27 (CHỦ NHẬT — không phải phiên) bị thêm vào lịch sử THẬT của CẢ
# SpaceX và ZaloPay, KHÔNG được restore, phải vá tay. Đó là nguồn DUY NHẤT của §31/WTD/MTD/
# since-inception ⇒ một dòng rác ở đây đi thẳng vào báo cáo nhà đầu tư.
WC_ROOT = wc_paths.find_wc_root(__file__)
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
ACCOUNTS = ["SpaceX", "ZaloPay"]


def _is_holiday(d):
    sys.path.insert(0, WC_ROOT)
    from trading_bot.vn_market import is_holiday
    return is_holiday(d)


def _today_ict():
    return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")


def _find_shared_date():
    """Ngày gần nhất mà dnse_raw_{date}.jsonl có bản ghi balances của CẢ 2 account."""
    today = _today_ict()
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        date = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        if date >= today:    # daily_nav_snapshot --from-raw từ chối ngày hôm nay
            continue
        d = datetime.strptime(date, "%Y-%m-%d")
        if d.weekday() >= 5 or _is_holiday(d.date()):   # T7/CN/lễ: bot vẫn ghi raw nhưng không có giá
            continue
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


def _run(cmd, cwd=WC_ROOT, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=180, env=env)
    return p.returncode, p.stdout, p.stderr


def _backup(path):
    """Backup tên DUY NHẤT (pid+uuid): hai lượt chạy đồng thời không ghi đè backup của nhau."""
    if os.path.isfile(path):
        bak = f"{path}.selfcheck_bak.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        shutil.copy2(path, bak)
        return bak
    return None


def _restore(path, bak):
    if bak and os.path.isfile(bak):
        shutil.move(bak, path)
    elif os.path.isfile(path) and not bak:
        # File didn't exist before the run but exists now -> our run created it, remove it.
        os.remove(path)


def _acquire_lock(lock_path):
    """flock độc quyền không chặn. Trả file object đang giữ khoá (đóng = nhả), hoặc None."""
    f = open(lock_path, "a")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def _make_sandbox(real_root, tmp_parent=None):
    """WC_ROOT giả: marker wc_env.sh, mọi entry cấp 1 symlink về cây thật, NGOẠI TRỪ `data`
    (cũng toàn symlink, riêng `execution_logs` là BẢN SAO thật) ⇒ ghi vào execution_logs chỉ
    chạm bản sao. Trả đường dẫn sandbox; người gọi rmtree."""
    sb = tempfile.mkdtemp(prefix="nav_2acct_sandbox_", dir=tmp_parent)
    for name in os.listdir(real_root):
        if name in ("data", "wc_env.sh"):
            continue
        os.symlink(os.path.join(real_root, name), os.path.join(sb, name))
    open(os.path.join(sb, "wc_env.sh"), "w").close()
    os.makedirs(os.path.join(sb, "data"))
    real_data = os.path.join(real_root, "data")
    for name in os.listdir(real_data):
        if name == "execution_logs":
            continue
        os.symlink(os.path.join(real_data, name), os.path.join(sb, "data", name))
    shutil.copytree(os.path.join(real_data, "execution_logs"),
                    os.path.join(sb, "data", "execution_logs"), symlinks=True)
    return sb


def _real_fingerprint(exec_dir):
    """(md5 các nav_history_*.csv, tên nav_snapshot_*/verified_snapshot_*) của execution_logs THẬT — để chứng minh sandbox
    không rò."""
    md5 = {}
    # md5 (bắt cả GHI ĐÈ file đã tồn tại, vd nav_snapshot_{acct}_{date}.json của ngày đang chạy)
    for pat in ("nav_history_*.csv", "nav_snapshot_*.json", "nav_gate_block_*"):
        for p in sorted(glob.glob(os.path.join(exec_dir, pat))):
            with open(p, "rb") as f:
                md5[os.path.basename(p)] = hashlib.md5(f.read()).hexdigest()
    # Chỉ tên file mà 3 script này có thể ghi (không lấy cả thư mục: bot/cron thật ghi dnse_raw,
    # journal... song song, sẽ gây FAIL giả).
    names = frozenset(n for n in os.listdir(exec_dir)
                      if n.startswith(("nav_snapshot_", "nav_gate_block_", "verified_snapshot_")))
    return md5, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--no-sandbox", action="store_true",
                    help="cơ chế cũ: gọi broker thật + ghi data/ thật (backup/restore). Chỉ để tái "
                         "hiện bug; mặc định chạy trên bản sao trong thư mục tạm.")
    args = ap.parse_args()

    lock = _acquire_lock(os.path.join(tempfile.gettempdir(), "nav_2acct_selfcheck.lock"))
    if lock is None:
        print("FAIL: một lượt nav_scripts_2account_selfcheck khác đang chạy (flock) — "
              "chạy song song sẽ giẫm backup/ghi chồng; thử lại sau.")
        return 1

    date = args.date or _find_shared_date()
    if date and date >= _today_ict():
        print(f"FAIL: --date {date} >= hôm nay (ICT) — `daily_nav_snapshot.py --from-raw` từ chối "
              f"ngày hôm nay; dùng ngày đã qua.")
        return 1
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

    sandbox = None
    run_root, run_env, exec_dir = WC_ROOT, None, EXEC_DIR
    fp_before = _real_fingerprint(EXEC_DIR)
    if not args.no_sandbox:
        sandbox = _make_sandbox(WC_ROOT)
        run_root = sandbox
        run_env = dict(os.environ, WC_ROOT=sandbox)
        exec_dir = os.path.join(sandbox, "data", "execution_logs")
        balance_raw = os.path.join(exec_dir, f"dnse_raw_{date}.jsonl")
        print(f"  sandbox: {sandbox} (--from-raw, không gọi broker, không chạm data/ thật)")

    nav_history_paths = {a: os.path.join(exec_dir, f"nav_history_{a}.csv") for a in ACCOUNTS}
    nav_snapshot_json_paths = {a: os.path.join(exec_dir, f"nav_snapshot_{a}_{date}.json") for a in ACCOUNTS}
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
            ], cwd=run_root, env=run_env)
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
                ], cwd=run_root, env=run_env)
                r["reconcile_rc"] = rc
                r["reconcile_stdout"] = stdout
            else:
                r["reconcile_rc"] = None
                r["reconcile_stdout"] = ""

            # 3) daily_nav_snapshot.py -- ghi nav_history_{account}.csv — trong sandbox là bản sao; --no-sandbox thì restore sau.
            rc, stdout, stderr = _run([
                sys.executable, os.path.join(MIKE_BIN, "daily_nav_snapshot.py"),
                "--account", account, "--date", date,
            ] + ([] if args.no_sandbox else ["--from-raw"]), cwd=run_root, env=run_env)
            r["daily_nav_rc"] = rc
            r["daily_nav_stdout"] = stdout
            if rc != 0:
                # rc≠0 làm bước 3 PASS rỗng (stdout trống ⇒ phép so "khác nhau" bị bỏ qua) — đúng
                # dạng selfcheck xanh giả (retro 2026-10-24 Pattern B): báo, đừng im.
                failures.append(f"{account}: daily_nav_snapshot.py rc={rc} ngày {date} — bước 3 không "
                                f"kiểm được gì (cuối tuần/lễ thiếu giá? thử --date khác). "
                                f"stderr={stderr.strip()[-200:]}")
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
        if sandbox:
            shutil.rmtree(sandbox, ignore_errors=True)
        for a in ACCOUNTS:
            _restore(nav_history_paths[a], backups.get(a))
            if snapshot_json_existed[a]:
                _restore(nav_snapshot_json_paths[a], backups.get(a + "_snap"))
            elif os.path.isfile(nav_snapshot_json_paths[a]):
                os.remove(nav_snapshot_json_paths[a])
        print(f"\n(Đã restore nav_history_*.csv + nav_snapshot_*.json về đúng trạng thái trước khi chạy.)")

    if not args.no_sandbox and _real_fingerprint(EXEC_DIR) != fp_before:
        failures.append(f"SANDBOX NGHI RÒ: nav_history/nav_snapshot/nav_gate_block của {EXEC_DIR} đổi sau lượt "
                        f"chạy. CÓ THỂ do cron NAV thật (EOD 19:10, nav_snapshot_daily 19:50, nav_sync_retry "
                        f"mỗi 15') ghi hợp lệ trong lúc selfcheck chạy — đối chiếu log cron/mtime TRƯỚC khi "
                        f"đụng vào dữ liệu; KHÔNG tự 'khôi phục'.")
    lock.close()

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
