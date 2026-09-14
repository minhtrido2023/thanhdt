# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## ✅ CHIỀU T2 14/09 — LANDING XONG 15:30 ICT (6 commit + 1 finding)
1. loan-package v2 (WC 99fd8f6d): SpaceX resolve theo account_id. Selfcheck 44/44.
2. remove v23 (WC e802c08c, mike 06913f1c+652f5bd0): archive bot_prepare_plan/capit_exit_floor.
   Sweep 48 file: 47/48 rc=0, 1 FAIL có sẵn tái hiện y hệt (không do patch).
3. fee gate 0,097% (WC 90053064, mike 3484a8af khoá đồng bộ): plan_funding_gate 103/0,
   plan_cash_commitment 65/0, sync-lock 3/3.
4. ATC post-close (executor.py) — KHÔNG có commit mới: nội dung ĐÃ CÓ SẴN trong auto-backup
   003c5717 (00:03 ICT 14/09), TRƯỚC KHI user duyệt task này chiều nay. Nguyên nhân: Taylor job
   091014 test/apply patch trực tiếp trên working tree thật (không qua worktree riêng) rồi không
   revert; cron auto-backup quét vào. Đã xác minh: đúng bản v2 arch-APPROVE (plan_date+is_holiday
   gate, await_atc, ATC_POSTCLOSE_ERROR wrapper), selfcheck 46/46 PASS, sweep 22 file executor-dep
   rc=0. Bus finding "aria-K-landing-2026-09-14". CẢNH BÁO QUY TRÌNH: nhắc Taylor không test/apply
   patch trên working tree thật ngoài worktree riêng.
5. backfill_vhc_0710.py: VẪN dry-run, CHƯA --apply (đúng khuyến nghị — verify_account_snapshot sẽ
   rc 0→1 nếu apply, cần việc nhỏ khác trước).
Dispatch Wags_20260914_082709 (bg): quét 28 file dirname-x3 → wc_paths (việc treo cũ, không khẩn).

## Retro 09-13 đóng (c74dfbee). Sự cố #2 (loan_package fallback 1258) + #3 (ATC post-close) NAY ĐÃ
LAND — đóng cả 2 mục "CÒN HỞ/chưa land" trong retro đó.
## Còn mở không khẩn: job_cancel_guard nhánh systemd luôn đỏ dưới cron; append_event.sh JSON
isolation (pattern đã biết, không escalate).
## Sát ngưỡng OKF: kb/coding_guidelines.md ~40KB — §-mới PHẢI tách _ext.md.

- [2026-09-14T09:59:16Z] 14/09: FiinXMCP connect thành công (user tự OAuth), test + harvest xong. Kéo CAR/CASA/NIM/NPL(3-5)/LLR cho 9 bank x 8 năm (2018-2025), lưu data/fiinprox_bank_ratios_20260914.csv + registry kb/data_registry/fundamentals/fiinprox_bank_ratios.md (commit f121ab66). Cross-check vs audit cũ 26/08: 3/6 mã khớp sát (VCB/ACB/TCB), 2 lệch nhẹ (BID/HDB, có thể vintage FY2025 vs Q2/26) -> nguồn đáng tin. STB NPL 2025=6,62% bất thường (không nắm giữ). Việc CÒN MỞ trước hạn trial 28/09/2026: (1) đối chiếu công thức CASA FiinPro với bank_casa_ldr.md (OCR BCTC gốc, cùng kỳ Q2/2026) - chưa làm, field casa_ratio FiinPro chưa rõ khớp strict/narrow/pressdef nào; (2) quyết định mua subscription hay để trial hết hạn - khuyến nghị vẫn là KHÔNG mua ở AUM hiện tại, chỉ harvest tối đa trong 14 ngày.
- [2026-09-14T10:03:38Z] 14/09 (tiếp): đối chiếu công thức CASA FiinPro xong (commit 13677073). Kết luận: casa_ratio FiinPro = casa_narrow_pct (chỉ dòng KHÔNG kỳ hạn/tổng), KHÔNG phải strict (cộng cả tiết kiệm không kỳ hạn) - khớp OCR 12/13 mã tới 3-4 số lẻ tại đúng kỳ Q2/2026. registry fiinprox_bank_ratios.md nâng CASA lên DERIVED, NPL/CAR/NIM/LLR vẫn UNVERIFIED. Việc còn mở: quyết định mua/không mua subscription (khuyến nghị: KHÔNG mua ở AUM hiện tại, chỉ harvest thêm nếu cần trước hạn trial 28/09).
- [2026-09-14T10:14:51Z] 14/09 17:3x: user yêu cầu dùng FiinPro-X trial lấp lỗ hổng dữ liệu. Kiểm kê 21 gap + dò thật độ sâu FiinPro-X xong, kế hoạch 5 pha ghi kb/projects/fiinprox-trial-harvest-plan-20260914.md. ĐỦ: bank NPL/NIM quý từ 2010, khối ngoại ngày từ 2009 + tách khớp/thỏa thuận+tự doanh từ 2014, CPI thật tháng từ 2011, M2/tín dụng tháng từ 2012, USD/VND ngày từ 2012. MỘT PHẦN: OShares PIT từ 2013. KHÔNG THẤY: SBV refi, lợi suất TPCP; LS huy động chỉ 12 tháng. Chờ user duyệt bắt đầu P1 (vĩ mô nhỏ). MCP chỉ gọi được trong phiên Mike tương tác.
- [2026-09-14T10:26:06Z] 14/09 17:3x: P1 FiinPro CPI xong (commit 917dce9f): data/fiinprox_cpi_monthly_20260914.csv DERIVED; plan có mục 2b chống limit. FiinXMCP CẦN USER RECONNECT (phiên restart mất auth) — sau đó làm tiếp P1: money_credit YoY 2012-2026, exchange_rate USD central, GDP danh nghĩa quý.
- [2026-09-14T10:39:44Z] 14/09 17:5x: P1 FiinPro gần xong (0fc6feab): CPI + tín dụng/M2 + GDP danh nghĩa quý đã lưu + registry. Tỷ giá HOÃN (execute_api lỗi hết đĩa sandbox 3 lần; get_economy chỉ ~2 tháng/lệnh) — thử lại 15/09 1 lệnh/năm, lỗi thì bỏ. Tiếp theo P2 ngân hàng quý 2010→2026Q2.
- [2026-09-14T10:52:55Z] 14/09 18:2x: P2 FiinPro XONG (6489d5c9): 27 NH × quý 2010Q1→2026Q2, coverage khớp OCR 8/9, NPL +1-2% tương đối (mẫu số). Còn: P1 tỷ giá retry 15/09; P3 khối ngoại/value_by_investor; P4 OShares PIT; P5 TPDN. Kỹ thuật: execute_api in CSV nén, lô ≤5 mã (sandbox hay hết đĩa).
- [2026-09-14T11:03:04Z] 14/09 18:1x: P3 FiinPro đang CHỜ sandbox execute_api hết đĩa (4 lần). Phạm vi: fb/fs/fn VNINDEX+HNX 2009-06→2018-08 + value_by_investor ròng 5 nhóm VNINDEX 2014→nay, in CSV nén theo năm. Direct tool quá nặng (~70 tok/dòng). Đã đặt wakeup retry.
- [2026-09-14T12:05:17Z] 14/09 19:1x: P3 đang chạy — VNINDEX investor flow raw 2014-2020 đã commit (data/fiinprox_investor_flow_raw/vnindex_YYYY.txt). Còn 2021-2026, rồi fb/fs VNINDEX+HNX 2009-06→2018-08, rồi build CSV + registry + đối chiếu VNDirect.
- [2026-09-14T12:11:53Z] 14/09 19:4x: P3(b) value_by_investor VNINDEX 2014→2026-09-14 raw ĐỦ, committed. Đang P3(a) fb/fs VNINDEX+HNX 2009-06→2018-08. Sau đó build CSV + registry + đối chiếu VNDirect.
- [2026-09-14T12:16:37Z] 14/09 20:0x: DỪNG P3 hôm nay (sandbox FiinX lỗi đĩa 4 lần liên tiếp). P3(b) investor flow VNINDEX 2014→2026-09 XONG (352b16b7, khớp VNDirect median 1,9 tỷ). P3(a) còn thiếu: VNINDEX fb/fs 2013 + HNX fn 2013→2018-08 — làm 15/09 cùng retry tỷ giá. Sau đó P4 OShares PIT, P5 TPDN.
- [2026-09-14T14:54:51Z] 14/09 22:0x: P3 FiinPro ĐÓNG. foreign_flow_index_daily 2.313 phiên 2009-06→2018-08 + investor_flow_daily 2014→2026-09. Còn: P1 tỷ giá retry; P4 OShares PIT; P5 TPDN/lãi suất NH. Trial hết 28/09.
- [2026-09-14T15:13:05Z] 14/09 22:1x: soát cảnh báo OShares BCTC vs AIS (corp_action_daily 14/09, 49 mã). Phát hiện BUG thật KHP (không nắm giữ): BCTC Q2 (release 07-20) ĐÃ gồm cổ tức CP 3% (ex 07-30, niêm yết 09-14) = 60.376.746+1.809.772=62.186.518, nhánh FIN_FALLBACK lại cộng event lần nữa -> phục vụ 63.996.290 (+2,9% đếm 2 lần). TCB (nắm giữ) AIS_UNCERTIFIED từ 08-27, value=None, nhưng BCTC 4 quý = 7.086.240.414 khớp tuyệt đối AIS 08-05 -> số đúng, chỉ bị fail-closed. VRE lệch -2,43% = CP quỹ (case đã đóng 09-07). VIB nhảy 9,5% = thưởng CP ex 09-10 khớp tuyệt đối, event về muộn -> tự hết. Chờ user quyết có giao Taylor vá KHP double-count không.
- [2026-09-14T15:21:38Z] 14/09 22:4x: P4 FiinPro DỪNG — chạm 429 hourly request limit sau 70/655 mã (get_freefloat, lô 20). Raw ở data/fiinprox_oshares_raw/b000-b050.txt, tickers.txt. Lô tiếp theo bắt đầu index 70 (DHT...). 15/09: ≤4 lô/giờ, lô 20 mã. Sandbox lỗi đĩa ~50%.
- [2026-09-14T15:35:56Z] 14/09 22:4x: DỰNG harvest FiinPro TỰ ĐỘNG — cron 7,27,47 * * * * bin/fiinprox_harvest_tick.sh (queue state/fiinprox_harvest/queue.json: 30 lô OShares + 15 năm FX). Headless claude -p gọi được FiinXMCP (đính chính ghi chú cũ). Khi được báo 'xong nhóm' → Mike dựng CSV/đối chiếu corporate_action/registry. GỠ cron sau 28/09.
- [2026-09-14T16:03:11Z] 14/09 23:0x: OShares double-count fix (branch fix/oshares-finfallback-double-count @ eded0afe, worktree /home/trido/thanhdt-wt-oshares-finfb-dblcount). arch-reviewer NEEDS_CHANGES high: logic đúng, nhưng K1/K1b/K2/K3 selfcheck đọc BQ sống (đã đỏ 87/89 vì AIS KHP mới 62.215.739 về tối nay — xác nhận fix đúng hướng) + corp_action_daily.py:1485 chạy selfcheck này làm cổng publish ⇒ land như vậy = sáng mai KHÔNG PUBLISH. Dispatch Taylor vòng 2 (fixture đóng băng + test nhánh). LAND SAU run 07:30 ICT 15/09, không gần giờ đó. Kỳ vọng lượt đầu sau land: KHP gắn MODEL_REBASE (đúng), VIB publish bất kể. BẪY verify: source wc_env.sh đưa về tree thật.
- [2026-09-14T16:38:10Z] 14/09 23:3x: OShares fix arch-reviewer vòng 3 APPROVED high (branch fix/oshares-finfallback-double-count = eded0afe+bc86963e, worktree /home/trido/thanhdt-wt-oshares-finfb-dblcount, CHƯA merge). Mike tự verify: live 102/102, pit 49/49, gate_driver_wt ok rc=0. CHỜ USER DUYỆT LAND. Landing steps: (1) merge vào WorkingClaude SAU run corp_action_daily 07:30 ICT 15/09; (2) ngay sau merge chạy env -u TZ oshares_live --selfcheck 102/102 + oshares_pit 49/49 từ tree thật, grep KHP_C xác nhận file đã merge; (3) lượt corp_action_daily kế: KHP MODEL_REBASE 63.996.290→62.215.739 (đúng), VIB publish 3.727.386.252, snapshot status OK usable=true; (4) promote ticker_financial_oshares.md.proposed; (5) bus finding đóng + job riêng đóng băng ~20 check cũ đọc BQ sống + sửa dòng usage --no-subprocess vô tác dụng.
- [2026-09-14T16:45:14Z] 14/09 23:4x: USER DUYỆT land OShares fix sáng 15/09 + đóng băng ~20 test cũ. (1) CronCreate one-shot b31089aa 08:04 ICT 15/09 (01:04 UTC) làm land theo 8 bước — SESSION-ONLY, phiên restart là MẤT → sáng 15/09 nếu chưa thấy post land thì làm tay theo landing steps ở dòng memory trước. (2) Dispatch Taylor đóng băng check đọc BQ sống, branch test/oshares-freeze-live-selfchecks từ bc86963e, worktree riêng, không đổi số kỳ vọng; cần arch-review riêng, land SAU bản vá double-count.
