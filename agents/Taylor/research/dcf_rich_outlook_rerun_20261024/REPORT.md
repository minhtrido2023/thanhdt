# DCF RICH — 5 kiểm tra bổ sung trước khi đổi cổng lag_dd_pack — job Taylor_20261024_045036

R&D paper, không wire, không sửa production hay artifact cũ. Ngày 2026-10-24. Nối tiếp
`../dcf_rich_outlook_20261024/` (verdict quant-skeptic: `mike/logs/verify_20261024_040741_4066620.log`).

## Kết luận

1. **Vế "RICH sâu VÀ ROE thấp ⇒ drift xấu" đứng vững.** Nó đúng ở cả 4 ngưỡng ROE5Y, khi bỏ các ca đổi số cổ phiếu,
   và khi đổi sang benchmark tổng lợi suất. **Ngưỡng 25% thì KHÔNG đứng**: nó nằm đúng chỗ nhóm ROE cao thiếu power
   (MDE 10pp). **Vế hàng hoá không đứng trên tập LAG thật.**
   - ROE thấp có BHAR60 lỏng từ −4,2 đến −6,3pp, CI loại 0 ở mọi ngưỡng 15/20/25/30.
   - Nhóm ROE cao **không bao giờ có ý nghĩa thống kê**. Ước lượng điểm của nó tăng dần theo ngưỡng: −0,7 → +0,3 →
     +4,0 → +7,7pp, trong khi n giảm từ 331 xuống 43.
2. **Miễn cho nhóm ROE≥25% chỉ là "chưa có bằng chứng bất lợi", chưa phải "an toàn".**
   - MDE (power 80%) là **10pp**. Power để bắt được một hiệu ứng −4,5pp chỉ có **28%**.
   - Ở ngưỡng 15%, MDE là 4pp. CI của nhóm ROE cao là [−3,3; +2,0], tức loại được −4,5pp (power 91%) nhưng không loại
     được −3pp (power 60%).
3. **Trên chính tập sự kiện LAG qualify, với đúng cửa sổ giữ lệnh LAG (+5→+30 phiên), RICH sâu chỉ kém −1,3pp
   [−3,7; +0,8], CI chứa 0.** Riêng nhóm ROE<25% kém −1,5pp [−3,9; +0,6]. Như vậy hiệu ứng có thật ở BHAR60 trên toàn
   mẫu surprise dương, nhưng **trên đúng đối tượng của cổng DD thì yếu và không có ý nghĩa thống kê**.
4. **Đề xuất (chỉ ĐỀ XUẤT, cần user duyệt):**
   - **Phương án B (khuyến nghị, an toàn nhất)**: chỉ đòi `dcf_override_reason` khi **RICH sâu (MoS < −100%)**,
     **KHÔNG miễn theo ROE**. RICH nhẹ và FAIR hạ xuống WARNING, kèm số (MoS, ROE5Y, bảng drift dưới đây). Lý do: việc
     thu hẹp từ MoS≤0 xuống < −100% có dữ liệu ủng hộ, vì RICH nhẹ không mang thông tin. Ngược lại, miễn theo ROE thì dựa
     vào một ngưỡng được chọn trong 4 ngưỡng thử, và trên tập LAG không có power.
   - Phương án C, nếu user muốn có miễn trừ: dùng ngưỡng **ROE5Y ≥ 15–20%, không dùng 25%**, và bỏ vế hàng hoá.
     Phải khai rõ N trials = 4 ngưỡng; 15% là ngưỡng duy nhất có power đủ để nói "loại trừ được −4,5pp".
   - KHÔNG khuyến nghị đề xuất gốc (25% + hàng hoá).

## Control (tái lập tay số cũ, bản copy panel.csv + analyze.py/robust.py)

`drift_robust.csv` mới **khớp từng byte** với bản cũ (so `round(6)`: True). Các số tái lập được:

| Chỉ số | Giá trị |
|---|---|
| NP yoy Q+1 RICH_DEEP − FAIR+CHEAP | +12,1pp [+6,9; +17,6] |
| BHAR60 lỏng, ALL | −3,4 [−5,5; −1,5] |
| BHAR60 lỏng, ROE<25% | −4,5 [−6,5; −2,7] |
| BHAR60 lỏng, ROE≥25% | +4,0 [−2,9; +10,6], n=84/44 quý |

Số ca đổi OShares >2% cũng tái lập được: **465/7.510**, trong đó RICH_DEEP là 115. Định nghĩa: max/min OShares PIT
trong [d0−30, d0+30], tính cả mức ngay trước cửa sổ. Ghi chú: định nghĩa so với d0 chỉ ra 243 ca.

## T1 — độ nhạy ngưỡng ROE5Y (BHAR60 excess của RICH_DEEP sau surprise dương; pp [CI95 bootstrap cụm quý])

| ngưỡng | nhóm | n / quý | lỏng | rank-RICH | lỏng IS 14-19 | lỏng OOS 20+ |
|---|---|---|---|---|---|---|
| 15% | ROE cao | 331 / 51 | −0,7 [−3,3; +2,0] | −1,4 [−4,2; +1,3] | +0,7 | −1,6 [−5,3; +1,8] |
| 15% | ROE thấp | 310 / 49 | **−6,3 [−8,7; −3,7]** | **−4,2** [−6,7; −1,6] | **−7,6** | **−5,8** |
| 20% | ROE cao | 175 / 51 | +0,3 [−3,4; +3,9] | −0,1 | +2,2 | −1,0 |
| 20% | ROE thấp | 466 / 50 | **−4,8 [−6,9; −2,7]** | **−3,7** | **−4,6** | **−4,8** |
| 25% | ROE cao | 84 / 44 | +4,0 [−2,5; +10,6] | +4,5 [−3,0; +12,4] | +4,3 | +3,7 |
| 25% | ROE thấp | 557 / 50 | **−4,5 [−6,7; −2,6]** | **−3,8** | **−3,7** | **−4,9** |
| 30% | ROE cao | 43 / 32 | +7,7 [−0,9; +17,8] | +9,4 [−0,3; +20,6] | +4,2 | +10,5 |
| 30% | ROE thấp | 598 / 50 | **−4,2 [−6,4; −2,2]** | **−3,6** | −3,0 [−6,1; 0,0] | **−4,7** |

- Hiệu (ROE cao − ROE thấp), ghép lỏng: +5,5 / +5,0 / +8,5 / +11,9pp; CI loại 0 ở cả 4 ngưỡng.
  Ở OOS, CI chạm hoặc chứa 0 ở mọi ngưỡng.
- BHAR20: ROE<25% −1,6 [−2,9; −0,3]; ROE≥25% +1,3 [−2,1; +4,9].
- **Ổn định:** vế ROE thấp **ổn định ở cả 4 ngưỡng** về dấu, độ lớn, và cả IS/OOS (trừ IS 30%, CI chạm 0). Vế ROE cao
  không ổn định: dấu đổi theo ngưỡng, không ngưỡng nào có ý nghĩa thống kê. Hiệu ứng thể hiện như một gradient đơn điệu
  theo ROE, chứ không phải một ngưỡng tự nhiên ở 25%.
- Hàng hoá (ALL ROE): −5,5 [−10,4; −0,6], n=83/34 quý. IS chỉ có n=11.

## T2 — Power / MDE (mô phỏng bootstrap cụm quý trên phân phối BHAR60 excess đã định tâm; t cụm-robust, α 5%)

| ngưỡng | nhóm ROE cao n / quý | ước lượng điểm | **MDE 80%** | power nếu thật là −4,5 | −3,4 | −3,0 |
|---|---|---|---|---|---|---|
| 15% | 331 / 51 | −0,7 | **4,0pp** | 91% | 72% | 60% |
| 20% | 175 / 51 | +0,3 | **5,0pp** | 71% | 48% | 39% |
| 25% | 84 / 44 | +4,0 | **10,0pp** | **28%** | 18% | 15% |
| 30% | 43 / 32 | +7,7 | **13,5pp** | 19% | 14% | 14% |

So sánh: MDE của nhóm ROE thấp chỉ 3,0–4,0pp. Trên tập LAG qualify, MDE của nhóm ROE cao là 5,0 / 6,5 / 8,5 / 17,5pp
(post_ex, theo thứ tự 15/20/25/30%).

**Đọc:** ở 25%, nghiên cứu không thể phân biệt "an toàn" với "tệ như nhóm ROE thấp". CI [−2,5; +10,6] tình cờ nằm trên
−4,5pp, nhưng power chỉ 28%. Bỏ các ca đổi OShares thì CI thành [−5,6; +8,8] và chứa −4,5pp (xem T4).
Ở 15%, kết luận mạnh hơn: tác hại (nếu có) nhỏ hơn khoảng 3,3pp.

## T3 — tập sự kiện LAG thật (`lag_live_schedule.live_lag_candidates()`: NP_R≥15 & prior_n_good≥4 & pa_HL3≥5)

- Join theo (mã, quý): khớp 7.473/7.510; **1.375 sự kiện qualify** trong 52 quý, gồm RICH_DEEP 307 · RICH_MILD 206 ·
  FAIR 204 · CHEAP 658.
- post = close d0+5 → d0+30, trừ VNINDEX cùng cửa sổ. Bản tự tính khớp `post_ret` của classified CSV với corr 0,9957.
- Ghép = khử trung bình đối chứng (FAIR+CHEAP qualify) trong cùng quý. Mẫu nhỏ nên không ghép theo ngành/cỡ.

| tập | BHAR60 | **post LAG (+5→+30)** | post IS | post OOS |
|---|---|---|---|---|
| RICH_DEEP ALL (n 302–305 / 49 quý) | −2,3 [−5,6; +0,9] | **−1,3 [−3,7; +0,8]** | −0,9 | −1,4 |
| (thô, không khử quý) | −4,2 [−8,1; −0,4] | −2,5 [−5,2; 0,0] | | |
| ROE<15% (160 / 41) | −4,2 [−8,6; +0,1] | −1,6 [−4,4; +1,0] | −3,9 | −0,7 |
| ROE<25% (265 / 47) | −3,2 [−6,7; +0,2] | −1,5 [−3,9; +0,6] | −2,3 | −1,1 |
| ROE≥15% (145 / 47) | −0,2 [−4,5; +3,7] | −0,9 [−4,0; +2,0] | +1,2 | −2,4 |
| ROE≥25% (40 / 26) | +3,4 [−4,6; +11,1] | +0,1 [−5,6; +5,8] | +4,4 | −4,6 (n=19) |
| Hàng hoá (61 / 35) | −2,6 [−7,5; +2,9] | **+0,8** [−3,2; +5,1] | | |

**Đọc:** cùng chiều với panel lớn, nhưng không ô nào có CI loại 0 trên cửa sổ LAG. Nhóm ROE≥25% chỉ có 40 sự kiện,
**không đủ để suy rộng**. Vế hàng hoá không tái hiện được (+0,8pp).

## T4 — bỏ 465 ca đổi OShares >2% ±30 ngày

| tập | BHAR60 lỏng |
|---|---|
| ALL | −3,3 [−5,7; −1,0] |
| ROE<25% | −4,0 [−6,4; −2,0] (OOS −4,2 [−6,9; −1,7]) |
| ROE<15% | −6,1 [−9,3; −3,3] |
| **ROE≥25%** | **+1,5 [−5,6; +8,8]** (n=73/40), giảm từ +4,0 |
| ROE≥15% | −0,6 [−3,4; +2,1] |
| Hàng hoá | −4,4 [−9,0; 0,0] |

Kết luận về nhóm ROE thấp **không đổi**. Ước lượng thuận lợi của nhóm ROE≥25% thì **một phần đến từ 11 ca đổi số cổ
phiếu**.

## T5 — benchmark VNINDEX tổng lợi suất

- Nguồn: `data/benchmark/vnindex_tr_daily.csv`, cột `tr_gross`. Registry ghi trạng thái CANONICAL, tự dựng: chỉ số giá
  HOSE + cổ tức tiền ước từ rổ HOSE PIT; rổ trước 2018 kém tin.
- Dùng bản gross vì Close cổ phiếu đã điều chỉnh cổ tức (gộp, chưa thuế).
- Kết quả **khác bản giá ≤0,1pp ở mọi ô**: ALL −3,4 [−5,4; −1,5] · ROE<25% −4,5 [−6,5; −2,7] · ROE≥25% +4,0
  [−2,9; +11,1] · 15%: −0,7 / −6,3. Bỏ ca đổi OShares cũng cho kết quả tương tự (`t1_t4_t5_drift.csv`, test `T5_*`).
- Lý do: excess đã ghép cùng quý × ngành × cỡ, nên benchmark gần như triệt tiêu. Cổ tức VN-Index chỉ khoảng 1,6–1,9%/năm,
  tức chừng 0,4pp trên 60 phiên (ước lượng), và chia đều cho cả hai nhóm.

## N trials, giới hạn

- Họ biến thể: 4 ngưỡng ROE × 4 cách ghép/kỳ × {giá, TR} × {đủ, bỏ ca đổi OShares}, cộng thêm tập LAG.
  **Nếu chọn 1 ngưỡng thì N trials = 4.** Ngưỡng 15% được chọn vì có power, không phải vì cho số đẹp nhất: số đẹp nhất
  cho nhóm ROE cao là 30%.
- Đây không phải chiến lược nên không có DSR/PBO.
- Các giới hạn cũ vẫn giữ nguyên: lãi suất chiết khấu có hindsight; OShares UNVERIFIED-PIT; cửa sổ 60 phiên chồng nhau;
  mẫu chỉ gồm mã có FCFE>0.
- Ở T3, ghép chỉ theo quý (không ghép ngành/cỡ) vì n nhỏ.
- ROE5Y không có NaN trong tập đã ghép.

## Tái lập

```
cd mike/agents/Taylor/research/dcf_rich_outlook_rerun_20261024
P=/home/trido/thanhdt/wc_venv/bin/python
$P analyze.py; $P robust.py      # control: drift_robust.csv == bản cũ
$P augment.py                    # panel_aug.csv (TR, OShares ±30d, LAG qualify, post_ret) ~30s
$P shchg.py                     # sh_chg_minmax.csv (465 ca)
$P rerun.py > rerun.log          # t1_t4_t5_drift.csv, t1_counts.csv, t2_mde.csv, t3_lag_qualify.csv, summary_rerun.json
```
