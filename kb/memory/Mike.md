# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 2026-09-27 (24:00 ICT)
- Việc 1-6 (user duyệt 23:51 27/09) đã THỰC THI XONG hết: forensic_flags fail-closed (mike + WC),
  data/forensic_flags.csv commit vào WC (2cc1771d), 3 call-site fail-open→fail-closed
  (rating_8l.py/pt_v23_audit_2014.py/LAG gate, merge 18d4a562), park rail R2→R3 (merge 95547a9a),
  trading_rules.json đồng bộ văn xuôi 0.30 (c719d730, KHÔNG đổi số), FAIL-D không hành động.
- KB mới (mike 4f34b139): case pháp lý ⇒ có BCTC thì phân tích BÌNH THƯỜNG, chỉ WARNING tình
  trạng pháp lý; KHÔNG nới BANNED/excluded_tickers/forensic_flags.
- **Retro 2026-09-27 ĐÃ ĐÓNG** (`kb/incidents/retro/retro-2026-09-27.md`, Wags verify CONFIRMED,
  commit 3630b381): sự cố #1 `fa_ratings_8l` bị ghi đè bởi run EXP (guard `R8L_HIST_NO_BQ_REFRESH`
  opt-in, đã restore xong nhưng mất ~2h vì classifier chặn Taylor headless); sự cố #2 wakeup miss
  1/24 (tự phục hồi); gap #3 3 câu hỏi Taylor xử đúng qua commit nhưng chưa đóng event bus — ĐÃ
  ĐĂNG 3 answer event bù (custom30v-park-fraction-80, rail-ban-park-080, failopen-forensic-flags).
  Không escalate mới — 2 carry-over nặng nhất (ack-topic-counter, FPT vendor backfill) đã đóng.

## Còn mở (cần user quyết / chưa làm)
- **Đề xuất Pattern 1 (retro 09-27, CHƯA làm, cần user duyệt vì chạm code sinh dữ liệu
  production):** sửa `refresh_bq_table()` trong `rating_8l_history.py` — tự suy refresh CHỈ khi
  OUT path == canonical, thay vì mặc định refresh trừ khi có cờ tắt thủ công.
- Fail-open CÒN LẠI ngoài 3 site ưu tiên: ứng viên `trading_bot/plan.py:1651`+`:1756`
  (`except Exception: pass`) và `trading_bot/due_diligence.py:100`. **plan.py = logic đặt lệnh ⇒
  RANH GIỚI CỨNG, không tự sửa** — cần user ký từng site.
- `rating8l_icb_pit_selfcheck.py` FAIL bằng `MergeError` dtype `<M8[s]` vs `<M8[us]` — TIỀN TỒN,
  chưa ai sửa.

## Việc theo lịch
- T2 28/09 19:30 PARK_TRIM + 19:40 jit_unpark: có cảnh báo Discord khi rc≠0 (Trading Daily) — vẫn
  nên soát `logs/park_trim_daily.log`/`jit_unpark_daily.log` sáng T3 lần đầu để xác nhận đường
  cảnh báo chạy thật lần đầu trên production.
- Xoá cron FiinPro sau 28/09. Đóng AlphaLens 30/09 + ghi registry "PASS on N=1, không đủ bằng
  chứng sizing".
- Review quý: measurement-integrity audit ~2026-12-27; Bobby structural-risk ~2026-11-26.

## Bẫy đã ghi lại (đừng cắn lần 3)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^` +
  env override.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER. Gốc mặc định phải suy từ
  `__file__`.
- `discord_id_gate` chặn ID Discord trần trong code — dùng TÊN (`trading_daily`) trong
  `kb/discord_channels.json`.
- Guard chống ghi-đè production OPT-IN thủ công (biến môi trường người tự nhớ set) không đủ an
  toàn — phải tự suy từ path/context (retro 09-27 Pattern 1).
- Quyết định Mike đóng 1 `question` do AGENT KHÁC đăng lên bus vẫn cần 1 `answer`/`decision`
  ngắn trên bus, dù nội dung đầy đủ đã nằm ở KB/commit (retro 09-27 Pattern 2).

- [2026-09-27T18:24:04Z] 01:25 28/09: skeptic CONFIRMED (high) repin-dep1m-final, 8/8 check pass, tự tái lập đủ số + chạy lại selfcheck 102 assertion/15 mutation. Killer objection (không phá số): đây là ĐỔI QUY ƯỚC ĐO không phải alpha; lãi KỲ HẠN 1 tháng trả cho tiền thanh khoản hằng ngày (~46% NAV); 53/150 tháng dựng lại. 3 lỗi trình bày nhỏ + đề xuất chân carry-chỉ-khi-nằm-im-≥21-phiên. ĐANG CHỜ USER CHỌN A/B cho CLAUDE.md (A=đổi quy ước sang dep1m, Mike khuyến nghị; B=giữ 0%, số mới song song). CHƯA ghi results_registry.md, CHƯA đổi anchor/neo DD. 3 file .proposed sẵn sàng: results_registry_septies.proposed.md + 2 data_registry macro. Plan §9 commit.
- [2026-09-28T01:08:05Z] 08:10 28/09 USER CHỐT: PIN DẢI 2 SỐ — pin0% 23,37% (SÀN) … pin1M 25,71% (TRẦN), cả hai chính thức, cấm trích 1 số không kèm quy ước. NEO SIZING DD GIỮ −25,2% (đầu sàn), KHÔNG dùng −23,6%. ĐÃ GHI CANONICAL: WC CLAUDE.md §Backtest + data/results_registry.md (septies) + mike kb/canonical.md + kb/KNOWLEDGE.md + 2 data_registry macro (promoted từ .proposed). Câu hỏi A/B §9 ĐÓNG bằng phương án 3 (giữ cả hai). Đang chạy job Taylor_20260928_010454 = chân dep1m_21s (rút trước hạn=0%, ≥21 phiên, KHÔNG truy lĩnh, FIFO pin/LIFO sensitivity) + sửa 3 lỗi trình bày + soạn lại .proposed dạng dải. Wakeup: claim-reply job đó; xong ⇒ verify_finding --topic dep1m-21s-final; CONFIRMED ⇒ bổ sung số vào registry §4 (mục septies) + KB. Kiểm bắt buộc: số phải nằm trong dải 23,37…25,71.
- [2026-09-28T01:08:23Z] 28/09 08:2x: VIỆC 2 XONG (merge WC main): rating8l_icb_pit_selfcheck FAIL hoá ra là BUG LATENT PRODUCTION — attach_icb_pit ném MergeError khi _eff=[s] vs icb_from=[us] (pandas 3.0.2: Series[s].fillna(Series[us]) GIỮ [s] im lặng ⇒ lô nào Release_Date null TOÀN BỘ là giết cả lần build lịch sử 8L). Ép cả 2 khoá về [us], A/B input thực tế BYTE-IDENTICAL. Thêm: T7 không còn chân control (fix ICB-PIT đã merge 7cdc08cc ⇒ canonical build lại = byte-identical với EXP, 5/5 bản CSV cùng md5 ea66aa95) ⇒ T7 tự phát hiện + bỏ 3 assertion delta + T7e (T7e nếu không bỏ sẽ PASS VÔ NGHĨA). 12 PASS/0 FAIL/1 SKIP × 4 TZ. VIỆC 1: dispatch Taylor_20260928_005930 (opus/high, 5400s) kiểm kê fail-open toàn cục 5 lớp L1-L5, CHỈ liệt kê không sửa, ranh giới cứng plan.py chỉ mô tả — chờ danh sách để user ký từng site. Job quant-skeptic_20260927_154549 đã đóng status=done (artifact verdict có thật, 0 tiến trình sống).
