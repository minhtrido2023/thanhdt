# REPORT V1D / V1E / V3A' / V4 — capacity nhân quả của pin LAG @50B (EXPLORATORY)
Job Taylor_20261020_162558 (theo khuyến nghị skeptic `logs/verify_20261020_160452_37110.log`). PREREG: V1D 2c1a3a71, V1E 12daef05,
V3A' 4b52b717, V4 a210a290 (commit 4482feb6a, TRƯỚC khi tính). Bản sao engine dbe28b85f (`eng/`; `eng_dep1m/` là symlink).
Không sửa pin/registry/pin_ledger/engine thật; **không đề xuất đổi luật**. Chân: p30_pin0 / p30_pin1M / p0_pin0 / p0_pin1M.

## Control + self-check
Control cuối `vz_ctlG_*` (mọi knob off): md5 CSV = 4707bcbe / bcd0469f / 537e349b / a6ba34d8 — **4/4 byte-identical**.
20/20 run biến thể: EXIT=0, `[selfcheck BAL/LAG] ... = 0 VND` (2/2 dòng), METRIC max err 0 VND (`out_metrics_*.csv`).

## Δ so pin (pp) — `out_metrics_V1D_V1D0.csv`, `out_metrics_V1E20.csv`, `out_metrics_V1E60.csv`, `out_metrics_V3Ap.csv`
| Biến thể | ΔCAGR theo chân | ΔSharpe | ΔMaxDD | ΔIS 14-19 | ΔOOS 20+ | Nhãn sàn 0,46 |
|---|---|---|---|---|---|---|
| V1A (cũ) block Volume=0 | −0,43 / −0,62 / −0,20 / −0,98 | −0,17…−0,10 | −4,6…−3,2 | −2,1…−1,9 | −0,1…+1,6 | 2/4 |
| **V1D** V1A + chặn mua/bán LAG khi ADV3M≤0 | **+1,79 / +2,03 / +1,81 / +1,25** | −0,11…−0,06 | −2,58…+0,87 | −2,64…−2,39 | +4,86…+6,49 | **vượt sàn 4/4 (DƯƠNG)** |
| V1D0 chỉ chặn ADV3M≤0 (không ZVF) | +1,38 / +1,56 / +1,07 / +0,98 | −0,16…−0,10 | −3,82…−0,08 | −3,66…−3,30 | +5,56…+6,60 | 4/4 (dương) |
| V1E20 block + trần 20%×trung vị dv(KL>0) 20 phiên trước | −0,86 / −0,40 / −0,49 / −1,07 | −0,21…−0,16 | −2,06…+0,51 | −2,77…−2,55 | +0,37…+1,88 | 3/4 (âm) |
| V1E60 như trên, 60 phiên | +0,64 / +1,22 / +1,18 / +0,32 | −0,10…−0,06 | −1,50…+0,63 | −2,53…−1,95 | +2,54…+4,97 | 3/4 (dương) |
| V1B (cũ, hindsight KL cùng phiên) | +2,50 / +2,09 / +3,31 / +1,64 | | | | | 4/4 |
| V3A' (state t−1) | +0,36 / +0,37 / +0,52 / +0,48 | +0,014…+0,027 | −0,90…+0,61 | +0,06…+0,28 | +0,64…+0,75 | 2/4 — **không đổi so V3A** |

Gia số V1D − V1A = +2,22 / +2,65 / +2,01 / +2,23pp (hiệu ứng chặn ADV3M≤0 khi đã chặn Volume=0).

## Tách book (book ref 25B riêng, tỷ VND; mô tả, không cộng ra combined) — `out_describe_*.csv`
| Biến thể | ΔBAL ref | ΔLAG ref | lô LAG (pin 1503/1545/1516/1553) | refund (pin 799…862) | % giá trị mua LAG ngày KL=0 / >20% khớp cùng ngày (pin 31% / 36–38%) | lô giữ >45 phiên | kẹt cuối kỳ |
|---|---|---|---|---|---|---|---|
| V1D | +1,5 / −5,4 / +12,5 / −3,2 | **+131,8 / +180,3 / +105,8 / +110,6** | 1781–1824 | 1051–1118 | 0% / 42–44% | 6 | 1–2 |
| V1D0 | 0 | +104,9 / +130,8 / +67,6 / +74,1 | 1897–1970 | 1228–1312 | 0% / 41–43% | 6 | 0 |
| V1E20 | **−102,8 / −126,1 / −54,5 / −110,6** | +103,8 / +138,3 / +54,9 / +66,4 | 1874–1928 | 1071–1131 | 0% / 44–46% | 0 | 0–1 |
| V1E60 | −29,2 / −17,9 / −6,0 / −50,4 | +78,9 / +110,0 / +77,9 / +90,6 | 1879–1967 | 1070–1161 | 0% / 44–47% | 0 | 0–1 |
V1E áp trần cho MỌI lệnh gọi có trần thanh khoản (BAL + LAG, cùng phạm vi V1B) ⇒ phần âm của V1E20 đến từ BAL; book LAG tăng ở mọi biến thể nhân quả.
Đếm engine `[V1D] sell_deferred` / `[ZVF] sell_blocked` là đếm phiên-lần-thử trên danh sách pending có bản trùng (cùng mã được xếp lại mỗi
phiên) ⇒ không dùng làm số lô; số lô dùng cột "giữ >45 phiên" (trần giữ 25) và "kẹt cuối kỳ".

## V4 — PnL LAG book ref của PIN theo điều kiện lệnh mua (`v4_pnl_liq.out`, `v4_pnl_by_year.csv`; hậu nghiệm, mô tả)
Z = Volume=0, X = KL>0 nhưng mua > 20% giá trị khớp cùng ngày, OK = còn lại (NA = 0 lệnh).
| Chân | % giá trị mua Z / X / OK | % PnL Z / X / OK | PnL lô tổng (tỷ) |
|---|---|---|---|
| p30_pin0 | 31,0 / 35,5 / 33,5 | 9,1 / 43,4 / 47,5 | 386,4 |
| p30_pin1M | 31,2 / 36,2 / 32,6 | 10,9 / 43,3 / 45,8 | 428,2 |
| p0_pin0 | 31,0 / 35,9 / 33,1 | 9,5 / 43,2 / 47,3 | 401,3 |
| p0_pin1M | 31,3 / 37,6 / 31,1 | 10,7 / 42,5 / 46,8 | 472,4 |
p30_pin0 theo giai đoạn: Z chiếm 6,4% PnL 2014–21 → 11,4% 2022–26; X 30,8% → 53,7%. Mua Z 2022–2026 (tỷ): 391 / 438 / 446 / 223 / 336.
Kiểm: 1 holding_id không có dòng mua (PnL 0,515 tỷ, không phân bổ); 1 lô còn dư cổ phiếu >1%.

## Trả lời câu hỏi cốt lõi
1. **Phần Volume=0 / ADV3M≤0 của pin LAG KHÔNG phải nguồn lợi nhuận**: chặn nó một cách nhân quả (V1D/V1D0) làm CAGR combined TĂNG
   +1,0…+2,0pp và LAG ref +68…+180 tỷ — vốn kẹt ở lô không thanh khoản được giải phóng sang sự kiện LAG khác (lô 1503→1781–1970).
   V4 khớp chiều này: nhóm Z = 31% giá trị mua nhưng 9–11% PnL. ⇒ pin KHÔNG bị thổi phồng bởi các lệnh khớp ngày không giao dịch.
2. **Nhưng chưa thể nói pin LAG "thực thi được ở 50 tỷ"**: ở MỌI biến thể nhân quả, 41–47% giá trị mua LAG vẫn > 20% giá trị khớp
   cùng ngày (X); V4: nhóm X gánh 43% PnL pin (54% giai đoạn 2022–26). Trần 20%×ADV3M của engine không ràng buộc tham gia theo phiên.
3. **ΔCAGR nhân quả = dải, dấu không ổn định theo định nghĩa trần**: V1D +1,25…+2,03 · V1E60 +0,32…+1,22 · V1E20 −1,07…−0,40
   (âm do BAL). ΔIS ÂM ở MỌI biến thể (−1,95…−3,66pp), ΔOOS dương (+0,37…+6,60) ⇒ Δ dồn vào 2020+, không đồng nhất IS/OOS —
   theo quy chuẩn "edge rớt IS/OOS" thì không dùng được như bằng chứng cải thiện. Khớp tiền lệ LIQ_ZERO_BLOCK 2026-08-02 (+4,08pp,
   skeptic INCONCLUSIVE: chưa tách "vốn chảy sang event tốt hơn" khỏi "sổ không fill nổi") — vẫn CHƯA tách được ở đây.
4. V3A': state(t−1) đổi ΔCAGR ≤0,05pp/chân; nhãn giữ "vượt sàn 2/4 chân".

## Giới hạn
Không có trần tham gia THEO PHIÊN nhân quả nào được đo (cần KL dự báo trước phiên); V1D hoãn bán vô hạn ≠ live (thoả thuận/khớp lẻ);
không mô hình slippage; DSR/PBO không tính (exploratory, không đề xuất luật); mã hủy niêm yết ngoài panel (V2).
