---
kind: incident
date: 2026-07-21
topic: eod-trading-report-cross-account-contamination
title: >-
  2026-07-21 — `eod_trading_report.sh` cross-account contamination: báo SAI mismatch cho CẢ SpaceX lẫn ZaloPay (lần 3 của cùng 1 bug class, KHÔNG được ghi bởi ai trước retro này)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-21 — `eod_trading_report.sh` cross-account contamination: báo SAI mismatch cho CẢ SpaceX lẫn ZaloPay (lần 3 của cùng 1 bug class, KHÔNG được ghi bởi ai trước retro này)

**Vốn: AN TOÀN** (bug ở tầng BÁO CÁO/đối soát, không phải đường đặt lệnh — 0 lệnh sai, 0 tiền
ảnh hưởng). **Chưa từng có bus event `error`/entry INCIDENTS.md nào cho việc này trước khi retro
hôm nay tự phát hiện qua rà bus finding/answer** (Mafee `eod-mismatch-fix-confirmed-2026-07-21`
12:19:06Z, `eod-report-account-filter-fix` 12:20:56Z; Spyros `eod-mismatch-ZaloPay-07-21-FALSE-
POSITIVE` 12:14:52Z, `eod-mismatch-SpaceX-07-21-FALSE-POSITIVE` 12:17:11Z).

**Triệu chứng**: `eod_trading_report.sh` (báo cáo EOD 15:00 ICT) báo mismatch broker_filled >
state_filled cho 5 mã CAPIT (NCT/PVT/SAB/SIP/VNM) ở CẢ HAI account cùng lúc — trông giống double-
buy nhưng không phải.

**Root cause (xác nhận bằng số khớp 100%)**: `eod_trading_report.sh` tính `real_filled_by_ticker`
bằng cách gộp TẤT CẢ record trong `dnse_raw_{plan_date}.jsonl` — file này CHUNG cho mọi account
trong ngày (SpaceX + ZaloPay), không lọc theo `account_no`. Hôm nay CẢ 2 account đều mua đúng 5 mã
CAPIT giống nhau → fill của account A bị cộng nhầm vào broker_filled của account B. Spyros verify:
`373(ZaloPay)+500(SpaceX)=873` khớp 100% số mismatch báo cho NCT; tương tự cho 4 mã còn lại.

**Fix (Mafee, cùng ngày, đã commit qua auto-consolidate 12:21:15Z, verify: `bin/eod_trading_
report.sh` dòng ~180-193 hiện tại có block `_target_account_no` resolve từ `secrets/trading_bot_
accounts.json` theo `label`, filter record `account_no != _target_account_no` trước khi tính
`real_filled_by_ticker`)**: 643 record SpaceX bị skip đúng khi chạy cho ZaloPay; mismatch 5 mã
biến mất; còn lại đúng 1 lệch thật (PVT +1 cổ phiếu, không liên quan cross-account). Spyros audit
độc lập CONFIRMED FALSE POSITIVE cho cả 2 account.

**3 câu hỏi bắt buộc:**

a. **TÁI DIỄN — LẦN THỨ 3 của CÙNG 1 bug class** "đọc file `dnse_raw_{date}.jsonl` (shared-by-
   date, không phải shared-by-account) mà không lọc `account_no`":
   - Lần 1: `2026-07-06 — Cross-account balance contamination` (dòng ~1114), file `daily_nav_
     snapshot.py`.
   - Lần 2: `RETRO — 2026-07-19` (dòng ~3026), file `reconcile_equity.py` + `verify_account_
     snapshot.py` — RETRO 07-19 đã tự gọi tên đây là "PATTERN, không phải lỗi đơn lẻ" và đề xuất
     "grep toàn repo cho mọi file đọc `dnse_raw_` " làm prevention.
   - Lần 3: hôm nay, file thứ 4 (`eod_trading_report.sh`) — **CHÍNH FILE NÀY đã được liệt kê
     trong kết quả grep của RETRO 07-19** ("6 file đọc `dnse_raw_*`") nhưng RETRO 07-19 KẾT LUẬN
     SAI rằng nó "an toàn by construction" cùng nhóm với `execution_quality_review.py`/
     `executor.py` — thực ra KHÔNG đúng: `execution_quality_review.py`/`executor.py` an toàn vì
     đọc field `accountNo` GẮN SẴN trên từng order record; `eod_trading_report.sh` lại tổng hợp
     qua 1 dict `real_filled_by_ticker` KHÔNG giữ `account_no` — khác cách xử lý, cùng file gốc.
     Grep đã chạy đúng, nhưng KHÔNG đủ sâu để phân biệt 2 cách dùng khác nhau của cùng 1 nguồn dữ
     liệu — chỉ liệt danh sách file đọc `dnse_raw_`, không audit TỪNG file có thực sự filter hay
     không.
b. **Fix HOÀN CHỈNH cho lần này** (verify bằng số khớp 100% + Spyros audit độc lập cả 2 account),
   nhưng **CÒN HỞ ở tầng cơ chế — giống hệt residual đã ghi 07-19, vẫn CHƯA làm**: (1) không có
   automated regression test/selfcheck 2-account-interleaved cho BẤT KỲ file nào trong 4 file đã
   biết đọc `dnse_raw_*` theo kiểu tổng hợp (không phải per-record accountNo); (2) `kb/coding_
   guidelines.md` §5/§6 (đề xuất từ RETRO 07-19: "thêm 1 dòng rule chung — file mới đọc `dnse_
   raw_{date}.jsonl` phải lọc theo account_no, không lấy bản ghi cuối cùng") **VẪN CHƯA ĐƯỢC
   VIẾT** — verify: `grep -n "dnse_raw_{date}\|shared-by-date" kb/coding_guidelines.md` → 0 kết
   quả. Đây CHÍNH LÀ prevention đã đề xuất 2 ngày trước, vẫn treo.
c. **PATTERN — đây là RETRO CALLOUT THỨ 2 của đúng pattern này** (lần 1 = RETRO 07-19). Theo
   bước 5/10 của quy trình retro: khi 1 pattern đã bị gọi tên ở 1 RETRO trước và VẪN tái diễn ở
   RETRO sau (dù có 1 ngày sạch — 07-20 — xen giữa), đây là tín hiệu prevention hiện tại CHƯA ĐỦ
   MẠNH, cần escalate thay vì lặp lại đúng câu khuyên cũ. Xem escalate bên dưới.

| # | Hạng mục | Phân loại | Nguồn gốc | Người ghi chép |
|---|---|---|---|---|
| 1 | `eod_trading_report.sh` cross-account contamination — file THỨ 4 cùng bug class, đã từng bị grep tới ở RETRO 07-19 nhưng đánh giá sai là "an toàn" | report-data-provenance | RETRO 07-19's grep-sweep chỉ kiểm tra "có đọc `dnse_raw_*` không", không kiểm tra "có giữ/lọc `account_no` qua bước tổng hợp không" — quy trình audit nông hơn cần thiết, không phải lỗi cá nhân | Mafee (fix + finding `eod-report-account-filter-fix`, 12:20:56Z) + Spyros (audit độc lập, `eod-mismatch-*-FALSE-POSITIVE`, 12:14-12:17Z); KHÔNG ai ghi vào `kb/INCIDENTS.md` trước retro hôm nay — retro tự bổ sung qua bus sweep |

**Prevention MẠNH HƠN — 2 đề xuất cũ (grep toàn repo, selfcheck 2-account) đã KHÔNG ĐỦ vì lần
này bug sống sót đúng NGAY SAU KHI grep đã chạy**, cần thêm 1 lớp không dựa vào con người tự nhớ
đọc kỹ:
1. **Viết rule vào `kb/coding_guidelines.md` NGAY** (không phải "nên làm" nữa — đã trễ 2 ngày kể
   từ khi đề xuất) — nội dung tối thiểu: "bất kỳ script đọc `dnse_raw_{date}.jsonl` để TỔNG HỢP
   (sum/count qua nhiều record) phải filter `account_no`/`accountNo` TRƯỚC khi gộp; nếu chỉ đọc
   field có sẵn trên từng record (không tổng hợp chéo) thì an toàn by construction — 2 trường hợp
   khác nhau, phải tự hỏi mình đang ở trường hợp nào".
2. **1 selfcheck DÙNG CHUNG cho cả 4 file** (`daily_nav_snapshot.py`, `reconcile_equity.py`,
   `verify_account_snapshot.py`, `eod_trading_report.sh`) — dựng 1 file `dnse_raw_test.jsonl` giả
   lập 2 account trộn lẫn, assert mỗi file chỉ tính đúng account được yêu cầu. Không cần 4
   selfcheck riêng — 1 file test data dùng chung, 4 lần gọi.
3. **Escalate bus question** (đúng bước 10) — xem bên dưới, vì đây là lần callout RETRO thứ 2 của
   đúng pattern, dù đã có prevention đề xuất từ lần 1.
