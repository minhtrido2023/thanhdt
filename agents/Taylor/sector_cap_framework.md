# Sector-cap cho custom30V — phương pháp & kết quả

**Job:** `Taylor_20260714_095953` · **Ngày:** 2026-07-14 · **Research-only, KHÔNG wire production.**

## 1. Câu hỏi

Basket custom30V (parking vehicle của V2.4, NEUTRAL) hiện dùng `BASKET_WT=namecap`: cap từng
tên ở 10% NAV, **không cap tổng ngành**. Tại rebal 2026-05-05, sector-8 (Financials + Real
Estate + Brokers) chiếm **95.5%** basket. Câu hỏi: cap ngành có cải thiện risk-adjusted return
không?

## 2. Định nghĩa sector-8

`sector_code = CAST(FLOOR(ICB_Code/1000) AS INT64) = 8` — đã verify trên dữ liệu thật, gồm:

| ICB | Nhóm | Ví dụ trong basket |
|---|---|---|
| 8355 | Ngân hàng | VCB CTG BID TCB VPB MBB HDB ACB SHB TPB LPB VIB MSB |
| 8633 | Bất động sản | VHM VRE IDC |
| 8773/8777 | Chứng khoán / dịch vụ TC | VIX VND SHS MBS EVF |

Đúng cụm Mike đã nhận diện (~93%). **Không phải chỉ ngân hàng** — đây là cụm tài chính rộng.

## 3. Cách đo tỷ trọng ngành (Task 1)

`mike/agents/Taylor/sector_conc_audit.py` — dựng lại basket tại **mọi** rebal q2m5 2014→nay theo
ĐÚNG công thức publisher production (`custom30_history.py`):

```
base_i = mcap_i(as-of rebal date) / Σ mcap   →   _cap_names(base, 0.10)
```

**Cross-check (bắt buộc, §6 provenance):** trọng số dựng lại khớp `data/custom30v_8l_publish.csv`
tới 4 chữ số thập phân tại rebal 2026-05-05 (VHM 0.1000, TCB 0.0894 vs 0.089388, LPB 0.0525 vs
0.052520, MBB 0.0777 vs 0.077741; set 30 tên trùng khít). → số đo dưới đây LÀ số production.

**Sector map = point-in-time**: ICB as-of ngày rebal (không dùng latest-row) → không look-ahead.
*Caveat:* nhánh `sectorcap` có sẵn trong `custom_basket.py` dùng **latest ICB** (`sec_map`, dòng
527-533). Giữ nguyên (dispatch yêu cầu chạy đúng code sẵn có); ICB gần như tĩnh nên ảnh hưởng
không đáng kể, nhưng đây là 1 điểm cần biết nếu wire.

## 4. Cách tính vốn hóa ngành thị trường (variant B)

Cap động = tỷ trọng vốn hóa THẬT của sector-8 trên toàn `ticker_prune` tại **đúng ngày rebal**:

```
mcap_i,t = Close(adj)_i,t × OShares_i(as-of, ffill từ ticker_financial)
mkt_w8_t = Σ mcap(sec=8) / Σ mcap(all sectors)        -- chỉ dùng dữ liệu ngày t
```

**Chọn `Price × OShares` hay `BVPS × PB`?** → dùng **Close × OShares**, vì đây là ĐÚNG định
nghĩa mcap mà `custom_basket.build_pit` dùng cho chính basket (dòng 546). Đo tử số (trọng số
basket) và mẫu số (trọng số thị trường) trên CÙNG một thước đo là điều kiện để phép so sánh có
nghĩa. `BVPS×PB` là đường vòng (PB = Price/BVPS → BVPS×PB = Price, nhưng mất chính xác qua 2 lần
làm tròn và rơi mất tên có BVPS≤0). Chỉ dùng nếu OShares thiếu — thực tế JOIN OShares phủ đủ
(499 tên/rebal 2026), nên không cần fallback.

Point-in-time: cap tại rebal `d` chỉ đọc dữ liệu ngày `d`, không look-ahead.

## 5. Cài đặt (env-gated, mặc định OFF)

- **Variant A** = `BASKET_WT=sectorcap` — dùng NGUYÊN code có sẵn (`sector_cap=0.50`,
  `sector_code=8`). Không sửa gì. Cơ chế này **chưa từng được backtest** trước job này.
- **Variant B** = flag MỚI `BASKET_SECCAP_MODE` trong `custom_basket.py` (pattern
  `BASKET_DCF_MODE`): `""`=OFF (mặc định, byte-identical) | `mktcap` | `mktx<f>`.
  Chỉ hợp lệ khi `weight_scheme=sectorcap`, sai → **raise** (không no-op ngầm).
- Guard: `seccap_dyn_selfcheck.py` — **9/9 PASS** (OFF byte-identical · cap động thật sự bind &
  khác fixed · multiplier đúng · raise đúng · đại số `_cap_sector` giữ Σw=1 + no-op khi dưới cap).
- §8: mọi run đặt `EXP_TAG` riêng → không đụng CSV R3 pinned.

## 6. Kết quả Task 1 — tập trung ngành là XU HƯỚNG DÀI HẠN, không phải cực đoan nhất thời

| Năm | w8 basket (production) | mkt_w8 (ticker_prune) |
|---|---|---|
| 2014 | 0.253 | 0.385 |
| 2016 | 0.141 | 0.426 |
| 2018 | 0.571 | 0.413 |
| 2020 | 0.574 | 0.478 |
| 2022 | 0.743 | 0.524 |
| 2024 | 0.774 | 0.506 |
| 2025 | 0.844 | 0.543 |
| 2026 | 0.895 | 0.609 |

- w8 production: mean 0.574 / median 0.613 / **min 0.034 / max 0.955** (2026-05-05).
- **Drift đơn điệu**, không phải nhiễu: 2014-16 ~14-25% → 2023-26 ~85-95%.
- **ĐÍNH CHÍNH tiền đề dispatch:** dispatch đoán mkt_w8 VN dao động "25-35%". Số thật:
  **mean 47.0%, hiện tại 63.7%** (2026-05-05). Thị trường VN **thật sự** nặng tài chính →
  cap theo vốn hóa thị trường KHÔNG khắt khe như dispatch hình dung.
- Basket vượt thị trường ở 36/48 rebal → yieldcombo có tilt tài chính THẬT, nhưng phần lớn
  mức tập trung là **phản chiếu thị trường**, không phải méo mó của selector.

**Vì sao drift:** selector = `rank(1/PE) + rank(1/PCF)`. Ngân hàng VN có PE/PCF thấp cấu trúc →
value-selector tự nhiên dồn vào tài chính. Đây là **hệ quả cơ học của chính value axis** mà
KB xác nhận là factor mạnh nhất (1/PE IC +0.125), không phải bug.

## 7. Cảnh báo phương pháp — IS/OOS KHÔNG phải công cụ đúng ở đây

Cap chỉ **bind** (thật sự cắt) chủ yếu ở giai đoạn OOS:

| Variant | bind IS (2014-19) | bind OOS (2020+) | mức cắt TB |
|---|---|---|---|
| A fix50 | **6/22** | **25/26** | 0.187 |
| B mktcap | 11/22 | 25/26 | 0.165 |
| B×1.5 | 3/22 | 12/26 | 0.045 |

Cơ chế **gần như ngủ đông in-sample** → walk-forward IS/OOS không thể validate nó (IS ≈ no-op
thì "PASS IS" là vô nghĩa). **Đúng bài học DT5G** (`IS 2014-19 = +0.00pp exactly, overlay dormant
in-sample → walk-forward là công cụ SAI`). Phải đọc kết quả qua **per-year LOO** + bản chất cơ
chế, không qua chữ ký IS/OOS.

## 8. Quy mô biến đổi — variant A khắc nghiệt hơn tên gọi

Tại 2026-05-05, 13 tên phi-tài-chính có tổng base weight **~4.5%** (đều small-cap, rank value
thấp nhất rổ). Cap sector-8 về 50% buộc 4.5% → 50% = **scale-up ~11×**:

| Tên | baseline | A_fix50 | B_mktcap |
|---|---|---|---|
| DCM | 0.0082 | **0.0913** | 0.0663 |
| DGC | 0.0078 | **0.0862** | 0.0626 |
| VGC | 0.0074 | **0.0825** | 0.0598 |
| VHC | 0.0051 | **0.0560** | 0.0406 |
| HHV | 0.0025 | **0.0281** | 0.0204 |

→ Variant A không phải "giảm nhẹ tài chính": nó biến đuôi small-cap kém-value nhất rổ thành
vị thế 8-9% NAV. DGC còn đang bị HOSE hạn chế giao dịch (QĐ 448) và **đã excluded** ở ZaloPay.
Đây là rủi ro thanh khoản + concentration MỚI, không phải giảm rủi ro.

## 9. Trả lời Task 3 — lệnh HPG→LPB

**Sector-cap là cơ chế TRỌNG SỐ, không phải cơ chế CHỌN TÊN.** Thành phần 30 tên **giống hệt**
dưới baseline/A/B. Cụ thể tại rebal 2026-05-05 (đã verify vs publish CSV):
- **LPB LÀ thành viên dưới MỌI biến thể** (baseline 5.25% · A 2.75% · B 3.50%).
- **HPG KHÔNG phải thành viên dưới BẤT KỲ biến thể nào** (không nằm trong 30 tên).

→ Sector-cap **không** đưa ra tên khác thay LPB. Lệnh swap HPG→LPB vẫn đúng hướng dưới cả 3
biến thể. Nhưng dưới sector-cap, LPB chỉ được mua **~½ size** (5.25%→2.75% ở A), và phần vốn
dôi ra phải chảy vào đuôi phi-tài-chính → rebalance sẽ **không còn là 1 lệnh swap 1-đổi-1** mà
là một đợt tái cân bằng rộng (13 tên phải mua lên nhiều lần).

## 10. Kết quả backtest — VERDICT: NO-GO cả 3 biến thể

### 10a. Full harness V2.4 (NAV 50B, NEUTRAL-only, self-check **0 VND** cả 4 run)

| Biến thể | CAGR | Sharpe | MaxDD | Calmar | IS 14-19 | OOS 20-26 |
|---|---|---|---|---|---|---|
| **baseline** (namecap, production) | 27.09% | 1.81 | −18.3% | 1.48 | 23.37 | 30.58 |
| A fix50 | 26.88% | 1.81 | −18.1% | 1.48 | 23.30 | 30.23 |
| B mktcap | 26.93% | 1.82 | −18.1% | 1.49 | 23.22 | 30.40 |
| B×1.5 | 27.05% | 1.82 | −18.3% | 1.48 | 23.27 | 30.60 |

Δ vs baseline: A **−0.21pp** FULL (IS −0.07 / OOS −0.35) · B **−0.16pp** (IS −0.15 / OOS −0.18).
**Chữ ký IS/OOS ÂM CẢ HAI VẾ** → trượt đúng chuẩn "PASS chữ-ký = cả hai dương" của registry.
Sharpe/Calmar lệch ≤0.01 = nhiễu. DD "tốt hơn" 0.2pp — xem 10b, đó là **pha loãng, không phải thật**.

*(baseline 27.09% ≠ 27.84% pinned = data-drift adjusted-price; đã tự chạy baseline cùng snapshot
để so cùng thước đo, đúng META caveat của registry.)*

### 10b. Vehicle thuần (custom30V level series, KHÔNG pha loãng bởi BAL/LAG) — **quyết định**

Harness pha loãng: parking chỉ là 1 phần NAV → thay đổi lớn ở basket hiện ra rất nhỏ ở hệ.
Đo thẳng vehicle mới thấy bản chất:

| Biến thể | CAGR | Sharpe | **MaxDD** | Calmar |
|---|---|---|---|---|
| **baseline** | 29.86% | 1.24 | **−41.0%** | 0.73 |
| A fix50 | 28.71% | 1.22 | **−42.1%** | 0.68 |
| B mktcap | 28.59% | 1.22 | **−42.1%** | 0.68 |
| B×1.5 | 29.37% | 1.24 | −41.3% | 0.71 |

**Cap ngành làm XẤU ĐI mọi chiều, kể cả drawdown** (A −1.15pp CAGR, −0.026 Sharpe,
**DD xấu hơn 1.2pp**, Calmar −0.047). Trực giác "tập trung = rủi ro → cap lại sẽ giảm DD"
**BỊ SỐ LIỆU BÁC BỎ**: đuôi phi-tài-chính của rổ này là small-cap thanh khoản mỏng, beta cao —
sập MẠNH HƠN nhóm ngân hàng vốn hóa lớn trong drawdown. Ép vốn vào đuôi đó = **tăng** DD.
→ 0.2pp DD "cải thiện" ở 10a là nhiễu pha loãng, không phải cơ chế thật.

### 10c. Turnover — chi phí harness KHÔNG hề tính

`build_pit` tính `ret = Σ(W×r)`, **không charge phí rebalance nội bộ basket** → turnover tăng
của A/B đang được MIỄN PHÍ trong 10a. Đo thật (`seccap_vehicle_compare.py`):

| Biến thể | turnover TB/rebal | annual × | phí thêm/năm @TC 0.3% |
|---|---|---|---|
| baseline | 0.607 | 2.43× | — |
| A fix50 | 0.680 | 2.72× | +0.09pp |
| B mktcap | 0.678 | 2.71× | +0.09pp |

→ Số −0.21pp của A ở 10a là **cận trên lạc quan**; thực tế còn xấu thêm ~0.09pp/năm.

### 10d. Verdict

**NO-GO cả 3 biến thể — không đề xuất wire gì.** Không phải "edge nhỏ/chưa đủ tin cậy" mà là
**sai dấu ở mọi chiều đo**: CAGR ↓ (cả IS lẫn OOS), Sharpe/Calmar ↓, **DD ↑ (xấu hơn)**,
turnover ↑ (chưa tính phí). Không cần DSR/PBO — DSR chỉ có nghĩa khi có ứng viên dương để wire.

**Đọc kết quả này thế nào:** tập trung 95.5% vào sector-8 là **hệ quả cơ học của value axis**
(1/PE + 1/PCF; ngân hàng VN có PE/PCF thấp cấu trúc) — đúng cái axis mà KB xác nhận là factor
mạnh nhất (IC +0.125, "Value dominates ALL regimes"). Cap ngành = **cắt chính alpha đó** và đổi
lấy đuôi small-cap kém-value hơn, rủi ro hơn. Rủi ro tập trung là THẬT và đáng theo dõi, nhưng
**sector-cap không phải công cụ xử lý nó** — nó làm hệ tệ hơn trên đúng chiều rủi ro (DD) mà
nó được kỳ vọng cải thiện.
