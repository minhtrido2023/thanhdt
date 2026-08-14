# -*- coding: utf-8 -*-
"""probe_p1_anchor_live_20260812.py — DRY-RUN đường gọi LIVE của P1 anchor (job Taylor_20260812_112700).

Điều kiện tiên quyết quant-skeptic đặt ra trước khi P1 được cân nhắc bật paper:
"exercise anchor_prices_for() against the live API in dry-run and confirm the [FAILSAFE]
branches print". Script này làm đúng thế — KHÔNG ghi file, KHÔNG sửa state, KHÔNG bật cờ ở
bất kỳ state thật nào (state dùng ở đây là bản dựng TRONG BỘ NHỚ).

Chạy: source wc_env.sh && $DNA_PYEXE mike/agents/Taylor/research/probe_p1_anchor_live_20260812.py
"""
import copy
import importlib.util
import os
import sys

WC_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "..", "..", "..", ".."))
sys.path.insert(0, WC_ROOT)

from trading_bot.brokers import DNSEBroker                      # noqa: E402
from trading_bot.discretionary_accumulation import resolve_price_band  # noqa: E402
from trading_bot.vn_market import now_ict, session_phase        # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "_disc_inject_probe", os.path.join(WC_ROOT, "mike", "bin",
                                       "discretionary_accumulation_inject.py"))
inj = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inj)

STATE = {
    "ticker": "TV1", "account": "SpaceX", "status": "active", "lot_size": 100,
    "target_qty": 2000, "baseline_qty_before_program": 0,
    "price_band": {"resting_limit": 19900, "no_chase_ceiling": 20000,
                   "max_no_chase_ceiling": 22000},
    "adv_ref_vnd": 701_000_000, "per_session_cap_pct_adv": 0.1,
    "opportunistic": {"k": 2.0, "m": 2.0},
    "dynamic_ceiling": {"enabled": True, "tau": 0.03, "sessions": 5},
}


def st(**over):
    s = copy.deepcopy(STATE)
    for k, v in over.items():
        if k == "price_band":
            s["price_band"].update(v)
        else:
            s[k] = v
    return s


def main():
    print(f"[probe] now_ict={now_ict():%F %H:%M} phase={session_phase()[0]}  "
          f"(bar hôm nay 'hoàn tất'? {inj.bar_is_completed_session(int(now_ict().replace(hour=9, minute=0).replace(tzinfo=inj._ICT_TZ).timestamp()))})")
    b = DNSEBroker(quote_only=True, label="probe-p1-anchor")
    b.connect()

    latest = {}
    for tk in ("TV1", "DGC"):
        print(f"\n===== {tk} — đường gọi LIVE thật =====")
        q = b.get_quote(tk)
        latest[tk] = float(getattr(q, "last", 0) or 0)
        print(f"  quote live: last={latest[tk]:,.0f} day_volume={getattr(q,'day_volume',None)}")
        anchors = inj.anchor_prices_for(b, st(ticker=tk), tk)
        print(f"  anchors (VND, cũ→mới) = {anchors}")
        if anchors:
            c, r, info = resolve_price_band(st(ticker=tk), anchors, latest[tk])
            print(f"  band: ceiling={c:,.0f} resting={r:,.0f} mode={info['mode']} "
                  f"anchor={info.get('anchor_vnd')} capped={info.get('capped_by_max')}")

    print("\n===== FAIL-SAFE trên đường LIVE (phải in [FAILSAFE], không được crash) =====")
    print("-- (1) mã không tồn tại → lỗi API/ payload rỗng")
    print(f"   → {inj.anchor_prices_for(b, st(ticker='ZZZZ'), 'ZZZZ')}")
    print("-- (2) sessions=99 (đòi 99 phiên hoàn tất, feed không đủ)")
    print(f"   → {inj.anchor_prices_for(b, st(dynamic_ceiling={'enabled': True, 'tau': 0.03, 'sessions': 99}), 'TV1')}")
    print("-- (3) broker không có client DNSE")
    print(f"   → {inj.anchor_prices_for(object(), st(), 'TV1')}")
    print("-- (4) cờ TẮT (mặc định production) → None, KHÔNG gọi API")
    print(f"   → {inj.anchor_prices_for(b, st(dynamic_ceiling=None), 'TV1')}")

    print("\n===== Guard sanity đơn vị/lệch giá, dữ liệu LIVE THẬT =====")
    a_dgc = inj.anchor_prices_for(b, st(ticker="DGC"), "DGC")
    if a_dgc and latest.get("TV1"):
        c, r, info = resolve_price_band(st(ticker="TV1"), a_dgc, latest["TV1"])
        print(f"  anchor DGC (~{a_dgc[-1]:,.0f}) áp lên giá live TV1 ({latest['TV1']:,.0f}) "
              f"⇒ mode={info['mode']} ceiling={c:,.0f} reason={info.get('reason')}")
    a_thousand = [v / 1000.0 for v in (inj.anchor_prices_for(b, st(), "TV1") or [])]
    if a_thousand:
        c, r, info = resolve_price_band(st(), a_thousand, latest["TV1"])
        print(f"  anchor sai ĐƠN VỊ (chia 1000) ⇒ mode={info['mode']} ceiling={c:,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
