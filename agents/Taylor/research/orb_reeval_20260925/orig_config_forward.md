# Config GỐC (đã validate) chạy FORWARD trên cửa sổ paper live — item 2/6

Job `Taylor_20260925_095910` · 2026-09-25 · PAPER-ONLY (không tiền thật)
Script tái lập: `orig_config_forward.py` · snapshot vendor đóng băng
`vn30f1m_live_snapshot_20260925.csv` sha256 `871aaebd41386fb9582710864634c2fbe1ec98fc1fef9350d869b920bd0968b2`
· trade log `orig_config_forward_trades.csv` · JSON `orig_config_forward_result.json`
Ablation/statistic bổ sung chạy dưới `$DNA_PYEXE` (scipy) — `orb_extra_ablation.py`, logic `sim()` trùng.

## Vì sao chạy cái này
Gate criterion #2 của `kb/paper_programs_registry.json` (`orb_intraday`) nói về khoản **lỗ cả năm
2024**. Khoản lỗ đó thuộc **config GỐC** — cái duy nhất từng được validate (`vn30f_orb_strategy.py`
mục C): exit 14:00 · stop 0.7% · lọc |OR30| ≥ 0.2% · TC 2.5bps. Config đang paper-trade
(`orb_pt.py`) khác 3 trục: exit 14:30 · KHÔNG stop · tất cả ngày. Cho tới nay **chưa lần nào**
config GỐC được đo trên dữ liệu forward ⇒ criterion #2 chưa từng có dữ liệu để trả lời.

Logic `sim()` **copy nguyên văn** từ `vn30f_orb_strategy.py::sim()` (stop theo low/high intraday,
thoát tại giá stop). Completeness dùng đúng quy tắc của `orb_pt.py` (bar cuối ≥ 14:25), không phải
`len(g)>=150` của script research — xem C4 trong `FINDINGS.md`.

## Kết quả — cửa sổ 2026-06-09 → 2026-09-24, cùng TC 2.5bps cho cả hai

| config | n | WR | mean/phiên | Sharpe | t | MaxDD | %stop | cum |
|---|---|---|---|---|---|---|---|---|
| **GỐC** exit14:00 · stop0.7% · \|OR\|≥0.2% | 35 | 40.0% | **−11.20bps** | **−3.05** | −1.14 | −5.5% | 37% | **−3.90%** |
| DEPLOY exit14:30 · no stop · all-days | 74 | 55.4% | +8.19bps | 1.39 | +0.75 | −6.2% | 0% | +5.91% |
| DEPLOY, chỉ trên 35 ngày GỐC có trade | 35 | 45.7% | −17.29bps | −2.65 | −0.99 | −9.1% | 0% | −6.05% |

Cross-check: dòng DEPLOY n=74 / WR 55.4% khớp đúng bộ 74 phiên của re-eval job `_052050`
(NAV +6.59% ở mô hình phí slip-1-tick riêng của `orb_pt.py`; ở đây +5.91% vì đã quy về TC 2.5bps).

Bootstrap (20k) mean của config GỐC: 95% CI **[−29.99, +7.80] bps/phiên**, P(mean ≥ 0) = 0.124.
t = −1.137, **p = 0.264** hai phía.

Theo tháng (config GỐC): 06 n=6 −9.04bps · 07 n=11 −5.51bps · 08 n=9 **−44.09bps** · 09 n=9 +13.29bps.

## Trả lời criterion #2: khoản lỗ ĐÃ LẶP LẠI trong cửa sổ forward

| | n | mean/phiên | Sharpe | cum |
|---|---|---|---|---|
| 2024 (lịch sử, FINDINGS C5) | 76 | −5.93bps | −1.84 | −4.50% |
| **Forward live 06→09/2026** | 35 | **−11.20bps** | **−3.05** | **−3.90%** |

Cùng dấu, độ lớn **lớn hơn** trên mỗi phiên. Criterion #2 hỏi "khoản lỗ 2024 được giải thích
HOẶC không lặp lại trong cửa sổ forward" — câu trả lời bây giờ là: **không được giải thích, VÀ
đã lặp lại** ⇒ criterion #2 chuyển từ `pending` sang **FAILED**.

**Giới hạn phải nói kèm** (bài học job trước — không claim quá dữ liệu): n=35, p=0.264, CI chứa 0.
Không thể bác bỏ "mean = 0" cho config GỐC trên cửa sổ này. Cái chắc chắn là **DẤU**: hai lần đo
độc lập (2024 lịch sử, 2026 forward) đều âm, không có bằng chứng nào cho thấy nó đã tự khỏi.

## Phân rã: cấu phần nào gây lỗ (ablation, cùng TC 2.5bps, cùng cửa sổ)

| biến thể | n | mean/phiên | cum |
|---|---|---|---|
| GỐC (exit14:00 · stop0.7% · \|OR\|≥.2%) | 35 | −11.20bps | −3.90% |
| bỏ stop (exit14:00 · no stop · \|OR\|≥.2%) | 35 | −21.02bps | −7.22% |
| đổi exit (exit14:30 · stop0.7% · \|OR\|≥.2%) | 35 | −7.35bps | −2.61% |
| bỏ lọc \|OR\| (exit14:00 · stop0.7% · all-days) | 74 | **+5.39bps** | +3.91% |

**Trục quyết định là bộ lọc |OR| ≥ 0,2%, không phải stop hay giờ thoát.** Bỏ stop làm TỆ HƠN
(−21bps) ⇒ stop không phải nguyên nhân; 13/35 phiên bị stop, mỗi phiên −72,5bps, còn 22 phiên
không stop +25,0bps. Chia 74 phiên deploy theo đúng bộ lọc đó:

- trong lọc (|OR| ≥ 0,2%): n=35, mean **−17,29bps**
- ngoài lọc (|OR| < 0,2%): n=39, mean **+31,06bps**
- Welch t = −2,25, **p = 0,028** (một so sánh, KHÔNG hiệu chỉnh đa kiểm định)

Trên lịch sử 670 phiên, `|OR| ≥ 0,2%` là lựa chọn có Sharpe CAO HƠN (2,22 vs 1,59 — FINDINGS §7).
Trên cửa sổ forward, dấu của nó **đảo**. Đây là chữ ký kinh điển của một trục bị chọn quá khớp
mẫu (in-sample selection), nhưng với 1 cửa sổ + p thô 0,028 thì nó là **cảnh báo**, chưa phải
kết luận đã kiểm định.

## Hệ quả cho registry
1. Criterion #2 → **FAILED** (không còn `pending`): lỗ lặp lại trên chính config mà criterion nói tới.
2. Verdict B (CONTINUE PAPER) của job `_052050` **không đổi**, nhưng nay có thêm một lý do độc lập
   mạnh hơn lý do thống kê: config đang chạy chưa từng được validate, và config từng được validate
   thì đang lỗ forward.
3. KHÔNG được dùng kết quả này để đề xuất đổi config (vd "bỏ lọc |OR| ra") — đó chính là hành vi
   đã tạo ra defect gốc: thay config cho tới khi số đẹp. Muốn đổi thì phải validate lại từ đầu với
   DSR/PBO và quant-skeptic.
