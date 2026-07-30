---
kind: incident
date: 2026-07-21
topic: zalopay-run-bot-rc1-capit-seed-shared
title: >-
  2026-07-21 — ZaloPay run_bot rc=1: 5 lệnh MUA CAPIT mất + executor seed_shared crash
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-21 — ZaloPay run_bot rc=1: 5 lệnh MUA CAPIT mất + executor seed_shared crash

**Job**: `Winston_20260721_024320` (ops-autofix dispatch). **Vốn: AN TOÀN** (không lệnh treo).

**Triệu chứng**: `run_bot.sh --account ZaloPay` (plan 2026-07-21) exit rc=1 sau 0'.
`executor.py:122 seed_shared` → `KeyError: 'BUY-NCT-02'`.

**Chuỗi sự việc (từ log/journal/artifact thật)**:
- 09:15 exec: chỉ `SELL-VPB-01` PLACE→FILL→DONE 800@24.800 (khớp đủ, 20M/99%). 5 lệnh MUA CAPIT
  (NCT/PVT/SAB/SIP/VNM) bị `%ADV BLOCKED …→0cp` vì `data/golive_v23_status.json` khi đó là **bản
  cũ tối qua với `capit_adv_caps={}` rỗng** (`plan.py:199` báo "có: []").
- 09:29 artifact được regen **ĐÚNG** (có ZaloPay+SpaceX) — **SAU** khi bot chạy.
- Resume sau đó: `_load_state` khôi phục state cũ (parents chỉ `SELL-VPB-01`, vì 5 buy qty=0 bị drop
  lúc seed), nhưng `seed_shared` lặp `self.plan.orders` vẫn còn `BUY-NCT-02` → `state[parents][BUY-NCT-02]`
  KeyError → rc=1. **Mọi resume (kể cả 13:00 chiều) sẽ crash.**

**Bằng chứng regression**: `%ADV BLOCKED` chỉ có ở log 07-21 (10 dòng); 0 dòng suốt 07-10..07-20.

**2 root cause — CẢ 2 ở vùng CẤM Winston, KHÔNG tự sửa**:
1. **Plan↔golive timing**: `run_bot` 09:05 chạy TRƯỚC khi `golive_v23_status.json` regen 09:29 → đọc
   caps rỗng → chặn buys. (crontab/generation — Taylor/DollarBill).
2. **executor.py `seed_shared` KeyError** khi `plan.orders` chứa order KHÔNG có trong `state[parents]`
   (do %ADV-drop). Cần tolerate mismatch. (executor code — Wags/Taylor).

**Impact**: ZaloPay MẤT 5 lệnh mua CAPIT hôm nay; resume chiều không tự bù được (crash).

**Đã làm (Winston, trong ranh giới)**: chẩn đoán từ log/journal/state/artifact; xác nhận vốn an toàn;
escalate bus `finding` + `question` (`escalate-ZaloPay-CAPIT-buys-missed-2026-07-21`) + Telegram
Trading Daily. **KHÔNG** patch executor/plan/golive, **KHÔNG** xóa state (đúng mandate).

**Chờ quyết định trước 13:00 ICT**: (A) patch executor seed_shared; (B) đảm bảo artifact tươi trước
run_bot; (C) có re-seed state để mua bù 5 lệnh chiều nay (chạm executor/xóa state → cần user duyệt).

**Resolution (cùng ngày, trước 13:00 ICT — job `Mafee_20260721_030327`, verify: `trading_bot/
executor.py:143-152` đọc trực tiếp, code hiện tại KHỚP mô tả fix):** `Executor._load_state()`
nhánh resume giờ `st.setdefault("parents", {})` rồi lặp `self.plan.orders` để backfill parent
fresh-state (`filled=0, done=False, ...`) cho MỌI order thiếu trong state cũ — không động parent
đã tồn tại (giữ nguyên `filled`/`done`/`children`). Verify trước khi áp dụng: `reconcile_parents_
selfcheck.py` PASS, `dryrun_zalopay_0721.py` PASS trên pipeline thật (0 lệnh đặt), self-check 0
VND (thay đổi thuần additive). Resume 13:00 ICT đặt bù đủ 5 lệnh CAPIT (xác nhận qua Spyros audit
`EOD-mismatch-ZaloPay-07-21-audit-complete`: state cuối ngày `done=true` cả 6 parent, fill khớp
plan). Bus question `escalate-ZaloPay-CAPIT-buys-missed-2026-07-21` đóng `[RESOLVED-BY-ACTION]`
05:49:51Z (Wags). **Fix ĐÃ COMMIT** (qua auto-consolidate, không phải uncommitted như trạng thái
lúc phát hiện). Root cause #1 (plan↔golive timing race, `run_bot` 09:05 chạy trước artifact regen
09:29) — CHƯA có fix riêng, nhưng residual risk giờ THẤP vì fix #2 (backfill parent) làm resume an
toàn ngay cả khi race này tái diễn (order thiếu ở state cũ tự backfill thay vì crash).
