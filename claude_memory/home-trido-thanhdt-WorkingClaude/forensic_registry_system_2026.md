---
name: forensic_registry_system_2026
description: 3-layer forensic system for 8L — persist human findings (KSF related-party) + detect + golden backstop
metadata: 
  node_type: memory
  type: project
  originSessionId: 4fb305f6-9ad2-4e2f-9dfd-b054819e2145
---

User ([REDACTED]20) raised 2 gaps: (1) golden-cell (pb_z) chỉ nhìn lịch-sử-BẢN-THÂN, thiếu chốt tuyệt-đối → cổ làm-giá đẩy cao/giữ lâu/rớt → PB_MA5Y bị thổi → pb_z≤−1 giả (dao rơi); (2) KSF lãi từ giao-dịch-NỘI-BỘ, và "ta không ghi nhớ forensic findings". → Built **3-layer forensic system**.

**Evidence first:**
- Golden absolute-backstop KHÔNG được data ủng hộ: sau gate CF_OA_3Y>0+book-OK (CTF fix), golden cohort robust mọi bucket PB-tuyệt-đối (rẻ +7.1%/mid +5.2%/đắt +5.0%, crash 5-7%); chia theo earnings-yield tuyệt-đối thì NGƯỢC (golden "đắt-trên-earnings" +7.1% > "rẻ" +4.3% = earnings đáy chu kỳ sắp hồi). → blanket absolute-valuation rule phản tác dụng; KHÔNG thêm.
- KSF forensic: NPM 0.45/EBITM 0.59/ROE **50%** nhưng **AR/rev 2.0x + cash-cycle 1256d** (lãi siêu cao, không thu tiền). cfo_np 1-quý 3.27 nhìn "đẹp" → ratio chuẩn KHÔNG bắt chắc related-party (chồng lấn BĐS). → cần lớp GHI NHỚ người.

**LAYER 1 — FORENSIC REGISTRY (`data/forensic_flags.csv`)** = persistence (giải đúng "không nhớ"). Cols: ticker,flag_type,severity(exclude|watch),date,source,note. Mirror moat_tags.csv nhưng cờ ÂM. Seeded: **KSF (related_party, exclude)**, CTF (distress_cashburn, watch).

**ĐÃ MỞ RỘNG TOÀN BỘ trade-universe + cap rating (user chọn "mạnh nhất", [REDACTED]20) — exclude áp 4 nơi, date-aware NO hindsight (chỉ từ flag date trở đi):**
1. `rating_8l.py` live: FORENSIC global → force zone 4_TRAP + loại golden-floor + **cap rating≥4** (out top30/buynow/live-custom30). KSF rating 2→4 ✓verified.
2. `custom_basket.build_pit.rating_asof`: nếu d≥flag_date → return 5 (KSF rớt custom30/V2.3 forward; KSF vốn KHÔNG có trong custom30_8l hiện tại).
3. BQ `fa_ratings_8l` (source cho golive direct-read + audits): **surgical INSERT row (KSF,[REDACTED]20,5,E)** — vì row mới nhất của KSF là 2026-04-29 (<flag) nên phải APPEND row tại flag date (không sửa row cũ). golive QUALIFY latest → KSF=5 (half-size bear/crisis). Lịch sử giữ rating 2.
4. Publisher code baked: `rating_8l_history.py` (CREATE OR REPLACE fa_ratings_8l) + `build_rating_8l_history.py` (pkl) APPEND override row @flag date → next full republish tự tái tạo. (KHÔNG full-republish lúc fix vì recompute có thể đổi rating mã khác = rủi; dùng surgical insert.)
PIT-honest: cap chỉ từ [REDACTED]20, backtest lịch sử KSF giữ rating thật (ta không biết trước).

**LAYER 2 — SUSPICION SCREEN (`forensic_screen.py` → `data/forensic_candidates.csv`)** = "làm sao nhận ra" (surface, KHÔNG phán). Signature KSF = ROE≥15% + AR/rev≥1x + cash-cycle dài + cfo3y/np thấp (ROE-cao discriminate: BĐS AR-cao thường ROE 1-6%; ROE 50%+AR 2x = bất thường). Ra 5 ứng viên: HDC(susp5,cfo3y/np −1.42), KSF(đã flag), VHM, BCM, L40(npm 108%=lãi ngoài-HĐ). Người soi footnote → confirmed vào Layer 1.

**LAYER 3 — golden floor**: giữ CF_OA_3Y>0+book-OK (validated [[value_composite_v3_2026]]); tôn trọng registry (flagged không được floor); KHÔNG thêm absolute-valuation backstop (data bác). Đuôi làm-giá hiếm → xử qua registry (known actors)+rating/liq gate, không bằng luật định-giá.

**Quy trình:** chạy forensic_screen định kỳ → review ứng viên → confirmed thêm vào forensic_flags.csv → rating_8l tự loại. ĐÃ mở rộng exclude sang trade-universe (cap rating, xem trên).

**SWEEP 5F+forensic 30 mã actionable un-audited ([REDACTED]20, workflow `forensic-5f-sweep`, 31 agents/1.4M tok):** Mỗi mã = BQ ratios + price-run-up + 5-Forces web → CLEAN/WATCH/EXCLUDE.
- **EXCLUDE 6 (đã wire vào forensic_flags.csv, đều đang ở BUY-NOW):** **PC1=fraud_confirmed** (2026-05-15 MPS bắt TOÀN BỘ C-suite + kế toán trưởng, embezzlement — cú bắt lớn nhất); **HHS** related_party (one-off 3507bn từ hợp nhất CRV, EBIT âm); **L40** non_operating (bargain-purchase 310bn post board-coup, NPM>100%); **KLB** related_party (Sunshine ecosystem lending + pump listing); **DIG** non_operating (NP 2026Q1 âm, CFO âm 5/6y, bán dự án, dilution); **BFC** pump_no_moat (sạch sổ nhưng NPK no-moat pumped 4.82x vào peak đang lăn xuống).
- **WATCH 18**: [BINARY_STRIPPED]. Borderline-exclude = **IJC** (KSF-like: cash-cycle 1953-4699d, CFO_3Y âm, PCF -11.5, Becamex receivables) + **VRE** (non-op NPM>>EBITM, Vingroup related-party) → đã thêm severity=watch.
- **CLEAN 6**: HPG, NT2, PAN, PVP, TPB, VHC (peer VHC clean vs ANV watch = peer-relative divergence).

**🔑 SYSTEMIC INSIGHT (quan trọng nhất):** failure mode chủ đạo KHÔNG phải fraud mà là **"no-moat cyclical pumped vào peak earnings" (VVS-trap)** — PE/PB rẻ trên list này là CỜ ĐỎ không phải xanh. Value composite (ey/cfy/ps) cao = artifact của (giá parabolic)×(EPS đỉnh chu kỳ). Screener đang hệ thống hút late-cycle commodity. → Registry per-name chỉ vá triệu chứng; **fix cấu trúc cần = peak-earnings/cyclical guard trên value_score** (ROE_Trailing >> ROE5Y/ROE_Min3Y gap = peak → demote) + moat-gate cho BUY-NOW. CHƯA build — chờ user. Patterns: RE/infra cluster (DIG/IJC/SZC/CTI/VRE) = non-cash profit/trapped capital → CFO-quality là screen quyết định; SOE-parent (BFC/DCM/PVT/SZC) governance-flag NHƯNG AR/rev thấp + CFO dương = KHÔNG phải related-party fraud (phân biệt quan trọng).
