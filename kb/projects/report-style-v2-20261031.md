# Báo cáo tài khoản chuẩn v2 — ngày / tuần / tháng / quý (MỞ, user duyệt khung 2026-10-31)

**Khung + luật đầy đủ:** `agents/Taylor/research/report_style_v2_20261031/REPORT_STYLE_V2.md` (+ `DIFF_VS_OLD.md`).
**Code:** `bin/report_v2/` (build.py · data_sources.py · render.py · narrative.py · artifact_lint.py). Selfcheck: `bin/report_v2_selfcheck.py`.

## Luật (rút gọn — chi tiết ở REPORT_STYLE_V2.md)
- Số CHỈ lấy từ pipeline: `nav_period_returns` (§31), `period_table_32`, `report_return_gate.position_returns` (§21), dnse_raw lọc `account_no` (§12). Agent KHÔNG viết số.
- **Hiệu suất = TWR trên vốn quản lý (luật 9b, user 31/10)**: tiêu đề/KPI/chart dùng tỷ suất giá đơn vị; NAV tuyệt đối chỉ trong **cầu NAV** (đầu kỳ → lãi/lỗ đầu tư → nạp/rút → cuối kỳ), có ở MỌI cadence.
- Agent chỉ viết `narrative.json`: headline ≤25 từ; ≤3 gạch/mục; ≤25 từ/gạch; outlook = bảng ≤4 kịch bản; số phải chép nguyên văn số builder đã in; SpaceX cấm tên nội bộ + từ vận hành; `internal` chỉ ZaloPay. Vi phạm ⇒ build rc=2 (sửa narrative, không nới luật).
- **r3 (31/10 chiều)**: số % sau từ chỉ hướng (tăng/lãi ↔ giảm/lỗ/sụt/mất/âm) hoặc có dấu viết tay phải khớp DẤU số pipeline ("tăng 1,89%" khi pipeline −1,89% ⇒ rc=2); số 0..12 kèm %/điểm % hết miễn; có "từ/còn/xuống/lên/về/đến" chen giữa ⇒ không suy hướng. Từ cấm = MỘT nguồn `bin/report_v2/vocab.py` (narrative + lint; tên riêng không phân biệt hoa/thường; `nan`/`None` chỉ chặn như token dữ liệu — "nan giải" qua). Giới hạn: "giảm 12,5%" với 12,5% là số dương (tỷ trọng) bị chặn nhầm ⇒ viết lại câu ("xuống 12,5%").
- `report_delivery_gate.py` + `send_report_email.py` chạy `artifact_lint` fail-closed: repr `['|`/`\n|`, `**`, dòng `|---`, `None`/`nan`, tên nội bộ (SpaceX), font PDF không phải Be Vietnam Pro hoặc không nhúng, quá trần trang, file sửa sau khi dựng (sha256 manifest).

## Cách chạy
```bash
python3 bin/report_v2/build.py <daily|weekly|monthly|quarterly> --account <SpaceX|ZaloPay> \
    --period <YYYY-MM-DD | YYYY-MM-DD_to_YYYY-MM-DD | YYYY-MM | YYYY-Qn> --out-dir reports [--narrative n.json]
    [--promote]   # chỉ ở lần dựng CUỐI: nháp qua artifact lint ⇒ về tên chuẩn
# rc: 0 xong · 2 narrative bị từ chối · 3 thiếu nguồn số bắt buộc · 4 nháp không qua lint (không promote)
#     · 5 bản chuẩn ĐÃ GIAO (sổ report_delivery.json) — không ghi đè · 1 lỗi khác
python3 bin/report_v2_selfcheck.py            # tháng+tuần+ngày × 2 TK; chạy thêm `env -u TZ` và TZ=America/New_York
python3 bin/report_v2_selfcheck.py --cadences quarterly   # quý (mặc định 2026-Q3)
bash bin/eod_report_v2_failopen_selfcheck.sh  # 7 nhánh fail-open của EOD
```
Đầu ra (r3): mọi lần dựng ghi NHÁP `reports/v2/draft/<stem>.md` + `reports/v2/draft/v2/<stem>/` (lượt quét 08:30 chỉ nhìn
`reports/*_report_*.md` ⇒ không giao nhầm nháp). `--promote` ⇒ `reports/<Acct>_<cadence>_report_<period>.md` (TÓM TẮT, tên chuẩn) +
`reports/v2/<stem>/` (PDF A4, HTML email ảnh cid, PNG+CSV chart, manifest.json); .md ghi CUỐI sau trần trang + lint. Dòng `<!-- report_v2_manifest: … -->`
trong .md khoá sha256 manifest.json (r3) + PDF; Discord nhận .md (bỏ dòng đó); email = HTML builder + PDF đính kèm; ZaloPay kèm .md
đã bỏ dòng đó, SpaceX KHÔNG kèm .md (PDF là bản đầy đủ); ghi chú đính kèm (daily) chèn vào thân HTML. Số TK trong dòng "Tài khoản:"
của .md: giữ mặc định, `REPORT_V2_SHOW_ACCOUNT_NO=0` để bỏ (user chưa quyết). `manifest.positions` = [mã, KL, ô tỷ suất như in] ⇒
cổng §21 kiểm bảng vị thế của bản ngày v2 (trước r3: 0 dòng).

## Đã gắn
- **Tháng/tuần**: `check_report_cadence.sh` — `V2_STEP` đứng đầu prompt dispatch (r3: dựng nháp, chỉ lần cuối `--promote`, rc=5 ⇒ chỉ chạy cổng; tháng `--timeout 5400`, tuần 3600, câu ngân sách đầu prompt); prompt cũ giữ nguyên làm DỰ PHÒNG khi build rc 1/3 (agent ghi `error report-v2-build-fail-<kỳ>` rồi soạn tay account đó).
- **Ngày**: `eod_trading_report.sh::_deliver_eod` (chỉ nhánh có lệnh, `--promote`) — FAIL-OPEN 2 tầng: build lỗi/quá 600s ⇒ bản text cũ; cổng chặn ĐÚNG ở bước artifact-lint của nó (`INCOMPLETE — artifact-lint BLOCK`) VÀ sổ giao chưa có kênh delivered ⇒ gửi lại bản text cũ (r3: lỗi email sau khi Discord đã nhận KHÔNG fail-open nữa). Mỗi lần rơi về text cũ ⇒ bus `Mafee error report_v2_fallback`. ZaloPay: .md = 3 dòng + nguyên bản text cũ. Rollback: `EOD_REPORT_V2=0`. `_nav_section` nay chạy TRƯỚC khối REPORT (hết cảnh báo "NAV hôm nay CHƯA có" lặp).
- **Quý**: builder có (`build.py quarterly --period 2026-Q4`, ≤8 trang; quý chứa ngày khởi điểm ⇒ đóng góp theo mã "không có"), chưa có lịch. Đề xuất: thêm cờ `--scheduled-quarterly` (CHƯA có trong `check_report_cadence.sh`) + cron 09:00 ICT ngày 1 tháng sau quý (Q4/2026 đóng 31/12 ⇒ chạy 01/01/2027) — cần user duyệt + `kb/cron_registry.md` (§11) trước khi cài.

## Giới hạn đã biết
- Discord (`notify_thread.sh`) không đính kèm file ⇒ PDF chỉ đi email.
- Dòng đối soát "giá đóng cửa sàn vs định giá CTCK" (tham khảo) lệch ≠0 khi CTCK định giá UPCOM/HNX khác giá đóng cửa (đo 30/09: DRI, SCL, TV1; SpaceX −370.000, ZaloPay −190.000 VND); cầu NAV + tỷ suất dùng định giá CTCK, lệch 0.
- Beta "không có" (chưa có nguồn pipeline). Bản ngày nhánh HOLD/không plan vẫn là text cũ.
