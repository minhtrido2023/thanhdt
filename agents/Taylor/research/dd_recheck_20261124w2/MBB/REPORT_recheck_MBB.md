# MBB — Rà lại DD theo luật B5 + E15/E16 (đợt 2, 24/11/2026, job Taylor_20261124_131354)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/MBB/REPORT_r3.md`, 08/11) + `ERRATA_r3_skeptic_final_20261108.md`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/mbb_r3.py` (LOCK md5 `f5ad8f9e…`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` đã bị TRIM khỏi git ngày 19/11 (commit `14ad1c925`). Khôi phục `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 agents/Taylor/research/dd_MBB_20261031` → `/tmp/ddrestore_MBB/`. 16/17 file trong `LOCK_md5.txt` khớp md5; file lệch duy nhất `data/deposit_rate_vn_events.csv` (đã thêm sự kiện sau 08/11) — lãi 12T hiệu dụng tại 03/11, 06/11 và 24/11 vẫn đều **7,40%** (`cctg_12m(2026-11-02)`, `effective_deposit_rate`) ⇒ r không đổi.
- **Calc:** `calc/calc_recheck.py`. **Chân CONTROL:** chạy lại `mbb_r3.py`, stdout trùng từng dòng `run2.txt` r3 (md5 `1c79f8d0…`) ngoại trừ các dòng `LOCK` (assert). Tâm 21.069 / P10 14.729 / P90 27.577 assert. Chạy 2 lần: `run1.txt` = `run2.txt` md5 `51bfb06b…`. Output `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá mới. Giá 19.250 (BQ 06/11/2026) kế thừa r3, chỉ cho nhãn và % dưới giá.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 21.069 đ/cp — vùng 14.729–27.577. KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 23.659 đ/cp (+12,30% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (N hiệu dụng thấp, 1.93)** — phân vị [fade 17, hold 21], 120 tháng, N hiệu dụng ≈ 1.9

- **Nhãn** (giá 19.250, BQ 06/11/2026, kế thừa r3): **TRONG vùng**. Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 21.069 = 17.909). Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới là soát cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: MBB không có tầng holding (MBV không hợp nhất, base = NPV0 sổ sách; công ty con hợp nhất) ⇒ v5 không áp. (ii) r: neo 03/11 7,40%, đọc lại 24/11 vẫn 7,40% ⇒ Δ = 0, r = 13,5%. (iii) RONIC terminal = Ke đã áp ở r3 (đính chính D1: g_RI = 0 mọi nhánh). (iv) Độ nhạy r ở r3 đã tính từ mô hình, khớp lại từng đồng (§2).
- **Sizing (V8, mới):** đề xuất **2% NAV** (đáy chuẩn 2–4%) — lý do: chất lượng tài sản Q3/26 đang xấu đi (§3), đuôi dưới phụ thuộc nhánh XẤU, % trọng số kết cục dưới giá 38,6%. Không đề xuất >4%.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ có ±50/±100bp | Bổ sung: 23.659 / 21.266 | 0 |
| 4 | V6 hai nền | Chưa có | Không tính được cho ngân hàng (§3) | 0 |
| 5 | D3 capex tuân thủ | Chưa soát | Soát: không có hạng mục (§3) | 0 |
| 6 | V8 sizing | Không nêu | 2% NAV | 0 |
| 7 | Cờ WARNING 12 (NPL/nhóm 2/bao phủ Q3 "chưa kiểm") | Mở | Đóng bằng số BCTC HN-Q3 đã đọc ở DD 31/10 (§3) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%). β = 1 (giả định). Δ đến 24/11 = 0.

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 19.250 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 23.659 | 16.545 | 30.969 | +2.590 | +12,30% | 25,5% |
| 12,5% (−100bp) | 23.191 | 16.217 | 30.357 | +2.123 | +10,07% | 25,5% |
| 13,0% (−50bp) | 22.087 | 15.443 | 28.911 | +1.019 | +4,83% | 27,8% |
| 13,4% (đầu trên dải Ke) | 21.266 | 14.867 | 27.835 | +197 | +0,94% | 38,6% |
| **13,5% BASE** | **21.069** | **14.729** | **27.577** | 0 | 0 | 38,6% |
| 14,0% (+50bp) | 20.126 | 14.068 | 26.343 | −942 | −4,47% | 44,1% |
| 14,5% (+100bp) | 19.252 | 13.455 | 25.198 | −1.817 | −8,62% | 53,6% |

- Bốn mốc ±50/±100bp khớp đúng số r3 §5 (23.191 / 22.087 / 20.126 / 19.252).
- Độ nhạy r của MBB lớn hơn FPT (+12,3% vs +6,7% ở Ke 12,3%) vì định giá RI có ROE_T > Ke vĩnh viễn trên sổ sách cuối 2029: phần RI terminal (ROE_T − Ke)×BV/Ke co giãn mạnh theo Ke.
- Nhãn TRONG ở mọi r trong bảng. Bản F (ROE_T −2pp) ở r 12,3%: 21.018 (P10 14.149); bản G (+2pp): 26.300.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** đã đúng — r3 đính chính D1 đặt g_RI terminal = 0 ở mọi nhánh (vốn mới sau 2029 sinh lời đúng Ke). ROE_T 14/16/18% được giữ trên sổ sách cuối 2029 (không ép về TB ngành — quy ước user 08/11: NARROW không thưởng, không trừ). Độ nhạy "3c chặt" (fade về trung vị ngành 12,97%) = 17.677 vẫn đo trên base **r2**, chưa chạy lại trên r3 (ERRATA); chỉ là độ nhạy rủi ro, không đổi headline.
- **D3 capex tuân thủ:** ngân hàng không có capex tuân thủ đáng kể. Nhu cầu vốn theo quy định (Basel III/TT14) đã đi vào base qua ROE_T hạ dưới lịch sử (`mbb_calc.py:133`) + payout tiền 30% (giữ lại 70%). Không lệch.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0); dải Ke 12,3–13,4% nay đã báo (§2); ±50/±100bp tính từ mô hình.
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ (r3 §7): trước CK 21.109, sau CK 5 tỷ (0,191%, ADV250 349,1 tỷ) 21.069; nhãn theo sau CK.
- **V5 moat:** đã đủ — `ADDENDUM_5F.md` (07–08/11/2026) < 12 tháng: **NARROW · COST/REGULATORY · không bền**; rủi ro số 1 = xói mòn CASA/chi phí vốn biên đúng lúc gánh MBV và chất lượng tài sản xấu đi. Kiểm nhanh 24/11: không có BCTC/CBTT mới được đọc trong recheck này.
- **V6:** `dd_blend_20261111/out/apply_dd.csv` dòng MBB ghi `tai chinh/thieu BCTC` — engine hai nền không áp cho ngân hàng (FCFE không định nghĩa được với ngân hàng). **Chưa có**, không tự tính.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** 2% NAV (§0).

### Chất lượng tài sản Q3/26 — đóng cờ 12 (số BCTC HN-Q3, đã đọc ở DD 31/10, `dd_MBB_20261031/calc/mbb_calc.py`, chạy lại 24/11)
| HN | 31/12/25 | 30/09/26 |
|---|---|---|
| Nhóm 2 (tỷ; % dư nợ) | 10.210 (0,94%) | **17.014 (1,32%)**, +67% YTD |
| NPL nhóm 3–5 | 14.027 (1,29%) | **21.474 (1,67%)** |
| Nhóm 2–5 | 2,24% | **2,99%** |
| Bao phủ | 93,7% | **84,7%** |
- Hình thành NPL mới 9T26 = ΔNPL + xoá nợ 7.877 = 15.324 tỷ (1,73%/năm dư nợ BQ); chi phí tín dụng 9T 1,46%, Q3 1,65%. Giữ bao phủ 93,7% ⇒ thiếu 1.940 tỷ DP (≈19% LNTT Q3).
- So mốc đổi nhận định r3 §10: nhóm 2 HN 17.014 < ngưỡng 20.000; nhóm 2–5 2,99% < 3,5%; bao phủ 84,7% > 75% ⇒ **chưa kích hoạt nhánh xấu**, nhưng cả ba đang đi về phía ngưỡng. Kịch bản XẤU (DP Q4 7.500 "xây lại bao phủ") đã mô hình hoá đúng rủi ro này; base không đổi.
- Còn **chưa kiểm**: CAR/Tier1 30/09 (chỉ có số 30/06: CAR HN 10,7%, riêng 10,28% — thứ cấp); số dư phải thu MBV 30/09.

## 4. Việc còn mở kế thừa (không chặn nhãn)
1. Phải thu bán nợ MBV 11.248 tỷ: số dư 30/09/26 chưa kiểm (bản E −86 đ).
2. Nghĩa vụ hỗ trợ MBV (cờ HARD ABANDON nếu ≥ 15.688): chưa có văn bản.
3. Phát hành riêng lẻ 200 triệu CP 2026 (~2%; thứ cấp Vietcap 07/08) — giá phát hành/pha loãng chưa vào mô hình.
4. Pháp lý sau 05/11 chưa quét lại (WARNING).

## 5. WARNING (giữ r3 §11)
MBV + ưu đãi MBV; nợ ngoại bảng/TT02; bên liên quan/top KH; CAR/CET1; sở hữu chéo; nghị quyết phát hành 2026; lỗ phái sinh suy luận; quota tín dụng; kiểm toán; pháp lý chưa quét sau 05/11. Pháp lý chỉ WARNING.

## 6. Phạm vi đề nghị cho phản biện (§E4)
Moat (NARROW + ROE_T 16% > TB ngành giữ vĩnh viễn trên sổ cuối 2029 — có là thưởng ngầm không), cân bằng hai chiều (lên: Ke 12,3% +12,3%; xuống: 3c chặt 17.677 trên base r2, chất lượng tài sản Q3), thiếu hạng mục (pha loãng phát hành riêng lẻ, phải thu MBV, nghĩa vụ vốn cấp 2), và kiểm bảng độ nhạy r §2.
