# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- Retro 2026-09-21 XONG (3 sự cố). #1 plan-approval cuối tuần TÁI DIỄN (Pattern 1, HOÀN CHỈNH theo
  thiết kế, 0 thiệt hại). #2 checker `ops_health_check.sh` escalate-đã-xong TÁI DIỄN ở call site
  MỚI, Wags tự vá + arch-review CONFIRMED cùng lượt (`ed4e35a0`/`118bdbfb`). #3 **nav-price-xcheck-
  stuck DRI (SpaceX+ZaloPay, lệch 8,0%) CÒN MỞ** — NAV 21/09 thật sự thiếu ở cả 2 account, >10h
  chưa ai chẩn đoán. **Mốc theo dõi: nếu tới 09:00 ICT 22/09 2 câu hỏi
  `nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-21` vẫn chưa có answer/finding → escalate ngay
  trong ngày, không đợi retro 09-22.**

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353`** (raw `p["broker"]`/`p["mode"]`, cùng lớp bug config.py hard-
   boundary) — CHƯA sửa. Deadline escalate: **trước retro 2026-09-22** nếu vẫn chưa fix.
2. **nav-price-xcheck-stuck DRI 21/09** — xem mốc theo dõi ở trên. Chưa loại trừ được corp-action
   thật (cổ phiếu/bonus, cần xử tay theo MIKE.md §PRICE_XCHECK 09-12) hay chỉ broker trễ đồng bộ.
3. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 đã đóng 09-20.
4. **`Wags/selfcheck-red: anomaly_gate_prod_parity_selfcheck.py`** + **`.../production_manifest_
   selfcheck.sh`** (mở 09-20) PENDING — correctness PASS, chỉ fail coverage-gate, theo dõi.
5. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25).
6. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức.
7. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — chưa có selfcheck/commit xác nhận.
8. Spend-report feedback loop — `.proposed` từ 09-20, lần chạy tự động đầu Chủ Nhật 2026-09-27.

## Còn mở không khẩn
- job_cancel_guard nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- append_event.sh JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

- [2026-09-22T02:10:45Z] 22/09 09:xx: nav-price-xcheck-stuck DRI (SpaceX+ZaloPay 09-21) đã CHẨN ĐOÁN xong — cổ tức tiền DRI 1.000đ/cp ex-date 09-22, khớp mẫu DGC nhưng còn dư 100đ/0,7% chưa khớp tuyệt đối. CHƯA vá NAV (manual, hoãn qua giờ ATO). Việc còn lại: patch NAV 09-21 mark giá CUM 14.900 sau khi xác nhận cum_dividend_excl đã trừ đúng khoản phải thu (§21), làm sau khi thị trường ổn định (~10-11h).
- [2026-09-22T09:10:27Z] 22/09 16:1x — ĐÍNH CHÍNH chẩn đoán DRI sáng nay: KHỚP TỪNG ĐỒNG, không có 'dư 100đ'. Giá CUM của chính broker là 14.800 (19:07 hạ xuống 13.800 = 14.800−1.000 cổ tức). 100đ 'dư' sáng nay là do tôi so BQ close 14.900 với giá broker — khác nguồn, không phải lỗi. cashDividendReceiving rỗng ngày 09-21 (ex-date 09-22) ⇒ KHÔNG có rủi ro đếm 2 lần cho snapshot 09-21.
22/09 16:1x — VIỆC 3 (vá NAV 09-21): KHÔNG vá được bằng pipeline hiện tại. Đã thử daily_nav_snapshot.py --account SpaceX --date 2026-09-21 --from-raw (có source wc_env.sh) → vẫn bị gate chặn: close_price 09-21=14.900 (cum) vs broker EOD marketPrice=13.700 (đã điều chỉnh) = 8,8%. Mismatch này VĨNH VIỄN cho ngày đó, không tự lành. nav_history hiện dừng ở 09-18, thiếu CẢ 09-21 lẫn 09-22 (09-22 sẽ chạy 19:50 tối nay). KHÔNG ghi tay dòng CSV (vi phạm §6). => Backfill 09-21 trở thành ACCEPTANCE TEST của L2/L3: sau khi land, chạy lại lệnh --from-raw trên cho CẢ 2 account, phải điền đúng với DRI mark giá CUM 14.900. Phải xong trước weekly report thứ Sáu (§31 nav_period_returns cần chuỗi NAV liền).
22/09 16:0x — Dispatch Taylor_20260922_090801 (bg, 90') làm L1→L4 corp-action-aware NAV gate. L1 (báo trước 19:00 T-1) có DEADLINE CỨNG: land trước 19:00 T4 23/09 để kịp thử thật trên VPB ISS 26,04% ex-date T5 24/09 (giữ SpaceX 1.100cp + ZaloPay 1.300cp).
- [2026-09-22T09:59:17Z] 22/09 17:0x — L1 corp-action forecast: arch-review ĐỘC LẬP của Mike = NEEDS_CHANGES (high), KHÁC với 'PASS' mà Taylor tự báo (Taylor tự gọi review riêng — KHÔNG tính là clearance). R1 (cửa sổ phiên) Taylor đã tự sửa ở ef544b1d, Mike tự verify selfcheck 28/28 qua 3 TZ. R2-R6 còn mở, đã dispatch vòng 2 Taylor_20260922_095858. Bài học: arch-review bắt được 'commit != code trên đĩa' (worktree bẩn lúc review) — Taylor vòng 1 khai PASS=26 của commit cũ. Deadline L1 vẫn 19:00 T4 23/09 (phép thử VPB).
22/09 17:0x — L2-L4 BỊ BÁC (Taylor tự arch-review, branch feat/nav-corpaction-gate @ c5bd6e9b). HAI LỖI NẰM TRONG SPEC CỦA MIKE, phải sửa hướng trước khi giao lại:
 (1) L3 tôi bắt kiểm bất biến qua cum_dividend_double_count -> nhưng ở chế độ live, hàm đó LUÔN trả tickers=[] (pending rỗng vì BQ chưa có phiên hôm nay lúc 19:10, daily_nav_snapshot.py:519-521) => điều kiện set(tickers)=={ticker} LUÔN False => vá xong vẫn không giải được ca DRI, chỉ đổi thông điệp lỗi. HƯỚNG SỬA: lấy ticker + cổ tức/cp TỪ CHÍNH snapshot corp_action_daily (nguồn đã tin dùng cho L1) rồi đối chiếu bằng chứng có sẵn lúc 19:10 (balances broker), KHÔNG chờ BQ xác nhận.
 (2) L4 tôi nói 'dò theo lịch thay vì biên độ giá' — đúng cho PHÁT HIỆN nhưng SAI cho CHẶN: chặn theo lịch sẽ chặn NAV cả 2 account ngày 23 VÀ 24/09 vì VPB dù cp==mp (gap thật 0,0%); ước tính ~10/28 phiên gần đây bị chặn oan. HƯỚNG SỬA: TÁCH phát hiện khỏi chặn — lịch chỉ để CẢNH BÁO (L1 đã làm); CHẶN phải dựa bằng chứng credit sớm THẬT (so qty với phiên trước, tái dùng confirmed_qty_multiplier_after có sẵn).
 Còn: rc=4 tái sử dụng khiến nav_sync_retry escalate với thông điệp 'lệch giá >5%' SAI cho ca L4 (§29); except Exception: pass dòng 265-266 fail-open im lặng; TOCTOU tính cum_div 2 lần qua BQ (dòng 760 rồi 886) = đường khác dẫn về đúng lỗi v1.
- [2026-09-22T10:44:27Z] 22/09 17:4x — L1 nav_exdate_forecast ĐÃ LAND: mike master @ 2a7dd54e (rebase len 84d2a675 roi ff-merge). arch-review APPROVED high sau 5 VÒNG. Selfcheck 58/58 chạy TỪ MASTER qua 3 TZ. Wiring [pipeline-0] dòng 501-512 bq_freshness_check.sh, TRƯỚC exit 1 đầu tiên (520). PHÉP THỬ THẬT: 19:00 ICT 23/09 chuỗi plan phải tự in cảnh báo VPB (ISS 26,04%, ex-right 24/09, giữ SpaceX 1.100cp + ZaloPay 1.300cp) — nếu KHÔNG thấy thì wiring hỏng, phải điều tra ngay tối 23/09. Tối 24/09 NAV sẽ bị PRICE_XCHECK chặn vì VPB — ĐÓ LÀ ĐÚNG THIẾT KẾ (sự kiện cổ phiếu luôn chặn), không phải bug; vẫn cần người xử tay cho tới khi L2-L4 xong.
CÒN LẠI: (1) L2-L4 chưa làm — spec cũ của Mike có 2 lỗi đã biết (L3 bắt bất biến qua cum_dividend_double_count vốn LUÔN trả tickers=[] ở chế độ live; L4 chặn theo lịch sẽ chặn oan ~10/28 phiên) => phải thiết kế lại: L3 lấy ticker+cổ tức từ snapshot corp_action_daily rồi đối chiếu bằng chứng có sẵn lúc 19:10; L4 tách PHÁT HIỆN (lịch, L1 đã làm) khỏi CHẶN (bằng chứng credit sớm thật: so qty với phiên trước, tái dùng confirmed_qty_multiplier_after). (2) nav_history vẫn thiếu 09-21 (và 09-22 nếu tối nay chặn) — backfill 09-21 là ACCEPTANCE TEST của L2/L3, cần xong trước weekly report thứ Sáu.
- [2026-09-22T11:11:42Z] 22/09 18:1x — Dispatch Taylor_20260922_111128 (bg 90') làm L2-L4 theo SPEC v2 do Mike thiết kế lại (spec v1 đã bị bác vì 2 lỗi của Mike). Luật hợp nhất v2:
 NHÁNH 1 qty_moved (broker qty hôm nay != phiên trước) = bằng chứng credit sớm THẬT -> CHẶN, bất kể biên độ giá (đây chính là L4: đóng lỗ hổng sự kiện tỉ lệ nhỏ ~1% giá rơi <5% mà gate không bật).
 NHÁNH 2 CASH_DIV khớp |broker_px − (bq_close − div)| <= 1 tick -> mark giá CUM, nhưng CHỈ sau khi khẳng định DƯƠNG bất biến: khoản phải thu của chính mã đó CHƯA nằm trong tiền broker (nguồn: balances broker + snapshot corp_action_daily, KHÔNG chờ BQ). Không khẳng định được -> FAIL-CLOSED.
 NHÁNH 3 >5% không khớp gì -> giữ nguyên hành vi hiện tại. NHÁNH 4 pass như cũ.
 Bất biến: gate KHÔNG được yếu đi ở bất kỳ nhánh nào; chỉ nhánh 2 được phép qua thêm.
 4 việc phụ bắt buộc: P1 rc riêng (vd rc=5) + sửa nav_sync_retry.sh để không escalate thông điệp 'lệch giá >5%' sai cho nhánh 1 (§29); P2 hết TOCTOU tính cum_div 2 lần qua BQ; P3 cấm except-pass im lặng; P4 ghi bằng chứng quyết định vào nav_snapshot JSON.
 NGOÀI PHẠM VI: tự quy đổi ngược qty cho sự kiện cổ phiếu (Mike đã hỏi user, CHƯA duyệt) — sự kiện cổ phiếu vẫn CHẶN + cần người; Taylor chỉ được ĐỀ XUẤT, không code.
 ACCEPTANCE TEST: backfill nav_history 09-21 cả 2 account bằng --from-raw, DRI phải mark giá CUM 14.900. Chạy trong worktree, KHÔNG ghi nav_history thật tới khi Mike land.
- [2026-09-22T11:54:27Z] 22/09 18:5x — L2-L4 v2 (fdc325ff) arch-review ĐỘC LẬP: NEEDS_CHANGES (high). KHÔNG LAND.
TIN TỐT: cả 2 lỗi spec v1 ĐÃ HẾT (reviewer giết 4/5 mutation trên classifier + 1 trên nav_sync_retry.sh THẬT). P2/P3 đạt, authority boundary sạch. P1 của Taylor ĐÚNG (verify bằng code consumer thật: eod_trading_report.sh:169 rc=4 tuyệt đối; nav_sync_retry.sh:51 rm marker+continue; nav_snapshot_daily.sh thông điệp generic).
KILLER OBJECTION (Mike tự đọc code xác nhận): return 5 ở ~:825 chạy TRƯỚC 'if args.from_raw' (~:830) chứa nhánh early_credit (~:848) — nhánh DUY NHẤT chia ngược qty theo qty_multiplier CONFIRMED. N1 chặn theo qty_now!=qty_prev mà chênh lệch đó KHÔNG BAO GIỜ biến mất => --from-raw về sau VẪN rc=5 VĨNH VIỄN => mỗi SHARE_EVENT (~1/tuần, 5/30 snapshot) = 1 lỗ vĩnh viễn trong nav_history (nguồn duy nhất §31/WTD/MTD). Ca thật VIB 09-09 (SpaceX 500->547, ZaloPay 200->219) hiện TỰ LÀNH được, v2 giết đường đó. Phát súng đầu: VPB, N1 bắn từ lần chạy 09-23.
+ 3 blocking khác: §29 thông điệp khẳng định 'CREDIT SỚM THẬT' mà chưa đối soát FILL (journal đã parse sẵn :744-750) và khuyên 'backfill --from-raw' mà chính nó chặn; ghi {nav:null} đè tên canonical nav_snapshot_{acct}_{date}.json không atomic (đè artifact audit dividend_adjusted_return.py viện dẫn); 3 hàm mới (_corp_action_daily_snapshot/held_event_next_session/previous_raw_qty) 0 assertion.
LỊCH: reviewer chứng minh gate là NO-OP phiên 22/09 (DRI ex-date = HÔM NAY không phải phiên kế tiếp) => KHÔNG có deadline tối nay. Cửa sổ thật: xong trước ~17:00 T4 23/09 để land trước cron 19:50. Không kịp thì để VPB 24/09 chặn bằng đường cũ, xử tay — KHÔNG land vội.
Dispatch vòng 2: Taylor_20260922_115410 (bg 90', opus/high).
nav_history vẫn thiếu 09-21 + 09-22; backfill 09-21 vẫn là acceptance test, chưa chạy được.
- [2026-09-22T12:30:49Z] 22/09 19:3x — L2-L4 v2 @ 66b3309a arch-review VÒNG 2: NEEDS_CHANGES (high), hẹp hơn nhiều. Dispatch vòng 3: Taylor_20260922_123031 (bg 60', opus/high).
ĐÃ ĐẠT (đừng audit lại): trục KL replay 2.700 ticker-day thật → 12 chặn, CẢ 12 là corp-action thật, 0 nhiễu. LIVE không bao giờ quy ngược KL. corp_actions.json chỉ đọc. Dung sai KL đúng (VPB 1.100cp: credit 286 vs kỳ vọng 286,45, tol 5,73 = 1,04% vị thế). event_code!=DIV ĐỦ (30 snapshot chỉ có ISS/AIS/DIV). net_fills_between đúng nửa mở. ops_runbook.proposed sạch (31 dòng, không sửa lén). Selfcheck 17/0+60/0+8/0 qua 3 TZ; §23 rộng: exrights 38/0, nav_exdate 58/0, nav_snapshot_daily 49/0.
SPEC MIKE SAI LẦN 4, Taylor đúng: Mike bảo 'để rơi xuống early_credit', nhưng early_credit chỉ bật khi lệch giá >5% nên sự kiện tỉ lệ nhỏ LỌT = mở lại lỗ hổng L4. Taylor áp thẳng multiplier trong gate là ĐÚNG.
CÒN 2 BLOCKING: [B1] :979-981  phục hồi theo SỰ TỒN TẠI action CONFIRMED chứ không theo bằng chứng mult giải thích được phần dư; guard ex_date (:362) chỉ sống khi ev tồn tại ⇒ TẮT khi lịch thiếu, mà snapshot lịch chỉ có từ 2026-08-13 ⇒ mọi backfill cũ hơn chạy KHÔNG guard, trong khi corp_actions.json có VHM mult 2.0. 2 ca ghi NAV SAI rc=0 đã dựng được. Vá: neo ex_date theo next_trading_day + đòi mult tái tạo được qty_prev+net_fill. [B2] :974 prev_d có thật mà qty_prev=None (mã chưa giữ) fail-open thành 'ok' ⇒ mã mới mua + ISS 1% lọt cả 2 trục; vá: qty_prev=0.0 (đo thật 1/600 ticker-day, phần dư 0,0 ⇒ không false-block).
NỢ CŨ phát hiện thêm (KHÔNG phải hồi quy, chưa sửa): nav_cum_dividend_selfcheck.py:34 neo WC_ROOT=dirname(dirname(MIKE_BIN)) ⇒ crash khi chạy từ worktree; từ master vẫn 38/0. Cùng lớp bug đã vá trong daily_nav_snapshot.py 09-12 bằng wc_paths.find_wc_root.
nav_history: SpaceX 09-22 Mike tự chạy lúc 19:12 (983.314.895, khớp active_nav plan DollarBill từng đồng), sau đó chuỗi EOD ghi đè 19:13:58 = 983.315.018. ZaloPay 09-22 đã có từ 19:10. CHỈ CÒN THIẾU 09-21 cả 2 account. Backup nav_history trước khi chạy selfcheck 2-account: /tmp/nav_history_guard_20260922/.
CHƯA CHẠY: bin/nav_scripts_2account_selfcheck.py (ghi đè nav_history thật) — để SAU 21:00 ICT.
- [2026-09-22T12:50:08Z] --append -
- [2026-09-22T13:32:21Z] 22/09 20:4x — L2-L4 corp_action_gate_v2 ĐÃ LAND: mike master 4dcc3643, arch-review APPROVED sau 5 VÒNG. current_ops Features-LIVE đã ghi (f5c99d32). 2 bus question nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-21 ĐÃ ĐÓNG.
NGHIỆM THU ĐẠT: nav_history 09-21 điền được CẢ 2 account rc=0 — SpaceX 974.653.192 / ZaloPay 950.813.808. Chuỗi NAV LIỀN MẠCH 5 phiên 09-16..09-22 cả 2 account => §31 weekly report thứ Sáu KHÔNG còn bị chặn. Gate làm đúng: DRI mark giá CUM 14.800 (không phải 13.700 của broker), trừ đúng 3.700.000 (SpaceX 3.700cp) / 1.900.000 (ZaloPay 1.900cp) khỏi tiền.
Selfcheck TỪ MASTER: e2e 38/0 + from_raw 64/0 + rc-harness 8/0 qua 3 TZ. §23 nav_scripts_2account_selfcheck.py PASS, nav_history IDENTICAL.
BÀI HỌC — spec của Mike sai 5 lần trong 1 việc, lần nào Taylor/reviewer nói ra cũng đúng: (1) L3 kiểm qua cum_dividend_double_count vốn luôn trả tickers=[] ở live; (2) L4 chặn theo lịch gây over-block; (3) đưa Taylor số DRI 14.900 trong khi 14.800 mới đúng; (4) bảo 'để rơi xuống early_credit' — sai vì early_credit chỉ bật khi lệch giá >5% nên sự kiện tỉ lệ nhỏ LỌT; (5) duyệt bản vá đổi mẫu số dung sai sang phần dư mà chỉ kiểm m<2, bỏ sót residual>base ⟺ m>2 nên NỚI ở nhánh mult>2. => Khi giao việc chạm tiền, LUÔN yêu cầu agent nói thẳng chỗ spec sai, và TỰ TÍNH LẠI trên MỌI nhánh tham số chứ không chỉ các ca reviewer đưa.
VIỆC LÀM SAU (chưa mở, ưu tiên giảm dần):
 1. corp_action_auto_confirm.py:143-161 — check_ratio so mult khai báo TỪNG chân với tỉ lệ TỔNG quan sát => xác nhận mult BỘ PHẬN như thể đầy đủ. Đây là chỗ rò thật của ca hỗn hợp leg <2% (NAV +1,5% im lặng ở m>2), KHÔNG phải first-match :381-393. Hướng: >1 candidate chung (ticker,ex_date) thì so TÍCH và TỪ CHỐI xác nhận chân đơn lẻ.
 2. nav_scripts_2account_selfcheck.py:45 + nav_cum_dividend_selfcheck.py:34 — neo WC_ROOT bằng đếm cấp dirname => hỏng khi chạy từ worktree (Mike phải patch tạm ra /tmp mới chạy được). Đổi sang wc_paths.find_wc_root. Sắc thái: nav_cum_dividend_selfcheck IMPORT daily_nav_snapshot (neo ĐÚNG) trong khi tự neo SAI => 2 gốc cây trong 1 tiến trình.
 3. vn_market.py:38-43 — _VARIABLE_HOLIDAYS chưa khai Tết ÂL 2027 (is_holiday(2027-02-16)=False). Nhánh này là nơi ĐẦU TIÊN daily_nav_snapshot.py phụ thuộc next_trading_day. Chiều lệch fail-closed. Khai trước 02/2027.
 4. kb/ops_runbook.md.proposed — Mike duyệt đưa live (mục rc=5 trong § NAV thiếu dòng).
 5. daily_nav_snapshot.py:1051-1053 — comment nói rõ 2% trùng RATIO_TOL=0.02 của corp_action_auto_confirm.py:41 (không độc lập như tưởng).
CÒN THEO DÕI: 19:00 T4 23/09 chuỗi plan PHẢI tự in cảnh báo VPB (ISS 26,04%, ex-right 24/09, SpaceX 1.100cp + ZaloPay 1.300cp) — không thấy thì wiring L1 hỏng, điều tra ngay tối 23/09. Tối 23/09 cron NAV 19:50 là lần chạy production ĐẦU TIÊN của gate mới với sự kiện cổ phiếu thật => theo dõi.
