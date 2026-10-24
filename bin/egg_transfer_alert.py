#!/usr/bin/env python3
"""egg_transfer_alert.py — nhắc user CHUYỂN Trứng vàng → cash trước phiên (chỉ cảnh báo, KHÔNG đặt lệnh).

Chính sách user chốt 2026-10-24: Trứng vàng (`egg.totalValue`) = TIỀN. DollarBill lập plan mua bình
thường (ngân sách = cash + Trứng vàng, không shrink/hoãn vì "thiếu tiền" khi Trứng vàng đủ bù). Phần
còn lại của chính sách nằm Ở ĐÂY: sáng ngày thực thi, nếu sức mua THẬT của broker chưa đủ cho Σ lệnh
MUA (tức user chưa chuyển Trứng vàng sang cash) → cảnh báo mỗi 15 phút, bắt đầu 08:30 ICT, tới khi đủ.

Đo bằng ĐÚNG `trading_bot.plan_funding_gate.check_plan_funding` mà bot dùng lúc 09:05 (cùng gói vay,
cùng phần còn lại theo exec state, cùng tín dụng JIT) → cảnh báo xuất hiện ⇔ gate sẽ BLOCK. Số tiền
cần chuyển = Σ mua còn lại − hũ chung − JIT hiệu lực (cận AN TOÀN, đúng tuyệt đối khi 1 nhóm gói vay;
KHÔNG dùng `fallback_bound` vì nó nhân (cash+bán)×3 ⇒ đòi thiếu).

⚠️ Xấp xỉ có chủ đích: chạy trên plan SAU `filter_excluded_tickers` + gỡ cờ đòn bẩy (bot cũng gỡ chúng
khi CAPIT lever tắt) nhưng KHÔNG tái dựng toàn bộ cascade của `bot_execute.main()` (trần %ADV, netting,
holds, rating…). Các bước đó chỉ GIẢM Σ mua ⇒ cảnh báo nghiêng về phía báo THỪA (user có thể chuyển nhiều
hơn cần), không báo muộn hơn gate. Bất biến: gate BLOCK ⇒ KHÔNG bao giờ ra "FUNDED" (arch-review 2026-10-24).

Read-only: chỉ gọi balances/ppse. Không ghi gì ngoài file state nhỏ (để báo "✅ đã đủ" đúng 1 lần).
Fail-loud (1 lần/ngày): lỗi bất kỳ → báo "công cụ nhắc lỗi, tự kiểm Trứng vàng" ĐÚNG 1 LẦN rồi exit 1 —
một cảnh báo chết im lặng còn tệ hơn báo động giả.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
sys.path.insert(0, WC_ROOT)

ROUND_UP_VND = 100_000          # làm tròn LÊN số cần chuyển tới 0,1 triệu — thiếu 1đ cũng vẫn BLOCK
TRADING_DAILY = "trading_daily"


def transfer_needed(fund: dict) -> float:
    """Số tiền mặt cần thêm để gate hết BLOCK; luôn ≥ ROUND_UP_VND khi gate BLOCK (không bao giờ 0).

    Cận AN TOÀN cho CẢ hai nhánh BLOCK: Σ mua − hũ − JIT (đúng tuyệt đối khi 1 nhóm gói vay; nhiều nhóm
    đòn bẩy thì THỪA nhẹ; không đo được gì ⇒ hũ=0 ⇒ X = Σ mua). Cố ý KHÔNG dùng `fallback_bound`: gate nhân
    (cash+Σbán)×3 nên đòn Σbán làm bound lớn ⇒ đòi THIẾU (arch-review vòng 2, ca cash 0 + lệnh bán).
    """
    if fund.get("action") != "BLOCK":
        return 0.0
    need = float(fund.get("need_vnd") or 0.0)
    gap = need - float(fund.get("shared_pot_vnd") or 0.0) - float(fund.get("jit_credit_effective_vnd") or 0.0)
    return max(float(ROUND_UP_VND), gap)


def _ceil_round(x: float) -> float:
    return -(-x // ROUND_UP_VND) * ROUND_UP_VND


def decide(fund: dict, egg_vnd: float) -> dict:
    """Thuần hàm. status: FUNDED | NOT_APPLICABLE | UNVERIFIED | SHORT_EGG_COVERS | SHORT_EGG_INSUFFICIENT."""
    act = fund.get("action")
    if act in ("SKIPPED",):
        return {"status": "NOT_APPLICABLE", "short": 0.0}
    if act == "OK":
        return {"status": "FUNDED", "short": 0.0}
    if act == "UNVERIFIED":
        return {"status": "UNVERIFIED", "short": 0.0}
    if act != "BLOCK":                                   # action lạ ⇒ không đoán là đủ
        return {"status": "UNVERIFIED", "short": 0.0}
    short = _ceil_round(transfer_needed(fund))
    if egg_vnd is None:
        return {"status": "SHORT_EGG_UNKNOWN", "short": short}
    if egg_vnd >= short:
        return {"status": "SHORT_EGG_COVERS", "short": short}
    return {"status": "SHORT_EGG_INSUFFICIENT", "short": short}


def render(account: str, plan_date: str, now_hm: str, d: dict, fund: dict, egg_vnd, n_sell: int = 0,
           approved: bool = True) -> str:
    tr = lambda v: f"{v / 1e6:,.1f}tr"   # noqa: E731
    head = f"🥚 **{account} — {now_hm} ICT · plan {plan_date}**"
    pre = "" if approved else "⚠️ Plan CHƯA duyệt — cần duyệt VÀ chuyển tiền. "
    blk = ("Chưa chuyển thì gate 09:05 BLOCK CẢ plan"
           + (f", kể cả {n_sell} lệnh BÁN" if n_sell else "") + " (bot chạy lại 13:00 hoặc chạy tay run_bot.sh).")
    if d["status"] == "SHORT_EGG_COVERS":
        return (f"{head}\n{pre}**CHUYỂN Trứng vàng → cash ≥ {tr(d['short'])} trước 09:05** để bot đặt được lệnh MUA "
                f"(Σ mua còn lại {tr(fund['need_vnd'])} > sức mua thật; Trứng vàng đang có {tr(egg_vnd)}). "
                f"{blk} Nhắc lại mỗi 15 phút tới khi đủ.")
    if d["status"] == "SHORT_EGG_UNKNOWN":
        return (f"{head}\n{pre}**CHUYỂN Trứng vàng → cash ≥ {tr(d['short'])} trước 09:05** (số ước lượng an toàn; "
                f"KHÔNG đọc được số dư Trứng vàng để đối chiếu). Σ mua còn lại {tr(fund['need_vnd'])}. {blk}")
    return (f"{head}\n{pre}🔴 **THIẾU CẢ KHI CHUYỂN HẾT Trứng vàng** — cần ≥ {tr(d['short'])} cash nhưng Trứng vàng chỉ "
            f"{tr(egg_vnd)} (thiếu thêm {tr(d['short'] - egg_vnd)}). Σ mua còn lại {tr(fund['need_vnd'])}. "
            f"Cần nạp thêm tiền hoặc giảm plan. {blk}")


def _state_path(account: str, plan_date: str) -> str:
    return os.path.join(WC_ROOT, "data", "execution_logs", f"egg_alert_state_{account}_{plan_date}.json")


def _read_state(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_state(path: str, obj: dict) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def _notify(msg: str) -> bool:
    """True nếu ÍT NHẤT một kênh trả rc==0 (stdout/stderr vẫn bỏ, nhưng rc không được nuốt)."""
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ok = False
    for script, extra in (("notify.sh", []), ("notify_thread.sh", [TRADING_DAILY])):
        p = os.path.join(root, "bin", script)
        if os.path.isfile(p):
            try:
                r = subprocess.run([p, msg, *extra], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                ok = ok or r.returncode == 0
            except Exception as ex:                                  # noqa: BLE001 — fail-safe
                print(f"[egg_transfer_alert] notify {script} lỗi: {ex}", file=sys.stderr)
    return ok


def run(account: str, plan_date: str | None, dry_run: bool) -> int:
    from trading_bot.vn_market import now_ict, is_holiday
    from trading_bot.config import load_config, load_accounts
    from trading_bot.plan import load_plan, filter_excluded_tickers, approval_block_reason
    from trading_bot.brokers import make_broker
    from trading_bot.plan_funding_gate import check_plan_funding

    now = now_ict()
    plan_date = plan_date or now.strftime("%Y-%m-%d")
    if plan_date == now.strftime("%Y-%m-%d") and (now.weekday() >= 5 or is_holiday(now.date())):
        print(f"[{account}] {plan_date} không phải ngày giao dịch — thoát.")
        return 0
    plan = load_plan(plan_date, account=account)
    if plan is None or not plan.orders:
        print(f"[{account}] không có plan/lệnh cho {plan_date} — thoát.")
        return 0
    cfg = load_config()
    prof = next((p for p in load_accounts(cfg) if p["label"] == account), None)
    if prof is None or prof["cfg"].get("mode") != "live":
        print(f"[{account}] không phải account live — thoát.")
        return 0
    plan, _ = filter_excluded_tickers(plan, prof.get("excluded_tickers"))
    approved = not approval_block_reason(plan)        # chưa duyệt VẪN nhắc (duyệt muộn 09:01 từng xảy ra)
    n_sell = sum(1 for o in plan.orders if str(o.side or "").lower() == "sell")
    for o in plan.orders:                              # bot gỡ cờ đòn bẩy plan tự viết khi CAPIT lever tắt/không duyệt
        for attr in ("loan_package_id", "lever_f"):
            if hasattr(o, attr):
                setattr(o, attr, None)

    broker = make_broker(prof["cfg"], otp=None, profile=prof).connect()
    exec_dir = os.path.join(WC_ROOT, "data", "execution_logs")
    try:
        with open(os.path.join(exec_dir, f"exec_{account}_{plan_date}_state.json"), encoding="utf-8") as f:
            execution_state = json.load(f)
    except Exception:
        execution_state = None
    fund = check_plan_funding(plan, broker, prof["cfg"]["mode"], execution_state=execution_state)
    bal = broker.client.balances(broker.account_id)
    egg_raw = (bal.get("egg") or {}).get("totalValue")
    egg = None if egg_raw is None else float(egg_raw)
    d = decide(fund, egg)
    hm = now.strftime("%H:%M")
    st_path = _state_path(account, plan_date)
    st = _read_state(st_path)
    # Bot ĐÃ chạy qua gate hôm nay (có exec state) nhưng không đối chiếu được phần còn lại (cascade đổi id lệnh)
    # ⇒ đo lại Σ mua gốc so với pp0Buy đã tiêu = số sai. Không spam số sai: tối đa 1 thông báo.
    if (d["status"].startswith("SHORT") and execution_state is not None and not fund.get("state_used")):
        print(f"[{account}] exec state tồn tại nhưng không đối chiếu được ({fund.get('state_note')}) — không nhắc số tiền.")
        if not dry_run and not st.get("state_mismatch_notified"):
            if _notify(f"ℹ️ **{account} — {hm} ICT**: bot đã chạy plan {plan_date} nhưng nhắc-chuyển-Trứng-vàng không đối chiếu "
                       f"được phần lệnh còn lại ({fund.get('state_note')}) — tự kiểm sức mua/lệnh MUA còn treo; sẽ KHÔNG nhắc số tiền nữa hôm nay (trừ khi plan được thay mới thì cũng không đối chiếu được — tự kiểm)."):
                _write_state(st_path, dict(st, state_mismatch_notified=True))
        return 0
    print(f"[{account}] {plan_date} {hm} status={d['status']} short={d['short']:,.0f} egg={egg} "
          f"need={fund.get('need_vnd')} action={fund.get('action')} approved={approved}")

    if d["status"].startswith("SHORT"):
        msg = render(account, plan_date, hm, d, fund, egg, n_sell=n_sell, approved=approved)
        print(msg)
        if not dry_run and _notify(msg):
            _write_state(st_path, dict(st, alerted=True, cleared=False, last_short=d["short"], last_at=hm))
    elif d["status"] == "FUNDED" and st.get("alerted") and not st.get("cleared"):
        late = (" Nếu bot đã BLOCK lúc 09:05 thì CHƯA có lệnh MUA nào khớp — bot chạy lại 13:00 hoặc chạy tay run_bot.sh."
                if (now.hour, now.minute) >= (9, 5) else "")
        msg = f"✅ **{account} — {hm} ICT**: sức mua đã đủ cho plan {plan_date} — hết nhắc chuyển Trứng vàng.{late}"
        print(msg)
        if not dry_run and _notify(msg):
            _write_state(st_path, dict(st, cleared=True, cleared_at=hm))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-date", help="YYYY-MM-DD (mặc định: hôm nay ICT) — dùng để thử với plan ngày mai")
    ap.add_argument("--dry-run", action="store_true", help="in kết quả, không gửi notify, không ghi state")
    a = ap.parse_args()
    try:
        return run(a.account, a.plan_date, a.dry_run)
    except Exception as ex:                                          # noqa: BLE001 — fail-loud 1 lần/ngày
        import traceback
        print(f"[egg_transfer_alert] LỖI: {ex}\n{traceback.format_exc()}", file=sys.stderr)
        if not a.dry_run:
            try:
                from trading_bot.vn_market import now_ict
                day = now_ict().strftime("%Y-%m-%d")
                sp = _state_path(a.account, a.plan_date or day)
                st = _read_state(sp)
                if not st.get("errored"):
                    if _notify(f"⚠️ **{a.account}**: công cụ nhắc chuyển Trứng vàng LỖI ({type(ex).__name__}: {str(ex)[:150]}) — "
                               f"hãy tự kiểm tra Trứng vàng đã chuyển sang cash chưa trước 09:05."):
                        _write_state(sp, dict(st, errored=True))
            except Exception:                                        # noqa: BLE001
                pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
