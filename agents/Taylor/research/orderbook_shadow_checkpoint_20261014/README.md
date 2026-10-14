# Checkpoint `order_book_execution_shadow` — 2026-10-14 (job Taylor_20261014_020345)

Chỉ-đọc: không đụng code đặt lệnh, không đụng broker. Mọi số dưới đây MEASURED hôm nay từ
`data/execution_logs/{orderbook_shadow_*.jsonl, dnse_raw_*.jsonl, exec_*_journal.csv, orderbook_markout.jsonl}`.
Tái lập (cwd = `/home/trido/thanhdt/WorkingClaude`): `python3 mike/agents/Taylor/research/orderbook_shadow_checkpoint_20261014/{diag_invalid,diag_stale,compare_flag_vs_keep}.py`.

## 1. 73 bản ghi REAL `snapshot_valid=False` — nguyên nhân
- **73/73 cùng MỘT nguyên nhân: `source_age_ms > 5000`** (min 5.226 · trung vị 9.815 · max 5.413.095ms).
  Cấu trúc sổ đầy đủ ở cả 73 (có bid+offer, `source_time_status=ok`, đơn vị đúng, latency snapshot→lệnh ≤763ms).
  Không có ca nào thiếu sổ / thiếu timestamp / lỗi parse.
- **`source_age` KHÔNG đo "feed trễ" mà đo "sổ đứng yên bao lâu".** `source_ts` = trường `time` của quote DNSE
  (`brokers.py::_l2_source_time`). Trên 6.427 bản ghi `quote_l2` thô của 14 phiên REAL: 1.417 cặp snapshot liên
  tiếp có `source_ts` không đổi thì sổ cũng y hệt; chỉ 6 cặp `source_ts` không đổi mà sổ khác.
  Tỉ lệ >5s trong phiên liên tục theo mã: TV1 98% · SCL 90% · CSV 79% · VPI 77% so với HPG 4% · VHM 4% · VIX 4% · MBB 7%.
  2 ca max (5,4 triệu ms) là lệnh VPI 13:00:06 với `source_ts` 11:29:53 = sổ chưa đổi từ trước giờ nghỉ trưa.
- "Dồn ở 09-29, 09-30, 10-02" là do đó là các phiên NHIỀU LỆNH (80/10/97 bản ghi REAL), không phải sự cố feed:
  tỉ lệ invalid 09-29 = 17/80, 10-02 = 18/97; 09-30 = 10/10 (toàn lệnh mã mỏng).
- Nhãn "ERROR telemetry" của probe vì vậy SAI TÊN cho tầng REAL: đây là fail-open đúng thiết kế trên sổ tĩnh.

## 2. Có làm lệch mẫu hợp lệ không — CÓ, về thành phần
| | INVALID (73) | VALID (160) |
|---|---|---|
| tỉ lệ loại theo book | BAL 10/16 · LAG 11/19 · DISC 1/2 (**59%**) | PARK 51/196 (**26%**) |
| `touch_depth_ratio` trung vị / p25 | 13,8× / 3,0× | 43,6× / 13,1× |
| nếu chấm v2 trên feature đã ghi | REDUCE 7 + DEFER 5 = **16,4%** | REDUCE 16 + DEFER 2 = 11,3% |
| fill-rate · markout 1m trung vị | 90,4% · +16,0bps (n=21) | 86,9% · +11,8bps (n=93) |

Luật 5s loại có hệ thống đúng vùng policy sinh ra để phục vụ (mã mỏng, sổ ít đổi). Trung vị tổng hợp
(fill-rate, adverse) không dịch đáng kể, nhưng mẫu hợp lệ = chủ yếu lệnh PARK bán 100cp trên mega-cap.
Tiêu chí N≥30 hợp lệ vẫn đạt (160), nhưng 160 đó KHÔNG đại diện cho lệnh BAL/LAG mã mỏng.

## 3. REDUCE/DEFER vs baseline HYBRID (ngoài mẫu)
- **Ngoài mẫu** = REAL, hợp lệ, `policy_version=spread_depth_v2`, phiên ≥ 2026-09-24 (ngưỡng v2 khoá 09-23): 151 dòng,
  **FLAG 14** (13 REDUCE + 1 DEFER) / KEEP 137. Lệnh thứ 15 (TV1 09-14, v1) là trước hiệu chuẩn ⇒ loại.
- **N độc lập** (child cùng parent KHÔNG độc lập; 2 account cùng mã cùng phiên chung một sổ):
  FLAG = 12 parent → **10 cụm (phiên, mã)** → **4 phiên**. 12/14 dòng FLAG nằm trong 2 phiên (09-29, 10-02).
- **Công cụ**: ghép cặp trong cùng cụm (FLAG − KEEP), hoán vị dấu CHÍNH XÁC (liệt kê đủ 2^n). Không t-test, không bootstrap dòng.
- Shadow là LOG-ONLY ⇒ mọi lệnh chạy đúng baseline. Phép so trả lời "lệnh bị gắn cờ có kết cục baseline tệ hơn không",
  KHÔNG phải phản thực "REDUCE/DEFER thì tốt hơn bao nhiêu".

| metric (FLAG − KEEP, cụm phiên×mã) | cặp | Δ trung bình | dấu +/− | p exact |
|---|---|---|---|---|
| fill-rate | 8 | −0,16 | 0/2 (6 hoà) | 0,50 |
| time-to-first-fill | 7 | +108s | 4/3 | 0,41 |
| slippage vs limit | 7 | 0,00bps | 0/0 | 1,00 |
| adverse 1m | 4 | −15,2bps | 2/2 | 0,75 |
| adverse 5m | 4 | +14,7bps | 2/2 | 0,88 |
| adverse 15m | 2 | −12,1bps | 1/1 | 1,00 |

Ở mức phiên (3 phiên có cả 2 nhóm) p nhỏ nhất ĐẠT ĐƯỢC là 0,25 ⇒ không thể có ý nghĩa thống kê dù hiệu ứng lớn cỡ nào.
**Kết luận: không phát hiện khác biệt nào; mẫu không đủ lực để phân biệt "không có hiệu ứng" với "có mà chưa thấy".**

Ba giới hạn của chính phép đo (không phải của N):
1. `slippage vs limit` suy biến: 137/139 bản ghi markout REAL = 0,0bps (lệnh limit khớp tại limit) ⇒ metric này không đo được gì.
2. `time-to-first-fill` bị lượng tử theo nhịp poll: 65 bản ghi ≈20s, 47 ≈280-290s ⇒ đo lịch poll của bot, không đo thị trường.
3. 13/14 cờ nằm trên child 100cp: `REDUCE` = `round_lot(100/2)` = **0cp**, tức REDUCE ≡ DEFER trên lệnh 1 lô.
   10/14 cờ là lệnh PARK bán mega-cap (VPB/VHM/BID/LPB/VCB/VRE) lúc touch tạm mỏng, không phải mã mỏng.

## 4. Gate
| # | Gate | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | Telemetry v1 traceable | **PASS** (có 2 giới hạn) | 704 bản ghi/37 phiên, `trace_id` duy nhất; 233/233 lệnh REAL nối được PLACE trong journal; fill nối 631/704; hậu kiểm 1m/5m/15m 497/497/424 trên 559. Giới hạn: (a) HOSE chỉ trả 3 mức (221/233 bản ghi REAL n=3; SCL 10, TV1 8) — "10 mức" chỉ có ở mã ngoài HOSE trong mẫu; (b) hậu kiểm REAL 93/139 (1m), 64/139 (15m). |
| 2 | Shadow không có đường broker | **PASS** | 704/704 `LOG_ONLY_NO_BROKER_PATH`; 233/233 lệnh REAL có PLACE qty+giá = baseline; 15/15 lệnh bị gắn cờ vẫn đặt ĐỦ KL baseline; `order_book_shadow_selfcheck.py` rc=0, `order_book_shadow_probe_selfcheck.py` 21/21. |
| 3 | ≥20 phiên + so sánh OOS | **PENDING** (chốt 10-21) | ≥20 phiên: đạt (37 phiên; REAL 14). So sánh OOS đã chạy: NULL, thiếu lực (bảng trên). Thêm 5 phiên tới 10-21 không đổi được lực. |
| 4 | Quant-skeptic + user sign-off | **PENDING** (chưa kích hoạt) | Không có đề xuất A/B/live nào ⇒ chưa có gì để review. |

## 5. Khuyến nghị (không đề xuất nào chạm live)
- KHÔNG đề xuất đổi child size / lịch HYBRID. Không có bằng chứng.
- Tới 10-21: đóng chương trình mẹ với kết luận "telemetry dùng được, policy spread_depth_v2 không có bằng chứng phân biệt" — đúng điều khoản không gia hạn lần 4. Nhánh `opening_cycle` (mốc 2027-01-25) không bị đóng theo.
- Nếu sau này mở lại: (i) tách "sổ tĩnh" khỏi "feed trễ" trong luật hợp lệ (dùng latency capture thay cho `source_age`), nếu không mã mỏng luôn bị loại; (ii) bỏ slippage-vs-limit, thay bằng shortfall so với mid lúc đặt; (iii) ghi thời điểm khớp thật thay vì thời điểm poll thấy.
