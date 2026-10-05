# Cổng giá trong phiên + điều tra + cutloss 4 chế độ — bản SHADOW (job Taylor_20261005_185546)

Đặc tả: `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md` (Q1, cutloss, 4 chế độ, duyệt
01:12 + 01:54 ICT 06/10). Mọi ngưỡng chép nguyên plan — không tune theo replay.

## File
| File | Vai trò |
|---|---|
| `bin/intraday_cutloss_engine.py` | engine thuần: cổng, phán quyết→hành động, đọc trả lời, phiên theo sàn, loại lệnh, 4 chế độ, mô hình khớp shadow |
| `bin/intraday_price_watch.py` | driver I/O: vũ trụ, DNSE chỉ-đọc (`ReadOnlyDNSE`), state nguyên tử, báo, dispatch, ccdb, `verdict`/`status` |
| `bin/intraday_price_watch_selfcheck.py` | 171 phép thử (engine + driver giả + replay dữ liệu phút thật) |
| `fixtures/replay_bars.json` + `fetch_replay_fixtures.py` | bar 1 phút DNSE PNJ/DGC/TV1 + VNINDEX |
| `mutation_run.py` | 59 đột biến cổng chính, sandbox /tmp |

## Kiểm chứng
- Selfcheck **171/171** dưới TZ không đặt / America/New_York / Pacific/Kiritimati / Asia/Ho_Chi_Minh
  (`$DNA_PYEXE`) và `python3` hệ thống. Đột biến **59/59 bị giết** (vòng 1: 51/59 — 8 con sống = 8 lỗ
  hổng test, đã thêm phép thử; 1 trong số đó lộ lỗi thật "GIỮ giữa chừng ⇒ ca bị đóng DONE").
- Lỗi thật selfcheck/replay bắt được khi dựng: (1) lệnh ATO chưa có kết quả mang sang phiên liên tục ⇒
  crash; (2) kết quả ATC lấy nhầm KL/giá phiên ATO; (3) lệnh chờ ở sàn khớp ở giá sàn thay vì giá khớp;
  (4) GIỮ giữa chừng đóng ca; (5) phán quyết đến sau khi ca đã xong không được ghi.
- Smoke test đọc DNSE thật 06/10 02:36 ICT (chỉ inquiry): 16 mã vũ trụ, book đúng, sàn UPCOM/HOSE đúng,
  proxy chặn `place_order`; ccdb đọc được Trading Daily.

## Replay (dữ liệu PHÚT thật; sổ lệnh lịch sử KHÔNG tồn tại ⇒ sổ giả = KL bar)
| Ca | Kết quả |
|---|---|
| PNJ 24/09 | kích hoạt **14:15** (ret −5,4%, idio −4,1%) — discretionary + NHIỄU ⇒ giữ; book V2.4 giả định + CHƯA RÕ ⇒ bán 50% qua ATC 33.300 |
| PNJ 28/09→ | chạm sàn 09:30 ⇒ GÃY ⇒ chế độ 4. Hàng đợi sàn 10% KL: bán hết 30.700 ngày đầu (CẬN LẠC QUAN). Hàng đợi 0%: kẹt 4 phiên (ATC + ATO mỗi phiên), bán xong 02/10 khi sàn mở, TB ≥ 23.050 vs 21.650 đóng cửa 05/10 |
| DGC 22/07 | ⚠️ **KÍCH HOẠT trong phiên** (10:45 ret −5,8%, idio −4,4%) — plan dự kiến KHÔNG bắt (dựa idio đóng cửa −2,2). Không tune |
| DGC 23/07 | kích hoạt 10:45; GÃY ⇒ bán 10.000cp TB 31.250 (−0,7% vs đóng cửa) — mã đang **khớp định kỳ** (17 bar/ngày), engine CHƯA mô hình hạn chế giao dịch |
| TV1 16/07 | kích hoạt 13:45 (UPCOM); NHIỄU ⇒ giữ; kịch bản GÃY ⇒ toàn LO (UPCOM), TB 20.753 |

## Phát hiện chính sách cần user biết (không tự đổi)
1. **HOSE: −5% ⇒ room ≤2%** ⇒ MỌI kích hoạt HOSE vào chế độ RÚT GỌN (điều tra 10', trả lời 15') và bán
   ở chế độ ≥2 (MP) / 3 (LO sàn) ngay; chế độ 1 (3 đợt LO) chỉ xảy ra với HNX/UPCOM hoặc khi giá hồi.
2. `depth2 < Q ⇒ chế độ 3` khiến mã thanh khoản mỏng (TV1, DRI) luôn bán bằng LO sàn quét sổ.
3. DGC 22/07: ngưỡng −5/−4 trong phiên bắt cả ngày mà plan nghĩ là "cả thị trường giảm".

## Giả định CHƯA xác minh
- **MP** gửi DNSE với `orderType="MTL"` (docstring `dnse_api`; vnstock ghi "MP/MTL"). **ATO** chưa có lệnh
  thật nào (0/975). Đã xác minh: LO; ATC trên HOSE (VHC 2026-07-10); ATC UPCOM bị từ chối (SCL 2026-10-01).
- HNX không ATO; UPCOM không ATO/ATC, khớp liên tục tới 15:00 (quy chế sàn — không gọi API thử).
- Mô hình khớp shadow: lệnh chờ ăn 30% KL mới, hàng đợi sàn 10% KL tại sàn, ATO/ATC ở sàn 10% KL phiên.
- Bar 09:15 = kết quả ATO, bar 14:45 = kết quả ATC (đo từ cấu trúc bar DNSE, chưa đối chiếu sở).
- Book: lệnh MUA gần nhất trong plan 150 ngày; excluded_tickers + state discretionary ⇒ DISCRETIONARY;
  không truy được ⇒ UNKNOWN, xử như discretionary (chỉ tự bán khi GÃY).
- Trả lời Discord: mọi tin không phải bot trong Trading Daily coi là của user (API không trả user id).
  Lệnh phải đứng riêng một dòng; user ra lệnh trước phán quyết ⇒ được tôn trọng; GIỮ giữa chừng ⇒ dừng.
- Mã chỉ-watchlist (không giữ, không lệnh mua) ⇒ chỉ báo, không dispatch (`--dispatch-watch` để bật).
- Mẫu số %NAV = `active_nav_<TK>.json.total_nav` (tối hôm trước, ghi rõ giờ).
- Báo Discord+Telegram khi đổi chế độ / bán xong, không báo từng lần khớp mô phỏng (tránh spam).
