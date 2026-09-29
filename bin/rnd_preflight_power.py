#!/usr/bin/env python3
"""Pre-flight khả thi cho MỘT hướng R&D — chạy TRƯỚC khi viết dòng code backtest đầu tiên.

Trả lời đúng một câu hỏi: "với effect size kỳ vọng của hướng này và số quan sát ĐỘC LẬP
có sẵn trong dữ liệu VN, có bao giờ đạt được DSR 0.95 (ngưỡng fleet) không?"
Nếu KHÔNG → đừng bắt đầu.

Vì sao tồn tại: chương trình ORB VN30F (2026-06→09) chạy 4 tháng R&D rồi mới phát hiện
DSR 0.95 cần 4.075 phiên = 16,2 năm > cả đời hợp đồng VN30F1M (9,13 năm). Phép tính đó
mất 30 giây và đáng lẽ phải là bước ĐẦU TIÊN. Xem
agents/Taylor/research/orb_threshold_recalc_20260925/ và orb_diagnosis_20260925/.

Công thức PSR/DSR giữ NGUYÊN quy ước của recalc.py (job Taylor_20260925_120926) và
analyse.py (job _111203) để số liệu so sánh được giữa các job.

Ví dụ:
  # ORB VN30F như đã đo — tái lập con số 4.075
  rnd_preflight_power.py --sharpe-ann 0.888 --obs-per-year 252 \\
      --n-available 1129 --n-trials 20 --n-rule per-day

  # Một selector cross-sectional, rebalance quý, kỳ vọng Sharpe 1.2
  rnd_preflight_power.py --sharpe-ann 1.2 --obs-per-year 252 \\
      --n-available 3000 --n-trials 30 --n-rule per-day

  # Một luật market-timing: N ĐỘC LẬP là số EPISODE regime, không phải số phiên
  rnd_preflight_power.py --sharpe-ann 1.5 --obs-per-year 4 \\
      --n-available 13 --n-trials 10 --n-rule per-episode
"""
import argparse, json, sys
import numpy as np
from scipy import stats as st

G = 0.5772156649

N_RULES = {
    "per-day": "1 quan sát = 1 phiên NAV. CHỈ hợp lệ khi mỗi phiên là một quyết định MỚI "
               "độc lập (vd long-short tái cân bằng hằng ngày). KHÔNG hợp lệ cho chiến lược "
               "giữ vị thế nhiều tuần — ở đó các phiên trong cùng vị thế là MỘT quan sát.",
    "per-episode": "1 quan sát = 1 episode regime / 1 lần vào-ra vị thế. Dùng cho MỌI luật "
                   "market-timing, macro gate, regime switch. VN từ 2014 chỉ có ~13 episode "
                   "DT5G — đây là lý do phần lớn nghiên cứu timing KHÔNG BAO GIỜ đủ power.",
    "per-event": "1 quan sát = 1 sự kiện (earnings release, ex-date, corp action, đáo hạn). "
                 "PHẢI chiết khấu cho chùm thời gian: các sự kiện rơi cùng 3 tuần công bố KQKD "
                 "tương quan chéo mạnh — chia cho ~số đợt công bố, không dùng số sự kiện thô.",
    "per-bet": "Grinold: breadth = số quyết định độc lập/năm = số mã × số lần tái cân bằng/năm. "
               "Dùng cho cross-sectional. Vẫn phải khai obs-per-year theo chuỗi return dùng để "
               "tính Sharpe (thường per-day).",
}


def psr(sr, sr0, n, sk, ku):
    den = np.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2)
    return st.norm.cdf((sr - sr0) * np.sqrt(n - 1) / den)


def sr0_of(n_trials, n):
    e = (1 - G) * st.norm.ppf(1 - 1 / n_trials) + G * st.norm.ppf(1 - 1 / (n_trials * np.e))
    return e / np.sqrt(n)


def solve_n(target, sr, n_trials, sk, ku, hi=10 ** 9):
    if psr(sr, sr0_of(n_trials, hi), hi, sk, ku) < target:
        return None
    lo = 10
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if psr(sr, sr0_of(n_trials, mid), mid, sk, ku) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def min_sr_for(target, n, n_trials, sk, ku):
    lo, hi = 0.0, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if psr(mid, sr0_of(n_trials, n), n, sk, ku) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sharpe-ann", type=float, help="Sharpe NĂM kỳ vọng của hướng này")
    g.add_argument("--mean-bps", type=float, help="lợi nhuận TB mỗi quan sát (bps); cần --sd-bps")
    ap.add_argument("--sd-bps", type=float, help="độ lệch chuẩn mỗi quan sát (bps)")
    ap.add_argument("--obs-per-year", type=float, required=True,
                    help="số quan sát/năm của chuỗi return dùng tính Sharpe (252 phiên, 12 tháng, 4 quý...)")
    ap.add_argument("--n-available", type=float, required=True,
                    help="số quan sát ĐỘC LẬP có sẵn trong dữ liệu VN hiện có")
    ap.add_argument("--n-trials", type=int, default=20,
                    help="số cấu hình/biến thể bạn SẼ thử (trung thực! mặc định 20)")
    ap.add_argument("--n-rule", required=True, choices=sorted(N_RULES),
                    help="cách bạn đếm N — bắt buộc khai, xem mô tả trong --help-rules")
    ap.add_argument("--max-history-years", type=float, default=None,
                    help="TRẦN CỨNG: tổng số năm dữ liệu có thể TỒN TẠI cho hướng này "
                         "(vd VN30F1M chỉ có từ 2017-08 = 9,13 năm; universe_pit từ 2014). "
                         "Nếu N cần > trần này thì phán NO-GO dù có chờ bao lâu.")
    ap.add_argument("--target-dsr", type=float, default=0.95)
    ap.add_argument("--skew", type=float, default=0.0)
    ap.add_argument("--kurt", type=float, default=3.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--help-rules", action="store_true", help="in bảng quy tắc đếm N rồi thoát")
    a = ap.parse_args(argv)

    if a.help_rules:
        for k, v in sorted(N_RULES.items()):
            print(f"\n{k}:\n  {v}")
        return 0
    if a.mean_bps is not None and a.sd_bps is None:
        ap.error("--mean-bps cần --sd-bps")

    if a.sharpe_ann is not None:
        sr = a.sharpe_ann / np.sqrt(a.obs_per_year)
    else:
        sr = a.mean_bps / a.sd_bps
    sk, ku, T, nt = a.skew, a.kurt, a.target_dsr, a.n_trials
    nav = a.n_available

    n_need = solve_n(T, sr, nt, sk, ku)
    dsr_now = float(psr(sr, sr0_of(nt, nav), nav, sk, ku))
    psr_now = float(psr(sr, 0.0, nav, sk, ku))
    z = st.norm.ppf(0.975) + st.norm.ppf(0.80)
    n_power = float("inf") if sr <= 0 else (z / sr) ** 2
    sr_min = min_sr_for(T, nav, nt, sk, ku)

    n_ceiling = a.max_history_years * a.obs_per_year if a.max_history_years else None
    feasible = n_need is not None and n_need <= nav
    reachable = n_need is not None and (n_ceiling is None or n_need <= n_ceiling)
    dsr_at_ceiling = (float(psr(sr, sr0_of(nt, n_ceiling), n_ceiling, sk, ku))
                      if n_ceiling else None)
    res = dict(
        sr_per_obs=float(sr), sharpe_ann=float(sr * np.sqrt(a.obs_per_year)),
        n_rule=a.n_rule, n_available=nav, n_trials=nt, target_dsr=T,
        dsr_now=dsr_now, psr_now=psr_now,
        n_for_target_dsr=n_need,
        years_for_target_dsr=(n_need / a.obs_per_year) if n_need else None,
        extra_years_needed=((n_need - nav) / a.obs_per_year) if n_need else None,
        max_history_years=a.max_history_years,
        n_ceiling=n_ceiling, dsr_at_max_history=dsr_at_ceiling,
        n_for_power80_2sided=(None if np.isinf(n_power) else float(n_power)),
        years_for_power80=(None if np.isinf(n_power) else float(n_power / a.obs_per_year)),
        min_sharpe_ann_detectable_now=float(sr_min * np.sqrt(a.obs_per_year)),
        effect_multiple_needed=float(sr_min / sr) if sr > 0 else None,
        verdict="GO" if feasible else ("MARGINAL" if reachable else "NO-GO"),
    )
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    print(f"QUY TẮC ĐẾM N: {a.n_rule}")
    print(f"  {N_RULES[a.n_rule]}")
    print(f"\nEffect giả định: Sharpe năm {res['sharpe_ann']:.3f} (SR/quan sát {sr:.5f}), "
          f"{a.obs_per_year:g} quan sát/năm")
    print(f"N độc lập có sẵn: {nav:,.0f}  ·  N_trials khai báo: {nt}")
    print(f"\nDSR hiện tại với N có sẵn : {dsr_now:.4f}   (PSR không deflate: {psr_now:.4f})")
    if n_need:
        print(f"N cần để DSR ≥ {T}       : {n_need:,} quan sát = {n_need/a.obs_per_year:.1f} năm")
        print(f"  còn thiếu               : {max(0, n_need-nav):,.0f} quan sát "
              f"= {max(0,(n_need-nav)/a.obs_per_year):.1f} năm")
    else:
        print(f"N cần để DSR ≥ {T}       : KHÔNG BAO GIỜ ĐẠT ở effect size này "
              f"(kể cả N → vô hạn)")
    if np.isinf(n_power):
        print("N cần cho power 80% (2 phía): VÔ HẠN (effect size = 0)")
    else:
        print(f"N cần cho power 80% (2 phía): {n_power:,.0f} = {n_power/a.obs_per_year:.1f} năm")
    if n_ceiling:
        print(f"\nTRẦN DỮ LIỆU ({a.max_history_years:g} năm = {n_ceiling:,.0f} quan sát): "
              f"DSR tối đa có thể đạt = {dsr_at_ceiling:.4f}"
              + ("  ← VẪN DƯỚI ngưỡng" if dsr_at_ceiling < T else "  (đạt được)"))
    print(f"\nVới N có sẵn, Sharpe năm TỐI THIỂU phát hiện được: {res['min_sharpe_ann_detectable_now']:.3f}"
          f"  (= ×{res['effect_multiple_needed']:.2f} effect giả định)")
    print(f"\n>>> PHÁN: {res['verdict']}")
    if res["verdict"] == "GO":
        print("    Dữ liệu hiện có ĐỦ để hướng này đạt ngưỡng fleet nếu edge đúng như giả định. Được phép bắt đầu.")
    elif res["verdict"] == "MARGINAL":
        print(f"    Phải CHỜ THÊM {max(0,(n_need-nav)/a.obs_per_year):.1f} năm dữ liệu. Chỉ bắt đầu nếu"
              " chấp nhận rõ ràng là chưa kết luận được trong khoảng đó — và ghi vào registry.")
    else:
        if n_ceiling and n_need and n_need > n_ceiling:
            print(f"    ĐỪNG BẮT ĐẦU. N cần ({n_need:,}) > TOÀN BỘ dữ liệu có thể tồn tại "
                  f"({n_ceiling:,.0f}). Chờ bao lâu cũng không đạt.")
        else:
            print("    ĐỪNG BẮT ĐẦU. Ở effect size này ngưỡng fleet không đạt được bằng cách tích luỹ dữ liệu.")
        print(f"    Đường ra duy nhất: tìm edge MẠNH HƠN ×{res['effect_multiple_needed']:.2f}, không phải N lớn hơn.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
