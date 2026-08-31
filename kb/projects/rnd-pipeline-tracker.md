# R&D pipeline tracker — mọi mục PAPER-ONLY trừ khi ghi rõ LIVE

> Tách ra khỏi `kb/current_ops.md` 2026-08-01 (token-cost review, user mandate) — đây là backlog
> nghiên cứu đang chạy, KHÔNG phải trạng thái an toàn/live cần biết mỗi phiên. Không injected vào
> `context_pack.md` — đọc file này khi cần theo dõi/cập nhật tiến độ R&D, hoặc khi checkpoint tới
> hạn cần xác nhận. Cập nhật lần cuối khi tách: 2026-08-01 (nội dung y nguyên từ current_ops.md).

Chi tiết đầy đủ từng mục: bus finding của Taylor + `kb/incidents/index.md`.

- **Insider-sell WATCH shadow (`insider_flags.py`)** (WATCH-only, chưa wire due-diligence, từ
  2026-07-29): cờ bán ròng nội bộ ≥1% CP lưu hành/90 ngày (chỉ `event_code IN ('DDIND','DDRP')`,
  TTL 90d). Scoping (job Taylor_20260729_015830 + Phụ lục A `_032713`) kết luận GO: overlap thấp
  với `anomaly_scan`/`forensic_flags` (7,1-21,7%), lift phần riêng 2,08× (z=5,74), ổn định IS/OOS;
  hai cờ bắn ở hai thời điểm khác nhau (insider sớm hơn ~2 tháng so với anomaly). **Review
  2026-08-29 (`insider-shadow-review-20260829`): NGỪNG wire (2/3 điều kiện FAIL), user CHỐT tiếp
  tục shadow** với ngưỡng NGỪNG mới đã điều chỉnh — tần suất thật ~7-9 mã/tháng (không phải ~3
  ước tính gốc) được CHẤP NHẬN; ngưỡng NGỪNG mới = **>9-10 mã/tháng**. **Review kế tiếp ~2026-09-29**
  (~1 tháng shadow sạch, trên nguồn snapshot). Migrate nguồn 2026-08-29 (job Taylor_20260829_160426,
  commit mike `7f13e11d` + root `3afec5bd`): đổi từ bảng live `tav2_bq.insider_transaction` (bị
  ghi đè `public_date`, look-ahead cho asof quá khứ) sang `tav2_mike.insider_transaction_snapshots`
  (vintage gần nhất <= asof, point-in-time đúng). `_get_insider_net_sell_flag()`/`_insider_scan()`
  trong `due_diligence.py` migrate cùng lượt — selfcheck `due_diligence_corp_flags_selfcheck.py`
  27/27 PASS (case E2 khớp tuyệt đối 2 bên), `insider_flags.py --selftest` PASS trên fixture rebuild
  từ vintage 2026-08-17 (fixture cũ dựng trên panel mutable đã trôi, không dùng lại). Điều kiện
  TIẾP TỤC (wire vào due-diligence report như dòng bằng chứng): shadow log sạch trên nguồn snapshot
  đến ~09-29 + qua quant-skeptic trước khi vào due-diligence chính thức (BẮT BUỘC, không đổi).
  **Tuyệt đối không hard-exclude ở bất kỳ giai đoạn nào** — 85% mã bị cờ không sập (§3.5 research
  file), chỉ là dòng bằng chứng WATCH cho người duyệt plan cân nhắc. Research đầy đủ:
  `mike/agents/Taylor/research/insider_transaction_scoping_20260729.md`.
- **EXTREME-regime gate — ĐÃ LIVE từ 2026-08-22** (SpaceX + ZaloPay, user sign-off):
  `extreme_regime_enabled=True` trong `overrides` của cả 2 account (`secrets/trading_bot_accounts.json`).
  Gate chain 6/6 PASS (quant-skeptic CONFIRMED high sau fix 2 TZ-fragile selfcheck, commit `70acee62`).
  Stress test `mike/agents/Taylor/stress_extreme_regime.py` 40/40 PASS (commit `08af2637`).
  `probe_linger_live_gate` vẫn True (paper-only, chưa go-live — feature riêng).
  History gate: paper `main` từ 07-01, checkpoint 07-28/08-04 (15/20 phiên, 0 marker EXTREME bắn),
  gate chain hoàn tất 08-22 sau 21/21 TZ-independent selfcheck pass.
- **Vol-scale buy chase-cap patch#3 — ĐÃ LIVE từ 2026-08-04** (`chase_cap_vol_scale_enabled=True`,
  k=2.0/ceil=0.04, commit `d4f667b` + mike `1396db13`, job `Taylor_20260804_124404`). Checkpoint
  07-28 kiểm lại: gate 1-3 PASS (80 lệnh BUY thật/13 phiên), gate 4 (real-fill vs proxy @50B)
  **RE-SCOPED chứ không PASS** — PaperBroker khớp đúng giá đặt nên không bao giờ sinh được bằng
  chứng fill thật; user chọn phương án A (chấp nhận rủi ro size-impact @50B chưa kiểm, NAV live
  hiện ~1,9% mức đó nên cùng bậc với paper đã test) — quant-skeptic CONFIRMED cao trước khi flip.
  Taylor chuẩn bị patch sẵn nhưng bị auto-mode classifier chặn khi tự áp ở phiên headless (đúng
  thiết kế); Mike áp trong phiên tương tác, 3 self-check chạy lại THẬT (không mô phỏng) đều PASS,
  commit ban đầu cũng bị classifier chặn — user cấp quyền tường minh mới qua được.
  **Mốc mở lại gate 4**: NAV live tiến gần 50 tỷ (theo dõi: gross lệnh/phiên vượt ~343tr).
- **Sector sweep: ĐÓNG 2026-08-30** — coverage đã đủ, không còn candidate mới đáng quét. Sweep
  thật đã đi tới **#20** (không phải #10 — dòng cũ lỗi thời), phủ 20 sector qua 20 file
  `agents/Taylor/*_valuation_framework.md`; verdict đồng nhất **LENS not BOOK** (Rule 3) qua mọi
  sector kể cả sector 2-mã (aviation HVN/SCS). Đối chiếu `ICB_Code` thật trong `ticker_prune`
  (2026-08-30, job `Taylor_20260830_034146`): các nhóm còn thiếu (bao bì giấy DHC/HHP n=2, lốp/phụ
  tùng ôtô CSM/DRC/VEA/PAC n=1-2 mỗi mã, nước sạch BWE n=1, media YEG n=1) đều rời rạc/không đủ N
  để thành 1 câu chuyện sector mạch lạc — không mở sweep #21. Utility điện (POW/NT2/PGV) ĐÃ nằm
  trong `energy_valuation_framework.md` (sub-universe "mature utility"), không phải gap.
- **Fill-timing khung giờ — ĐÃ LIVE từ 2026-08-22** (SpaceX + ZaloPay cả 2, user sign-off):
  `fill_timing_live_gate=False` + `fill_timing_hybrid_live_gate=False` trong `overrides` cả 2 account.
  Gate chain 5/5 PASS (quant-skeptic CONFIRMED high). Hybrid block schedule: `["11:00","11:15","13:00","13:15","13:30"]` ICT.
  Edge: +17.6bps BUY (t=12.0), +11.8bps SELL. `probe_linger_live_gate` vẫn True (paper-only).
  History: edge đo từ 07-09 (`Taylor_20260709_101602`), gate 5 PASS 08-22 sau ≥5 phiên paper BUY fill
  + 0 reject + 4/5 phiên hybrid + selfcheck TZ 21/21.
- **V2.5**: R&D-complete, DISABLED. Reminder 2026-07-07: Mike hỏi user go-ahead integration.
- **DC-book (ConvergePort) idle-cash waterfall** (paper `main` only, từ 07-06): thứ tự ưu
  tiên giải ngân **BAL/LAG (full trước) → DC book (double-confirm sector-lens BUY ∧ 8L rating≤2,
  capacity ~10-15B ex-DHG) → custom30V**; reverse-unwind khi BAL/LAG có deal lại. Backtest gốc:
  +5.0pp sleeve parking (~+3.5pp/năm SpaceX-now), nhưng DSR phần excess chỉ 0.775 (<0.95 ngưỡng
  an toàn) — bảo hiểm hợp lý, CHƯA phải alpha tin cậy cao → lý do bắt buộc paper trước. Trong EOD
  daily report. Review = EVENT-ANCHORED (khi chu kỳ reverse-unwind đầu tiên hoàn tất + settle 4-6
  tuần), sàn ~2 tháng, trần ~2026-10-06 (trượt theo nếu LAG refill trượt lịch).
  ✅ **4 fix đã ÁP DỤNG từ 2026-07-20** (`SLEEVE_VERSION="v2"`, job `Taylor_20260720_091731`) —
  đoạn "bug trigger nhị phân, sửa tại mốc review" ở trên đã LỖI THỜI, giữ lại làm lịch sử số liệu
  cũ: (1) trigger continuous-residual — xong; (2) rebalance cadence q2m5 — xong; (3) cap gộp
  0,15/tên DC↔custom30V — xong; (4) liquidity floor 3B thay hard-exclude DHG — xong. Thêm v2.1
  (job `Taylor_20260825_170138`): PER_NAME_CAP siết riêng 10 mã capacity-limited
  (MBB/HDB/VCB/VCI/VND/HCM/PVT/HAH/CTR/DBC), còn lại giữ 0,20.
  📌 **08-31**: gate mở rộng từ NEUTRAL-only sang `state not in (NEUTRAL, BULL, EXBULL)` (job
  `Taylor_20260831_014244`, commit WorkingClaude `b9c585ab`) — cơ chế deploy/weight/trigger/cadence
  KHÔNG đổi, `SLEEVE_VERSION` vẫn "v2", chỉ mở phạm vi state được ghi lại để paper bắt đầu tích
  luỹ bằng chứng BULL tự nhiên (27 phiên lịch sử trước đó toàn NEUTRAL). Selfcheck +11 test group F
  (78/78 pass). Đọc số liệu mới nhất từ `dc_book_waterfall_paper_nav.csv`, không dùng số IS/OOS cũ
  trong đoạn trên (đo trên trigger nhị phân đã lỗi thời).

## Checkpoint quá hạn — cập nhật 2026-08-22
- **EXTREME-regime gate: ĐÃ LIVE 2026-08-22** (xem mục trên) — đóng.
- **Fill-timing: ĐÃ LIVE 2026-08-22** (xem mục trên) — đóng.
- Vol-scale chase-cap patch#3: **ĐÃ LIVE 2026-08-04** — đóng.
