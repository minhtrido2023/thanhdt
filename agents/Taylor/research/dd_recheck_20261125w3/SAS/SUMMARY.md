# SAS — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032443 → resume Taylor_20261125_053002) — **DỪNG ở Bước 0**

Nguồn: `dd_redo_20261105/SAS/REPORT_r3.md` (sổ rev2, CONFIRMED kiểu cũ `rule_backfill_20261122`, chưa qua DD_GENERAL) · mô hình `calc_r3/model_sas_r3.py` (bị TRIM 19/11; khôi phục `git archive 14ad1c925^ … | tar -x -C /tmp/ddrestore_w3a/mike`; LOCK `LOCK_r3_md5.txt` md5 `62c5bd1f…` = `assumptions_md5` sổ; mọi file khớp trừ `data/deposit_rate_vn_events.csv` đã append sự kiện sau 08/11 — r vẫn 13,5% do model tự assert) · probe `calc/step0_probe_sas.py` (md5 `e3b71437…`; run1 = run2 md5 `54e58b7b…`; CONTROL tái lập headline 31.658 đúng từng đồng).

## Bước 0 (tham số nền bị phủ?): **CÓ — RONIC terminal (D4, user 22/11 19:07)**
- r3 khoá 08/11 (trước D4). Terminal = E₂₀₂₈/(r−g), g {2;3;4}% KHÔNG trích tái đầu tư (REPORT_r3 §1 dòng 7: "Gordon không trừ tái đầu tư giữ quy ước 08/11") ⇒ RONIC ngầm = ∞ > Ke ở mọi ô trục g.
- Moat **NARROW** (LOCATION/REGULATORY, `moat_durable=false`; ADDENDUM_5F_r1 §1–3 đã chỉ ra mô hình "ngầm thưởng kiểu WIDE") ⇒ D4/V5 bắt buộc RONIC = Ke (TV = E/r).
- Tham số nền khác đạt: r 13,5% (`effective_deposit_rate('2026-11-25')` = 7,40% CCTG 12M 02/11, Δ 0); không holding; độ nhạy r tính từ mô hình (r3 §5).
- Theo HANDOFF ⇒ **không chạy skeptic, không dựng E17/adj.json, không viết LEDGER_PROPOSAL**. Số dưới là ĐO để Mike/user quyết rev3, chưa phản biện.

## Số đo (sau CK 5 tỷ 5,93%; trước CK trong ngoặc) — mù giá
| Biến thể | Tâm | P10 / P50 / P90 | Δ vs r3 |
|---|---|---|---|
| r3 (sổ rev2) | 31.658 (33.652) | 25.083 / 31.402 / 38.043 | — |
| **D4: RONIC = Ke** | **27.426 (29.154)** | **22.379 / 27.333 / 32.368** | **−13,37%** |
| D4 @ Ke 12,3% (E15) | 29.062 | 23.457 / 28.928 / 34.542 | +5,97% so D4 |
| D4 @ Ke 13,4% | 27.551 | — | +0,46% so D4 |
| D4 r −100 / −50 / +50 / +100bp | 28.768 / 28.071 / 26.828 / 26.271 | — | +4,9 / +2,3 / −2,2 / −4,2% so D4 |

**E16 (asof 2026-11-20, `dd_history_label_SAS_2026-11-20.csv`):** SAS: so với lịch sử 10 năm của chính mã — **KHÔNG CHẮC (N hiệu dụng thấp, 1.99)** — phân vị [fade 2.5, hold 1.7], 120 tháng, N hiệu dụng ≈ 1.99; ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.36). Chỉ hiển thị.

## Vì sao không làm cơ học
Δ D4 −13,4% > 5% và đổi tâm base ⇒ B2 cần phản biện đầy đủ. Cờ ĐỈNH LỢI NHUẬN (ROE TTM/5Y 2,36) cùng hướng với điểm ADDENDUM_5F: N0 giữ biên đỉnh 9T/2026 (NPM 23,1% vs chu kỳ 14,5%) mãi mãi — V5 cấm ÉP biên về TB ngành ở pha dự báo, nhưng đây là hạng mục skeptic DD_GENERAL sẽ hỏi (chiều xuống, chưa định lượng ở đây). Mở từ r3 §9 (hai chiều): bên trả cổ tức đầu tư (A8 +1,5…+4,7k), thuế GTGT khấu trừ 240,6 (A2 +1,6k), phải thu DH 242 (A6 −1,7k), lãi Q4 tiền gửi (+40…+70 đ), thầu Long Thành.

## Đề xuất cho Mike/user (chọn 1)
- **(a) rev3 đầy đủ (khuyến nghị):** áp D4 → khoá PREREG mới → skeptic DD_GENERAL → E17 (hạng mục mở §9 r3 + biên đỉnh) → LEDGER_PROPOSAL.
- (b) rev3 cơ học chỉ D4 (27.426; P10–P90 22.379–32.368), nhãn REFUTED_OPEN + E17 trên base đó.

## Nhãn
Giữ sổ rev2 (31.658, TRONG). Đọc sau khoá: giá tham chiếu 06/11 kế thừa 34.200 > mọi biến thể D4 ⇒ nếu áp D4 thì nhãn sẽ đổi TRONG → TRÊN/nửa trên vượt P90 (32.368) — thêm lý do cần B2. Luật 4 không đạt ở mọi biến thể.

## Khuyến nghị lớp: **FULL** (rev3 + skeptic), chờ Mike/user chọn (a)/(b).
