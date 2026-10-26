# REPORT — Chu kỳ hàng hoá từ bảng TE mới (job Taylor_20261026_075337, 2026-10-26)

Chỉ nghiên cứu. Không wire, không sửa production, không đổi pin/registry. Mọi số dưới đây đo trong phiên này;
file nguồn ghi cạnh từng mục. PREREG-3 (B3) commit `da1681489`, md5 `645855027e026fe87de04e00ca877df7`,
commit trước khi chạy `b3_patterns.py`.

## Trả lời 4 câu hỏi của user

1. **Có bổ sung được tín hiệu cho cổ phiếu chu kỳ hàng hoá không?** Có, nhưng là tín hiệu về **KQKD**, không phải
   tín hiệu về **giá cổ phiếu**. Giá bình quân quý của hàng hoá (TE daily, biết ngay sau khi quý kết thúc, trung vị
   29 ngày trước khi BCTC ra) dự báo tốt tăng trưởng doanh thu (IC 0,44) và lợi nhuận (IC 0,45) của mã sản xuất
   (**kết luận**, giữ được ở OOS 2023+). Nhưng giá cổ phiếu đã phản ánh phần này trong chính quý đó. Thị trường chỉ
   phản ứng với phần LN mà hàng hoá **không** giải thích được.
2. **Model hiện có có cần chỉnh không?** **Không.** Trong ledger pin hiện hành, nhóm mã sản xuất hàng hoá đóng góp
   18,2% PnL và có lợi suất trên vốn cao hơn nhóm còn lại. Không đo được bẫy value ở đỉnh chu kỳ gây hại trong
   BAL/LAG/custom30V. Mẫu ở đáy chu kỳ quá nhỏ (n = 2, 7 và 22) để kết luận theo chiều nào.
3. **Có pattern nào dự báo chu kỳ hàng hoá và giá cổ phiếu không?** **Không có pattern nào qua cổng.** Đã thử 13
   trial đăng ký trước. p Bonferroni nhỏ nhất là 0,31, BH q nhỏ nhất 0,27. Cổ phiếu chạy **cùng tháng** với hàng hoá
   (IC 0,23) nhưng không có độ trễ khai thác được (IC 0,04 đến 0,05 ở trễ 1–3 tháng). Ô momentum 1,05 (phát hiện
   post-hoc trước đây) cho +5,8pp nhưng p = 0,13, và gần như bằng 0 (+1,0pp) ở 3 họ hàng hoá mới.
4. **Nên tận dụng chu kỳ hàng hoá thế nào?** Dùng như **công cụ đọc KQKD** (display, kiểm tra plan, phân loại
   surprise cho LAG), không dùng như tín hiệu mua/bán. Chi tiết theo nhóm ở §6.

## 1. B1 — Kiểm kê 103 mã TE (`te_inventory_raw.csv`, `te_key_stats.csv`, `commodity_map_te.csv`)
Nguồn: `commodity_prices` với `source='trading_economics' AND cadence='daily'`, 237.934 dòng, 2016-10-25 → 2026-10-23
(`fetch_te.py`). Freshness (`data/commodity_freshness_state.json`, ref 2026-10-26): 228 OK, 1 STALE (tea).
Bản đồ mới `commodity_map_te.csv` có 55 dòng / 24 họ (tier A 25 mã = panel chính, B 13, D 17 chỉ mô tả). Bản
`commodity_map.csv` đóng băng của PREREG-2 không bị đụng.

**Hổng mà TE đã lấp:** BDI ngày từ 2016-10 (trước đây chỉ có từ 2026-05) → VOS. Chỉ số container ~SCFI từ 2016
(81% phiên đứng giá, tức cập nhật theo tuần) → HAH. Thép cây SHFE CNY/t từ 2016 (chuỗi thép đầu tiên của fleet)
→ HPG/TLH/POM/SMC. Cao su TSR20 ngày. Urê và DAP ngày từ 2019-06. Crack Spread Index → BSR. Thêm các đầu vào
ngược chiều: quặng sắt, than cốc (HPG), lưu huỳnh (DAP/lân), PVC (BMP/NTP).

**Bẫy mới (đều đã đo):**
| metric_key | Bẫy |
|---|---|
| `phosphorus` | ~1.000 CNY/t là **quặng photphat**, không phải P4 vàng (cỡ 20–30k CNY/t, `ước lượng` theo hiểu biết thị trường). Chỉ có từ 2022-08, 94% phiên đứng giá, 43 giá trị khác nhau ⇒ vô dụng cho DGC/PAT |
| `hrc_steel` | USD/t, đỉnh 1.945 năm 2021 ⇒ HRC **Mỹ**, không phải HRC TQ/VN |
| `rice` | Gạo thô CBOT USD/cwt, không phải gạo VN 5% |
| `coffee` | Arabica; VN sản xuất Robusta |
| `lean_hogs` | CME Mỹ, không đồng pha heo hơi VN |
| `soda_ash` | Soda (Na2CO3), không phải xút (CSV) |
| `sulfur` | Năm 2026 lên tới 11.084, so với trung vị 653 năm 2020 (×7). Chưa xác minh đơn vị/series |

**Hổng còn lại:** vonfram APT (MSR, vẫn không có gì) · xút · P4 · cước tàu dầu BDTI/BCTI (PVT/VIP/GSP) · heo hơi VN
trước 2019 · cá tra/tôm · hồ tiêu, điều, Robusta, gạo VN theo ngày · HRC TQ/VN · kali.

## 2. B2 — Nowcast KQKD (`b2_nowcast.py`, `b2_decomp.py` → `b2_pooled.json`, `b2_ic_family.csv`, `b2_decomp.json`)
**Thiết kế:** c_yoy = log(giá TB quý Q ÷ giá TB quý Q−4) của hàng hoá, nhân dấu của họ. Tín hiệu biết được từ
qend+2 ngày và chỉ giữ khi có trước ngày công bố. Biến đích là BCTC **bản công bố đầu tiên** (theo `Release_Date`,
chống restate):
- rev_yoy = log(DT_P0/DT_P4)
- np_d = (LN_P0−LN_P4)/DT_P4
- gpm_d = biên gộp P0 − P4

Phản ứng giá được đo vượt trội so với bình quân đều universe_pit:
- pre: từ ngày có tín hiệu đến trước ngày công bố
- ann: từ phiên trước ngày công bố đến phiên đầu tiên sau ngày công bố
- post60: 60 phiên từ phiên đầu tiên sau ngày công bố

N độc lập = họ × quý (8 họ, 36 quý, 250 quan sát). CI bootstrap theo quý; p theo circular-shift permutation.

| Quan hệ (gộp tier A) | IC | CI90 | p | IS / OOS |
|---|---|---|---|---|
| c_yoy → rev_yoy | 0,443 | [0,35; 0,53] | 0,0005 | 0,37 / 0,41 |
| c_yoy → np_d | 0,450 | [0,32; 0,55] | 0,0005 | 0,50 / 0,35 |
| c_yoy → gpm_d | 0,233 | [0,12; 0,34] | 0,049 | 0,21 / 0,30 |
| c_qoq → np_qd | 0,261 | [0,14; 0,37] | 0,0005 | 0,25 / 0,24 |
| c_yoy → ann | 0,105 | [−0,03; 0,23] | 0,097 | 0,16 / 0,14 |
| c_yoy → post60 | −0,020 | [−0,16; 0,12] | 0,78 | 0,01 / −0,11 |

Theo họ (IC với np_d): urê 0,93, BDI 0,63, DAP 0,53, container 0,49, cao su 0,48, đường 0,43, thép SHFE 0,35,
dầu thô 0,03. Dầu gần như không dự báo được LN của PVS/PVD/GAS, vì phơi nhiễm có độ trễ hợp đồng. Ở tier B,
crack spread → BSR có IC 0,69. Đầu vào ngược chiều cho dấu đúng: quặng sắt → HPG −0,49, than cốc −0,47, lưu huỳnh
→ DAP −0,35.

**Tách surprise (POST-HOC, N = 30 quý).** np_hat là phần LN do hàng hoá giải thích, fit expanding chỉ bằng dữ liệu
quá khứ (PIT); IC với np_d thực là 0,30. Phản ứng công bố với np_hat có b = 0,08 (t = 1,6), với phần dư có
b = 0,17 (t = 3,3). Ở post60, phần dư có t = 2,0. Phần hàng hoá ở OOS có b = −0,13 (t = −2,3), tức là LN tăng nhờ
hàng hoá còn có xu hướng bị bán sau công bố. Hàm ý cho LAG: một SUE dương chủ yếu do giá hàng hoá **không phải là
bất ngờ**. Đây là **giả thuyết cần PREREG**, chưa phải kết luận.

Self-check: tính lại tay DPM 2023Q2 và DRI 2021Q1 từ BQ; c_yoy, rev_yoy, np_d khớp tới 1e-4.

## 3. B3 — Pattern chu kỳ → giá cổ phiếu (`b3_patterns.py` → `b3_results.json`; PREREG-3)
| Giả thuyết | Kết quả | p | Bonf×13 | BH q |
|---|---|---|---|---|
| H-a ô chính θ 1,05 / MA252 / 63 phiên | TB cụm +5,8pp CI90 [+0,4; +11,3], 36 sự kiện / 6 cụm, MDE 9,1pp, đường nền +2,7pp, IS +4,5 / OOS +18,6, LOFO min +3,9 | 0,128 | 1 | 0,32 |
| H-a, chỉ 3 họ MỚI (thép/BDI/container) ở ô chính | +1,0pp, 12 sự kiện / 6 cụm | 0,39 | – | – |
| H-a ô tốt nhất θ 1,10 / 252 / 63 (chọn sau) | +6,4pp, 9 cụm, 7/9 dương | 0,024 | 0,31 | 0,27 |
| H-b trễ 1 / 2 / 3 tháng | IC 0,041 / 0,052 / −0,042 | 0,24 / 0,17 / 0,25 | 1 | ≥0,32 |
| H-b (mô tả) đồng thời k=0 | IC 0,228, IS 0,23 / OOS 0,25 | 0,0005 | – | – |
| H-b (mô tả) cổ phiếu dẫn k=−1 | IC −0,027 | 0,46 | – | – |
| H-c bẫy value đỉnh chu kỳ (giả thuyết: âm) | +1,3pp (**sai dấu**), SE 6,6pp, 34 / 13 đơn vị | 0,38 | 1 | 0,45 |
| H-d gap hàng hoá tăng, cổ phiếu chưa tăng | −2,6pp (**sai dấu**), 35 / 266 | 0,77 | 1 | 0,77 |

**Kết luận B3:** không có edge giao dịch đạt cổng. H-a dương nhưng underpowered (MDE 9pp, 6–9 cụm). Ở 3 họ hàng hoá
mới, nơi phép thử thực sự là ngoài mẫu, nó gần như bằng 0. Đọc cùng nghiên cứu WB, ô 1,05/3M là một ứng viên yếu,
nên để paper PREREG-2 tự trả lời; không nên mở thêm biến thể. Cổ phiếu định giá cùng nhịp với hàng hoá, nên
"mua khi hàng hoá vừa tăng mà cổ phiếu chưa chạy" không có cơ sở.

Self-check: tính lại tay sự kiện steel_cn 2017-11-07 từ parquet được X = 0,115451, khớp file.

Ghi chú diễn giải PREREG: ở H-d, cụm "≥24 quan sát" được hiểu là ≥24 điểm c63 theo ngày (lịch sử expanding),
không phải 24 mẫu quý. Ở H-a, cụm được nối chuỗi (chain), nên có cụm kéo dài hơn 1 năm. Cách này bảo thủ vì cho ít
cụm hơn.

## 4. B4 — V2.4 đối xử mã chu kỳ (`b4_model_audit.py`, `b4b_custom30v.py`)
Ledger: chỉ đọc `data/pinned_ledgers/2026-10-08__R3-park0-pin0pct-SAN__537e349b.csv.gz` (đầu SÀN), 1.912 holding đã đóng.

| Book | Nhóm | Holding | PnL (tỷ) | % tổng PnL | Lợi suất / vốn mua |
|---|---|---|---|---|---|
| BAL | producer | 51 | 40,0 | 7,2% | 12,8% |
| BAL | còn lại | 340 | 114,6 | 20,5% | 6,2% |
| LAG | producer | 86 | 61,7 | 11,0% | 8,1% |
| LAG | còn lại | 1.412 | 338,5 | 60,5% | 4,2% |

Đóng góp lớn nhất là GAS (BAL 14,7 + LAG 26,8 tỷ) và DGC (LAG 9,7 tỷ). Lỗ lớn nhất là KSV (BAL −2,7 tỷ) và DBC
(LAG −2,2 tỷ).

**Pha chu kỳ lúc vào lệnh:** pha = phân vị expanding của giá TB 63 phiên, chỉ có từ ~2018.
- BAL vào mã producer khi hàng hoá ở tercile trên 73,5% số lần, so với nền 57,5%: nghiêng nhẹ về đỉnh. Lệnh vào ở
  đỉnh có vượt trội −1,7pp so với lệnh khác cùng book ±30 ngày (n = 25). Lệnh vào ở đáy +19,3pp, nhưng n = 2, không
  đọc được.
- LAG vào ở đỉnh 61,5% số lần (nền 53,3%). Vượt trội ở đỉnh +0,4pp, ở đáy −4,4pp (n = 7).
- custom30V: mã producer chiếm 16,7% số dòng thành viên-quý. Vượt trội ở đỉnh −0,6pp/quý (n = 65), ở đáy +2,3pp
  (n = 22). Hiệu −2,9pp, CI90 [−11,2; +6,4], qua 31 kỳ rebal.

**Kết luận B4: không chỉnh model.** Lớp nhẹ nhất có thể thêm là **cờ display-only** "pha chu kỳ hàng hoá" cạnh các
mã producer trong plan/báo cáo: phân vị TB63, R/MA252 và nowcast giá TB quý YoY. Không làm gate, không làm tilt.
Lý do: không có bằng chứng tác hại, mẫu đáy chu kỳ quá nhỏ, và H-c còn sai dấu.

## 5. Ảnh chụp hiện tại (`snapshot_20261023.csv`, dữ liệu tới 2026-10-23, chỉ mô tả)
Đây là nowcast cho BCTC Q3/2026 đang ra trong mùa này: thay đổi giá TB Q3 so với Q3/2025 (log), có nhân dấu theo
vai trò producer/consumer.
- **Thuận cho producer:** container +0,80 (HAH), crack spread +0,91 (BSR), BDI +0,43 (VOS), Brent +0,29
  (PVS/PVD/GAS), cao su TSR20 +0,29 (DRI/PHR/DPR/TRC/GVR; ngược chiều cho DRC/CSM).
- **Đi ngang:** thép SHFE −0,02 (HPG), urê 0,00, DAP +0,03.
- **Bất lợi:** lưu huỳnh +1,25. Đây là CHI PHÍ cho DDV/LAS/DGC, và series chưa xác minh.

Theo B2, phần này thị trường **đã biết**. Dùng để đọc xem KQKD có "đúng như hàng hoá nói" hay không, không dùng để
mua trước công bố.

## 6. Khuyến nghị (xếp theo mức tự tin)
**(1) Dữ liệu (cao):**
- Cài cron cho `commodity_freshness_monitor.py` (đang chờ user).
- Xin bq_admin bổ sung: vonfram APT, xút, P4, BDTI/BCTI, HRC TQ, giá cá tra/tôm/tiêu/điều/Robusta VN.
- Xác minh series `sulfur` 2026.
- Ghi các bẫy `phosphorus`/`hrc_steel`/`rice`/`coffee`/`lean_hogs` vào `kb/data_registry/feeds/bq_commodity_prices.md`
  (Winston sở hữu file này; Taylor chỉ đề xuất).

**(2) Hiển thị / paper (trung bình–cao):**
- Khối "nowcast KQKD theo hàng hoá" cho mã producer trong mùa BCTC (bảng §5), display-only.
- Giữ nguyên paper PREREG-2 (ô 1,05/3M, WB); không mở biến thể TE song song.

**(3) PREREG forward cần đóng băng (trung bình):**
- "LAG surprise decomposition": trong LAG, tách SUE thành phần giải thích được bởi giá TB quý hàng hoá (fit expanding)
  và phần dư.
- Giả thuyết: phần dư dự báo post-60 tốt hơn SUE thô ở mã producer.
- Đo paper từ mùa BCTC Q4/2026 (2027-01 → 2027-03). Cổng: ≥ 2 mùa BCTC, quant-skeptic CONFIRMED.
- Kết quả post-hoc hiện có là t = 2,0 ở phần dư và t = −2,3 ở phần hàng hoá OOS, trên 30 quý.

**(4) Thay đổi model:** không có đề xuất. Chưa có gì qua cổng.

**Tận dụng theo nhóm:**
- **Producer thượng nguồn** (cao su, phân bón, dầu khí, đường, thép):
  - Giá TB quý là nowcast KQKD tốt (IC 0,35–0,93 theo họ).
  - Dùng để soát plan: mã producer mà nowcast âm sâu thì LAG không nên coi SUE âm là bất ngờ.
  - Không mua theo momentum hàng hoá.
- **Người dùng đầu vào, ngược chiều** (HPG với quặng/than cốc, BMP/NTP với PVC, DRC/CSM với cao su, DAP với lưu
  huỳnh):
  - Dấu đúng ở nowcast LN (IC −0,29 đến −0,49), nên đọc biên theo chênh lệch đầu ra − đầu vào.
  - HPG cần cả thép SHFE lẫn quặng + than cốc.
- **Vận tải/cước** (VOS–BDI, HAH–container, BSR–crack):
  - Nowcast mạnh (IC 0,49–0,69).
  - H-a ở 3 họ mới không có edge giá.
  - Thiếu cước tàu dầu cho PVT/VIP/GSP.
- **Nông sản VN** (gạo, cà phê, cá tra, heo, tiêu, điều):
  - TE **không phủ đúng hạng hàng VN**; đây là hổng dữ liệu, chưa thể nghiên cứu.
  - Heo dùng `data/hog_price_vn.csv` (2019+).

## Tái lập
```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/commodity_cycle_te_20261026
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY fetch_te.py && $PY build_map.py          # B1 (BQ, source='trading_economics', cadence='daily')
$PY b2_nowcast.py && $PY b2_decomp.py        # B2 (seed 20261026 / 7)
$PY b3_patterns.py                           # B3 theo PREREG-3 (seed 20261026), ~vài phút
$PY b4_model_audit.py && $PY b4b_custom30v.py  # B4 (đọc ledger pin, không ghi)
```
Dữ liệu cổ phiếu là `data/bq_cache` (mirror BQ, vintage 2026-10-23). Không dùng `ticker_prune` và không dùng `profit_*`.
Universe = `universe_pit`, dùng cho cả hai chân nên không có MIXED-universe.

**Rủi ro tồn dư:**
- TE có thể đã sửa lịch sử (backfill một lượt 10-24/25, không có vintage).
- `PE` trong `ticker` được giả định là PIT.
- `Close` là giá điều chỉnh của bản cache hiện tại.
- B2 có 36 quý, có chồng lấn YoY; đã xử lý bằng circular-shift nhưng N hiệu dụng thấp hơn 36.
