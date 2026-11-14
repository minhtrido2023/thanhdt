# Phân kỳ RSI + thu hẹp vai Livermore — NO-GO / ĐÓNG 2026-11-14 (user duyệt, `decided_by: user`)

**Verdict:** hướng **phân kỳ RSI** = **NO-GO** (0/48 trial). Vai Livermore **thu hẹp về 3 việc cơ học**, bỏ dự báo hướng VNINDEX H20 và "đọc DT5G sớm hơn". Κ **không chạy** (user bỏ). Quant-skeptic không chạy (user không yêu cầu).

## Số đo (job `Taylor_20261114_063556`, PAPER-ONLY)
- PREREG `agents/Taylor/research/livermore_divergence_20261114/PREREG.md` md5 **cd943e11b9fbc923221d02812989d007** (chốt trước khi engine chạy); REPORT.md md5 850f0becb063c7f19c4a65670768aaae.
- G1 trượt: **0/48** trial có BSS OOS > 0 với CI loại 0; 0/48 qua BH-FDR; **DSR lớn nhất 0,005**; **PBO 0,74**.
- U2 (cổ phiếu): **0/24** có exR dương CI loại 0; **0/24** dương sau phí (exR OOS lớn nhất +0,36pp vs chi phí vòng 0,594pp).
- U1 (VNINDEX) **không đủ N**: 0–20 sự kiện/loại trong 13 năm, MDE hit 37–88pp.
- H2: R² call Livermore ~ (mom20, mom60, rp250) = 0,20–0,29 (LOO 0,09–0,15) < 0,5 ⇒ G0/H2 không kích hoạt.
- Artifact: `agents/Taylor/research/livermore_divergence_20261114/` (REPORT.md, results.csv, summary.json, selfcheck.json).
- Số DT-lead post-hoc (7/13, 6/11) **KHÔNG phải bằng chứng** (chọn sau khi biết kết quả).

## Quyết định user 14/11/2026
1. Đóng phân kỳ RSI vào NO-GO và thu hẹp vai Livermore. 2. Bỏ đo κ (60 lượt). 3. Cổng giải thể 12 lần đọc diễn giải là cổng **GIẾT** (chỉ phát hiện edge ≥ ~25pp; không chứng minh được edge nhỏ hơn).

## Vai mới (DISPLAY-ONLY)
(a) trợ lý thực thi lệnh vào deal discretionary — ENTRY_VERDICT cơ học (zone_lo, zone_hi, max_px, wait_sessions=5, confirm_close, confirm_vol_mult, cancel_px; plan §5); (b) khối "Kỹ thuật" weekly/monthly mô tả vùng/khối lượng, số do script tính, KHÔNG dự báo hướng; (c) INVALIDATION/kỷ luật điểm hỏng mỗi deal. Đọc theo MÃ (FPT/NNC/VGS…) tiếp tục, chấm riêng.
**Bỏ:** dự báo hướng VNINDEX H20; "đọc DT5G sớm hơn". Entry sống đang chờ chấm (LVR-2026-10-21 due 18/11; LVR-STK FPT/NNC 03/12; VGS/NNC 10/12) giữ nguyên, append-only.

## Cơ chế (nhánh `feat/livermore-role-narrowed-20261114`)
`livermore_trigger_check.py` (cò cron 19:45) + `livermore_run.sh` + `livermore_report_block.py` mặc định TẮT lập forecast VNINDEX; bật lại chỉ bằng env `LIVERMORE_VNINDEX_FORECAST=1`. Crontab KHÔNG đổi (script tự no-op, scorer vẫn chạy).

## ĐỪNG đề xuất lại
Phân kỳ RSI làm tín hiệu/đặc trưng (VNINDEX hay cổ phiếu) và dự báo hướng VNINDEX bằng đọc tape — **trừ khi có dữ liệu mới hoặc PREREG riêng** (kèm N độc lập đủ cho MDE và qua quant-skeptic).
