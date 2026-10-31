# Báo cáo tài khoản chuẩn v2 — ngày / tuần / tháng / quý (MỞ, user duyệt khung 2026-10-31)

**Khung + luật đầy đủ:** `agents/Taylor/research/report_style_v2_20261031/REPORT_STYLE_V2.md` (+ `DIFF_VS_OLD.md`).
**Code:** `bin/report_v2/` (build.py · data_sources.py · render.py · narrative.py · artifact_lint.py). Selfcheck: `bin/report_v2_selfcheck.py`.

## Luật (rút gọn — chi tiết ở REPORT_STYLE_V2.md)
- Số CHỈ lấy từ pipeline: `nav_period_returns` (§31), `period_table_32`, `report_return_gate.position_returns` (§21), dnse_raw lọc `account_no` (§12). Agent KHÔNG viết số.
- **Hiệu suất = TWR trên vốn quản lý (luật 9b, user 31/10)**: tiêu đề/KPI/chart dùng tỷ suất giá đơn vị; NAV tuyệt đối chỉ trong **cầu NAV** (đầu kỳ → lãi/lỗ đầu tư → nạp/rút → cuối kỳ), có ở MỌI cadence.
- Agent chỉ viết `narrative.json`: headline ≤25 từ; ≤3 gạch/mục; ≤25 từ/gạch; outlook = bảng ≤4 kịch bản; số phải chép nguyên văn số builder đã in; SpaceX cấm tên nội bộ + từ vận hành; `internal` chỉ ZaloPay. Vi phạm ⇒ build rc=2 (sửa narrative, không nới luật).
- `report_delivery_gate.py` + `send_report_email.py` chạy `artifact_lint` fail-closed: repr `['|`/`\n|`, `**`, dòng `|---`, `None`/`nan`, tên nội bộ (SpaceX), font PDF không phải Be Vietnam Pro hoặc không nhúng, quá trần trang, file sửa sau khi dựng (sha256 manifest).

## Cách chạy
```bash
python3 bin/report_v2/build.py <daily|weekly|monthly> --account <SpaceX|ZaloPay> \
    --period <YYYY-MM-DD | YYYY-MM-DD_to_YYYY-MM-DD | YYYY-MM> --out-dir reports [--narrative n.json]
# rc: 0 xong · 2 narrative bị từ chối · 3 thiếu nguồn số bắt buộc · 1 lỗi khác
python3 bin/report_v2_selfcheck.py            # tháng+tuần+ngày × 2 TK; chạy thêm `env -u TZ` và TZ=America/New_York
```
Đầu ra: `reports/<Acct>_<cadence>_report_<period>.md` (TÓM TẮT, tên chuẩn ⇒ cadence/ledger/return gate giữ nguyên) +
`reports/v2/<stem>/` (PDF A4, HTML email ảnh cid, PNG+CSV chart, manifest.json). Dòng `<!-- report_v2_manifest: … -->`
trong .md khoá sha256 PDF; Discord nhận .md (bỏ dòng đó); email = HTML builder + PDF đính kèm.

## Đã gắn
- **Tháng/tuần**: `check_report_cadence.sh` — `V2_STEP` đứng đầu prompt dispatch; prompt cũ giữ nguyên làm DỰ PHÒNG khi build rc 1/3 (agent ghi `error report-v2-build-fail-<kỳ>` rồi soạn tay account đó).
- **Ngày**: `eod_trading_report.sh::_deliver_eod` (chỉ nhánh có lệnh) — FAIL-OPEN 2 tầng: build lỗi/quá 600s ⇒ bản text cũ; cổng chặn bản v2 ⇒ gửi lại bản text cũ. ZaloPay: .md = 3 dòng + nguyên bản text cũ. Rollback: `EOD_REPORT_V2=0`. `_nav_section` nay chạy TRƯỚC khối REPORT (hết cảnh báo "NAV hôm nay CHƯA có" lặp).
- **Quý**: chưa có lịch. Đề xuất: cron `check_report_cadence.sh --scheduled-quarterly` 09:00 ICT ngày 1 tháng sau quý (Q4/2026 đóng 31/12 ⇒ chạy 01/01/2027) — cần user duyệt + `kb/cron_registry.md` (§11) trước khi cài.

## Giới hạn đã biết
- Discord (`notify_thread.sh`) không đính kèm file ⇒ PDF chỉ đi email.
- Dòng đối soát "giá đóng cửa sàn vs định giá CTCK" (tham khảo) lệch ≠0 khi CTCK định giá UPCOM/HNX khác giá đóng cửa (đo 30/09: DRI, SCL, TV1; SpaceX −370.000, ZaloPay −190.000 VND); cầu NAV + tỷ suất dùng định giá CTCK, lệch 0.
- Beta "không có" (chưa có nguồn pipeline). Bản ngày nhánh HOLD/không plan vẫn là text cũ.
