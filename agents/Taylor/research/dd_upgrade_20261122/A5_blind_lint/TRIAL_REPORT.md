# A5 — TRIAL_REPORT `bin/dd_blind_lint.py` (thử trên file cũ thật, 22/11/2026)

Đo bằng: `python3 bin/dd_blind_lint.py <file>` (mode mặc định `sector`, không `--ticker` ⇒ dùng 36 mã sổ) trên
26 brief `agents/Taylor/research/dd_*/brief*.md` + 27 `kb/data_registry/market-state/sector_read_*.md` (53 file).
Tổng sau chỉnh regex: PATH_LEAK 65 · TICKER 114 · VERDICT_LEAK 29 · PRICE_TOKEN 21 · MULTIPLE 6 · MARKET_CAP 2.
rc=0: brief 0/26, sector_read 7/27.

**Lưu ý đọc số:** brief DD là cho agent BIẾT mã ⇒ TICKER/PATH_LEAK trong brief là đúng bản chất (không phải báo giả, chỉ là chạy sai mode — linter dành cho brief giao agent MÙ, dùng `--mode skeptic`/`--ticker` tuỳ ngữ cảnh). Ca "sạch" thật chỉ đo được trên sector_read (đọc mù).

## Bảng 12 file (đủ ≥10; PAT ×2 + VLB bắt buộc)
| File | Bị bắt | Đánh giá thủ công |
|---|---|---|
| dd_PAT_20261114/brief.md | PRICE_TOKEN (Giá đóng cửa 72.700), TICKER, PATH_LEAK, VERDICT (vùng giá) | ĐÁNG báo (bắt buộc bắt: có giá) |
| dd_PAT_20261114/brief_r2.md | PRICE_TOKEN ×2 (72.700; 24,5k), MULTIPLE (P/B ~2), REFUTED, PATH | ĐÁNG báo (bắt buộc bắt: giá + P/B) |
| sector_read_da_xay_dung_dnb_20261122.md | PATH_LEAK `dd_VLB_20261122` (dòng 289), TICKER VCB (dòng 163-164, nguồn lãi suất) | ĐÁNG báo — ca F7 gốc (PATH_LEAK bắt đúng) |
| sector_read_fertilizer_dap_20261028.md | không | sạch ✔ (đúng) |
| sector_read_gach_nung_icd_binhduong_20261103.md | không | sạch ✔ |
| sector_read_hoa_chat_xut_clo_20261109.md | không | sạch ✔ |
| sector_read_xe_tai_thuong_mai_vn_20261101.md | không | sạch ✔ |
| sector_read_dien_mat_troi_thuy_dien_nho_20261120.md | không | sạch ✔ |
| sector_read_vlxd_nhe_aac_20261029.md | không | sạch ✔ |
| sector_read_thuy_dien_20261112.md | PATH_LEAK dd_VCP_20261112 (dòng 21) | ĐÁNG báo (đường dẫn DD của mã VCP lọt vào đọc mù) |
| sector_read_than_20261111.md | PATH_LEAK dd_CST ×3 | ĐÁNG báo (như trên) |
| sector_read_power_consulting_20261028.md | TICKER DGC/DRI/TV1 (dòng 21), NT2 ×2 | ĐÁNG báo (nêu mã của sổ); DGC/TV1 ở dạng "case discretionary" nhưng vẫn là tên mã |
| sector_read_khi_dot_lpg_20261109.md | PRICE_TOKEN `609.000đ` (dòng 51) | **BÁO GIẢ** — giá bình gas 12kg bán lẻ, không phải giá cổ phiếu |
| sector_read_kcn_cho_thue_dat_20261101.md | TICKER VCB ×2 (dòng 164,170) | **BÁO GIẢ ngữ nghĩa** — "CCTG 6M VCB 7,5%" = lãi suất ngân hàng làm nguồn; vẫn là mã trong sổ, luật máy chặn đúng chữ. Gắn `<!-- blind-ok: nguồn lãi suất -->` |
| sector_read_bds_nha_o_do_thi_phia_bac_20261031.md | TICKER VCB (dòng 36) | **BÁO GIẢ ngữ nghĩa** — như trên (cùng loại) |

## Số báo giả (đánh giá thủ công)
- Sector_read sạch thật: 7/27 file rc=0 (gồm 6 file trong bảng). 20/27 bị báo: phần lớn là PATH_LEAK/TICKER ĐÁNG báo.
- Báo giả còn lại đã nhận diện (liệt kê, không ẩn): (1) giá hàng hoá "609.000đ" (LPG) — regex không phân biệt được giá hàng với giá cổ phiếu khi dòng có "thị trường"; (2) VCB/bank ticker khi dùng làm NGUỒN lãi suất (2 file); (3) `PRICE_TOKEN` "đ"-token cạnh chữ "đóng cửa/thị trường" cho giá hàng hoá thi thoảng lọt; (4) P/B ngành `P/B 1,42x` trong sector_read_ngan_hang_quoc_doanh — theo SPEC vẫn flag MULTIPLE (đa số ngành, không phải mã) ⇒ cần `blind-ok`.
- Đã chỉnh qua vòng 1: bỏ "CSV" khỏi danh sách mã (đuôi file); phủ định ("không thấy forward return", "mù") không bị báo; `đ/kg`, `đ/USD`, "trung tâm" (tỷ giá), "ly tâm" (bê tông), số có đơn vị `k thùng/dwt/m³` không bị báo; "vốn hoá" kèm số xa qua `;` / "lãi vay vốn hoá" không bị báo; "PE 2025" (năm) không bị báo; `rẻ/đắt` chỉ báo khi sát "cổ phiếu/định giá/mã/vùng".
- Báo giả còn lại ≈ 3 loại, ~4 ca trên 53 file; không khử được hoàn toàn bằng regex ⇒ cơ chế thoát `<!-- blind-ok: lý do -->` (liệt kê ở "miễn: n").
- KHÔNG đạt mục tiêu "0 báo giả" tuyệt đối: còn ≥4 ca nêu trên (mục tiêu đặt trước khi đo; nêu thẳng). Nên Mike cân: coi rc=1 là CẢNH BÁO, chưa chặn cứng, tới khi có số báo giả trên brief mới.
- Chưa đo: tỉ lệ bắt-sót (false negative) ngoài 2 brief PAT + ca VLB — cần tập có nhãn.
