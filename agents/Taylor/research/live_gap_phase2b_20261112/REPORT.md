# GĐ2-B — vòng 2 áp required_change của quant-skeptic cho GĐ2A (job `Taylor_20261112_125912`, 12/11/2026)

Brief: `brief.md`. Không wire, không đổi production, không đề xuất luật. Mọi số đo trong phiên này từ file trong thư mục (md5: `MD5SUMS`).
Code: `build_panel.py` (panel), `analyze.py` (đơn biến/H1–H4/placebo/power), `episodes.py` (H5). Tag tập: `liqz_all` (ledger dựng lại với `LIQ_ZERO_BLOCK=lag`),
`old_adv100` (ledger cũ lọc `adv_pct<=100`), `*_nativefee` (độ nhạy phí engine gốc).

## 0. Trả lời 3 câu (ngắn)

**(a) Có đặc trưng nào phân loại deal BAL/LAG bền IS→OOS trên tập giao dịch được không? KHÔNG.**
0 đặc trưng qua BH-FDR (q<0,10) ở CẢ IS lẫn OOS, trên cả hai tập sạch. Placebo (hoán vị excess trong năm, 20 lần): số "qua cả hai" TB 0,00 (liqz_all) / 0,05 (old_adv100);
số phát hiện OOS riêng lẻ của placebo TB 6,75 / 6,70 vs thật **1 / 1** ⇒ thật không vượt placebo.
Sống sót lẻ (mỗi ô một era, và khác nhau giữa hai tập ⇒ không bền): `FSCORE` LAG IS (liqz_all, ρ +0,195, q 0,042) · `D_RSI` LAG IS (old_adv100, ρ +0,247, q 0,041) · `dd52` BAL OOS (liqz_all, ρ +0,223, q 0,043) ·
`pe_rel5y` LAG OOS (old_adv100, ρ +0,141, q 0,085 — **dấu ngược** với IS −0,140). **Biến mất sau khi làm sạch:** `log_adv20` (liqz_all: LAG IS −0,018 / OOS −0,079; BAL −0,101 / −0,017 — đặc trưng "duy nhất dương cả hai era" của GĐ2A chỉ là sản phẩm của fill ảo) và H1-IS (xem §3).
**(b) H5 sau khi đo đúng:** trên chuỗi lãi PIT thật (fiinprox dep1m, kỳ hạn 1 THÁNG) theo episode, hiệu ứng "−11,6pp" của GĐ2A **không còn**: Δ gộp −1,18pp thô / −0,37pp sau khử mức năm (7 episode, liqz_all); 4/6 episode âm, nhưng cả hai band đảo dấu khi bỏ 2026. N độc lập = 2–7 episode ⇒ **không kết luận được, không có bằng chứng ủng hộ**. H5 bản cũ (hurdle không-PIT) vẫn ra −13,3pp nhưng mang cờ biết-trước ⇒ không dùng.
**(c) KHÔNG phát hiện được vì lực thấp:** hiệu ứng đặc trưng–excess có ρ ≲ 0,25–0,3 ở ô nhỏ (BAL IS: 72 sự kiện/28 tháng). MDE Fisher (80% lực, α 0,05, n_eff sau ICC tháng): ρ 0,24–0,36; theo số tháng (cận bảo thủ): 0,42–0,52. Lực mô phỏng ở ρ=0,20 và 0,15 xem §5. "Không có nền" → **"không phát hiện được ở ρ≈0,2 với 28–43 cụm tháng"**; không phải bằng chứng vắng mặt.

## 1. Panel fidelity (việc 1)

- **Ledger dựng lại** `LIQ_ZERO_BLOCK=lag`, cấu hình C1fix_v3: code vá `sb_liq` (sandbox đóng băng như 1b), data CURRENT frozen, AUDIT_END 2026-06-19, `NAV_TOTAL_B=50 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off`, threads=1.
  Ledger md5 `151bd903c7ef3f59ed7e9787e8aa4322` (`ledgers/`, tên có `_liqzblag`). **Self-check 0 VND: BAL err = 0, LAG err = 0, NAV identity err = 0** (`engine_liqz.log` dòng 72–75). Chạy 431s, exit 0.
- **Báo cả hai tập:** ledger mới: 888 deal có nhãn (BAL 268 / LAG 620), tỷ lệ deal có mua > 100% ADV20: BAL 6,0% / LAG **7,4%**.
  Ledger cũ: 932 (BAL 268 / LAG 664), LAG **45,6%** (BAL 6,0%); lọc `adv_pct<=100` ⇒ 608 deal (LAG 159 IS + 198 OOS = 357 sự kiện sau gộp).
- **Vì sao 303/664 deal LAG cũ mua median 8,4 tỷ/phiên ở mã adv20 ~3 tr** (đọc code, chưa đo từng mã): (1) `simulate_holistic_nav.py` L1198–1212: `liquidity_lookup[(tk, ngày)]` thiếu key hoặc ≤0 và
  `liquidity_require_positive=False` ⇒ `daily_max` giữ nguyên `remaining_value` ⇒ mua TRỌN size trong 1 phiên, bỏ qua trần thanh khoản; (2) `pt_v23_audit_2014.py` L265–290/L1403: cờ chỉ bật khi `LIQ_ZERO_BLOCK=lag|both`, mặc định tắt (legacy, giữ tên file pin cũ);
  (3) xác nhận bằng hiệu ứng: bật cờ ⇒ tỷ lệ LAG >100% ADV rơi 45,6% → 7,4% và nhãn LAG 664 → 620. Phần 7,4% còn lại là deal có ADV đo được nhưng ramp 3 phiên vẫn vượt — chưa tách.

## 2. Bảng đơn biến + H1–H5 trên tập giao dịch được (việc 2)

Họ FDR thực: `liqz_all` **83 (IS) / 86 (OOS)**; `old_adv100` **82 / 85** (GĐ2A ghi sai 90). Cột KHÔNG BAO GIỜ kiểm (hằng/nhị phân/thiếu): `cfoa_pos` (nhị phân), `dt5g_state`, `dt5g_cand_clock` (gần hằng), `refi_chg6m`, `comm_chg3m`.
`dd52` là biến **cấp mã** (drawdown 52 tuần của chính mã), không phải vĩ mô; câu "không phân biệt được với hiệu ứng năm" của GĐ2A **bỏ**: bootstrap theo tháng và hoán vị-trong-năm cho kết quả trái chiều ở nhiều cột (vĩ mô gần hằng trong năm), không phép nào phân xử ⇒ đọc theo placebo (§0a), không theo p đơn lẻ.

| H (khai trước) | liqz_all IS Δ (n trong/ngoài) | liqz_all OOS Δ | old_adv100 IS | old_adv100 OOS |
|---|---|---|---|---|
| H1 LAG SUE≥P67 & ey_pct≥2/3 | +3,86 (36/253, p 0,168) | +6,84 (28/294, p 0,062) | +2,56 (p 0,384) | +6,04 (15/174, p 0,313) |
| H2 BAL ey−hurdle>0 ⚑ | +3,07 (p 0,560) | +7,90 (123/62, p 0,053) | +1,66 (p 0,869) | +7,67 (p 0,070) |
| H3 hàng hoá 3T tăng | +10,2 (17/21, p 0,097) | +2,41 (p 0,519) | +7,98 (p 0,488) | −0,35 (p 0,970) |
| H4b LAG edge<20 vs ≥20 | +1,30 (p 0,664) | −5,10 (47/281, p 0,337) | −1,69 (p 0,593) | −3,42 (p 0,523) |
| H5 hurdle 3T tăng ⚑ (hurdle không-PIT) | +3,83 (p 0,295) | −13,29 (95/423, p<0,001) | +2,00 (p 0,600) | −16,60 (64/311, p<0,001) |

H1-IS (GĐ2A: +6,83pp, p 0,011) **không còn** trên tập sạch (+3,86, p 0,168 / +2,56, p 0,384) ⇒ gỡ khỏi kết luận. Không H nào qua ngưỡng nào ở cả hai era. ⚑ = hurdle không PIT (§3).
Mức quality OOS thật (thay "quality bị bác"): `ROE_Min5Y` BAL ρ +0,084 (p 0,276) / LAG +0,009 (p 0,837); `ROIC5Y` BAL +0,126 (p 0,024, q 0,295) / LAG −0,010 (p 0,919) (liqz_all, OOS).
IS: `ROE_Min5Y` BAL −0,206 / LAG +0,064; `ROIC5Y` BAL +0,141 / LAG −0,049. ⇒ quality **không được ủng hộ cũng không bị bác**: ρ nhỏ, CI chứa 0, dưới MDE (§5).
Value LAG sau làm sạch: IS `ey` +0,145 (q 0,567), `comp_v3` +0,139 (q 0,567), `pe_rel5y` −0,036; OOS +0,084 / +0,038 / +0,136 — tất cả không qua FDR. "Value LAG mạnh IS, chết OOS" của GĐ2A là hiệu ứng fill ảo, **gỡ**.
Sự kiện (liqz_all, excess TB / trung vị): BAL IS 72 sk +2,80/−2,15 · BAL OOS 190 +10,01/+5,31 · LAG IS 292 +3,92/+1,94 · LAG OOS 328 +8,26/+6,93. Số tháng độc lập 28–43 ô (`events_liqz_all.csv`).

## 3. Hurdle — cờ "bias biết-trước" (việc 3)

`hurdle_pit` (12T) có 26 mốc neo hồi tố 2026-06-19 (registry `kb/data_registry/macro/deposit_rate_vn.md` caveat b) ⇒ **KHÔNG PIT**. Cờ ⚑ bias biết-trước gắn cho: `hurdle_pct`, `hurdle_chg3m`, `spread_ey_hurdle`, `spread_mkt_hurdle`, `radar_score`, H2, H5 (bản hurdle_pit).
Nhãn excess dùng hurdle: **hindsight chấp nhận được vì nhãn là ex-post**; nhưng hurdle làm ĐẶC TRƯNG/ĐIỀU KIỆN vào là lỗi nhìn trước ⇒ các kết quả trên không dùng làm bằng chứng.
Bỏ cụm "OOS qua Bonferroni". H5 hạ thành **giả thuyết hình thành từ chính 2022–23/2026**, không có kiểm định ngoài mẫu.

## 4. H5 theo episode trên chuỗi PIT thật (việc 4)

Chuỗi: fiinprox dep1m (Big-4 cá nhân **kỳ hạn 1 tháng**, PIT thật 2019-02→2026-09, tháng T dùng từ ngày 1 tháng T+1) — **khác 12T** của hurdle_pit. CCTG (`cctg_rate_vn`): 1 anchor + 3 mốc từ 2026-10 ⇒ không dựng được episode, không dùng.
"Tăng" tại t: dep1m_known(t) − dep1m_known(t−91d) ≥ band; episode = cụm tháng liên tiếp. Δ = TB excess trong episode − TB excess ngoài mọi episode (cùng vùng 2019-05→). Không dùng chuỗi mốc tay. N độc lập = số episode.

| liqz_all, band>0 (7 episode) | n | Δ thô (pp) | Δ sau khử mức năm |
|---|---|---|---|
| 2021-05→07 | 22 | +14,12 | +3,91 |
| 2021-10 | 23 | +6,93 | −3,28 |
| 2022-05 | 0 | — | — |
| 2022-07→08 | 11 | −6,32 | −1,69 |
| 2022-11→2023-03 | 14 | −0,38 | +0,38 |
| 2025-01→03 | 26 | −4,53 | −0,49 |
| 2026-02→05 | 28 | −15,14 | −1,07 |
| **gộp** | 124 vs 430 | **−1,18** | **−0,37** |

Band ≥0,2pp: chỉ **2 episode** (2022-11→2023-03; 2026-02→05), gộp −10,78 thô / −0,55 khử năm. Bỏ từng năm: band>0 Δ từ −5,53 (bỏ 2021) đến −0,37, nhưng **bỏ 2026 ⇒ +2,45** (đảo dấu); band 0,2: −7,7…−13,6, bỏ 2026 ⇒ −1,32 (gần 0). Tập `old_adv100`: gộp +1,64 thô / −0,20 khử năm (band>0), −15,56 / −4,08 (band 0,2, chỉ 10 sự kiện trong).
Đọc: 2/6 episode dương, 4/6 âm thô; sau khử mức năm biên độ ≤ ~4pp, dấu lẫn lộn. IS 2014–18: chuỗi PIT thật chưa có ⇒ không kiểm được (chuỗi dựng lại `idle_rate_proxy` baseline cho 0 episode tăng ≥0,2, `recon_IS`). **Kết luận (b): sau khi đo đúng, H5 không còn bằng chứng; không bác được vì N≤7.**

## 5. Họ FDR, placebo, lực (việc 5)

- Họ: §2. Placebo q10: liqz_all IS TB 0,40 (max 2) / OOS TB 6,75 (trung vị 5,5, max 17); old_adv100 IS 0,90 / OOS 6,70. Thật: 1/1 trên cả hai tập.
- ICC theo tháng của excess (liqz_all): BAL IS 0,085 · LAG IS 0,209 · BAL OOS 0,152 · LAG OOS 0,400 ⇒ n_eff 63 / 132 / 117 / 86. MDE Fisher (α 0,05, lực 80%) ρ: 0,35 / 0,24 / 0,26 / 0,30 (α 0,01: 0,41 / 0,29 / 0,31 / 0,36); theo số tháng: 0,51 / 0,42 / 0,45 / 0,43. (`mde_*.csv`; công thức `tanh((z_a/2+z_b)/√(n_eff−3))`, tương đương `rnd_preflight_power` — chưa chạy script đó.)
- Lực mô phỏng (bootstrap-theo-tháng, 80 lần, α 0,05), liqz_all, ρ thật 0,10 / 0,15 / 0,20: BAL IS 0,15 / 0,28 / 0,51 · LAG IS 0,36 / 0,68 / 0,90 · BAL OOS 0,31 / 0,51 / 0,75 · LAG OOS 0,46 / 0,70 / 0,98. Tập old_adv100 (nhỏ hơn) ở ρ=0,20: BAL IS 0,48 · LAG IS 0,66 · BAL OOS 0,75 · LAG OOS 0,74 (`power_*.csv`).
- **Không phát hiện được:** ρ<~0,25 ở BAL IS và mọi ô tập old_adv100; hiệu ứng nhỏ kiểu quality (ρ~0,1) ở mọi ô.

## 6. Cơ sở phí & FIFO live (việc 6)

- Engine native: mua 0,15% (BAL) / 0,25% (LAG), bán 0,35–0,85% (gồm thuế + trượt giá); live: 0,097%/chiều, thuế bán 0,1%. **Cơ sở thống nhất (nhãn chính):** quy engine về phí live — mua ×(1+0,097%), bán ×(1−0,097%−0,1%) (`build_panel.py` `FEE_LIVE`, `TAX_SELL`; cùng cơ sở cho deal live).
  Độ nhạy phí native (`*_nativefee`): H5 OOS old_adv100 −16,5pp vs −16,6pp; IS +1,99 vs +2,00 ⇒ kết luận không đổi theo cơ sở phí. Không tách trượt giá engine riêng.
- **FIFO live đã sửa:** lô đóng một phần tách thành deal đóng (đủ nhãn) + deal mở (hậu tố `_C`/`_O`); lệnh bán book X hết lô X thì trừ lô book khác cũ nhất (cờ `sold_by_other_book`). Kết quả live: 12 deal đóng gắn nhãn, 10 mở.
  SCL 26/10→30/10 cả 2 TK: **−7,70%** ret / −7,78pp excess; SCL 10/08→30/10: SpaceX +18,00pp / ZaloPay +19,32pp; VPB ZaloPay 26/10→29/10 **−2,64pp**; VPB SpaceX 26/10→04/11 **−5,51pp** (đóng bằng lô PARK gán book khác, cờ). VPI 4 dòng −21,2…−21,8pp; CSV −0,24pp.
  Chỉ 12 deal / 4–5 mã độc lập: không suy luận thống kê (như GĐ2A).

## 7. Giới hạn đã biết
- Nguyên nhân 303 deal LAG ADV~3tr suy từ code + hiệu ứng, chưa liệt kê từng mã. 7,4% LAG >100% ADV còn lại chưa tách.
- H5 N≤7 episode; 2022-05 tháng có 0 sự kiện. Chuỗi 1T ≠ hurdle 12T; không có chuỗi 12T PIT.
- `rnd_preflight_power.py` chưa chạy, dùng công thức tương đương + mô phỏng.
- Không đa biến, không wire. Quant-skeptic CONFIRMED vẫn là điều kiện trước mọi bước tiếp.
