#!/usr/bin/env python3
"""
anomaly_escalate.py — escalate anomaly_scan tier-H trips vào hệ due-diligence
============================================================================
Job Taylor_20260717_113024. Đọc emit-json của anomaly_scan.py, phân vai theo
đúng thiết kế user duyệt 2026-07-17:

  PRIMARY (cảnh báo SỚM) = tín hiệu GIÁ/KHỐI LƯỢNG (tier_h: FLOOR2/IDIOCRASH/…).
    Khi trip → post Trading Daily NGAY + tự động KHỞI ĐỘNG due-diligence:
    dispatch Wendy (pháp lý) + Spyros (rủi ro) đánh giá. KHÔNG tự mua/bán —
    quyết định cuối vẫn cần user/Mike. Lý do dùng giá/volume làm primary: nó
    bắt DGC ĐÚNG ngày sự việc thật 2026-03-17 (khởi tố), trong khi trạng thái
    RES/diện-kiểm-soát mãi 2026-05-13 mới có — TRỄ 57 ngày lịch (~38 phiên).

  SECONDARY (theo dõi THỰC THI, KHÔNG phải cảnh báo sớm) = trạng thái sàn RES/NRM.
    Chỉ post Trading Daily với nhãn rõ "theo dõi thực thi thoát vị thế" — dùng để
    biết mã còn bán được không / thanh khoản còn không khi lập kế hoạch THOÁT.
    KHÔNG dùng làm cơ sở phát hiện sớm rủi ro pháp lý (nó là lagging).

Idempotency (coding_guidelines §5): mỗi (ticker|alert_date) chỉ escalate 1 lần —
ledger data/anomaly_escalations.json ghi ATOMIC SAU khi dispatch đã phát đi.
Nếu dispatch fail → KHÔNG mark → retry lượt sau (thà lặp review còn hơn bỏ sót).
ops_health_check gọi 08:20 + 12:45 → dedup này giữ mỗi trip chỉ báo/dispatch 1 lần.

Usage:
  anomaly_escalate.py --emit-json PATH            # thật (post + dispatch)
  anomaly_escalate.py --emit-json PATH --dry-run  # in ra sẽ làm gì, không side-effect
"""
import argparse, json, os, subprocess, datetime

ROOT = "/home/trido/thanhdt/WorkingClaude/mike"
WC = "/home/trido/thanhdt/WorkingClaude"
LEDGER = os.path.join(WC, "data", "anomaly_escalations.json")
TRADING_DAILY = "1521470705563340910"
NOTIFY = os.path.join(ROOT, "bin", "notify_thread.sh")
DISPATCH = os.path.join(ROOT, "bin", "dispatch.sh")


def _load_ledger():
    if os.path.exists(LEDGER):
        try:
            return json.load(open(LEDGER))
        except Exception:
            return {}
    return {}


def _save_ledger(led):
    tmp = LEDGER + ".tmp"
    json.dump(led, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, LEDGER)


def _notify(msg, dry):
    if dry:
        print(f"[dry-run] notify Trading Daily:\n{msg}\n")
        return True
    r = subprocess.run([NOTIFY, msg, TRADING_DAILY], capture_output=True, text=True)
    return r.returncode == 0


def _dispatch_bg(target, prompt, dry):
    """Phát dispatch nền cho agent DD. Trả về job_id (hoặc 'DRY'/None)."""
    if dry:
        print(f"[dry-run] dispatch {target} --bg:\n  {prompt[:160]}...\n")
        return "DRY"
    env = dict(os.environ, DISPATCH_FROM="Taylor")
    # --thread: script chạy từ cron (không có DISCORD_THREAD_ID) → không ghim thì thông báo
    # của job rơi về con trỏ global = topic user mở gần nhất. Anomaly luôn thuộc Trading Daily,
    # cùng nơi _notify() ở trên gửi (fix 2026-07-22).
    r = subprocess.run([DISPATCH, target, prompt, "--bg", "--thread", TRADING_DAILY,
                        "--timeout", "900"],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"  ⚠️ dispatch {target} FAIL rc={r.returncode}: {r.stderr.strip()[:200]}")
        return None
    out = (r.stdout + r.stderr)
    for tok in out.replace("(", " ").replace(")", " ").split():
        if tok.startswith("job="):
            return tok.split("=", 1)[1]
    return "issued"


def escalate(emit, dry=False):
    led = _load_ledger()
    asof = emit.get("asof", "?")
    new_h, new_status, changed = [], [], False

    # PRIMARY — tier-H giá/volume → khởi động due-diligence
    for a in emit.get("tier_h", []):
        key = f"{a['ticker']}|{asof}"
        if key in led:
            continue  # đã escalate trip này rồi
        tk, reasons = a["ticker"], a["reasons"]
        alert = (f"🚨 **ANOMALY tier-H (CẢNH BÁO SỚM giá/khối lượng)** — `{tk}` [{reasons}] "
                 f"phiên {asof}\n"
                 f"  ret {a['ret']:+.1f}% (VNI {a['vni_ret']:+.1f}%, idio {a['idio']:+.1f}%) "
                 f"vol {a['vol_x']:.1f}x giá {a['close']:,.0f}\n"
                 f"→ **Tự động khởi động due-diligence**: Wendy (pháp lý) + Spyros (rủi ro) đang đánh giá.\n"
                 f"  ⚠️ KHÔNG tự mua/bán — quyết định cuối chờ user/Mike duyệt. "
                 f"(Tín hiệu giá dẫn trước tin chính thức — DGC 2026-03-17 vs RES 2026-05-13, trễ 57 ngày.)")
        _notify(alert, dry)
        wprompt = (f"[DUE-DILIGENCE anomaly early-warning] Mã {tk} có tín hiệu giá/khối lượng bất "
                   f"thường [{reasons}] phiên {asof} (ret {a['ret']:+.1f}%, idio {a['idio']:+.1f}% — "
                   f"loại trừ phiên cả thị trường sập). Đây là CẢNH BÁO SỚM, tin chính thức có thể "
                   f"chưa ra. Nhiệm vụ pháp lý/compliance: rà soát có sự kiện pháp lý/khởi tố/hạn chế "
                   f"giao dịch/vi phạm công bố thông tin nào liên quan {tk} gần đây không; mức độ "
                   f"nghiêm trọng + đường giải quyết. KHÔNG quyết định mua/bán — chỉ đánh giá. "
                   f"Ghi finding lên bus khi xong.")
        sprompt = (f"[DUE-DILIGENCE anomaly early-warning] Mã {tk} tín hiệu giá/khối lượng bất thường "
                   f"[{reasons}] phiên {asof} (ret {a['ret']:+.1f}%, idio {a['idio']:+.1f}%). Nhiệm vụ "
                   f"rủi ro/audit: đánh giá rủi ro vị thế nếu đang giữ (thanh khoản còn không, khả năng "
                   f"thoát), khuyến nghị theo dõi/haircut/không hành động. KHÔNG quyết định mua/bán — "
                   f"chỉ đánh giá rủi ro. Ghi finding lên bus khi xong.")
        wjob = _dispatch_bg("Wendy", wprompt, dry)
        sjob = _dispatch_bg("Spyros", sprompt, dry)
        if wjob and sjob and not dry:
            led[key] = {"escalated_at": datetime.datetime.now().isoformat(timespec="seconds"),
                        "tier": "H", "reasons": reasons, "wendy_job": wjob, "spyros_job": sjob}
            changed = True
        new_h.append(tk)

    # SECONDARY — trạng thái sàn RES/NRM: theo dõi THỰC THI, không phải cảnh báo sớm
    for c in emit.get("status_changes", []):
        tk = c.get("ticker")
        now = c.get("now", {})
        key = f"STATUS|{tk}|{now.get('admin')}|{now.get('method')}|{now.get('sanction')}"
        if key in led:
            continue
        was = c.get("was")
        msg = (f"📋 **Trạng thái sàn đổi (THEO DÕI THỰC THI — KHÔNG phải cảnh báo sớm)** — `{tk}`\n"
               f"  {c.get('type')}: {json.dumps(was, ensure_ascii=False) if was else 'baseline'} "
               f"→ {json.dumps(now, ensure_ascii=False)}\n"
               f"  Dùng cho lập kế hoạch THOÁT vị thế (còn bán được không / thanh khoản). "
               f"Đây là tín hiệu XÁC NHẬN muộn, không phải phát hiện sớm rủi ro pháp lý.")
        _notify(msg, dry)
        if not dry:
            led[key] = {"escalated_at": datetime.datetime.now().isoformat(timespec="seconds"),
                        "type": "STATUS", "now": now}
            changed = True
        new_status.append(tk)

    if changed:
        _save_ledger(led)
    return new_h, new_status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-json", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(args.emit_json):
        print(f"anomaly_escalate: không thấy emit-json {args.emit_json} — bỏ qua (scan chưa chạy?)")
        return
    emit = json.load(open(args.emit_json))
    nh, ns = escalate(emit, dry=args.dry_run)
    if nh:
        print(f"ANOMALY_ESCALATE: {len(nh)} tier-H MỚI khởi động due-diligence: {nh}")
    if ns:
        print(f"ANOMALY_ESCALATE: {len(ns)} thay đổi trạng thái sàn (theo dõi thực thi): {ns}")
    if not nh and not ns:
        print("ANOMALY_ESCALATE: không có trip/đổi trạng thái MỚI (đã escalate trước đó hoặc sạch).")


if __name__ == "__main__":
    main()
