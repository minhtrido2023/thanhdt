# Charter — Order-book execution shadow (10-level bid-ask) (`order_book_execution_shadow`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-08-18 · **Kết thúc dự kiến:** 2026-10-21

## 🎯 Mục đích

Giảm implementation shortfall/slippage và adverse selection của child order bằng dữ liệu snapshot 10 mức bid-ask; đây là nghiên cứu execution-only, KHÔNG tạo alpha, KHÔNG đổi chọn mã/sizing/lệnh.

## 📅 Nghiệm thu / mốc kết thúc

CỬA SỔ MỚI 2026-10-21 (đặt 2026-09-23, job Taylor_20260923_051148, user chốt phương án (A) SỬA rồi CHẠY LẠI). ⚠️ ĐÂY KHÔNG PHẢI GIA HẠN ĐỂ GOM THÊM MẪU — mốc 20 phiên đã vượt từ 09-23 (22 phiên có record, 21 phiên có ≥1 snapshot hợp lệ) và công thức Wilson của 2 lần gia hạn trước KHÔNG áp dụng ở đây vì nó dành cho ca thiếu mẫu. Cửa sổ này để tích luỹ mẫu ở đúng chỗ đang thiếu: tầng REAL (lệnh tài khoản thật) mới có N=26 thô / 9 hợp lệ, trong khi tầng PROBE đã có 295 và KHÔNG cần thêm. Tiêu chí kết thúc = **N≥30 quan sát hợp lệ ở TẦNG REAL**, không phải số phiên. Nếu tới 10-21 tầng REAL vẫn <30 thì đó là câu trả lời về TẦN SUẤT CƠ HỘI (~1,8 quan sát hợp lệ/phiên có lệnh thật) chứ không phải lý do gia hạn lần 4: khi đó chốt kết quả trên mẫu đang có và đóng chương trình.

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) Telemetry v1 ghi được snapshot 10 mức, quyết định baseline/HYBRID, child order, fill và hậu kiểm 1/5/15 phút với khóa nối traceable — Pha 0: chỉ instrumentation; không tác động cách đặt lệnh paper hoặc live.
- ⏳ (pending) Shadow policy chỉ đưa khuyến nghị KEEP/REDUCE/DEFER; không có đường gọi broker, không đổi child size, không đổi lịch HYBRID — Pha 1: policy đơn giản, khóa trước rule và version.
- ⏳ (pending) Có >=20 phiên evidence và so sánh ngoài mẫu với baseline HYBRID theo slippage, fill-rate, time-to-fill và adverse selection — Không dùng P&L/alpha làm tiêu chí.
- ⏳ (pending) Quant-skeptic review trước bất kỳ paper A/B có tác động execution; user sign-off trước mọi thay đổi live

## ℹ️ Ghi chú vận hành

Kế hoạch đã được user chốt 2026-08-14 và duyệt triển khai telemetry v1 ngày 2026-08-15: ưu tiên cải thiện chất lượng fill và giảm chi phí giao dịch, không nghiên cứu alpha. Schema khóa version: orderbook_l2_v1 + orderbook_execution_v1; giá VND, quantity G1 là shares, timestamp nguồn tách timestamp capture, snapshot quá 5 giây hoặc thiếu timestamp nguồn = INVALID và policy bắt buộc KEEP (fail-open baseline). Shadow policy spread_depth_v1: KEEP mặc định; REDUCE khi spread >=2 tick và touch depth <1x child; DEFER khi spread >=4 tick và touch depth <0,5x child. Kết quả shadow KHÔNG có đường gọi broker/không được đọc vào giá, KL hoặc lịch HYBRID. Raw + telemetry giữ ít nhất xuyên review 16/09 và 30 ngày sau review. Hậu kiểm 1/5/15 phút dựng offline, không thêm API call. RESILIENCE LOẠI KHỎI v1 theo user duyệt 2026-08-15: cadence 60s không đủ đo tái tạo sổ trong vài giây; muốn nghiên cứu phải mở chương trình/log riêng. Mọi số tách theo side, ticker-liquidity bucket và phiên; paired comparison cùng opportunity, không so P&L toàn portfolio.

[2026-09-23, job Taylor_20260923_051148 — ÁP DỤNG PHƯƠNG ÁN (A)] Checkpoint 09-23 báo 2 chặn: (1) hậu kiểm 1/5/15′ coverage ~1,6%, (2) policy KEEP 300/301 nên gate 3 không có độ tương phản. CẢ HAI đều được chẩn đoán lại và CẢ HAI chẩn đoán đầu đều SAI về nguyên nhân:
  · (1) KHÔNG phải thiếu mẫu mà là probe ĐỌC THIẾU NGUỒN. 259/265 quan sát rơi vào nhánh 'không có chuỗi giá nào để so'. Gốc: 91% mẫu là account `main`, mà `main` chạy broker `phs`, và `PHSBroker.get_quote()` dựng `l2_snapshot` nhưng KHÔNG BAO GIỜ ghi `quote_l2` — bản ghi `quote_l2` cuối có account_label=main là 2026-08-17, TRƯỚC ngày trial bắt đầu. Thêm phiên không sinh thêm điểm markout nào. Chuỗi giá của `main` vẫn có trên đĩa ở `probe_ticks_<account>_<date>.csv` (cadence 60s, sống thêm 30′ sau khi parent khớp — đúng bằng cửa sổ 1/5/15′). Probe đọc thêm nguồn này ⇒ coverage 1m/5m/15m 1,5%/1,5%/0,8% → **93,2%/93,2%/82,3%** trên ĐÚNG mẫu 22 phiên đã có. Gate 1 ĐẠT, không cần thu thêm ngày nào.
  · (2) KHÔNG phải ngưỡng quá chặt mà là MẪU KHÔNG ĐỒNG NHẤT. Tách tầng: PROBE (295 bản ghi, lệnh churn 100 CP trên 6 mega-cap) có `touch_depth_ratio` trung vị **763×** và `spread_ticks` = 1,0 ở 283/298, không bao giờ vượt 2,0 ⇒ KHÔNG ngưỡng spread+depth nào phân biệt được gì, và cũng không nên. Tầng REAL: trung vị **2,2×**, p25 1,3×, min 0,3× — đúng vùng policy phục vụ. Gộp 2 tầng là lý do cả checkpoint đọc ra 'policy vô dụng'. Mọi số của probe nay TÁCH TẦNG.
  · Ngưỡng hiệu chuẩn lại thành `spread_depth_v2` (reduce spread≥1 tick & depth<2,0 · defer spread≥2 & depth<1,0), chọn theo tiêu chí PHÂN BIỆT: trên mẫu đã thu cho **4/9 = 44% khác-baseline ở tầng REAL và vẫn 0/289 ở tầng PROBE**. v1 giữ nguyên trong lịch sử; `policy_version` đóng dấu vào từng bản ghi nên 2 thế hệ không lẫn.
  · Hậu kiểm ghi ra artifact RIÊNG `data/execution_logs/orderbook_markout.jsonl` (schema `orderbook_markout_v1`, nối bằng `trace_id`) — KHÔNG sửa bản ghi `orderbook_execution_v1` đã nằm trên đĩa, vì đó là bằng chứng immutable của thời điểm đặt lệnh và 321 bản ghi đã thu phải giữ nguyên để còn so được.
  · Adverse-selection đọc lại trên mẫu đầy đủ: 1m **+13,8bps** · 5m **+8,0bps** · 15m **−0,0bps** — suy giảm về 0, hình dạng của tác động TẠM THỜI. Con số cũ (+18/+21/+46bps, dốc LÊN theo thời gian) dựng trên N=4 và là nhiễu.
  · ⚠️ Hai cơ sở giá KHÔNG trộn: `dnse_raw`→mid, `probe_ticks`→last. Mỗi quan sát ghi kèm `markout_basis`; mẫu hiện tại mid=6 / last=259. So markout giữa 2 basis phải tách.
  · VẪN THUẦN SHADOW: `behavior_contract = LOG_ONLY_NO_BROKER_PATH`, không field nào đi vào `_child_qty`/`_limit_price`/lịch HYBRID. Gate 4 (user sign-off) CHƯA đụng tới.
  · Đo: `order_book_shadow_probe_selfcheck.py` 21/21 × 4 TZ + `env -u TZ` + `$DNA_PYEXE`, 7/7 mutation chết bằng assertion; `order_book_shadow_selfcheck.py` PASS × 4 TZ + py3.10, mutation revert ngưỡng về v1 chết. §23 quét rộng `trading_bot/config.py`: 12 selfcheck rc=0.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/orderbook_shadow_<account>_<date>.jsonl — schema orderbook_execution_v1: trace_id parent/child, baseline, KEEP/REDUCE/DEFER, latency và snapshot immutable`
- `data/execution_logs/dnse_raw_<date>.jsonl kind=quote_l2 — schema orderbook_l2_v1, G1 10 mức, VND + shares, source_ts/source_age_ms`
- `data/execution_logs/exec_<account>_<date>_journal.csv — PLACE/FILL/DONE nối bằng child_oid; hậu kiểm 1/5/15 phút dựng offline từ snapshot kế tiếp`
- `data/execution_logs/probe_ticks_<account>_<date>.csv — chuỗi giá `last` cadence 60s (Executor._probe_tick_log); NGUỒN MARKOUT DUY NHẤT của account paper `main` vì broker `phs` không ghi `quote_l2`. Lọc account test theo CỘT `account`, không theo tên file.`
- `data/execution_logs/orderbook_markout.jsonl — schema `orderbook_markout_v1`, hậu kiểm 1/5/15′ dựng OFFLINE, nối với quan sát bằng `trace_id`, kèm `markout_basis` + `stratum`.`
