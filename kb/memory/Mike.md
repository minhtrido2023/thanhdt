# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 09/11 → 10/11)
## Đang chờ user
- Retro 09/11 ghi xong (kb/incidents/retro/retro-2026-11-09.md). Escalation đang mở: retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm (khuyến nghị A: checker dùng lịch phiên) — KHÔNG mở trùng.
- Cần kiểm: báo cáo tuần 02–06/11 đã gửi ĐỦ kênh chưa (`report_delivery_gate.py`; state/report_delivery.json không thấy key 2026-11-02) + file ZaloPay. Memory cũ "BQ Price chờ OK UPDATE" đã lỗi thời (Wags làm tươi cache G2).
- Fix chưa làm: (i) close_bus_question yêu cầu --verified-by theo measured_by; (ii) wakeup gate kiểm hành động thật (MISS 3 ngày liền, 25% hôm 09/11); (iii) dedupe APPROVAL_GATE_BLOCK theo (account, plan_date) (100 event/5h); (iv) anomaly-flags-stale + chuỗi park vòng CN lỗi lịch ngày-lịch vs ngày-phiên.
- LAG luật 5 (user 09/11): mua LAG cần DD + giá<=tâm; thoát = 1 tháng dương (known_date,n>=30) → user xét candidate quý; mốc 15/12; bin/lag_gate_exit_check.py CHƯA có cron (hỏi user). Plan 10/11 = 0 lệnh HOLD.
- DD: DGC không giảm (user), DCM r7 không làm, CK holding chốt C (base 0% + nhãn nhạy). Sổ dd_price_zones 73 entry CHƯA commit (backup cron gom). GVR/HTN/MZG/YEG/PHP chưa DD.
- Chờ user OK: 2 cron work-tree; thẻ tần suất Livermore; macro TE Làn 2; pnj-bctc-q3-review-trigger; approve_plan_simple.sh thiếu --dry-run. Lệnh đối ứng cùng mã: chưa guard code.
## Mốc
DT CRISIS ~11/10 sớm nhất; nav-loss-brake 11-09; commodity 11-25; BĐS 11-26; Livermore H20 03/12; LAG 12-15; audit đo lường ~12-27.

- [2026-11-10T03:42:43Z] 10/11: DD pha loãng — Taylor_20261110_034232 làm HHS_r4+SCL_r4 (dd_dilution_update_20261110); xong → fundamental-skeptic → nhập entry mới vào kb/dd_price_zones.json
- [2026-11-10T04:03:02Z] 10/11: skeptic HHS_r4+SCL_r4 CONFIRMED(medium) không đổi nhãn; vòng 2 sửa Taylor_20261110_040253 → xong thì nhập 2 entry vào kb/dd_price_zones.json (từ ledger_proposed_entries.json, SCL ex-basis, HHS có ex_basis_pending/field mới cần kiểm schema)
- [2026-11-10T04:07:39Z] 10/11: ĐÃ nhập SCL rev5 (cơ sở EX) + HHS rev4 (cum, ex_basis_pending) vào kb/dd_price_zones.json (75 entry, selfcheck 0 lỗi). dd_price_zone_watch_selfcheck.py KeyError center_alt là LỖI CÓ SẴN (đã có trước thay đổi). Việc mở: HHS chuyển cơ sở ex khi có GDKHQ quyền mua; sau 08/12 kiểm kết quả quyền SCL; Winston: BQ Close SCL chưa điều chỉnh lùi 09/11.
- [2026-11-10T05:30:36Z] 10/11 12:3x user: edge-health theo THÁNG cho BAL (âm⇒khoá mua, dương⇒mở, âm⇒khoá lại) + nghiên cứu gate vs mù. Taylor opus: IMPL job Taylor_20261110_053022 (worktree, commit trên nhánh, KHÔNG merge; sau: claim-reply → arch-reviewer opus → vá → merge main + doc kb/projects/bal-edge-monthly-gate-20261110.md); RESEARCH job Taylor_20261110_053025 (agents/Taylor/research/bal_edge_monthly_gate_20261110, sau: claim-reply → quant-skeptic → báo user, không wire). LAG giữ luật 09/11.
- [2026-11-10T06:12:26Z] 10/11 13:1x BAL edge gate: IMPL v1 commit d0e01e21e (wt-bal-edge-gate-20261110) arch-review NEEDS_CHANGES → Taylor vòng 2 job Taylor_20261110_061206 (MIN_N=1, stale LOCKED vẫn chặn, closed_months phiên thật, alert --update, flock). Sau: claim-reply → verify selfcheck → merge CHỈ KHI user OK cron 00:40 ICT (đã hỏi). RESEARCH job Taylor_20261110_053025 còn chạy → quant-skeptic → báo user. Trạng thái BAL hiện LOCKED (thang 2026-10 −4,91%).
