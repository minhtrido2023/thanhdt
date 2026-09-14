---
kind: derived-file
status: DERIVED — khối ngoại ròng (khớp lệnh + thoả thuận) khớp VNDirect finfo 2024-2025 median lệch 1,9 tỷ/phiên (384/494 phiên ≤5 tỷ); tổng năm khớp số báo chí; 3 nhóm trong nước UNVERIFIED
source: data/fiinprox_vnindex_investor_flow_daily_20260914.csv (raw: data/fiinprox_investor_flow_raw/vnindex_YYYY.txt)
group: feeds
writer: Mike (thủ công qua FiinXMCP execute_api → client.PriceStatistics().get_value_by_investor, KHÔNG script/cron)
upstream: FiinPro-X trial, hết hạn 2026-09-28
created: 2026-09-14
---

# `fiinprox_vnindex_investor_flow_daily` — giá trị ròng theo nhóm nhà đầu tư, VNINDEX, 2014-01-02→2026-09-14

3.165 phiên, tỷ VND (2014-2015: 1 số lẻ; 2016+ số nguyên). Cột:
`foreign_matched_net_bn` (ngoại khớp lệnh) · `foreign_deal_net_bn` (ngoại thoả thuận) ·
`proprietary_net_bn` (tự doanh CTCK) · `local_institutional_net_bn` · `local_individual_net_bn` · `flags`.
**Duy nhất** trong repo có tách khớp lệnh/thoả thuận và tự doanh/tổ chức/cá nhân.

## Độ phủ theo nhóm
| Giai đoạn | Có |
|---|---|
| 2014-01 → 2016-03 | chỉ ngoại khớp/thoả thuận + tự doanh (tổ chức trùng tự doanh ⇒ để trống; cá nhân null) |
| 2016-04 → 2026-08 | đủ 5 nhóm (2.550 phiên đủ cả 5) — trừ tự doanh trống 2022-03-03→2022-05-16 |
| 2026-09-03 → 2026-09-14 | `provisional` — tổ chức trùng tự doanh, cá nhân trống (provider chưa chốt) |

## Đối chiếu
- **vs VNDirect finfo `/v4/foreigns` code VNINDEX, 2024-01→2025-12 (494 phiên chung)**: |lệch| median
  1,9 tỷ, p95 26 tỷ; 6 phiên lệch lớn nhất đều là VNDirect trả **0** (thiếu dữ liệu phía VNDirect,
  vd 2025-04-04 FiinPro −2.762 tỷ). Tổng 494 phiên: VNDirect −206.009 vs FiinPro −210.817 tỷ.
- Tổng năm ngoại ròng (khớp+thoả thuận): 2018 +43.371 · 2021 −57.848 · 2022 +26.963 · 2024 −90.271 ·
  2025 −125.261 tỷ — cùng bậc số báo chí công bố cho HOSE.
- Lô thoả thuận lớn tách được: 2018-05-18 +28.571 (Vinhomes), 2018-10-02 +11.318, 2017-11-07 +5.547,
  2019-05-21 +5.789, 2020-06-15 +15.103, 2025-08-04 −9.846 tỷ.

## Bẫy
1. **5 nhóm KHÔNG cộng về 0** — |tổng| median 64 tỷ (2016) tăng lên 300 tỷ (2025). Nguồn nhóm khác
   nhau (cá nhân/tổ chức có thể chỉ khớp lệnh, tự doanh gồm cả thoả thuận). Đừng suy nhóm thứ 5
   bằng phần dư.
2. Tổ chức trong nước **có thể đã gồm tự doanh** (giai đoạn đầu trùng hệt) — không cộng 2 cột.
3. Ngày có lô thoả thuận khổng lồ, `local_individual_net_bn` âm tương ứng (2018-05-18 −30.767) =
   phía bán của lô thoả thuận bị gán cho cá nhân ⇒ phân tích dòng tiền cá nhân phải loại các ngày
   `|foreign_deal_net_bn|` lớn.
4. 2018-01-23/24 = 0/trống (gap provider). 2022-08-24 provider trả trùng, đã bỏ bản thứ hai.

↩ [Về nhóm feeds](index.md) · [Về index tổng](../index.md)
