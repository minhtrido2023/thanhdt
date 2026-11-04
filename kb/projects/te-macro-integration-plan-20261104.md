# Kế hoạch tích hợp `tav2_bq.macro_indicator` (TradingEconomics) — 04/11/2026
> User duyệt 5 đề xuất 04/11 23:52 ICT (`decided_by: user`). Mọi mục là DISPLAY/CROSS-CHECK/PAPER — KHÔNG gắn gate, KHÔNG đổi sizing.

## Bẫy phải xử lý trước (ràng buộc cho mọi bước)
1. Look-ahead: `observation_date` series tháng/quý = cuối kỳ, không phải ngày công bố; `fetched_at` chỉ có từ 30/10 ⇒ phải có độ trễ công bố giả định.
2. `vn_bond_10y` lệch VBMA +0,13…+0,21pp ⇒ chỉ dùng Δ, mức giữ UNVERIFIED.
3. Backfill 4 chữ số thập phân vs dòng hằng ngày 2 chữ số ⇒ không dùng tick nhỏ.
4. Writer ngoài repo (cron 15:00 UTC) — chưa xác định chủ.

## Làn 1 (song song, độc lập write-scope)
| Bước | Việc | Ai / model | Xong khi |
|---|---|---|---|
| A1 | Registry: thay `macro_indicator_tpcp10y.md` bằng `macro_indicator.md` (45 series, cadence, bẫy 1-4); cập nhật `macro/index.md` | Winston (data-ops), sonnet/medium | registry đúng số series, ghi rõ writer = "ngoài repo, chủ: <user xác nhận>" |
| A2 | Thêm dòng freshness `macro_indicator` vào `bq_freshness_check.sh` (fail-closed: series hằng ngày cách >3 ngày lịch ⇒ cảnh báo Trading Daily) | Winston → arch-review nhẹ (script ops, không chạm tiền) | selfcheck rc=0 dưới `env -u TZ`; giả lập stale ⇒ cảnh báo |
| B1 | View `tav2_bq.macro_indicator_pit`: bảng độ trễ công bố theo series (nguồn lịch GSO/NHNN/ISM… phải dẫn), `available_date = observation_date + lag`, chọn bản ghi sớm nhất theo `available_date` (không dùng fetched_at); daily series lag 0-1 | Taylor, sonnet/medium; quant-skeptic verify | selfcheck: 0 dòng nhìn thấy trước available_date; CPI/PMI khớp NSO/fiinprox 13/13 tháng; ghi `data_registry` |
| C1 | Check chéo tuần (CHỈ CẢNH BÁO, không tự sửa): (a) TE `vn_policy_rate` vs `sbv_refi_events.json` — mở rộng `sbv_policy_verify.py` có sẵn thành nguồn thứ 2; (b) TE `vn_cpi_yoy` vs `NSO_CPI_YOY_REAL` + `fiinprox_cpi_monthly` | Taylor, sonnet/medium (chung phiên B1 nếu muốn tiết kiệm) | selfcheck có ca lệch giả lập ⇒ cảnh báo; gắn vào cron tuần có sẵn `refresh_deposit_cctg_weekly.sh` (KHÔNG thêm dòng crontab) |

## Làn 2 (sau B1)
| Bước | Việc | Ai | Xong khi |
|---|---|---|---|
| D1 | Dòng DISPLAY "Thanh khoản VN": liên ngân hàng 3M − lãi suất điều hành (hiện +2,33pp, phân vị 93% từ 2012) vào `dna_report` + `deposit_cctg_trend_check`; nhãn "giả thuyết chưa kiểm" | Taylor, sonnet | dòng hiển thị, fail-closed khi stale, không gate |
| D2 | Nghiên cứu paper: spread thanh khoản có dẫn lãi huy động/kill-switch A không? N độc lập (số chu kỳ) khai trước, PREREG, khung nhân quả (N nhỏ) | Taylor, opus/medium + quant-skeptic | verdict; REFUTED/INCONCLUSIVE ⇒ chỉ giữ dòng hiển thị |
| E1 | `macro_snapshot_asof.py --asof DATE` (đọc `macro_indicator_pit`): 1 khối bối cảnh vĩ mô cho Bobby (mù) + khối "điều thị trường chưa tính" trong DD; ánh xạ ngành (bán lẻ→PNJ/MWG, xây dựng→thép/xi măng, FDI/IIP→KCN, xuất khẩu→logistics) | Taylor, sonnet; thêm bước vào skill `due-diligence` | chạy cho 3 as-of lịch sử, không rò dữ liệu sau as-of |

## Làn 3 (sau D2/E1, thấp ưu tiên)
F1 Pillar B ứng viên (US 2Y/10Y, DXY, USD/CNY, USD/VND): PREREG, paper-only, khung nhân quả với N=3–5 cú sốc, Bobby phân loại mù trước, quant-skeptic; KHÔNG wire, không đụng `macro_state_live.py` tới khi user duyệt riêng.

## Thứ tự & chi phí
Làn 1 = 3 dispatch (Winston A1+A2 gộp 1; Taylor B1+C1 gộp 1) · Làn 2 = 2–3 dispatch · Làn 3 = 1. Dùng gộp chuỗi để khỏi trả overhead lặp.

## Câu hỏi mở cho user
1. Ai/đâu chạy writer 15:00 UTC (để Winston ghi registry + biết nơi sửa nếu scrape hỏng)?
2. Duyệt tạo view mới `tav2_bq.macro_indicator_pit` (read-write BQ; chỉ tạo view, không đổi bảng gốc)?
3. Độ trễ công bố: chấp nhận nguyên tắc BẢO THỦ (lấy muộn hơn lịch thật vài ngày) cho series tháng/quý?
