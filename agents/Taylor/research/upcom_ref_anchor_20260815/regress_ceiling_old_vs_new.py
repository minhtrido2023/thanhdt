#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PHẦN 3 — hồi quy: trần luật A CŨ (giá đóng) vs MỚI (giá tham chiếu) trên mã UPCOM.

Job Taylor_20260815_034407.

VÌ SAO KHÔNG HỒI QUY THẲNG TRÊN `q.ref`: đại lượng đó chỉ đọc được SỐNG, DNSE không có
endpoint lịch sử (đã kiểm, README §1.7). Nên hồi quy dùng **bình quân gia quyền dựng lại từ
bar 1 phút nguồn VCI** làm đại diện cho giá tham chiếu UPCOM — đại diện này KHÔNG phải giả
định: nó đã được đối soát trùng `q.ref` thật **6/7 mã TỚI TỪNG TICK** ngày 08-14→08-15
(README §1.4), với ca mạnh nhất là SCL tái lập sai lệch −3,36% với sai số 0,012pp.

ĐỌC KẾT QUẢ CHO ĐÚNG — trần lệch theo HAI CHIỀU và hai chiều hỏng KHÁC HẲN nhau:
  · trần CŨ CAO HƠN trần đúng ⇒ cổng chống-đuổi bị NỚI, mua đắt hơn mức user duyệt.
    Đây là chiều MẤT TIỀN THẬT.
  · trần CŨ THẤP HƠN trần đúng ⇒ cổng bị SIẾT, lệnh có thể không đặt được dù giá vẫn
    trong ngân sách. Đây là chiều MẤT CƠ HỘI (đúng cái rủi ro kẹt mà luật A sinh ra để cắt).

Chạy: python3 regress_ceiling_old_vs_new.py
"""
import csv
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
TAU = 0.03                      # ngân sách trần luật A user duyệt
UPCOM_TICK = 100.0              # bước giá UPCOM (VND)
RULE_A_TICKERS = {"DRI", "SCL", "TV1"}   # mã UPCOM ĐANG trong phạm vi luật A


def tick_round(p, tick=UPCOM_TICK):
    """Làm tròn XUỐNG về bước giá — đúng cách một lệnh mua đặt được trên bảng."""
    return float(int(p / tick) * tick)


def load_rows():
    with open(os.path.join(HERE, "vwap_daily.csv"), encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


def main():
    rows = load_rows()
    by_tk = {}
    for r in rows:
        try:
            vwap, close = float(r["vwap"]), float(r["close"])
        except (TypeError, ValueError):
            continue
        if vwap <= 0 or close <= 0:
            continue
        by_tk.setdefault(r["ticker"], []).append((r["d"], vwap, close))

    out = {"tau": TAU, "n_ticker": len(by_tk), "per_ticker": {}, "pooled": {}}
    pooled_dev, pooled_vnd_rel, pooled_over, pooled_under, pooled_n = [], [], 0, 0, 0

    for tk in sorted(by_tk):
        recs = sorted(by_tk[tk])
        devs, rel_vnd, over, under, breach = [], [], 0, 0, 0
        worst = None
        for d, vwap, close in recs:
            # Giá trong CSV theo đơn vị nghìn đồng (nguồn VCI) → quy về VND.
            ref_v, close_v = vwap * 1000.0, close * 1000.0
            c_new = tick_round(ref_v * (1 + TAU))
            c_old = tick_round(close_v * (1 + TAU))
            dev = c_old / c_new - 1.0          # >0: trần cũ CAO hơn (nới cổng)
            devs.append(dev)
            rel_vnd.append(c_old - c_new)
            if c_old > c_new:
                over += 1
            elif c_old < c_new:
                under += 1
            if abs(dev) > TAU:                 # sai số cơ sở giá > CẢ ngân sách trần
                breach += 1
            if worst is None or abs(dev) > abs(worst[1]):
                worst = (d, dev, c_old, c_new)
            pooled_dev.append(dev)
            pooled_vnd_rel.append(c_old - c_new)
        pooled_over += over
        pooled_under += under
        pooled_n += len(recs)
        adev = sorted(abs(x) for x in devs)
        n = len(adev)
        out["per_ticker"][tk] = {
            "trong_pham_vi_luat_A": tk in RULE_A_TICKERS,
            "n_phien": n,
            "median_abs_pct": round(adev[n // 2] * 100, 4),
            "p90_abs_pct": round(adev[int(n * 0.90)] * 100, 4),
            "max_abs_pct": round(adev[-1] * 100, 4),
            "n_tran_cu_CAO_hon": over, "pct_tran_cu_CAO_hon": round(over / n * 100, 1),
            "n_tran_cu_THAP_hon": under, "pct_tran_cu_THAP_hon": round(under / n * 100, 1),
            "n_sai_so_vuot_ca_tau": breach, "pct_sai_so_vuot_ca_tau": round(breach / n * 100, 2),
            "median_lech_VND": round(statistics_median_abs(rel_vnd), 1),
            "max_lech_VND": round(max(rel_vnd, key=abs), 1),
            "phien_te_nhat": {"ngay": worst[0], "lech_pct": round(worst[1] * 100, 4),
                              "tran_cu_VND": worst[2], "tran_dung_VND": worst[3]},
        }

    ap = sorted(abs(x) for x in pooled_dev)
    N = len(ap)
    out["pooled"] = {
        "n_phien_ma": N,
        "median_abs_pct": round(ap[N // 2] * 100, 4),
        "p90_abs_pct": round(ap[int(N * 0.90)] * 100, 4),
        "p95_abs_pct": round(ap[int(N * 0.95)] * 100, 4),
        "max_abs_pct": round(ap[-1] * 100, 4),
        "n_vuot_1pct": sum(1 for x in ap if x > 0.01),
        "pct_vuot_1pct": round(sum(1 for x in ap if x > 0.01) / N * 100, 2),
        "n_vuot_ca_tau_3pct": sum(1 for x in ap if x > TAU),
        "pct_vuot_ca_tau_3pct": round(sum(1 for x in ap if x > TAU) / N * 100, 2),
        "n_tran_cu_CAO_hon": pooled_over, "pct_tran_cu_CAO_hon": round(pooled_over / N * 100, 1),
        "n_tran_cu_THAP_hon": pooled_under, "pct_tran_cu_THAP_hon": round(pooled_under / N * 100, 1),
        "mean_lech_co_dau_pct": round(st.fmean(pooled_dev) * 100, 4),
    }

    # Chỉ nhóm mã ĐANG trong phạm vi luật A — con số đáng quan tâm nhất cho vận hành.
    scope = [abs(x) for tk in RULE_A_TICKERS if tk in by_tk
             for x in [c_old_dev for c_old_dev in _devs_of(by_tk[tk])]]
    if scope:
        s = sorted(scope)
        out["chi_ma_trong_pham_vi_luat_A"] = {
            "ma": sorted(RULE_A_TICKERS & set(by_tk)),
            "n_phien_ma": len(s),
            "median_abs_pct": round(s[len(s) // 2] * 100, 4),
            "p90_abs_pct": round(s[int(len(s) * 0.90)] * 100, 4),
            "max_abs_pct": round(s[-1] * 100, 4),
            "pct_vuot_1pct": round(sum(1 for x in s if x > 0.01) / len(s) * 100, 2),
            "pct_vuot_ca_tau_3pct": round(sum(1 for x in s if x > TAU) / len(s) * 100, 2),
        }

    print(json.dumps(out, ensure_ascii=False, indent=2))
    with open(os.path.join(HERE, "regression_ceiling.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return 0


def _devs_of(recs):
    for _d, vwap, close in recs:
        c_new = tick_round(vwap * 1000.0 * (1 + TAU))
        c_old = tick_round(close * 1000.0 * (1 + TAU))
        yield c_old / c_new - 1.0


def statistics_median_abs(xs):
    a = sorted(abs(x) for x in xs)
    return a[len(a) // 2]


if __name__ == "__main__":
    raise SystemExit(main())
