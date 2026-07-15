# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn lần cuối 2026-07-13 00:36 ICT (job Mike_20260712_173001, daily retro 2026-07-12).
> Lịch sử đầy đủ: kb/INCIDENTS.md (RETRO 2026-07-12, 5 sự cố, Wags-verified) + git log.

## Đang chờ / treo — QUAN TRỌNG NHẤT
- **Plan ZaloPay 2026-07-13 (2 lệnh) cần user DUYỆT TAY trước preflight 08:45 ICT** —
  `data/trade_plans/plan_ZaloPay_2026-07-13.json` tồn tại đúng ngày, nhưng
  `approved_by=None`. Plan SpaceX cùng ngày là HOLD (0 lệnh, `approved_by=auto`) — không
  cần duyệt.
- **3 mục chờ xác nhận qua cron thật thứ Hai 07-13 18:30/19:00 ICT** (đã ghi chi tiết ở
  `kb/current_ops.md`, không lặp lại đây): (1) `vnindex_5state_dt5g_live` có dòng
  06-24→07-13 NEUTRAL(3); (2) `custom30v_8l` writer đã hồi sinh (lastModified qua
  06-18); (3) freshness-check 8 bảng 19:00 chạy thật lần đầu, kỳ vọng 2 WARN hợp lệ
  (lag_edge_health mtime probe + fin-breadth probe), 0 false-block.
- **M5 còn nợ** (từ audit cron-order 07-12): `executor.py` đọc `ticker_prune.parquet`
  monolith chết từ 06-26, ảnh hưởng 2 paper trial evidence (EXTREME-regime,
  chase-cap) — chưa dispatch Taylor xem, không khẩn (chỉ ảnh hưởng paper, không live).
- Bus question `retro-pattern-recurring-dataprovenance-2` (2026-07-10, đề xuất tổng quát
  hoá freshness-check cho MỌI cặp producer→consumer nội bộ) — vẫn CHƯA có answer, 3 ngày
  rồi, ưu tiên thấp.

## RETRO 2026-07-12 — tóm tắt (chi tiết đầy đủ: kb/INCIDENTS.md)
5 sự cố, tất cả bắt được TRƯỚC khi gây hại thật, tất cả fix+verify (quant-skeptic
CONFIRMED) trong ngày, bản RETRO đã qua Wags xác minh độc lập (tìm 2 gap, đã sửa):
1. `golive_recommend_v23.py` hardcode w_LAG=65% lệch spec pinned (a776a9a) — money-path,
   phát hiện TÌNH CỜ (không phải audit).
2. C1 CRITICAL: `publish_gated_state.py` đọc DT5G qua cache T-1 thay vì live (4995262).
3. H2 HIGH: `shares_outstanding_live` freshness check miscalibrated (6459b6d).
4. R1 CRITICAL + F1 MEDIUM: LAG live-candidate mù event <30 phiên (f7463e3) + freshness
   ticker_financial bị early-filer reset đồng hồ (1b2fd13).
5. `lag_edge_health.csv`: 2 tiền đề chẩn đoán sai liên tiếp, KHÔNG có bug thật.

**Pattern xuyên suốt:** `data-registry-accuracy` là nguồn incident chính 2 ngày liên tiếp
(07-11 SIGNAL_V11 base-leak → 07-12 có 3 case: C1/H2/R1+F1) — CHƯA đủ điều kiện escalate
(cần cùng nhãn tường minh ở 2 RETRO liên tiếp, đây là lần đầu gọi tên). Nếu audit tiếp theo
vẫn tìm thêm 1 case nhóm này → escalate thật ở RETRO ngày đó. Pattern phụ mới:
`execution-money-path` (sự cố 1) lộ ra ngoài phạm vi mọi audit hôm nay — gợi ý audit theo
yêu cầu cụ thể có góc mù, không thay được 1 lần rà toàn diện.

## Trạng thái R&D/production đã đóng hôm nay (không cần hỏi lại)
- Momentum-deals: ĐÃ ĐÓNG + THỰC THI PRODUCTION (đóng MOM_N/MOM_S trong TIER_BAL, commit
  4fbd492+9df396d). Baseline R3 chính thức mới: **27.84%/1.84/-18.2%/1.53**.
- V2.5 leverage: NO-GO, giữ DISABLED (đóng luôn reminder cũ 2026-07-07 "go-ahead
  integration" — verdict cuối cùng = không tích hợp).
- Q-sleeve (rổ nhỏ chất lượng cao): NO-GO cả 2 trục, đóng.
- fa_ratings rebuild + cron BQ-write-identity: hoàn tất, publish thật thành công.
- cron_registry.md tạo mới (commit a78123e) + coding_guidelines §11.

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Same-day data: bắt buộc DNSE API, cấm BigQuery cho tới sau 23:45 ICT sync
  (coding_guidelines.md §6).
- Trước khi báo 1 vấn đề "còn mở/chưa xử lý" → verify ARTIFACT thật, đừng chỉ tin trạng
  thái job/bus question chưa có answer.
- Trước khi commit 1 bản RETRO/tổng hợp quan trọng → dispatch Wags xác minh độc lập trước
  (đã làm đúng hôm nay, tìm ra 2 gap thật, đáng làm tiếp các lần sau).
- `daily_retro.sh` chạy 00:30 ICT, review "hôm qua" qua `date -d yesterday`.
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp —
  dispatch DollarBill để SINH plan mới thì được; RENAME/XOÁ file plan đã tồn tại thì KHÔNG.

## Pattern A (job nền chết vì lifecycle) — ĐÃ ĐÓNG từ 07-09, không tái phát.

- [2026-07-13T01:48:52Z] Dang cho job Winston_20260713_014816 (fix: send_plan_report second-chance re-check ~23:00 ICT, idempotent, chong tai dien incident 07-13 plan-khong-duoc-gui-lai-de-duyet). Plan ZaloPay 07-13 da duoc user duyet + ghi vao file (approved_by=user 08:45 ICT). Con no rieng: code-gate approval trong bot_execute.py (vung cam, can user sign-off rieng, KHONG lam hom nay).
- [2026-07-13T02:12:26Z] Da cai cron second-chance 23:00 (send_plan_report --second-chance, verify OK). Dang cho Taylor_20260713_021202 (thiet ke code-gate approval trong bot_execute.py) - CAN THAN vi co the phat hien rui ro chan ca giao dich thuong le SpaceX neu requires_user_approval=true la default cho moi plan. Neu Taylor bao cao rui ro nay thi PHAI dung lai hoi user cach xu ly, KHONG tu quyet.
- [2026-07-13T02:30:22Z] Code-gate approval bot_execute.py XONG + CONFIRMED (commit 27e1282). Dang vá 1 lo hong nho residual (approved_by string 'None'/'null' khong duoc chuan hoa) - job Taylor_20260713_023002. Sau khi xong: bao cao tong ket ca 2 viec hom nay (second-chance cron + code-gate) cho user.
- [2026-07-13T04:49:55Z] User phat hien bao cao TUAN bi bo sot (khong co cron tu dong cho weekly/monthly, phu thuoc Mike tu nho). Da dispatch 2 viec song song: Taylor_20260713_044913 (soan bao cao tuan 07-06->07-10 cho ca SpaceX+ZaloPay, dung verify pipeline that) va Winston_20260713_044945 (them check WARN vao ops_health_check.sh de tu canh bao khi bao cao tuan/thang qua han - chong tai dien). Sau khi Taylor xong: Mike PHAI TU DOC LAI bao cao truoc khi gui cho user/Discord, khong tu dong post.
- [2026-07-13T10:07:46Z] User lo lang du lieu 8L co cap nhat day du khong (mua BCTC Q2 dang bat dau). Dispatch Winston_20260713_100733 audit toan dien: fa_ratings_8l/fa_ratings freshness that (query BQ live), dong bo voi ticker_financial, cadence weekly cron co du cho mua BCTC cao diem khong, downstream custom30_8l/pt_8l_daily doc dung bang khong, data_registry.md trap check. Cho ket qua.
- [2026-07-13T10:32:35Z] Dang cho Winston_20260713_103213 (fix cache sync 8L + tang tan suat mua BCTC + sua data_registry.md doc). Audit truoc (Winston_20260713_100733) xac nhan du lieu 8L hom nay DAY DU - khong co gap thuc te, chi co gap ky thuat cache (khong anh huong tien that) + can theo doi cron thu Bay 07-18 lan dau chay tu dong that.
- [2026-07-13T14:37:03Z] Phat hien LON: 27 script doc file monolith ticker_prune.parquet chet tu 06-26 (khong chi executor.py da biet). Dispatch song song Winston_20260713_143546 (fix duong dan 27 file) + Taylor_20260713_143629 (danh gia tac dong research, UU TIEN: chase-cap review du kien MAI 07-14 co bi anh huong khong). CAN theo doi ky, day co the anh huong toi ket luan cua nhieu sector-sweep/backtest da tuong la dong.
- [2026-07-14T10:49:38Z] User duyet (a) them dong tan suat lich su P(NEUTRAL->BEAR) vao dna_report/eod_trading_report (nhan ro base-rate, khong phai du bao) va (b) sua 2 loi: DT4-gate stale date tag + ZaloPay EOD bao loi gia khi Mike chu dong khong lap plan. Dispatch Taylor_20260714_104928 xu ly ca 2 gop chung (tranh xung dot file).
- [2026-07-14T16:08:15Z] User chi dao quy tac VAN HANH VINH VIEN moi: tu ngay 15 thang dau moi quy (1/4/7/10) den het thang, quet lai rating 8L MOI NGAY (tru T7/CN/le). Cua so dau tien 15-31/7/2026 BAT DAU NGAY MAI. Dispatch Winston_20260714_160739 thiet ke cron 1-dong tu-kiem-tra dieu kien ngay-thang + xoa cron tam thoi Thu Ba cu (da duoc thay the) + cap nhat cron_registry.md thanh quy tac vinh vien. Can xong + verify TRUOC KHI het ngay hom nay vi cua so bat dau mai.
- [2026-07-14T17:44:42Z] KHAN: ticker_financial co the bi ghi de/hong - MAX(time) lui tu 07-08 (xac nhan hom qua) ve 05-04 (query that Mike vua lam). Dispatch Winston_20260714_174411 dieu tra khan. Neu that su hong, can quyet dinh truoc 20:00 ICT toi nay (lan chay that dau tien cron quy moi se doc du lieu nay).
- [2026-07-15T05:43:01Z] User duyet doi gio 3 cron co phan thi truong (eod_trading_report 15:00->19:10, pt_8l_daily 17:45->19:20, telegram_run_daily 18:00->19:35) ra sau moc DT5G state that su san sang (19:00 bq_freshness_check), khong chi sau 17h. Dispatch Winston_20260715_054242 (lan 2, lan 1 bi loi backtick trong prompt nen da kill + dispatch lai sach). Cho trinh bay diff truoc khi cai.
