# -*- coding: utf-8 -*-
"""Sinh 2 file bootstrap snapshot .json.proposed (dieu 13 coding_guidelines).
CHI GHI duoi .json.proposed — KHONG dung file trade_plans that."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ledger import plan_orders, journal_fills, dates_for
from reconcile import broker_positions, ledger, ACC
from make_snapshot import OPENING, BOOK_MAP, BOOK_OVERRIDE, Lots

OUT = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
ASOF = "2026-08-03"
DAY0 = "2026-08-04"

PLAY_FOR_OPENING = {"EXCLUDED": "LEGACY_EXCLUDED", "LEGACY_ORPHAN": "LEGACY_ORPHAN",
                    "PARK": "NEUTRAL_park"}

NEEDS_CONFIRM = {
    ("ZaloPay", "VPB", "PARK"): {
        "reason": "Lo goc 7.500cp la vi the LEGACY co truoc khi bot quan ly (createdDate 2025-11-20), "
                  "KHONG co lich su FILL noi bo. Bot da trim 8 lan x 800cp (07-15..07-27) va MOI lenh trim "
                  "deu duoc plan gan book='custom30V_parking' (tu 07-22 co them play_type='PARK_TRIM') "
                  "— tuc plan da doi xu lo nay nhu mot slot PARK. NHUNG cac vi the legacy khac cua cung "
                  "account (MSH/TCM/TLG/VHC/VIB) lai duoc gan book='legacy_orphan' khi ban. Vay nhan cua "
                  "1.100cp con lai la PARK hay LEGACY_ORPHAN la QUYET DINH CUA NGUOI, khong suy duoc tu du lieu.",
        "alternatives": ["PARK", "LEGACY_ORPHAN"],
        "impact": "1.100cp x 25.500 = 28,05tr VND. Neu la PARK -> tinh vao park_mv_live cua L1; "
                  "neu LEGACY_ORPHAN -> khong tinh, park_mv_live giam 28,05tr.",
    },
    ("SpaceX", "LPB", "PARK"): {
        "reason": "Order BUY-LPB-01 ngay 2026-07-15 KHONG co truong `book` trong plan JSON (plan hom do dung "
                  "schema cu). Suy ra PARK tu van ban trong CHINH plan do, khong phai tu ten ma.",
        "alternatives": ["PARK"],
        "impact": "900cp x 53.000 = 47,70tr VND. Bang chung van ban rat manh, gan nhu chac chan PARK.",
    },
}

CONTRADICTS_PLAN_NOTE = {
    ("SpaceX", "VPB"): "plan_SpaceX 07-28..08-04 ghi book_note='LAG/PARK' va existing_lag_holds[VPB]; "
                       "lich su fill BAC BO: 100% 2.300cp den tu 2 lenh mua PARK 07-01/07-02 "
                       "(BUY-VPB-03 5.600cp book=custom30V_parking) tru lenh ban PARK 07-06 (3.300cp). "
                       "SpaceX CHUA TUNG co lenh mua VPB nao mang book=LAG.",
    ("SpaceX", "VND"): "plan_SpaceX_2026-07-31 existing_lag_holds ghi {ticker:VND, book:'LAG'}; lich su fill "
                       "BAC BO: 400cp mua 07-01 book=custom30V_parking, ban 100cp 07-06 book=custom30V_parking "
                       "-> 300cp con lai 100% PARK. SpaceX chua tung co lenh mua VND book=LAG.",
}


def build(label):
    lots = Lots()
    for sym, qty, cost, created, book, _ in OPENING[label]:
        lots.buy(sym, book, qty, cost, created,
                 f"vi the mo dau truoc khi bot quan ly. Nguon: broker snapshot dau tien cua account trong "
                 f"data/execution_logs/dnse_raw_2026-07-06.jsonl (loc account_no={ACC[label]}, dieu 12): "
                 f"openQuantity={qty}, costPrice={cost}, createdDate={created}. Khong co FILL trong journal noi bo.")
        lots.by[(sym, book)][-1]["play_type"] = PLAY_FOR_OPENING.get(book, "")
    for e in ledger(label):
        key = (label, e["date"], e["parent_id"])
        if key in BOOK_OVERRIDE:
            book, why = BOOK_OVERRIDE[key]
            why = "book RONG trong plan; suy tu van ban: " + why
        elif e["book"]:
            book = BOOK_MAP.get(e["book"], e["book"])
            why = f"plan_{label}_{e['date']}.json order id={e['parent_id']} book='{e['book']}'" + \
                  (f" play_type='{e['play_type']}'" if e["play_type"] else "")
        else:
            book, why = "UNRESOLVED", "khong co truong book va khong co bang chung van ban"
        ev = (f"{e['date']} {e['side'].upper()} {e['qty']}cp @VWAP {e['vwap']:,.0f} — journal "
              f"data/execution_logs/exec_{label}_{e['date']}_journal.csv parent_id={e['parent_id']}; {why}")
        if e["side"] == "buy":
            lots.buy(e["ticker"], book, e["qty"], e["vwap"], e["date"], ev)
            lots.by[(e["ticker"], book)][-1]["play_type"] = e["play_type"] or ""
        else:
            lots.sell(e["ticker"], book, e["qty"], e["date"], ev)
    return lots


for label, acc_no in ACC.items():
    pos, ts = broker_positions(acc_no)
    lots = build(label)
    recs, per_ticker = [], collections.Counter()
    for (ticker, book), pool in sorted(lots.by.items()):
        for lot in pool:
            if lot["qty"] <= 0:
                continue
            if ticker not in pos:          # broker la nguon chuan tac: khong con giu -> khong vao snapshot
                continue
            r = {"ticker": ticker, "qty": lot["qty"], "book": book,
                 "play_type": lot.get("play_type", ""),
                 "entry_date": lot["entry_date"],
                 "cost_price_vnd": round(lot["cost_price"], 2),
                 "source": "bootstrap",
                 "evidence": lot["evidence"]}
            nc = NEEDS_CONFIRM.get((label, ticker, book))
            if nc:
                r["needs_user_confirmation"] = True
                r["ambiguity"] = nc
            cp = CONTRADICTS_PLAN_NOTE.get((label, ticker))
            if cp:
                r["contradicts_plan_artifact"] = cp
                r["needs_user_confirmation"] = True
            recs.append(r)
            per_ticker[ticker] += lot["qty"]

    recon = []
    for t in sorted(set(pos) | set(per_ticker)):
        b = pos[t]["openQuantity"] if t in pos else 0
        l = per_ticker.get(t, 0)
        recon.append({"ticker": t, "broker_openQuantity": b, "bootstrap_qty": l, "diff": b - l,
                      "broker_cost_price": pos[t]["costPrice"] if t in pos else None,
                      "bootstrap_wavg_cost": round(sum(x["qty"] * x["cost_price_vnd"] for x in recs if x["ticker"] == t)
                                                   / l, 2) if l else None})
    for r in recon:
        if r["bootstrap_wavg_cost"] and abs(r["bootstrap_wavg_cost"] - (r["broker_cost_price"] or 0)) > 5:
            r["cost_gap_vnd_per_share"] = round(r["bootstrap_wavg_cost"] - r["broker_cost_price"], 2)
            r["cost_gap_note"] = ("Chenh = co tuc TIEN MAT: DNSE dieu chinh GIAM costPrice dung bang co tuc/cp, "
                                  "bootstrap ghi gia THUC TRA tu journal. KHONG anh huong so luong (qty doi soat "
                                  "khop tuyet doi -> khong co co tuc CO PHIEU / chia tach). Moi ty suat per-position "
                                  "phai qua mike/bin/dividend_adjusted_return.py — dieu 21 coding_guidelines.")
    ok = all(r["diff"] == 0 for r in recon)

    doc = {
        "_schema": "bootstrap_book_snapshot/v1 (DE XUAT — chua duyet)",
        "_status": "PROPOSED — CAN NGUOI (Mike/user) XAC NHAN TRUOC KHI DUNG. Khong duoc dung lam dau vao "
                   "sinh lenh trim khi chua duoc duyet.",
        "account_label": label,
        "account_no": acc_no,
        "day0_date": DAY0,
        "broker_source": {"file": "data/execution_logs/dnse_raw_2026-08-03.jsonl", "kind": "positions",
                          "ts": ts, "account_filter": f"account_no == {acc_no} (dieu 12 coding_guidelines)",
                          "note": "Phien 2026-08-03 la phien cuoi cung co du lieu broker; 2026-08-04 chua co fill "
                                  "nao khi lap snapshot -> trang thai nay = day-0 state cua 2026-08-04."},
        "method": {
            "1_ledger": "Duyet moi journal exec_{label}_{date}_journal.csv theo thu tu ngay; chi lay event=FILL.",
            "2_delta_trap": "qty tren dong FILL la TICH LUY THEO child_oid -> lay delta = qty(dong nay) - qty(dong "
                            "truoc CUNG child_oid). Cong don tho se dem trung (bay so 1, muc F2 thiet ke).",
            "3_book_tag": "parent_id cua journal == PlannedOrder.id trong plan_{label}_{date}.json -> lay truong "
                          "`book`/`play_type` cua CHINH lenh do. Day la bang chung TAI THOI DIEM MUA, khong phai "
                          "suy luan theo ten ma.",
            "4_fifo": "Lenh ban tieu thu lo FIFO TRONG CUNG book cua lenh ban.",
            "5_reconcile": "Sum(lo) moi ma phai bang openQuantity cua broker. Lech -> bao, KHONG tu sua lo cho khop "
                           "(dieu 5 coding_guidelines).",
        },
        "reconcile_ok": ok,
        "reconcile": recon,
        "positions": recs,
        "unresolved": [],
        "known_gaps": [],
    }

    if label == "ZaloPay":
        doc["unresolved"] = []
        doc["known_gaps"].append({
            "id": "journal_misses_ATC_fills",
            "severity": "MEDIUM — khong anh huong snapshot nay, nhung anh huong co che F sau nay",
            "case": "VHC 2026-07-10: plan ban 1.800cp; journal exec_ZaloPay_2026-07-10_journal.csv chi ghi 1.200cp "
                    "(FILL cuoi 14:29:59). Snapshot broker luc 15:00:11 cung file dnse_raw_2026-07-10.jsonl cho "
                    "openQuantity 0 / closedQuantity 1.800 -> 600cp con lai khop trong phien ATC SAU KHI vong poll "
                    "cua executor da ket thuc.",
            "implication": "Journal KHONG phai ban ghi day du cua fill. So lo dung thuan tu journal se SAI KHI lenh "
                           "khop o ATC. => Doi soat hang ngay voi openQuantity (muc F4) la BAT BUOC, khong phai tuy chon; "
                           "va nen bo sung mot lan doc broker sau ATC vao cuoi phien.",
            "affects_this_snapshot": "KHONG — VHC da ban het (broker openQuantity=0) nen khong co mat trong snapshot. "
                                     "Moi ma DANG GIU deu doi soat khop tuyet doi.",
        })
        doc["known_gaps"].append({
            "id": "DGC_excluded",
            "severity": "INFO",
            "case": "DGC 10.000cp — vi the legacy, nam trong excluded_tickers cua account (dieu 7 coding_guidelines). "
                    "Khong co FILL noi bo nao. Ghi book=EXCLUDED, KHONG vao so PARK, khong tinh vao sizing.",
        })

    path = os.path.join(OUT, f"bootstrap_book_snapshot_{label}_20260804.json.proposed")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    print(f"WROTE {path}  lots={len(recs)} reconcile_ok={ok} "
          f"needs_confirm={sum(1 for r in recs if r.get('needs_user_confirmation'))}")
