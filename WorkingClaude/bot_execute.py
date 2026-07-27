# -*- coding: utf-8 -*-
"""Bước 2 — Thực thi trading plan trong phiên (chạy sáng trước 09:15, để chạy cả ngày).

  python bot_execute.py                       # MỌI account có plan hôm nay, 1 process
  python bot_execute.py --account main        # chỉ 1 account (lặp lại được)
  python bot_execute.py --otp main=123456 --otp acc2=654321   # Smart OTP theo account
  python bot_execute.py --otp 123456          # 1 OTP áp cho mọi account live cùng login
  python bot_execute.py --date 2026-06-13     # ép ngày plan
  python bot_execute.py --once                # 1 vòng rồi thoát (debug)
  python bot_execute.py --force-phase MORNING # test ngoài giờ (paper)
  python bot_execute.py --probe HPG [--broker dnse]  # dump quote thô rồi thoát
  python bot_execute.py --send-otp acc_dnse   # gửi email OTP (DNSE email_otp) rồi thoát

Tất cả account chạy trong MỘT vòng lặp, dùng chung quota participation
(các tài khoản không tự cạnh tranh nhau trên cùng một mã).
Dừng khẩn cấp: tạo file data/BOT_STOP (hủy lệnh treo MỌI account rồi thoát).
Giết process giữa chừng vô hại — chạy lại là resume từ state đã lưu.
"""

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):  # console Windows cp1252 → utf-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from trading_bot.config import load_config, load_accounts, pick_accounts, EXEC_DIR
from trading_bot.brokers import make_broker, get_quote_source, get_dnse_client
from trading_bot.plan import (load_plan, filter_excluded_tickers, net_offsetting_orders,
                              cap_capit_orders, cap_lag_orders, approval_block_reason)
from trading_bot.netting_recon import (reconcile_netted_fills, get_net_fill_from_journal,
                                       write_recon_log)
from trading_bot.executor import Executor, run_session, _publish_bot_event
from trading_bot.vn_market import today_ict

_LOCK_HANDLES = []  # giữ sống file descriptor để lock tồn tại suốt vòng đời process

_WC_ROOT = os.path.dirname(os.path.abspath(__file__))
_TRADING_DAILY_THREAD = "1521470705563340910"  # cùng thread run_bot.sh dùng


def _alert_approval_block(label, plan_date, reason):
    """Alert khi approval gate chặn plan: stdout + bus event + Discord + Telegram.

    Mọi kênh fail-safe (không bao giờ raise) — alert hỏng không được làm hỏng phần
    còn lại của phiên (account khác trong cùng process vẫn phải chạy bình thường).
    """
    msg = (f"⛔ APPROVAL GATE — account {label}: plan {plan_date} bị TỪ CHỐI thực thi.\n"
           f"{reason}\n"
           f"Xử lý: user duyệt plan, ghi approved_by vào "
           f"data/trade_plans/plan_{label}_{plan_date}.json rồi chạy lại "
           f"bin/run_bot.sh --account {label} --auto-otp.")
    print(msg)
    _publish_bot_event("error", "APPROVAL_GATE_BLOCK", {
        "account": label, "plan_date": plan_date, "reason": reason,
    })
    notify_thread = os.path.join(_WC_ROOT, "mike", "bin", "notify_thread.sh")
    if os.path.isfile(notify_thread):
        try:
            subprocess.Popen([notify_thread, msg, _TRADING_DAILY_THREAD],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             close_fds=True)
        except Exception:
            pass
    try:
        with open(os.path.join(_WC_ROOT, "secrets", "telegram_config.json"),
                  encoding="utf-8") as f:
            tg = json.load(f)
        from telegram_recommend import send_telegram_text
        send_telegram_text(tg["bot_token"], tg["chat_id"], msg, parse_mode="")
    except Exception:
        pass


def _notify_trading_daily(msg):
    """Post msg → Trading Daily Discord + Telegram — fail-safe (không bao giờ raise)."""
    notify_thread = os.path.join(_WC_ROOT, "mike", "bin", "notify_thread.sh")
    if os.path.isfile(notify_thread):
        try:
            subprocess.Popen([notify_thread, msg, _TRADING_DAILY_THREAD],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             close_fds=True)
        except Exception:
            pass
    try:
        with open(os.path.join(_WC_ROOT, "secrets", "telegram_config.json"),
                  encoding="utf-8") as f:
            tg = json.load(f)
        from telegram_recommend import send_telegram_text
        send_telegram_text(tg["bot_token"], tg["chat_id"], msg, parse_mode="")
    except Exception:
        pass


def _alert_recon_failure(label, plan_date, failures):
    """Netting reconciliation post-fill phát hiện bất nhất → BÁO LOUD, KHÔNG tự gộp.

    Fail-loud theo coding_guidelines §5/§6: bus error + Discord + Telegram. Không raise
    (để account khác vẫn được audit + report), nhưng caller đặt exit ≠ 0 để giám sát bắt.
    """
    lines = "\n".join(f"  • {f['ticker']}: {f['reason']}" for f in failures)
    msg = (f"⚠️ NETTING RECON FAIL — account {label} ({plan_date}): đối soát post-fill lệnh "
           f"đã netted phát hiện {len(failures)} bất nhất, CẦN NGƯỜI KIỂM TRA (không tự gộp):\n"
           f"{lines}")
    print(msg)
    _publish_bot_event("error", "NETTING_RECON_FAIL", {
        "account": label, "plan_date": plan_date, "failures": failures,
    })
    _notify_trading_daily(msg)


def _reconcile_net_fills(executors, net_adjustments, pre_net_refs, plan_date):
    """Đối soát post-fill cho các lệnh đã netted — chạy SAU khi phiên đóng (fills đã chốt).

    Với mỗi account có netting (net_adjustments[label] non-empty): đọc GIÁ KHỚP THẬT của lệnh
    net (parent `NET-<ticker>-<SIDE>`) từ journal FILL của executor (avg_price broker qua
    `get_net_fill_from_journal`, KHÔNG phải giá đặt lệnh — §6), chạy `reconcile_netted_fills`:
      • records → ghi audit-trail JSONL (2 leg từng book @ cùng giá thật);
      • failures → BÁO LOUD (bus error + Discord + Telegram), KHÔNG tự gộp.
    Đây là AUDIT read-only + ghi log atomic — process chết trước khi chạy chỉ mất audit, không
    ảnh hưởng lệnh (side-effect đã xảy ra trong phiên). ref_price_of dùng ref trước-net để định
    giá chuyển nội bộ khi NET=0 / net order khớp 0cp (không có giá khớp thật để dùng).
    Trả list label có failures (caller đặt exit ≠ 0)."""
    failed = []
    for e in executors:
        adj = net_adjustments.get(e.label)
        if not adj:
            continue
        refs = pre_net_refs.get(e.label, {})
        get_net_fill = (lambda tk, side, _j=e.journal_file:
                        get_net_fill_from_journal(_j, tk, side))
        ref_price_of = lambda tk, _r=refs: _r.get(tk)
        records, failures = reconcile_netted_fills(adj, get_net_fill, ref_price_of)
        if records:
            path = write_recon_log(records, e.label, plan_date, EXEC_DIR)
            print(f"[{e.label}] ✅ netting reconcile: {len(records)} mã audited → {path}")
        if failures:
            failed.append(e.label)
            _alert_recon_failure(e.label, plan_date, failures)
    return failed


def _acquire_account_lock(label, plan_date):
    """Khoá độc quyền per (account, plan_date) — chống 2 tiến trình bot_execute.py cùng
    chạy 1 account/ngày (vd heartbeat autoheal đua với cron đúng giờ, 2026-07-02: cả 2
    process cùng khớp đủ toàn bộ plan độc lập → mua GẤP ĐÔI mọi lệnh, tài khoản âm tiền).
    Trả True nếu giữ được khoá (tiếp tục chạy); False nếu process khác đang giữ (bỏ qua
    account này, KHÔNG phải lỗi — tiến trình kia đang xử lý đúng rồi)."""
    os.makedirs(EXEC_DIR, exist_ok=True)
    path = os.path.join(EXEC_DIR, f"exec_{label}_{plan_date}.lock")
    f = open(path, "a")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False
    _LOCK_HANDLES.append(f)  # không đóng — giữ khoá tới khi process thoát
    return True


@contextlib.contextmanager
def _otp_flow_lock(cred_file):
    """Khoá độc quyền LIÊN TIẾN TRÌNH cho trọn chu trình OTP (send → đọc Gmail → tạo
    trading-token). Key theo file credentials: các account CHUNG login DNSE (SpaceX +
    ZaloPay dùng chung secrets/dnse_credentials.json → chung hộp Gmail OTP + chung token
    cache) phải chờ nhau; login khác nhau không chặn nhau. Sự cố 2026-07-08: 2 cron
    09:05 chạy cùng giây, cả 2 cùng send_email_otp rồi cùng đọc Gmail với cùng cutoff →
    cùng lấy 1 mã; bên submit sau dính INVALID_OTP ('have been used'). Blocking là chủ
    đích — bên chờ tối đa ~95s (fetch của bên giữ khoá timeout 90s), xong reload token
    cache là dùng chung token, khỏi cần OTP mới."""
    os.makedirs(EXEC_DIR, exist_ok=True)
    key = os.path.basename(cred_file) if cred_file else "default"
    with open(os.path.join(EXEC_DIR, f"otp_{key}.lock"), "a") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def parse_otp(items):
    """["main=123456","acc2=654321"] hoặc ["123456"] → (dict label→otp, otp chung)."""
    per, common = {}, None
    for it in items or []:
        if "=" in it:
            k, v = it.split("=", 1)
            per[k.strip()] = v.strip()
        else:
            common = it.strip()
    return per, common


def main():
    ap = argparse.ArgumentParser(description="Thực thi trading plan (đa tài khoản)")
    ap.add_argument("--account", action="append", default=None,
                    help="label account (lặp lại được); mặc định mọi account enabled")
    ap.add_argument("--date", default=None, help="plan date YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--mode", default=None, choices=["paper", "live"],
                    help="override mode cho MỌI account được chọn")
    ap.add_argument("--otp", action="append", default=None,
                    help="Smart OTP: 'label=123456' (lặp lại) hoặc '123456' chung")
    ap.add_argument("--once", action="store_true", help="chạy 1 vòng rồi thoát")
    ap.add_argument("--max-cycles", type=int, default=None)
    ap.add_argument("--force-phase", default=None,
                    choices=["MORNING", "AFTERNOON", "ATC"], help="test ngoài giờ")
    ap.add_argument("--probe", default=None, metavar="SYMBOL",
                    help="in payload quote thô của 1 mã rồi thoát")
    ap.add_argument("--broker", default="phs", choices=["phs", "dnse"],
                    help="broker cho --probe")
    ap.add_argument("--send-otp", default=None, metavar="LABEL",
                    help="gửi email OTP cho account DNSE (email_otp) rồi thoát")
    ap.add_argument("--auto-otp", action="store_true",
                    help="tự động gửi + đọc OTP qua Gmail API cho account DNSE live")
    args = ap.parse_args()

    if args.probe:
        b = get_quote_source(args.broker).connect()
        q = b.get_quote(args.probe)
        print(json.dumps(q.raw if q else None, indent=2, ensure_ascii=False, default=str))
        print("\nparsed:", q)
        return 0

    # Config (và plan bên dưới) được đọc MỘT LẦN ở đây rồi ĐÓNG BĂNG trong RAM cho cả
    # phiên bot — CHỦ ĐÍCH, không phải bug (ghi chú audit Winston_20260711_031745):
    # executor phải chạy deterministic theo đúng bản config/plan đã duyệt lúc khởi động;
    # hot-reload giữa phiên = lệnh đặt ra khác bản user đã duyệt. Hệ quả vận hành: sửa
    # trading_rules.json / plan_*.json trên đĩa GIỮA phiên KHÔNG có hiệu lực cho tới lần
    # restart tự nhiên kế tiếp (vd nghỉ trưa 11:30 → resume 13:00). Cần can thiệp ngay
    # trong phiên: dùng kill-switch data/BOT_STOP, đừng sửa file rồi chờ bot tự thấy.
    base = load_config()

    if args.send_otp:
        profiles = pick_accounts(load_accounts(base), [args.send_otp])
        c = get_dnse_client(profiles[0].get("credentials_file"))
        c.send_email_otp()
        print(f"✅ đã gửi OTP vào email (hạn 2 phút) — chạy lại với "
              f"--otp {args.send_otp}=<mã>")
        return 0

    if args.auto_otp:
        from gmail_otp_reader import fetch_dnse_otp
        auto_profiles = pick_accounts(load_accounts(base), args.account)
        for p in auto_profiles:
            cred_file = p.get("credentials_file")  # None → get_dnse_client uses default
            c = get_dnse_client(cred_file)
            if c.has_trading_token():
                print(f"[{p['label']}] trading-token còn hạn — bỏ qua OTP")
                continue
            with _otp_flow_lock(cred_file):
                # Trong lúc chờ khoá, process khác (account chung login) có thể đã tạo
                # token — reload cache từ đĩa rồi kiểm tra lại trước khi xin OTP mới.
                c._load_token_cache()
                if c.has_trading_token():
                    print(f"[{p['label']}] trading-token vừa được tiến trình khác tạo "
                          f"(chung login) — dùng chung, bỏ qua OTP")
                    continue
                print(f"[{p['label']}] gửi email OTP...")
                sent_at = time.time()
                c.send_email_otp()
                print(f"[{p['label']}] chờ OTP từ Gmail (tối đa 90s)...")
                # sent_after chặt (đúng khuyến nghị trong docstring fetch_dnse_otp):
                # chỉ nhận email đến SAU request của chính mình (buffer 5s cho lệch
                # đồng hồ), loại hẳn email OTP cũ/của request khác còn trong hộp thư.
                otp_code = fetch_dnse_otp(timeout=90, sent_after=sent_at - 5)
                c.create_trading_token(otp_code)
                print(f"[{p['label']}] ✅ trading-token OK (hạn 8h)")

    profiles = pick_accounts(load_accounts(base), args.account)
    otp_by_label, otp_common = parse_otp(args.otp)
    plan_date = args.date or today_ict().strftime("%Y-%m-%d")

    shared_fills = {}                            # sổ participation chung của fleet
    net_adjustments = {}                         # label -> adj của net_offsetting_orders
    pre_net_refs = {}                            # label -> {ticker: ref_price} TRƯỚC khi net

    executors = []
    approval_blocked = []                        # account bị approval gate từ chối
    for p in profiles:
        cfg = dict(p["cfg"])
        if args.mode:
            cfg["mode"] = args.mode
        # Plan cũng đóng băng theo phiên như config — xem ghi chú by-design tại
        # load_config() phía trên.
        plan = load_plan(plan_date, account=p["label"])
        if plan is None:
            print(f"[{p['label']}] không có plan cho {plan_date} — bỏ qua "
                  f"(chạy bot_prepare_plan.py trước)")
            continue
        before = len(plan.orders)
        plan, blocked = filter_excluded_tickers(plan, p.get("excluded_tickers"))
        if blocked:
            print(f"[{p['label']}] ⚠ BỎ {len(blocked)}/{before} lệnh cho mã "
                  f"excluded_tickers={sorted({o.ticker for o in blocked})}: "
                  f"{[o.ticker for o in blocked]} — không bao giờ tự động giao dịch "
                  f"các mã này (xem trading_bot_accounts.json).")
        # Netting lệnh NGƯỢC CHIỀU cùng mã trong cùng plan (vd SELL park + BUY LAG cùng VPB)
        # → 1 lệnh NET ra broker; phần bù trừ là chuyển nội bộ giữa book (0 phí/spread). ĐẶT
        # SAU filter_excluded, TRƯỚC các trần %ADV — CHỦ ĐÍCH: trần đo tác động THỊ TRƯỜNG, mà
        # chỉ phần NET mới thật chạm thị trường (xem docstring net_offsetting_orders). Lưới an
        # toàn tầng chuẩn hoá plan: V23Strategy tự net sẵn, case cần gộp đến từ plan LLM-authored
        # của DollarBill. ref_price trước-net + adj giữ lại để reconcile post-fill (netting_recon).
        pre_net_refs[p["label"]] = {o.ticker: o.ref_price for o in plan.orders}
        plan, net_adj = net_offsetting_orders(plan)
        net_adjustments[p["label"]] = net_adj
        for a in net_adj:
            print(f"[{p['label']}] ⟲ NET {a['ticker']} ({a['action']}): {a['reason']}")
        # Trần %ADV cho book CAPIT (X·ADV20·D, đọc từ data/golive_v23_status.json) — enforce
        # ở ĐÂY, không dựa vào plan generator nhớ áp, giống filter_excluded_tickers ngay trên.
        # Fail-closed khi thiếu cap/artifact cũ: chặn lệnh chứ không mua không giới hạn.
        plan, capped = cap_capit_orders(plan, p["label"])
        for a in capped:
            print(f"[{p['label']}] ⚠ CAPIT trần %ADV {a['action']} {a['ticker']}: "
                  f"{a['qty_before']:,} → {a['qty_after']:,} cp — {a['reason']}")
        # Trần %ADV cho book LAG (20% ADV/phiên = liquidity_volume_pct của LIQ_LAG trong
        # backtest pinned R3) — đóng lỗ hổng live-vs-backtest 2026-07-21. Cùng luồng, cùng
        # nguyên tắc fail-closed như CAPIT ngay trên; phần bị cắt tự mua tiếp phiên sau qua
        # diff target-vs-thật của plan hôm sau.
        plan, lag_capped = cap_lag_orders(plan, p["label"], account_mode=cfg["mode"])
        for a in lag_capped:
            print(f"[{p['label']}] ⚠ LAG trần %ADV {a['action']} {a['ticker']}: "
                  f"{a['qty_before']:,} → {a['qty_after']:,} cp — {a['reason']}")
        if not plan.orders:
            print(f"[{p['label']}] plan {plan_date} không có lệnh — bỏ qua")
            continue
        # Code-gate approval (2026-07-13): plan yêu cầu duyệt mà chưa duyệt → TỪ CHỐI
        # account này (account khác không liên quan vẫn chạy), exit code cuối ≠ 0 để
        # run_bot.sh/heartbeat/ops_health_check bắt được. Xét SAU filter_excluded_tickers
        # để "có lệnh" nghĩa là lệnh THẬT SỰ sắp được đặt.
        gate_reason = approval_block_reason(plan)
        if gate_reason:
            _alert_approval_block(p["label"], plan_date, gate_reason)
            approval_blocked.append(p["label"])
            continue
        if not _acquire_account_lock(p["label"], plan_date):
            print(f"[{p['label']}] ⚠ đã có tiến trình bot_execute.py khác đang xử lý "
                  f"{plan_date} (lock đang giữ) — bỏ qua, KHÔNG chạy trùng.")
            continue
        otp = otp_by_label.get(p["label"], otp_common)
        if cfg["mode"] == "live" and otp is None and not args.auto_otp:
            print(f"⚠ [{p['label']}] mode live chưa có --otp: nếu otp_token cache "
                  f"còn hạn vẫn chạy được, hết hạn lệnh sẽ bị từ chối.")
        broker = make_broker(cfg, otp=otp, profile=p).connect()
        if cfg["mode"] == "paper" and hasattr(broker, "set_fallback_refs"):
            broker.set_fallback_refs({o.ticker: o.ref_price for o in plan.orders})
        executors.append(Executor(plan, broker, cfg, shared=shared_fills))

    if not executors:
        if approval_blocked:
            print(f"⛔ {len(approval_blocked)} account bị approval gate chặn "
                  f"({', '.join(approval_blocked)}), không account nào chạy — exit 2.")
            return 2
        print(f"ℹ️ không có account nào có plan/lệnh cho {plan_date} — không phải lỗi, "
              f"chỉ là ngày không giao dịch. Thoát bình thường.")
        return 0

    run_session(executors, once=args.once, max_cycles=args.max_cycles,
                force_phase=args.force_phase)
    # Đối soát post-fill cho lệnh đã netted (fills đã chốt sau run_session). Audit + fail-loud.
    # Fail-loud = bus error NETTING_RECON_FAIL + Discord + Telegram (trong _alert_recon_failure);
    # ops_health_check bắt event error này. Không đổi exit-code (side-effect lệnh đã xảy ra;
    # đây là AUDIT post-hoc, không nên đổi trạng thái thoát của tầng đặt lệnh live).
    recon_failed = _reconcile_net_fills(executors, net_adjustments, pre_net_refs, plan_date)
    if recon_failed:
        print(f"⚠️ netting reconciliation FAIL: {len(recon_failed)} account "
              f"({', '.join(recon_failed)}) — đã BÁO LOUD (bus/Discord/Telegram), cần người kiểm tra.")
    if approval_blocked:
        print(f"⛔ lưu ý: {len(approval_blocked)} account đã bị approval gate chặn đầu "
              f"phiên ({', '.join(approval_blocked)}) — exit 2 để giám sát bắt được.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
