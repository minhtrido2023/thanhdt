# REPORT V1 — Volume=0 trong pin cơ sở (EXPLORATORY)
Job Taylor_20261020_122917 → tiếp tục Taylor_20261020_153324 (V1B/V1C chạy lại sau reboot). PREREG_V1.md md5 e88d1e23 (9e309ac8b).
Bản sao engine `eng/`, `eng_dep1m/` (simulate_holistic_nav.py giống hệt nhau). Không sửa engine thật/pin/registry; không đề xuất đổi luật.
Ngữ nghĩa (user xác nhận): Volume=0 = không có giao dịch khớp.

## (a) Mô tả (v1a_describe.out, v1a_adv.json)
- LAG mua: 498–505/4267–4500 lệnh khớp ngày KL=0 ≈ **31% GIÁ TRỊ mua LAG**; LAG bán: ≈ 27% giá trị (gần hết reason TIME).
  ~99% giá trị các lệnh này nằm ở dòng giá carry (O=H=L=C và = Close phiên trước).
- BAL: 0 lệnh mua KL=0; bán 1–2 lệnh (HPX 2023-10-10). ETF_PARK: không có trong cache ticker (miss) — giới hạn, ngoài phạm vi.
- Phân tầng theo ADV 3M (`Volume_3M_P50`): **gần trọn 31% kia rơi vào mã có ADV3M ≤ 0** — engine BỎ QUA trần 20%×ADV khi ADV ≤ 0
  (mua trọn size 1 phiên); thêm ~13% giá trị mua LAG ở mã ADV3M ≤ 0 nhưng phiên đó KL>0. Tức ~44% giá trị mua LAG pin không bị trần thanh khoản.

## (b)+(c) Δ so pin (pp), 4 chân — out_metrics_V1A.csv, out_metrics_V1B_V1C.csv
| Biến thể | ΔCAGR | ΔSharpe | ΔMaxDD | ΔIS 14-19 | ΔOOS 20+ | Nhãn |
|---|---|---|---|---|---|---|
| **V1A block (CHÍNH)** | −0,98…−0,20 | −0,17…−0,10 | −4,6…−3,2 | −2,1…−1,9 | −0,1…+1,6 | **vượt sàn ở 2/4 chân** (p30_pin1M −0,62, p0_pin1M −0,98) |
| V1B block_advbuy* | +1,64…+3,31 | −0,11…−0,01 | −2,5…−2,1 | +1,1…+1,9 | +1,9…+4,7 | vượt sàn 4/4 (dấu DƯƠNG) |
| V1C block_advboth* | +1,82…+3,34 | −0,09…+0,05 | −2,7…−0,9 | +1,9…+3,0 | +1,7…+3,7 | vượt sàn 4/4 (dấu DƯƠNG) |
\* giả định mô hình hoá.

- V1A: MaxDD xấu thêm 3,2–4,6pp ở cả 4 chân, đáy dời về 2019-03→2020-03; LAG ref NAV cuối giảm (vd p30_pin0 439→397B), số lô LAG tăng
  1503→1558 (lệnh hoãn khớp phiên sau). Năm tệ nhất Δ: 2019 (−5,2…−6,1pp); 2021 tốt hơn (+3,5…+10,6pp).
- **V1B/V1C Δ dương KHÔNG phải "Volume=0 có lợi"**: biến thể THAY trần ADV3M bằng 20%×KL CHÍNH phiên khớp. Ngày sự kiện LAG có KL >>
  trung vị 3M ⇒ trần nới ra: tổng mua LAG 8.459→12.620B (p30_pin0), số lô 1503→1936. Đây là dùng KL cùng phiên (không biết lúc mở cửa =
  hindsight, PREREG §5) ⇒ V1B/V1C là cận LẠC QUAN về thanh khoản, không phải stress. So V1B−V1A = +2,6…+3,5pp = hiệu ứng nới trần, tách
  khỏi hiệu ứng Volume=0 (V1A).
- Đếm engine (`[ZVF]`, LAG lượt chính): V1A buy_blocked 3882–3908 phiên-lệnh; V1C sell_capped 8626–8912. sell_blocked đếm MỖI lần thử lại/phiên.

## Control + self-check
Control `ZVF_MODE=off` 4 chân byte-identical với pin (logs/vz_ctl_*, phiên trước) — chạy lại cuối job ở REPORT tổng.
Mọi run V1A/B/C: log `[selfcheck BAL/LAG] ... = 0 VND` (2/2); METRIC max err ≤ 0,001 VND (dư số thực).

## Giới hạn
Trần KL ngày (V1B/C) không nhân quả; lệnh hoãn khớp Open phiên sau là cơ học, không phải ước lượng slippage; ETF_PARK ngoài phạm vi;
mã đã hủy niêm yết ngoài panel → V2.
