# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Retro 2026-09-09 — XONG (job Mike_20260909_173507)
File `kb/incidents/retro/retro-2026-09-09.md` (commit fcf63e01), Wags CONFIRMED. 3 sự cố, 2 pattern.
Pattern A đã QUYẾT (2026-09-10): `Wags/nav-price-xcheck-gate-can-quyet-dinh-user-2026-09-10` ĐÃ
ĐÓNG, user duyệt phương án C qua Discord — Taylor sửa `daily_nav_snapshot.py` tự quy đổi
qty/giá theo corp-action CONFIRMED khi chạy `--date` lịch sử + bật gate PRICE_XCHECK cho cả
trường hợp đó (commit `c30e0580`), rồi backfill lại NAV 09-09 bằng kết quả đã sửa. Đề xuất "so
giá×khối lượng" trong finding gốc SAI tiền đề (đã đính chính trong question trên) — không làm.

## Bus question đang mở, CHƯA fix (theo dõi tiếp)
1. `Mafee/nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-09` — status DIAGNOSED_NOT_FIXED lúc
   viết dòng này; đã có fix (commit `c30e0580`, xem Pattern A ở trên) — kiểm NAV 09-09 đã backfill
   xong chưa trước khi coi mục này đóng.
2. `Mike/bq-cache-manifest-not-updated-by-selfheal-2026-09-09` — self-heal `_drifted_years()`
   (commit 3ff20579) refresh bảng nhưng quên rewrite manifest.json → preflight fail giả, mọi
   dispatch BQ đang fallback network. Chưa sửa.
3. `Wags/wags-fix-not-confirmed: coord-2026-09-07` — doc drift cron vn_realestate_monthly_check.sh.
   Cửa sổ theo dõi: trước cron chạy lại ~10-06.
4. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C.

## Retro 2026-09-08 — XONG, backup silent-failure (lần 4, đã fix hoàn chỉnh) + BQ cache
ticker_prune lệch (sự cố gốc dẫn tới commit 3ff20579 ở trên) — xem file retro nếu cần chi tiết.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## CCS/8L accruals R&D — ĐÓNG HẲN 2026-09-06
Phase 0→0b→R3→Phase2-NARROW, tất cả NO-GO (lần thứ 3). Mở lại chỉ khi có dữ liệu ngoài mẫu 2014-2026.

## BAL/custom30V R&D — ĐÓNG HẲN 2026-09-09, 5 vòng đều NO-GO
BAL vòng 1-3 (attribution, adaptive-exit, gate NEUTRAL) + custom30V vòng 4-5 (selector, placebo
overweight-bank) — tất cả NO-GO, không wire gì. Input đầy đủ cho review VPI/BAL 09-16.
User chốt (decided_by=user): overweight bank trong custom30V (49,1%/67,5%/93,3%) là TÁC DỤNG PHỤ
của pool định nghĩa bằng thanh khoản, không phải chủ ý — giảm tỷ trọng bank là mục tiêu hợp lệ.
Placebo vòng 5 (P1/P2 tách nguồn +2,62pp) đang chạy, output tại
agents/Taylor/research/custom30v_placebo_20260910/.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

- [2026-09-09T18:04:00Z] VÒNG 5 placebo XONG (job Taylor_20260909_165335, done). KẾT LUẬN: (Y) THÊM TÊN RẺ chiếm ưu thế, (X) pha loãng ngành ÂM ở cấp rổ. Cấp NAV: TỔNG +2,621pp = ΔP1 +0,622 (23,7%) + ΔP2 +1,303 (49,7%) + tương tác +0,695 → luật chốt trước = HỖN HỢP (không đạt ngưỡng 60% để gán nhãn). Cấp rổ gross: ΔP1 −3,064pp (âm!), ΔP2 +5,731pp — ΔP2 là thành phần DUY NHẤT có CI95 loại trừ 0 [+0,05;+8,30], P(ΔP2>ΔP1)=0,996. ⇒ nguồn thật của +2,62pp là 132 tên đã qua cổng chất lượng chưa từng được chấm điểm định giá, KHÔNG phải ít ngân hàng hơn. Tỷ lệ phân rã KHÔNG đo chính xác được (%ΔP1 CI [−52%;+91%]) — đừng trích 23,7%/49,7% như số đã xác lập. PHÁT HIỆN QUAN TRỌNG NHẤT CHO CHÍNH SÁCH USER: ngân hàng CHÍNH LÀ nguồn thanh khoản — cắt 16pp trọng số bank tốn gần như KHÔNG GÌ về CAGR (+0,62pp, không phân biệt được với 0) nhưng LUÔN trả bằng ADV: giữ pool 60 ép đếm −23,8% ADV, nới pool −70,7%. Khác hẳn fincap (cắt trọng số cùng tập tên) = mất tiền thật −0,32..−0,84pp. Prior SAI đã ghi: thứ hạng yieldcombo TRONG nhóm tài chính CÓ thông tin (mode=random xoá sạch cả 2 hiệu ứng, 97,8% rơi vào số dư). Đề xuất luật cho vòng sau (CHƯA backtest, cần prereg MỚI): trần theo SỐ TÊN tài chính trong top-30 (k≈6), giữ pool 60, giữ yieldcombo chọn tên điểm cao nhất — 3 điều kiện: giữ thứ hạng, k chốt trước không quét, khai trước kỳ vọng ΔCAGR≈0 mục tiêu là hồ sơ tập trung ngành. Bài học harness (đề xuất thành luật coding_guidelines): script nghiên cứu ghim snapshot BQ phải GÁN CỨNG os.environ['BQ_LOCAL_CACHE'], KHÔNG dùng setdefault vì wc_env.sh luôn export trước → probe âm thầm đọc cache sống. Không wire gì.
- [2026-09-10T12:59:13Z] 2026-09-10 AMH review (user hỏi, topic 1547589883999158363): viết kb/projects/amh-adaptivity-review-20260910.md — edge_health SỐNG + wired (w_LAG gate đang kích hoạt 0.50; EXBULL-suppress live), ecology REFUTED, fitness/biodiversity chết path Windows. 8 gap, 7 hướng; ưu tiên #1 BAL edge-gate đối xứng LAG. CHƯA dispatch — chờ user chọn hướng.
- [2026-09-10T13:22:13Z] 2026-09-10 AMH: user DUYET ca 7 huong. XONG #7 (commit 30878a9b, fitness_matrix+biodiversity_test song lai), #5 (skill quant-research buoc 18 biodiversity gate, commit outer repo), #6 (kb/projects/amh-structural-break-protocol-20260910.md + kb/structural_break_watch.json, gop vao review quy Bobby 11-26; commit 5d9d4686). DANG CHAY 3 job Taylor opus/high: A=Taylor_20260910_131906 BAL edge-gate (DEADLINE 09-16, input cho review VPI/BAL), B=Taylor_20260910_131908 change-point+fitness matrix, C=Taylor_20260910_131910 market-efficiency gauge. Buoc ke tiep cua Mike: doc ket qua 3 job -> tong hop -> quyet co dispatch quant-skeptic khong. Wakeup turn PHAI bat dau bang jobs.sh claim-reply tung job.
