#!/usr/bin/env python3
"""So hai file của `snapshot_probe.py` (TRƯỚC vs SAU cửa sổ nhìn lùi) và in DELTA đầy đủ.

Không có ngưỡng, không có tóm tắt "ổn": in ra TỪNG mã đổi, phân loại theo hướng đổi, và đếm
riêng chữ ký RESTATE trên neo KHÔNG kiểm chứng được (`FIN_FALLBACK`/`ANCHOR_UNVERIFIED`) — đó là
con đường DUY NHẤT một số tương lai vào được câu trả lời, theo đúng định nghĩa của
`lookahead_cost_probe.py`. Chữ ký thô KHÔNG được trích dẫn (7/11 ca của nó vô tội).
"""
import argparse
import json

LOOKAHEAD_METHODS = ("FIN_FALLBACK", "ANCHOR_UNVERIFIED")


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def kind(before, after):
    b, a = before["value"], after["value"]
    if b is None and a is not None:
        return "CỨU (None -> số)"
    if b is not None and a is None:
        return "MẤT (số -> None)"
    if b is None and a is None:
        return "vẫn None, đổi nhãn"
    return "ĐỔI SỐ" if abs(b - a) > 1.0 else "cùng số, đổi nhãn"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    a = ap.parse_args()
    B, A = load(a.before), load(a.after)
    assert B["asof"] == A["asof"] and B["tickers"] == A["tickers"], \
        "hai snapshot khác rổ/asof — không so được"
    print(f"asof={A['asof']} · rổ {A['n_universe']} mã\n"
          f"  TRƯỚC: {B['wc']}\n  SAU  : {A['wc']}")
    for tag in ("pit", "live"):
        bb, aa = B["branches"][tag], A["branches"][tag]
        # "đổi" = đổi GIÁ TRỊ, hoặc đổi NHÃN, hoặc đổi NEO. So bằng giá trị đã chuẩn hoá chứ
        # không bằng chuỗi mô tả (§28 coding_guidelines) — và một dòng y hệt nhau ở cả ba mặt
        # KHÔNG được lọt vào danh sách, nếu không "10 mã đổi" đọc thành sai sự thật.
        def _same(b, x):
            v = (b["value"] is None and x["value"] is None) or (
                b["value"] is not None and x["value"] is not None
                and abs(b["value"] - x["value"]) <= 1.0)
            return (v and b["method"] == x["method"] and b["anchor_date"] == x["anchor_date"]
                    and b["anchor_source"] == x["anchor_source"])

        rows = [(tk, bb[tk], aa[tk]) for tk in A["tickers"] if not _same(bb[tk], aa[tk])]
        n_none_b = sum(1 for tk in A["tickers"] if bb[tk]["value"] is None)
        n_none_a = sum(1 for tk in A["tickers"] if aa[tk]["value"] is None)
        la_b = sorted(tk for tk in A["tickers"]
                      if bb[tk]["restate_future_ais"] and bb[tk]["method"] in LOOKAHEAD_METHODS)
        la_a = sorted(tk for tk in A["tickers"]
                      if aa[tk]["restate_future_ais"] and aa[tk]["method"] in LOOKAHEAD_METHODS)
        print(f"\n=== nhánh {tag.upper()} ===")
        print(f"  từ chối (value=None): {n_none_b} -> {n_none_a}  (phủ {n_none_b - n_none_a:+d} mã)")
        print(f"  LOOK-AHEAD (RESTATE trên neo {LOOKAHEAD_METHODS}): "
              f"{len(la_b)} {la_b} -> {len(la_a)} {la_a}")
        print(f"  thêm: {sorted(set(la_a) - set(la_b))} · bớt: {sorted(set(la_b) - set(la_a))}")
        print(f"  số mã đổi (số HOẶC nhãn): {len(rows)}")
        for tk, b, x in rows:
            print(f"   {tk:5s} [{kind(b, x):18s}] {b['method']:<18s} {b['value']} "
                  f"(neo {b['anchor_date']}/{b['anchor_source']})")
            print(f"          {'':18s}  -> {x['method']:<18s} {x['value']} "
                  f"(neo {x['anchor_date']}/{x['anchor_source']})")


if __name__ == "__main__":
    main()
