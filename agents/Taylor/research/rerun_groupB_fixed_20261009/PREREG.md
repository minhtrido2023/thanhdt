# PREREG — Nhánh 4: chạy lại "nhóm B" trên engine đã sửa bug custom30V double-count

Job `Taylor_20261008_172556` · user duyệt 2026-10-09 00:25 ICT · PAPER-ONLY (live park = 0).
Viết + commit TRƯỚC khi có bất kỳ số treatment nào (lúc commit chỉ 4 chân control đang chạy).
Bối cảnh: `mike/reports/rnd_rejected_vs_corrected_r3_review_20261008.md` §2.B.

## 1. Giả thuyết
- **H1 (bug có hướng).** Bug cũ (chuỗi return rổ park chain trên `Close_adj × OShares`) bơm return giả
  vào ngày có bước số CP; ngân hàng VN phát CP thưởng dày nhất ⇒ control custom30V (nặng bank) được thổi
  nhiều hơn treatment giảm bank. Dự báo: trên engine sửa, Δ(treatment − control) **dịch lên** so với Δ cũ,
  và dịch nhiều hơn ở chân cắt bank nhiều hơn.
- **H2 (claim canonical).** "custom30V thắng nhờ BREADTH" (registry 2026-07-12 Q-sleeve) còn đứng ⇔ cả
  Q8/Q12/QF8 vẫn thua control ≤ −0,385pp FULL ở CẢ HAI quy ước tiền nhàn rỗi.

## 2. Thiết kế (khai trước, không đổi sau khi thấy số)
- Engine: worktree `wt-repin-dep1m-2809` @ `03b12e46` (= `f66dab18` đã tái lập byte-identical cả 2 pin
  + knob `BASKET_WDUMP` env-OFF chỉ ghi file phụ trọng số ngày). Lệnh = `run_leg.sh` (env pin R3 nguyên văn,
  snapshot `bq_cache_asof20260729_postrestate`, `BASKET_CA_SNAPSHOT` 0927, threads=1, `$DNA_PYEXE`, AUDIT_END 2026-06-19).
- **Knob park: 0,7** — đúng knob các nhánh gốc đã đo (Q-sleeve/seccap/fincap/L1 đều `PARK_STATES=3:0.7`).
  Không có pin ở 0,7 ⇒ chạy control 0,7 trên engine sửa. Kèm control 0,3 phải tái lập md5 pin
  `4707bcbe` (pin0%) / `bcd0469f` (pin1M) — **lệch ⇒ DỪNG, không đọc số treatment**.
- Mỗi chân chạy 2 lần: `IDLE_CARRY_TIER=off` (pin0%, SÀN) và `=dep1m` (pin1M, TRẦN).
- Ngoài phạm vi: Q12-BULLEXT (trục BULL-extension thuộc nhóm A của review — verdict đứng, bug làm nó trông
  tốt hơn mà vẫn NO-GO); park 0,3 cho treatment (không đủ thời gian trong job; ghi là việc tiếp nếu cần).

| Họ | Chân | env khác control (control = `BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.7`) | Neo so 1 trục |
|---|---|---|---|
| (1) Q-sleeve | q8 | `BASKET_WT=ew BASKET_TOPN=8 BASKET_GATE_RATING=2 BASKET_LIQ_FLOOR_B=5` | ctrl (bó 4 knob = 1 vehicle khai trước 07-12) |
| | q12 | như q8, `TOPN=12` | ctrl; q8 (1 trục TOPN) |
| | qf8 | `BASKET_WT=ew BASKET_TOPN=8 BASKET_GATE_RATING=none BASKET_QFLOOR=1 BASKET_LIQ_FLOOR_B=5` | ctrl (bó) |
| (2a) sector-cap | secA | `BASKET_WT=sectorcap` | ctrl |
| | secB | `BASKET_WT=sectorcap BASKET_SECCAP_MODE=mktcap` | secA |
| | secBx | `BASKET_WT=sectorcap BASKET_SECCAP_MODE=mktx1.5` | secB |
| (2b) fincap | eyonly | `BASKET_SELECT=eyonly` (neo của họ fincap, như 07-14) | ctrl |
| | fc30 | `BASKET_SELECT=eyonly BASKET_WT=fincap` (cap mặc định 0,30) | eyonly |
| | fc45 | `... BASKET_FIN_CAP=0.45` | fc30 |
| | fc55 | `... BASKET_FIN_CAP=0.55` | fc45 |
| (3) L1 pool | l1a | `BASKET_CFO_POOL=90` | ctrl |
| | l1b | `BASKET_CFO_POOL=120` | l1a |

**N_trials = 12** (12 chân treatment trên; eyonly tính là trial). PBO: CSCV S=16 trên 13 cấu hình (ctrl + 12),
riêng cho từng quy ước. Họ được GHIM bằng file manifest (md5 từng CSV) trước khi chạy DSR/PBO.

## 3. Chỉ tiêu báo cho MỖI chân × 2 quy ước
CAGR / Sharpe(252) / MaxDD / Calmar · IS 2014-19 / OOS 2020+ · Δ per-year + LOO (bỏ từng năm, CAGR log
hoá năm) · bank share rổ park (tỷ trọng TRỌNG SỐ ngày từ `BASKET_WDUMP`, route PIT `value_panel_2014.csv`
as-of quý; kèm share theo SỐ TÊN) · DSR (chuỗi excess vs control, N=12; kèm DSR raw-vs-SRctrl kiểu 09-09) ·
bootstrap khối L=63 B=4000 CI95 của Δ · self-check 0 VND · dòng tham khảo so với leg park=0 đã pin
(`537e349b` 22,12% / `a6ba34d8` 25,42%) — **khác ≥2 trục, chỉ là tham khảo, không phải A/B**.
So 1 trục chạy bằng `bin/pin_ledger.py compare` trên kho SANDBOX (`PIN_STORE_WC_ROOT`), KHÔNG pin vào kho thật.

## 4. Luật verdict (sàn nhiễu 0,385pp = sàn đã dùng ở vòng 4, 09-09)
Áp ở pin0% (sàn); pin1M phải cùng dấu, không thì nhãn "HẾT Ý NGHĨA".
- **ĐẢO → ứng viên GO**: ΔCAGR > +0,385pp ∧ ΔIS>0 ∧ ΔOOS>0 ∧ Calmar ≥ ctrl ∧ CI95 bootstrap loại 0 ∧ DSR ≥ 0,95.
  (GO thật vẫn cần quant-skeptic + user; live park=0 nên không wire gì.)
- **ĐẢO DẤU nhưng chưa chứng minh**: ΔCAGR > +0,385pp, trượt ≥1 điều kiện còn lại.
- **HẾT Ý NGHĨA**: |ΔCAGR| ≤ 0,385pp, hoặc IS/OOS trái dấu với |Δ| nhỏ, hoặc 2 quy ước trái dấu.
- **ĐỨNG (NO-GO)**: ΔCAGR ≤ −0,385pp.
- L1 (verdict cũ "chưa chứng minh"): ĐỨNG nếu vẫn dương mà trượt DSR/CI; NÂNG thành ứng viên nếu đạt đủ;
  ĐẢO nếu ≤ −0,385pp.
- Họ seccap/fincap: verdict cũ chấm trên Δ vs neo trực tiếp (secA vs ctrl, fcX vs eyonly) — giữ nguyên neo đó.
- **H2**: đứng ⇔ q8, q12, qf8 đều ĐỨNG ở cả 2 quy ước. Bất kỳ chân Q nào HẾT Ý NGHĨA/ĐẢO ⇒ claim phải sửa.
- **H1** kiểm bằng dấu của (Δ_mới − Δ_cũ) và tương quan với Δbank-share. Caveat khai trước: Δ_cũ đo trên
  vintage `data/bq_cache` sống tháng 7 ⇒ (Δ_mới − Δ_cũ) lẫn bug + vintage; chỉ đọc chiều, không đọc biên độ.
