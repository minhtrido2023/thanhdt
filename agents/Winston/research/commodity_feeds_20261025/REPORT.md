# REPORT — Feed giá hàng hoá còn thiếu (job Winston_20261025_062823, 2026-10-25)

## Kết luận
**Không dựng được chuỗi lịch sử đủ dùng cho bất kỳ mục ưu tiên nào bằng nguồn MIỄN PHÍ truy cập được từ môi trường này.**
Chỉ thu được 4 điểm rời của APT vonfram (`apt_tungsten_snapshots.csv`) — KHÔNG phải chuỗi, không dùng backtest được.
Không bịa, không nội suy. Nút thắt thật là **dữ liệu trả phí/đăng nhập**, không phải thiếu code.

## Môi trường thăm dò
`curl` từ máy này bị chặn/anti-bot: SunSirs (JS challenge), Stooq (JS challenge), Trading Economics 403, Investing.com 403,
IMF 403, FRED không kết nối (000), ChemAnalyst 403. Yahoo `^BDI` 404. WebFetch đọc được SMM news, SunSirs news, stock-marketdata, Mendeley (trang mô tả).
Chưa thử trình duyệt có JS (có thể mở được SunSirs/Stooq) — xem Đề xuất.

## Từng chuỗi
| # | Chuỗi | Kết quả | Độ phủ | Ghi chú |
|---|---|---|---|---|
| 1 | Vonfram APT 88,5% | Chỉ 4 điểm rời trong tin (CSV) | 2025-07-16, 11-28, 12-31, 2026-02-09 | SMM trang giá `metal.com/tungsten/201308090018` có bảng ngày nhưng **khoá đăng nhập** (cột giá ẩn). SunSirs có APT nhưng chỉ đọc được bài tin; trang giá bị JS challenge. Fastmarkets/Argus trả phí ⇒ chỉ ghi tên. |
| 2 | BDTI/BCTI ngày | **Không có** nguồn free | 0 | Baltic Exchange trả phí; Barchart (BDTI.BI, từ 2000) tải về cần membership. Chỉ có điểm rời trong TradeWinds (record thấp 429; 904 năm 2022) — không dùng. |
| 3 | BDI ngày dài hạn | Chưa lấy được CSV dài | 0 mới | `stock-marketdata.com/bdi.html` chỉ ~30 phiên HTML (9/14→10/23/2026) — trùng `bdi_daily_real.csv`, vô ích. Barchart/ABCBourse: lịch sử dài ở bản trả phí. **Ứng viên free:** Mendeley DOI 10.17632/t76ckh2ygg.1 (CC BY 4.0, BDI + Cape/Panamax/Supramax/Handysize **ngày 2012-08-01→2019-07-31**) — mới đọc trang mô tả, CHƯA tải được file (API 404); cần tải tay trên trình duyệt. Còn hở 2019-08 → 2026-04. |
| 4 | P4 phốt pho vàng, SCFI/FBX | Không làm | — | Hết hướng free trong phiên; FBX: Freightos công bố bản chỉ số có "Download report (free)" (cần email), chưa kiểm. |

## Đối chiếu chéo APT (cùng khung thời gian)
Chuỗi tin nhất quán nội tại: 260k (07/2025) → 490k (11/2025) → 670k (12/2025) → 1,0 triệu (02/2026) = ×3,8. Cộng với tin thứ cấp (chưa mở trang gốc, KHÔNG đưa vào CSV): tháng 3/2026 đỉnh ~1,5 triệu, đầu 6/2026 hợp đồng 760k, tháng 7/2026 −15% (ChemAnalyst). Hướng và cỡ độ lớn khớp MSR ×3,45; chưa có 2 nguồn độc lập cho cùng một ngày.
Lưu ý đơn vị: APT nội địa TQ CNY/t (có thể gồm VAT 13%) khác APT châu Âu USD/mtu — không trộn.

## PIT
Mỗi dòng ghi `published_date`. Điểm 2025-12-31 chỉ biết từ bài 2026-02-09 ⇒ dùng được từ ngày đăng.

## ĐỀ XUẤT (cần Mike/user duyệt — chưa cài gì)
1. **Mở khoá nhanh nhất:** user/Mike tải tay Mendeley BDI 2012–2019 (CC BY 4.0) + xin **FBX CSV** Freightos (email analyst, miễn phí).
2. **APT:** cào trang SunSirs product page bằng trình duyệt headless (Playwright) vì JS challenge; hoặc đăng ký tài khoản miễn phí SMM xem bảng ngày. Cần kiểm điều khoản (SMM/SunSirs cấm scrape tự động? chưa đọc ToS ⇒ rủi ro chặn).
3. **Cron đề xuất (CHƯA cài):** `fetch_apt_sunsirs.py` hằng tuần T6 sau 18:00 ICT ghi append-only `data/apt_tungsten_weekly.csv` (cột date,value,unit,source_url,published_date); chạy sau khi dựng được fetcher và qua cổng §14 freshness.
4. **BDTI/BCTI:** nếu cần thật, cân nhắc Barchart/Baltic (trả phí) — chỉ ghi giá, chưa mua. Lựa chọn thay: proxy cổ phiếu dầu khí vận tải (PVT) không thay được.
5. Đừng chờ feed để quyết định MSR: tín hiệu giá đã ×3 nên pha đầu đã qua.

## Draft data_registry (status ĐỀ XUẤT — chưa ghi vào kb/)
```
feeds/apt_tungsten_snapshots.md — status: ĐỀ XUẤT / PARTIAL — 4 điểm rời, KHÔNG phải chuỗi; cấm dùng backtest.
Bẫy: CNY nội địa (VAT 13%?) ≠ USD/mtu châu Âu; ngày giá vs published_date.
feeds/bdi_daily.md — bổ sung: lịch sử chỉ từ 2026-05; backfill ứng viên = Mendeley 2012–2019 (chưa tải).
freight_rates_quarterly.csv — chưa có entry registry (TRAP-tiềm-năng: dựng lại theo quý, không phải nguồn gốc).
```
