# PREREG B/C — replay survivorship: bỏ TGG/GAB, cap khớp 5%/10% ADV pha bơm/xả, GAB nguồn thứ hai (job Taylor_20261020_113646)

EXPLORATORY. Không sửa pin/registry/pin_ledger, không đề xuất đổi luật, không sửa engine. Viết + md5 + commit TRƯỚC khi tính.
Kế thừa nguyên replay `../survivorship_replay_20261020/` (PREREG md5 21165fd1; code svr_replay.py/svr_lib.py import nguyên văn).
Cố định: kịch bản Z, exit X-liq, 4 chân pin (4707bcbe/bcd0469f/537e349b/a6ba34d8), sàn nhiễu 0,46pp.

## C (đã làm TRƯỚC prereg này — là kiểm dữ liệu, không phải tính kết quả)
`c_gab_compare.py` + `c_gab_compare.out`: SSI iBoard (dữ liệu ngày, tải 2026-10-20) khớp KL khớp lệnh VNDirect tuyệt đối ở 99,6% số
ngày (679 ngày); Simplize tháng = khớp lệnh + thỏa thuận (từ 2021-01 trùng tuyệt đối nm+pt của VNDirect ở 12/15 tháng; trước 2021
VNDirect không có cột thỏa thuận, phần dư Simplize là các lô tròn). ⇒ KL khớp lệnh VNDirect ĐÚNG; "7,7×" là so khớp lệnh với
khớp lệnh+thỏa thuận. Hệ quả cho replay: vào lệnh dùng `liq` = KL khớp lệnh (đúng); thoát X-liq dùng `val` = nmValue+ptValue
(thỏa thuận không phải thanh khoản khớp được ⇒ lạc quan) → biến thể `exit_nm`.

## Biến thể (lưới đầy đủ, mọi ô được báo)
- **w**: `orig` = trọng số replay CONFIRMED (w_median v2 cũ, book_fraction cũ — có bug CUSTOM ở park 0,3) để so trực tiếp dải chính;
  `fixA` = w_median từ v2 sau fix A (`../survivorship_sensitivity_v2_20261020/out_summary.json`) + book_fraction loại ETF_PARK.
- **set**: M (14) · M−TGG−GAB (12) · M−GAB (13).
- **cap**: 20% (gốc) · 10% · 5% của thanh khoản, áp cho CẢ dung lượng khớp vào (PART×liq) VÀ thoát X-liq (PART×val) trong ngày thuộc pha.
- **scope** pha: `phase` (chính) = ngày d (trên lịch giá của mã, ≤DL) thỏa ÍT NHẤT một:
  bơm: Close(d) ≥ 2 × min(Close 250 phiên gần nhất gồm d); xả: Close(d) ≤ 0,5 × max(Close 250 phiên gần nhất gồm d);
  cửa sổ sụp: d ∈ [LT−365 ngày, DL]. `all` (cận) = mọi ngày. Ngoài pha giữ 20%.
- **exitval**: `ptin` (gốc, nm+pt) · `nm` (chỉ khớp lệnh).
- **var**: UB, MID, LIVE (+ _ALLOC*, không prereg như cũ). cfg BAL/LAG/MIX.
Luật khớp còn lại giữ nguyên (≤5 phiên, bỏ nếu <30% mục tiêu, phí 0,1%).

## Kiểm tái lập (bắt buộc trước khi đọc)
Ô (w=orig, set=M, cap=20, exitval=ptin) phải tái tạo `out_replay_results.csv` gốc (Z, liq; UB/MID/LIVE và _ALLOC; BAL/LAG/MIX) với chênh |Δ| ≤1e-12.
Lệch ⇒ dừng, báo.

## Báo cáo chính (B)
UB MIX dải 4 chân ở: (i) set M−TGG−GAB cap 20; (ii) set M cap 10/5 phase; (iii) M−TGG−GAB cap 5 phase; cạnh dải UB gốc; kèm
MID/LIVE cùng ô. Báo cả w=orig và w=fixA; **nhãn dùng fixA** (đúng PREREG v2 §1). Nhãn theo từng ô: "vượt sàn chiều thiệt" nếu
max dải ≤ −0,46; "vượt sàn chiều lợi" nếu min ≥ +0,46; "dải cắt sàn" nếu dải chứa ±0,46; "dưới sàn" nếu cả dải trong (−0,46; +0,46).
"Dấu MID/LIVE không đổi" = dấu của dải (hoặc dải dưới sàn) giống ô gốc.

## Báo cáo C
UB/MID/LIVE MIX: set M−GAB (cap 20); set M exitval=nm (cap 20 và cap 5 phase). Không nhân hệ số ADV cho GAB vì nguồn đã xác minh
(hệ số = 1); nếu skeptic cần, hệ số 1/7,7 là sai theo bằng chứng trên.
