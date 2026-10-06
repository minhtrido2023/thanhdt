# Cổng giá trong phiên + điều tra + cutloss 4 chế độ — bản SHADOW (job Taylor_20261005_185546)

Đặc tả: `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md` (Q1, cutloss, 4 chế độ, duyệt
01:12 + 01:54 ICT 06/10). Mọi ngưỡng chép nguyên plan — không tune theo replay.

## VÒNG 2 (job Taylor_20261005_195221) — sửa trọn 7 mục chặn + 4 mặc định an toàn của arch-reviewer

Shadow guarantee giữ nguyên (ReadOnlyDNSE, không đụng executor/plan/bot_execute). Chưa merge, chưa cài cron.

| # | Mục | Sửa |
|---|---|---|
| 1 | dispatch tự chặn (DISPATCH_FROM=Taylor ⇒ exit 2) | `DISPATCH_FROM=intraday_watch` (không phải agent ⇒ không self-dispatch, không auto-callback). `dispatch_argv()` là nguồn argv duy nhất; selfcheck chạy ĐÚNG argv đó vào stub bash mô phỏng parser + 2 chặn định tuyến, và đối chiếu mọi cờ với parser của `mike/bin/dispatch.sh` thật. Đối chứng: đổi lại `Taylor` ⇒ stub trả rc=2 ⇒ test đỏ |
| 2 | dispatch hỏng im lặng | bắt rc≠0 / `TimeoutExpired` / `OSError`; tin T0 gửi SAU bước dispatch nên nói đúng: "⚠️⚠️ KHÔNG CÓ ĐIỀU TRA TỰ ĐỘNG — <lỗi thật>… ANH CẦN TỰ XEM". Job đã chạy mà kết thúc failed/timeout/done không phán quyết (đọc `bus/jobs/<job>.json`) ⇒ báo ngay + dừng dispatch hôm nay |
| 3 | kill giữa :531-:552 mất T0 | **hộp thư đi bền** trong state: mọi tin xếp hàng + ghi đĩa trước khi gửi, gạch từng kênh sau khi gửi OK; cờ `t0_pending` trên đĩa; ngân sách 40s/lượt (< timeout 55). Docstring sửa: báo = at-least-once thật, dispatch = at-most-once. Test kill giữa T0, giữa PHÁN QUYẾT, giữa dispatch |
| 4 | fan-out | ≤2 điều tra/lượt quét (ưu tiên vị thế lớn), ≤3/ngày, 1 điều tra hết giờ/hỏng ⇒ dừng dispatch tới hết ngày; `--retries 0`, `--timeout` = hạn điều tra + 5'. ≥3 mã cùng lượt / ≥2 mã chạm sàn / thiếu VNINDEX ⇒ MỘT cảnh báo gộp "CẢ THỊ TRƯỜNG", không mở ca, không dispatch; mã được xét lại riêng khi lượt sau không còn chung |
| 5 | lỗi im lặng | crash cấp cao nhất + LiveMarket khởi tạo lỗi ⇒ cảnh báo 1 lần/ngày (cờ ghi trước khi gửi) rồi exit≠0; sức khoẻ mỗi lượt: lỗi giá >50%, vị thế TK lỗi, VNINDEX thiếu, ccdb lỗi (≤1/60' mỗi loại); kết quả Notifier được KIỂM (kênh lỗi thử lại ≤5 lượt, rồi báo qua kênh còn sống); 14:50 tóm tắt 1 dòng |
| 6 | lệnh trả lời nhầm lệnh thật | bắt buộc tiền tố: "SHADOW GIỮ PNJ" / "SHADOW BÁN PNJ" / "SHADOW BÁN 50% PNJ"; "BÁN PNJ" trần bị bỏ qua; mọi tin hướng dẫn ghi "ĐÂY LÀ CHẠY THỬ (SHADOW), KHÔNG CÓ LỆNH THẬT" |
| 7 | cron_registry §11 | `kb/cron_registry.md.proposed` (2 dòng, giữ dạng UTC: `* 2-7 * * 1-5` + `30 1 * * 1-5` cho nhắc 08:30) |

**Mặc định an toàn (hằng số, CHỜ USER CHỐT):**
- (a) `engine.NON_AGENT_DEFAULT = HOLD`: không có phán quyết của agent (`source` = `timeout` | `no_dispatch`) ⇒ GIỮ + cảnh báo lớn, KHÔNG bán 50%. CHƯA RÕ **do agent** vẫn bán 50% (chính sách đã duyệt). Nguồn kết luận ghi riêng trong state/log.
- (b) `excluded_tickers` của TK hoặc `data/intraday_watch/restricted.json` (danh sách TAY — chưa có field DNSE nào đã xác minh cho "hạn chế giao dịch") ⇒ chỉ báo + điều tra; KHÔNG đặt lệnh kể cả khi user ra lệnh (báo "thao tác tay").
- (c) kích hoạt ≥14:00 (`LATE_TRIGGER`) hoặc hạn trả lời >14:15 (`NO_EOD_DEFAULT_AFTER`) ⇒ mặc định chỉ áp từ 09:15 phiên sau; 08:30 nhắc 1 lần. Lệnh SHADOW tường minh của user vẫn áp ngay (lựa chọn của Taylor — user chủ động thì tôn trọng).
- (d) log `ALT_THRESHOLD` song song: ngưỡng tương đối HOSE −3% / HNX −4,5% / UPCOM −7% / idio −3% (hành động vẫn theo −5%/−4%); `latency_min` + `source` + `compressed` mỗi phán quyết ⇒ tóm tắt 14:50 tách tỉ lệ hết giờ rút gọn vs thường.
- Book: thêm nhãn `custom30V_parking` + đọc `park_add_/jit_unpark_/park_trim_/bootstrap_book_snapshot_`. Trên vị thế thật 05/10 (dnse_raw, lọc §12): r1 để **TPB** (SpaceX) rơi UNKNOWN; r2 **28/28 có book, 0 UNKNOWN**.

**Kiểm chứng r2:** selfcheck **268/268** × {`env -u TZ`, `Pacific/Kiritimati`, `America/New_York`, `Asia/Ho_Chi_Minh`} × {`$DNA_PYEXE`, `python3`}. Đột biến **119/121 bị giết** (chạy song song 8 luồng); 6 đột biến reviewer thấy SỐNG ở r1 — bỏ flock, bỏ lưu trước dispatch, bỏ lọc account §12, bỏ @mention, bỏ huỷ ở chế độ 2, bỏ lưu trước khi gửi (bỏ cả 3 chỗ) — **đều bị giết**. 2 con sống là **tương đương đã phân tích**: bỏ 1 hoặc 2 trong 3 chỗ ghi đĩa trước khi gửi (dư thừa nhau + `t0_pending` tính lại được) — không đổi hành vi. Vòng chạy đầu r2 có 5 con sống thật (gộp cảnh báo lặp, cờ `late`, `latency_min` trong state, 2 biến thể lưu) ⇒ đã thêm phép thử. Smoke DNSE thật (chỉ-đọc, giờ ép 10:00): 16 mã, 0 lỗi giá, VNINDEX chưa có bar ⇒ cảnh báo sức khoẻ đúng thiết kế.

**Replay thay đổi do (c):** PNJ 24/09 (T0 14:15) và TV1 16/07 (hạn 14:23) giờ hoãn sang 09:15 phiên sau — PNJ-BAL CHƯA RÕ bán 50% sáng 25/09 (TB 33.550) thay vì ATC 24/09.

---

## File
| File | Vai trò |
|---|---|
| `bin/intraday_cutloss_engine.py` | engine thuần: cổng, phán quyết→hành động, đọc trả lời, phiên theo sàn, loại lệnh, 4 chế độ, mô hình khớp shadow |
| `bin/intraday_price_watch.py` | driver I/O: vũ trụ, DNSE chỉ-đọc (`ReadOnlyDNSE`), state nguyên tử, báo, dispatch, ccdb, `verdict`/`status` |
| `bin/intraday_price_watch_selfcheck.py` | 268 phép thử r2 (engine + driver giả + stub dispatch.sh + replay dữ liệu phút thật) |
| `fixtures/replay_bars.json` + `fetch_replay_fixtures.py` | bar 1 phút DNSE PNJ/DGC/TV1 + VNINDEX |
| `mutation_run.py` | 121 đột biến r2 (59 r1 + 62 mới), sandbox /tmp, song song |

## Kiểm chứng (r1 — xem số r2 ở trên)
- Selfcheck **171/171** dưới TZ không đặt / America/New_York / Pacific/Kiritimati / Asia/Ho_Chi_Minh
  (`$DNA_PYEXE`) và `python3` hệ thống. Đột biến **59/59 bị giết** (vòng 1: 51/59 — 8 con sống = 8 lỗ
  hổng test, đã thêm phép thử; 1 trong số đó lộ lỗi thật "GIỮ giữa chừng ⇒ ca bị đóng DONE").
- Lỗi thật selfcheck/replay bắt được khi dựng: (1) lệnh ATO chưa có kết quả mang sang phiên liên tục ⇒
  crash; (2) kết quả ATC lấy nhầm KL/giá phiên ATO; (3) lệnh chờ ở sàn khớp ở giá sàn thay vì giá khớp;
  (4) GIỮ giữa chừng đóng ca; (5) phán quyết đến sau khi ca đã xong không được ghi.
- Smoke test đọc DNSE thật 06/10 02:36 ICT (chỉ inquiry): 16 mã vũ trụ, book đúng, sàn UPCOM/HOSE đúng,
  proxy chặn `place_order`; ccdb đọc được Trading Daily.

## Replay r1 (dữ liệu PHÚT thật; sổ lệnh lịch sử KHÔNG tồn tại ⇒ sổ giả = KL bar)
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
