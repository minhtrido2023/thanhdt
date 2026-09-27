# Audit độc lập rổ park custom30V bằng PHƯƠNG PHÁP VỊ THẾ (share-count replay)

job `Taylor_20260927_101335` · 2026-09-27 · PAPER-ONLY · **không re-pin, không đổi rail, không merge**
PREREG: [`PREREG.md`](PREREG.md) (viết 17:18:31 ICT, trước con số đầu tiên lúc 17:22:17 — đã được
quant-skeptic xác minh bằng mtime)

## 0. Câu trả lời ngắn cho user

> "số CP sau ex-right tăng nhưng giá thực tế cũng giảm ngay, không thể tái tạo lợi nhuận ảo.
> Lỗ hổng ở đâu? Số thực tế là số nào?"

**Lập luận của bạn đúng, và nó đúng một cách đo được.** Dựng lại rổ park như một danh mục cổ phiếu
thật — giữ số CP, mark theo **giá thô** của đúng phiên đó, áp từng sự kiện quyền tại ngày GDKHQ —
cho ra chuỗi **khớp** chân production hiện hành (`BASKET_RETURN_OSHARES=flat`) — trong giới hạn phép
kiểm phân giải được, xem ngay dưới — và **không** cho ra chuỗi cũ. Lỗ hổng nằm đúng ở chỗ đã được sửa (commit `1b89881b`): chuỗi cũ tính
`mcap = Close_đã_điều_chỉnh × OShares`, tức **cộng thêm** bước số CP lên trên một chuỗi giá **đã**
trung hoà sẵn chính sự kiện đó — cú giảm giá bị khử hai lần, chỉ còn lại phần tăng số CP.

**Độ mạnh của kết luận, tách làm hai — đây là điều bản vòng 2 nói QUÁ và đã bị `quant-skeptic`
bắt (vòng 3, xem §9):**
- **Cơ chế** (phantom = `Close_adj × OShares`): xác nhận với biên **~60σ** — chênh LEGACY−FLAT là
  **+18,588pp** còn mọi dư lượng đo được ở cấp **±0,02pp/năm** trên chính lớp sự kiện bị nghi.
- **"Không có lỗ hổng MỚI"**: chỉ đúng **cho chân RETURN**, và chỉ ở độ phân giải **~±0,6pp/năm**
  (CI95 bootstrap theo ngày trên toàn bộ dư lượng ngoài quyền mua), **KHÔNG** phải ±0,300pp như
  ngưỡng PREREG hàm ý. Chân **TRỌNG SỐ** không được audit này chứng nhận (§5.5).

**Số thực tế của chân park** (cửa sổ 2014-08-05 → 2026-06-19, 11,87 năm, tham số pin R3):

| Chân | CAGR chân park | Ý nghĩa |
|---|---:|---|
| **ENGINE_FLAT** = production hiện hành | **17,857%** | chuỗi `Close` đã điều chỉnh, không có số CP |
| ENGINE_LEGACY = trước khi sửa | 36,445% | **+18,6pp phantom** — không phải lợi nhuận |
| REPLAY_B = replay vị thế, một biến khác duy nhất | 17,322% | thô, chưa trừ phần quyền mua |
| REPLAY_A = đúng mô hình bạn mô tả (giữ số CP giữa các kỳ, phí 0,1%/chiều) | 16,875% | thêm phí nội bộ rổ + tiền cổ tức nằm chờ |

## 1. Vì sao đây là bộ tái lập THỨ BA, độc lập thật

| | ENGINE_FLAT | ENGINE_LEGACY | REPLAY |
|---|---|---|---|
| Giá dùng để tính lợi nhuận | `Close` (đã điều chỉnh hồi tố) | `Close × OShares` | **`Price` THÔ** |
| Cổ tức CP / thưởng | ngầm trong `Close` | ngầm + cộng lại lần nữa qua `OShares` | **tường minh**: `N ×= (1+Σq)` tại ngày GDKHQ |
| Cổ tức tiền | ngầm (tái đầu tư) | ngầm | **tường minh**: `cash += N×D` |
| Nguồn sự kiện | vendor (không thấy được) | vendor + `ticker_financial.OShares` | `tav2_bq.corporate_action`, vintage pin riêng |
| Code chung với `custom_basket.py` | — | — | **không dòng nào** (kể cả `_cap_names` viết lại; quant-skeptic đo tương đương 7,5e-16) |

Hai bảo hiểm chống "harness tự khẳng định":
- `[harness]` — hai chân engine tái lập lại **từ panel đã dump** khớp chính `build_pit()` tới
  **max |Δ| = 4,0e-15** (assert cứng; sai là abort, không đọc số replay).
- `[identity]` — replay với **mọi sự kiện bị tắt và không phí** phải khớp một chuỗi giá thô
  **viết độc lập**: **max |Δ| = 4,9e-15**. Đây là phép kiểm bộ máy NAV (số CP, tiền dư,
  carry-forward), **không** đúng-theo-định-nghĩa.

## 2. Vòng 1 SAI — quant-skeptic REFUTED, cả 3 lỗi đều thật

Bản đầu của replay đã bị `quant-skeptic` bác bỏ và **cả ba phát hiện đều đúng**. Ghi lại vì mỗi lỗi
là một cái bẫy dùng lại được, không phải sự cố một lần:

| # | Lỗi vòng 1 | Bằng chứng cơ học | Ảnh hưởng | Đã sửa |
|---|---|---|---|---|
| 1 | **Trễ trọng số 1 phiên.** Đặt số CP ở giá đóng phiên `d` với `wmap[d]` rồi giữ sang `d+1` ⇒ `w_d` ăn lợi nhuận `d→d+1`, còn engine ăn `(d−1)→d`. Mà `wmap[d]` vốn đã dựng từ `mcapw` phiên trước ⇒ trễ thêm trọn một phiên. REPLAY_B khác ENGINE_FLAT **2 biến**, không phải 1 | so trực tiếp `replay()` vs `engine_legs()`/`attribute.py` | −0,395pp trên chân replay, −0,422pp trên chân flat — **lớn hơn cả ngưỡng 0,300pp** | giao dịch tại giá đóng phiên **trước**, với `w_d` — đúng quy ước engine. Mutation **M5** dựng lại lỗi này |
| 2 | **Hệ số cùng ngày NHÂN thay vì CỘNG.** `fac *= (1+q)` mỗi sự kiện. Hai đợt cùng đi ex thì mỗi `exercise_ratio` đều quy về số CP **gốc** ⇒ đúng là `1+Σq` | đối chiếu cột `OShares` của chính panel (nguồn độc lập): HPG 2015-05-08 thật **1,499959** vs code **1,560000** (+4,00% CP ảo); HDB 2020-10-01 1,299997 vs 1,322500; MBB 2018-07-06 1,190000 vs 1,197000; SSB 2022-06-16 1,193456 vs 1,201874 | +0,123pp/năm thổi lên, và là nguyên nhân trực tiếp của 2/15 dòng trong chính bảng dẫn chứng vòng 1 | `fac = 1 + Σq`. Sau sửa HPG 2015-05-08 `r_replay −1,14%` ≈ `r_flat −1,18%` (trước: +2,72%). Mutation **M1b** dựng lại lỗi này |
| 3 | **`searchsorted` dồn sự kiện trước panel vào phiên 1.** 1.453 dòng vintage có ex-date trước phiên đầu bị đóng dấu vào 2013-12-23 | đếm trực tiếp | không đổi NAV (phiên 1 chưa giữ gì) nhưng **thổi mọi con số đếm 1,4-1,9×**: quyền mua 366 → **195** trong cửa sổ | bỏ tường minh, đếm riêng |
| 4 | **Cửa sổ CAGR có 0,616 năm chưa đầu tư** (chuỗi bắt đầu 2013-12-23, rebal đầu 2014-08-05) | — | pha loãng mọi Δpp hệ số 0,95 | đo từ rebal đầu tiên = đúng cửa sổ PREREG |

Lỗi 1 là loại nguy hiểm nhất: **`[harness]` 4e-15 vẫn PASS** vì nó chứng nhận `engine_legs()` (căn
đúng) chứ không phải chân đang bị đem so. Bài học đưa vào code: assert phải phủ **chính chân** được
dùng để kết luận. Thêm `[identity]` chính vì vậy.

## 3. Kết quả — chân replay khớp FLAT, không khớp LEGACY

Cửa sổ 2014-08-05 → 2026-06-19 (11,87y). Tham số pin R3 y nguyên: `BASKET_SELECT=yieldcombo`,
`ETF_LIQ=custompitg` (quality=none / rebal=q2m5 / gate=3), `BASKET_WT=namecap`, top30, cap 0,10,
`BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
`BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet`, `UNIVERSE_SOURCE=pit`.
48 kỳ rebal · 204 tên union · 30 tên/kỳ. `members_df` + `bx` được assert **byte-identical** giữa
hai chân engine ⇒ A/B thật sự một biến.

| | CAGR | Δ vs FLAT | corr ngày vs FLAT | TE vs FLAT |
|---|---:|---:|---:|---:|
| ENGINE_FLAT | 17,857% | — | — | — |
| ENGINE_LEGACY | 36,445% | +18,588pp | 0,963 | 6,31%/năm |
| REPLAY_B (thô) | 17,322% | −0,536pp | **0,99865** | **1,18%/năm** |
| REPLAY_A | 16,875% | −0,983pp | 0,99789 | 1,47%/năm |

### Dải xác nhận (quyền mua không mô phỏng được)

Quyền mua (`Quyền mua CP cho Cổ đông hiện hữu`) là lớp sự kiện duy nhất replay **không** định giá
được: bảng vendor không có giá phát hành (`ref_price` NULL), nên replay chịu cú giảm giá ngày ex mà
không nhận giá trị quyền ⇒ thiên lệch ÂM **của replay**. PREREG đã ghi trước là so ngưỡng trên số
**đã trừ** phần này. Vì phần trừ (~0,4-0,6pp) **lớn gấp đôi ngưỡng**, báo theo **DẢI** chứ không
một con số — cách vạch ranh quyết định con số:

| Cách trừ | CAGR | Δ vs FLAT | Ghi chú |
|---|---:|---:|---|
| **BAND_LO** — chỉ trung hoà phiên mà sự kiện DUY NHẤT là quyền mua | 17,712% | **−0,145pp** | bảo thủ nhất |
| **BAND_HI** — trung hoà cả phiên có quyền mua đi kèm sự kiện khác | 17,944% | **+0,086pp** | rộng tay nhất với engine |

| **UNMODELLED** — trung hoà MỌI phiên vendor re-base vĩnh viễn mà replay KHÔNG có sự kiện | 17,498% | **−0,359pp** | **NGOÀI ngưỡng** — xem cảnh báo ngay dưới |

**Δ ∈ [−0,145; +0,086] pp — cả hai đầu của dải neo-theo-quyền-mua đều TRONG ngưỡng 0,300pp chốt
trước.**

> ⚠️ **Nhưng phải công bố cùng lúc: carve UNMODELLED cho −0,359pp, tức NGOÀI ngưỡng.** Bản vòng 2
> của báo cáo này in hai đầu dải mà **bỏ dòng thứ ba**, dù `attribute.py` in đủ cả ba cạnh nhau
> (`attribute.log:23,25`). Carve UNMODELLED có lý lẽ **mạnh hơn** hai carve kia ở một điểm: nó neo
> vào chỗ giá **thực sự** re-base (đo trên panel) chứ không neo vào `exright_date` của vintage —
> mà vintage có thể sai ngày (ca SHS 2022-04-18). Vậy ĐỌC ĐÚNG là: kết quả **phụ thuộc cách carve**,
> dải thật rộng hơn dải đã báo, và ngưỡng 0,300pp **không** phân giải được ở mức đó. Cái vẫn đứng
> vững sau mọi cách carve là **cơ chế** (18,588pp phantom) và **dư lượng trên chính lớp sự kiện
> nghi vấn** (±0,02pp/năm, §3b).

38 name×session bị
trung hoà ở BAND_HI, trong đó **20** có sự kiện khác (cổ tức CP / cổ tức tiền) đi ex cùng ngày —
tức BAND_HI xoá luôn phán quyết của replay trên chính lớp sự kiện đang audit. Đó là lý do phải báo
dải, và là lý do của giới hạn ở §5.

### Dư lượng ngoài quyền mua = +0,0083 (≈ +0,07pp/năm), và nó KHÔNG nằm ở sự kiện

Phân rã theo nhãn sự kiện (`attribute.log`), tổng đóng góp `w × (r_replay − r_flat)`:

| Nhãn | n | tổng | pp/năm |
|---|---:|---:|---:|
| RIGHTS (mọi biến thể) | 38 | −0,0627 | −0,528 |
| FREESHARE | 114 | +0,0009 | +0,008 |
| DIV | 238 | +0,0030 | +0,025 |
| DIV+FREESHARE | 45 | −0,0003 | −0,002 |
| NONE (không sự kiện) | 74.859 | +0,0047 | +0,040 |

Hai điều đọc được:
1. **Trên chính lớp sự kiện cổ tức CP / thưởng — lớp mà bug cũ khai thác — hai chuỗi khớp tới
   +0,008pp/năm.** Đây là câu trả lời trực tiếp cho user: giá giảm đúng bằng phần CP tăng, không
   tái tạo được lợi nhuận ảo.
2. Dư lượng còn lại **không** tụ ở ngày sự kiện: trong 48 name×session có |đóng góp| > 10bp (không
   phải quyền mua, tổng +0,0094), chỉ **4/48** nằm trong ±5 phiên của một sự kiện corp-action nào.
   Chúng là lớp nhiễu **chất lượng dữ liệu cột `Price`**: 176 name×session có `Price` **đứng yên
   đúng bằng phiên trước** trong khi `Close` đã đổi (giá thô bị chép 1 phiên, **ngoài** ngày ex nên
   detector không bắt) — VEA 2020-03-11/12, BID 2022-01-20/21, VPB/VCB 2025-08-14/15. Tổng đóng góp **ròng** của
   chúng là **+0,0037**, nhưng **gross Σ|đóng góp| = 0,0883 (0,744pp/năm)** — gấp **24×** số ròng.
   Tức chúng triệt tiêu **theo kiểu thống kê giữa 176 mục độc lập**, KHÔNG phải "triệt tiêu theo
   cặp t/t+1" như bản vòng 2 viết. *(Bản vòng 2 chép lại đúng cái mô hình mà `selfcheck_replay.py:15-16`
   và `attribute.py:46-51` của chính job này khai là SAI: với rebal hằng ngày, trọng số vào lợi nhuận
   theo quan hệ tuyến tính nên giá kẹt KHÔNG telescope. Số đúng, cơ chế sai — đúng lớp bẫy §29
   `coding_guidelines`.)* Đây là điểm yếu của replay (cần ngày chính xác), **không** của engine (dùng luôn hệ
   số điều chỉnh của vendor nhúng trong `Close`).

## 3b. Độ phân giải THẬT của phép kiểm — số mà vòng 2 chưa hề tính

`resolve_power.py` / [`resolve_power.log`](resolve_power.log). Bootstrap **theo NGÀY** (khối = 1
phiên, 4.000 lần resample) trên chuỗi đóng góp `w × (r_replay − r_flat)`, tách theo nhãn sự kiện.
Đây là câu trả lời cho "phép kiểm này phân giải được tới đâu" — `attribute.py` trước đó chỉ in
**gross Σ|đóng góp|**, con số phạt quá tay một lớp nhiễu trung bình-0 (`GROSS 1,264pp/năm` ⇒ kết
luận "không phân giải được dưới ~1,26pp" là **quá bi quan**, còn `[−0,145;+0,086]` là **quá lạc
quan** — nó là dải theo *cách carve*, không phải dải theo *nhiễu lấy mẫu*).

| Lớp | n | ròng pp/năm | SE boot | **CI95** | gross pp/năm |
|---|---:|---:|---:|---|---:|
| **Lớp ĐANG AUDIT** (FREESHARE + DIV+FREESHARE) | 159 | **+0,005** | 0,006 | **[−0,005; +0,017]** | 0,039 |
| DIV (cổ tức tiền) | 238 | +0,025 | 0,017 | [−0,003; +0,063] | 0,071 |
| NONE (không sự kiện) | 74.859 | +0,039 | 0,318 | [−0,594; +0,668] | 8,947 |
| **MỌI thứ trừ quyền mua** | 75.256 | **+0,070** | 0,311 | **[−0,526; +0,707]** | 9,057 |
| RIGHTS (không mô phỏng được) | 38 | −0,527 | 0,130 | [−0,804; −0,298] | 0,528 |

**Đọc đúng, một câu:** trên **chính lớp sự kiện mà bug cũ khai thác** (cổ tức CP / thưởng), hai
chuỗi khớp tới **±0,02pp/năm** — chặt hơn ngưỡng PREREG **15 lần**, và đây là con số chịu lực.
Trên **tổng thể**, phép kiểm chỉ phân giải tới **~±0,6pp/năm**: nó **không** đủ mạnh để tuyên bố
"không còn sai số nào ở đâu cả", chỉ đủ để loại bỏ một sai số cỡ **18,6pp**.

### IS / OOS — walk-forward (§18 `coding_guidelines`), cũng chưa có ở vòng 2

| Kỳ | n phiên | FLAT | LEGACY | REPLAY_B | **Δ B−FLAT** | **phantom LEGACY−FLAT** |
|---|---:|---:|---:|---:|---:|---:|
| FULL 2014-08→2026-06 | 2.965 | 17,857% | 36,445% | 17,322% | **−0,536pp** | **+18,588pp** |
| IS 2014-08→2019-12 | 1.354 | 9,982% | 26,713% | 9,687% | **−0,295pp** | **+16,731pp** |
| OOS 2020-01→2026-06 | 1.611 | 24,630% | 44,890% | 23,872% | **−0,759pp** | **+20,259pp** |

Phantom hiện diện **mạnh ở CẢ HAI nửa** (+16,7 / +20,3pp) ⇒ kết luận về cơ chế không phải hiện
tượng một giai đoạn. Nhưng chênh thô replay−flat **lớn gấp 2,6× ở nửa sau** (−0,759 vs −0,295pp)
— con số toàn kỳ che mất điều đó. Phần lớn là do quyền mua (drag gần như không đổi: −0,315 pp/năm
IS vs −0,345 OOS trên nhãn RIGHTS thuần), còn lớp FREESHARE ổn định hai nửa (+0,009 IS / +0,007 OOS).


## 4. Ledger phiên LEGACY ≠ FLAT — phantom trông như thế nào

**313 name×session / 255 phiên**, 230 phiên dương / 25 âm, đóng góp phiên lớn nhất **+8,18pp**.
File: [`ledger_legacy_vs_flat.csv`](ledger_legacy_vs_flat.csv),
[`ledger_legacy_by_session.csv`](ledger_legacy_by_session.csv).

> Con số này **khác** "159 phiên / 143 dương / max +15,0pp" mà quant-skeptic đo trước đó — không
> phải mâu thuẫn: đây đếm **đóng góp có trọng số vào chỉ số** trên đúng cửa sổ + đúng membership pin
> R3, còn phép đo kia chạy trên bảng BQ thô. Cả hai nói cùng một hiện tượng.

### 3 ca quant-skeptic nêu — replay khớp chân nào

| mã | ngày | w | raw Δ% | adj Δ% | ΔOShares% | **r_legacy%** | **r_flat%** | **r_replay%** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ACB | 2024-05-31 | 0,054 | −16,16 | −0,22 | +15,00 | **+14,74** | **−0,22** | **−0,18** |
| TCB | 2024-06-20 | 0,080 | −48,65 | +2,69 | +100,00 | **+105,38** | **+2,69** | **+2,69** |
| HPG | 2025-06-26 | — | — | — | — | — | — | **không nằm trong rổ** phiên đó (rebal hoạt động 2025-05-05) ⇒ đóng góp **0** vào chỉ số |

TCB là ca sạch nhất: giá thô giảm **−48,65%** vì chia thưởng 1:1, số CP tăng **+100%**. Chuỗi cũ ghi
**+105,38%** trong MỘT phiên. Replay giá thô — cầm đúng số CP mới, mark đúng giá mới — ghi **+2,69%**,
**bằng đúng** chân production tới hai chữ số.

### Ca minh hoạ cơ chế rõ nhất — VPB 2018

| ngày | việc xảy ra |
|---|---|
| 2018-06-18 | thưởng 31,6% **+** cổ tức CP 30,217% cùng đi ex ⇒ hệ số thật **1,6182**; giá thô 49.500 → 30.300 |
| 2018-08-01 | `OShares` mới bước lên (+64,07%) — **6 tuần sau**, vì bước này khớp ngày công bố quý chứ không khớp sự kiện |

Chuỗi cũ ghi **+62,18%** vào phiên 2018-08-01 — một ngày mà giá thô chỉ **−1,11%** và `Close` chỉ
**−1,15%**. Không có cú giảm giá nào bù lại, vì cú giảm giá đã xảy ra từ 06-18 và đã bị `Close` hấp
thu. Replay ghi **−1,11%**. (Bước này không được cổng re-date bắt: tổng `exercise_ratio` 0,61817 lệch
0,0225 so với tỉ lệ thật 0,6407, vượt dung sai 0,0148 ⇒ rơi về ngày công bố — đúng thiết kế
"fallback là staleness, không bao giờ là số sai", nhưng nó cho thấy vì sao chân return **không được**
chứa số CP.)

## 5. Giới hạn — cái audit này KHÔNG chứng minh

1. **Chân FLAT KHÔNG được chứng nhận trên ngày ex QUYỀN MUA** (195 sự kiện trong cửa sổ, 91 mã).
   Replay thiếu giá phát hành nên không kiểm được ở đúng đó; phần trừ 0,4-0,6pp **giả định** engine
   đúng ở chỗ replay không soi được. Bất kỳ sai số nào của engine tụ riêng vào ngày quyền mua sẽ vô
   hình với phép đo này. Muốn đóng lỗ này cần nguồn giá phát hành (FiinProX / công bố thông tin).
2. **Bước sửa `Price` kẹt ngày GDKHQ có bơm thông tin chuỗi đã điều chỉnh vào chân "thô"**:
   `P_t := Close_t/ratio_{t+1}`. Về đại số, nếu một ô được sửa **đồng thời** là ngày bước số CP thì
   lợi nhuận replay của ô đó **co về đúng** `Close_t/Close_{t−1}` — replay bị cưỡng bức khớp chuỗi
   nó đang audit. Đã giới hạn bước sửa vào **ngày ex thật của sự kiện điều chỉnh giá** (8 ô toàn
   panel, từ 273 ô của vòng 1) và **đo**: **0 ô** giao với một bước số CP trong rổ ⇒ đường cưỡng bức
   không bao giờ được đi. Assert cứng trong selfcheck — và từ vòng 3 bằng điều kiện **đúng và mạnh
   hơn** (`0d2`): ô sửa **không nằm trong rổ** phiên đó, đo được **0/8**, vì phép co cũng xảy ra
   trên ô sửa có cổ tức TIỀN (`r_rep = r_flat·(1−D/P)`) mà `0d` không thấy — 5/8 ô sửa là DIV-only.
3. Replay **không** mô phỏng: thuế, slippage, lãi tiền gửi, ngày nhận cổ tức thật (giả định nhận
   ngay tại ex-date — làm **lợi** cho replay, biên nhỏ), và không có sự kiện gộp/tách ngược (bảng
   vendor không có mã sự kiện đó cho VN).
4. Vintage `corporate_action` đọc LIVE 2026-09-26 trong khi panel giá pin asof 2026-07-29. Không tạo
   look-ahead (mọi ex-date sau 2026-06-19 bị `snap()` loại), nhưng là survivorship của **lịch sự
   kiện**; chuỗi giá đem so cũng chỉ phản ánh sự kiện đã thực hiện nên coi là không đáng kể.
5. **Audit này chứng nhận chân RETURN. Nó KHÔNG chứng nhận chân TRỌNG SỐ** —
   `custom_basket.py:544` vẫn là `bx["mcapw"] = bx["pxw"] * bx["OShares"]`, tức **đúng cấu trúc
   giá × số CP** mà bản sửa `1b89881b` đã bỏ khỏi chân return. Đo được (`resolve_power.py` §3):
   trong **900** phiên ticker×session **TRONG RỔ** mà hệ số điều chỉnh giá bước >0,5%, chỉ **153
   (17%)** có `OShares` bước **cùng phiên**; 747 phiên lệch ngày, 662 phiên lệch >5 ngày, khoảng
   cách tới bước `OShares` gần nhất median **96 ngày** (p90 826). Điều này **KHÔNG in ra phantom
   return** như chân return cũ — trọng số được chuẩn hoá theo tiết diện rồi cap 0,10, và
   `custom_basket.py:112-120` khai đây là staleness **chấp nhận có chủ ý** ("Falling back is a pure
   staleness cost, never a wrong number"). Nhưng replay **nhập `wmap` nguyên xi** (`replay.py:390`)
   nên **không có khả năng** test chỗ đó: mọi sai số của chân trọng số xuất hiện **giống nhau** ở
   cả replay lẫn engine và triệt tiêu khỏi phép so. Muốn đóng: A/B riêng trên `BASKET_OSHARES_STEP`.
   *(Đây là giới hạn PHẠM VI, không phải phát hiện lỗi — ghi ra vì §4 của báo cáo này dùng ca VPB
   2018 để lập luận "chân return KHÔNG ĐƯỢC chứa số CP", và cùng cấu trúc đó vẫn sống ở chân trọng số.)*
6. **`replay.py:150` (`ratio.shift(-1)`) và `attribute.py:57` (`ratio.shift(-j)`) ĐỌC TƯƠNG LAI.**
   Cả hai là chẩn đoán offline và chứng minh được là vô hại trên chân đem kết luận (M4: ΔCAGR
   **+0,0000pp**, 0 phiên lệch). **Không dòng nào trong hai file này được phép tái sử dụng trên
   đường LIVE.**

## 6. Selfcheck

`selfcheck_replay.py` — **6 mutation + 6 property**, chạy dưới **3 múi giờ** (`Asia/Ho_Chi_Minh`,
`TZ` bỏ hẳn qua `env -u TZ`, `America/New_York`) theo §16 `coding_guidelines`, mỗi chân là một
interpreter riêng. Log: [`selfcheck_replay.log`](selfcheck_replay.log).

**Kết quả: 4 chân chạy (`Asia/Ho_Chi_Minh`, `UNSET`, `UNSET`, `America/New_York`), 88 dòng `PASS`,
`FAIL` = 0, cả 4 đều `rc=0`, log kết thúc bằng `DONE`.** Check `0d2` fire ở **cả 4** chân, mỗi lần
`trong rổ = 0`. Không có chênh lệch nào giữa các múi giờ ⇒ replay không phụ thuộc `TZ` của caller.

Hai điều phải đọc trong log, đều ghi ra thay vì vá im lặng:
- Dòng tổng kết in **"6 mutation + 5 property"** vì hằng số đếm property viết cứng `5` từ vòng 2
  trong khi vòng 3 thêm `0d2`. Thân log liệt kê đủ **6** property theo tên (`0a, 0b, 0c, 0d, 0d2,
  M4`) nên đếm lại được. Không sửa giữa lúc đang chạy để 3 chân TZ không đọc hai bản code khác nhau.
- Chân `UNSET` xuất hiện **hai lần** và PASS cả hai. Lần đầu mất dòng `rc=`: tôi chạy
  `pkill -f "run_selfcheck.sh"` mà pattern **khớp luôn command line của chính lệnh đó**, giết cả
  shell gọi và parent của run — python con sống sót và in PASS, nhưng `rc=` và chân TZ thứ ba không
  bao giờ được ghi. `run_selfcheck_finish.sh` chạy tiếp hai chân còn lại vào cùng log, giữ nguyên
  `flock`. *(Bài học cùng lớp §29: `pkill -f <chuỗi>` trong một lệnh có chứa chính chuỗi đó là
  self-kill — dùng PID từ `pgrep` rồi loại `$$`.)*

Hai check là **property** chứ không phải mutation, có chủ đích — vòng 1 sai theo đúng chiều ngược
lại (assert "phải lệch" lên một thứ chứng minh được là không thể lệch), và lý do vòng 1 đưa ra cho
việc không lệch ("giá kẹt triệt tiêu t/t+1") là **mô hình sai** (xem §3 item 2). Lý do thật là
**0 ô giao với bước số CP** — đo được, và chính nó là điều đáng assert.

### Vòng 3 thêm / sửa

- **`0d2` (MỚI) — điều kiện đúng, mạnh hơn `0d`.** `quant-skeptic` chỉ ra: phép co-về-`Close` do
  px-repair **không chỉ** xảy ra trên bước số CP. Trên ô sửa mà sự kiện là **cổ tức TIỀN**, lợi
  nhuận replay co về `r_flat·(1−D/P)` — cũng là cưỡng bức, mà `0d` (chỉ kiểm `|fac−1| > 1e-12`)
  **không thấy**; mà **5/8 ô sửa toàn panel đúng là DIV-only**. Điều kiện đủ và duy nhất cần là ô
  sửa **không nằm trong rổ** phiên đó. Đã đo và assert: **trong rổ = 0** (cả 8/8 ô sửa đều ngoài
  rổ) ⇒ đường cưỡng bức không bao giờ được đi, **với mọi loại sự kiện**. Đây là mảnh bằng chứng
  chịu lực nhất bảo vệ tính độc lập của replay, và vòng 2 đã assert nó bằng điều kiện quá hẹp.
- **Điểm mù của detector giá kẹt — thật về đại số, RỖNG trên panel này.** `replay.py:152` đòi
  `ratio > lo*1.005` với `lo = min(ratio_prev, ratio_next)`. Nếu `Price` ngày ex là bản **chép
  nguyên** phiên trước (kẹt *hoàn toàn*, không kẹt một phần) thì `ratio_d == ratio_prev == lo` và
  bất đẳng thức **ngặt** không bao giờ thoả ⇒ detector cấu trúc **không bắt được** dạng đó — đúng
  dạng mà registry `price-volume/ticker_price_stale_on_exdate.md` mô tả. Tôi đếm trên chính panel
  đang dùng (`blindspot.py` / [`blindspot.log`](blindspot.log)): 2.531 ô ex-date price-adjusting →
  detector bắt **8** ô (kẹt một phần), điểm mù **0** ô, giao **0**. Không ô nào lọt ⇒ **không con
  số nào của báo cáo bị ảnh hưởng**. Không sửa giữa audit (M4 cho thấy toàn bộ repair đáng
  **0,0000pp**); ghi lại vì tái dùng `replay.py` trên panel khác thì phải đổi sang `>=` hai phía.
- **Sự cố §8 `coding_guidelines` — HAI instance `run_selfcheck.sh` chạy song song, ghi đè nhau.**
  `quant-skeptic` bắt được log đang bị trộn (header `TZ=Asia/Ho_Chi_Minh` trên thân in
  `TZ='(unset)'`, kèm lỗ sparse). Hai run đều ghi `selfcheck_replay.log` và cùng bộ
  `levels_sc_*.parquet`; vì check M4 **đọc parquet từ ĐĨA** (`selfcheck_replay.py:125-126`), nó có
  thể đã so artifact của **hai run khác nhau**. Đã vá hai lớp: `flock -n` độc quyền trong
  `run_selfcheck.sh` (instance thứ hai thoát rc=8 thay vì ghi đè), và `SC_RUN="r$$_"` làm không
  gian tên artifact riêng theo PID (`selfcheck_replay.py` + `replay.py` nhận qua `--out-prefix`;
  `rights_not_modelled*.csv` cũng tách theo prefix). Log hiện tại là **một lần chạy duy nhất**
  giữ lock, artifact mang tiền tố PID — kiểm được bằng dòng `SC_RUN=` ở đầu log. Bản log bị trộn
  giữ lại ở `selfcheck_replay_RACED.log` để đối chiếu.

## 7. §6 PREREG — "số thực tế" ở cấp hệ thống (A/B R3)

Đổi **đúng một biến**: chân park của lệnh pin R3 production (`PARK_STATES="3:0.3"` = park 0,30,
user chốt 2026-09-27 15:48 ICT). Wrapper `run_ab.py` chỉ bọc `custom_basket.build_pit` — engine giữ
nguyên byte, membership / ADV / allocator / NAV không đổi. Chân control `ENGINE_FLAT` đi qua đúng
wrapper đó và **assert max |Δ| < 1e-9** so với `build_pit()` gốc, để chứng minh wrapper là no-op
trước khi đọc chân treated.

### Kết quả A/B (một biến = chân park)

| Chân park | Final NAV | CAGR | Sharpe | MaxDD | Calmar | Δ CAGR vs control |
|---|---:|---:|---:|---:|---:|---:|
| **ENGINE_FLAT = control (production)** | 688,77B | **23,43%** | 1,88 | −14,4% | 1,63 | — |
| REPLAY_B (replay, một biến) | 686,64B | **23,40%** | 1,88 | −14,4% | 1,63 | **−0,03pp** |
| REPLAY_A (đúng mô hình user, có phí nội bộ rổ) | 671,86B | **23,18%** | 1,87 | −14,4% | 1,61 | **−0,25pp** |

`self-check 0 VND` trên CẢ BA chân (`[selfcheck BAL]` và `[selfcheck LAG]`: cash-flow identity max
err = 0 VND, final NAV identity err = 0 VND). Wrapper được chứng minh no-op trên chân control
(max |Δ| = 3,997e-15 vs `build_pit()` gốc).

Chênh ở cấp hệ thống **nhỏ hơn nhiều** so với chênh ở cấp chân park (−0,536pp) vì park chỉ ăn 30%
tiền nhàn rỗi và chỉ ở trạng thái NEUTRAL: −0,03pp (REPLAY_B) tới −0,25pp (REPLAY_A). MaxDD không
đổi, Sharpe gần như không đổi.

**KHÔNG re-pin.** Đây là phép đo, không phải đề xuất đổi anchor.

### ⚠️ Phát hiện PHỤ, ngoài phạm vi job — anchor 23,37% không tái lập được từ code canonical

Control của tôi cho **23,43%**, không phải **23,37%** của anchor vừa commit (`6989fb54`). Nguyên nhân
đã truy được bằng bằng chứng cơ học, không suy đoán:

- `lag_dnpr_harness.py:1695-1696` (canonical) hardcode `parse_dates=["entry"]` +
  `set_index("entry")` ⇒ dùng nhãn **as-of (peeking)**. Log của tôi in dòng edge-alloc **cũ**
  (`thr=4.0%; ... %time<thr=53%`), **không có** `label_col`.
- `failc_ab_20260927/failc_new.log` in `source=lag_edge_health.csv label_col=known_date rows=583
  ... %time<thr=52%`. Chuỗi `label_col` **không tồn tại** trong canonical
  (`grep -rn label_col --include=*.py` chỉ ra selfcheck + `golive_recommend_v23.py` + worktree).
- Patch nằm ở branch **`fix/failc-sweep-8callsites-2709`** (worktree
  `mike/agents/Taylor/wt-failc-sweep-2709`, `546d5c83`) — **CHƯA MERGE**.
- `data/lag_edge_health.csv` hiện có **cả hai** cột (`entry,known_date`) nhưng consumer canonical
  index lên `entry` ⇒ vẫn peeking.

⇒ **23,37% là số của code chưa merge; production hôm nay tái lập 23,43%.** Δ chỉ −0,06pp nên không
phải sự cố tiền thật, nhưng anchor trong `data/results_registry.md` đang trỏ tới một cấu hình không
tồn tại trên `main`. Đã ghi bus `finding:anchor-2337-tu-code-CHUA-MERGE`. **Cần user duyệt**: merge
branch rồi re-pin, HOẶC đổi anchor về 23,43% và ghi rõ là nhãn as-of. Tôi không tự quyết.


## 9. `quant-skeptic` vòng 3 — phán quyết trên chính bản vòng 2

**Phán quyết: `CONFIRMED-WITH-CAVEATS`** (JSON `verdict: CONFIRMED`, `confidence: medium`).

Cái nó **không** phá được, dù được lệnh đánh thẳng vào đòn 8 (double-count) trên chính replay:
- Tái lập **bằng tay từ BQ LIVE** hai ô sự kiện chủ lực, khớp bảng §4 tới 2 chữ số:
  ACB 2024-05-31 (`Price 29.400→24.650`, `OShares ×1,15` **cùng phiên**) → `r_replay −0,179%` vs
  `r_flat −0,225%` vs `r_legacy +14,74%`; TCB 2024-06-20 (`Price 48.300→24.800`, `OShares ×2,0`
  **cùng phiên**) → `r_replay +2,692%` vs `r_flat +2,691%` vs `r_legacy +105,38%` = **đúng bằng tỉ
  lệ `Close` nhân 2** — chính phép nhân đôi, in ra thành một dòng.
- Tự liệt kê 8 ô px-repair và xác nhận **8/8 ngoài rổ** ⇒ đường cưỡng bức chưa bao giờ được đi
  (nay đã thành assert `0d2`).
- Quy ước trọng số **là quy ước của engine**, không phải chọn cho khớp: `custom_basket.py:22` +
  `:555`, harness 3,997e-15 so `build_pit()`.
- Không look-ahead (0 hit cột forward), không survivorship (`custom_basket.py:647` gate ngày về
  phía trước, flag date 2026-06-20 > cuối cửa sổ 2026-06-19), self-check **0 VND** cả 3 chân A/B.

Cái nó **phá được** — và đều đúng, đã sửa trong bản này:

| # | Phát hiện | Đã xử lý |
|---|---|---|
| 1 | **Báo cáo bỏ 2 số bất lợi mà chính `attribute.log` in ra**: carve UNMODELLED **−0,359pp** (NGOÀI ngưỡng) và gross noise floor **1,264pp/năm** | công bố cả hai ở §3 + cảnh báo đọc-đúng; §0 tách "cơ chế 60σ" khỏi "không lỗ hổng mới ~±0,6pp" |
| 2 | **Độ phân giải bị nói quá**: `[−0,145;+0,086]` là dải theo *cách carve*, không phải theo *nhiễu lấy mẫu* | §3b mới — bootstrap theo ngày tôi tự chạy: lớp đang audit **+0,005 CI[−0,005;+0,017]**, tổng thể **+0,070 CI[−0,526;+0,707]** |
| 3 | **Cơ chế telescoping ở §3 là mô hình mà chính selfcheck của job khai là SAI** | xoá; thay bằng gross 0,0883 vs ròng +0,0037 (**24×**) = triệt tiêu thống kê giữa 176 mục độc lập |
| 4 | **Chân TRỌNG SỐ chưa bao giờ được audit** — `custom_basket.py:544` `mcapw = pxw × OShares` vẫn đúng cấu trúc giá × số CP | §5.5 mới, tôi tự đo: **900** phiên trong rổ giá re-base >0,5%, chỉ **153 (17%)** có `OShares` bước cùng phiên |
| 5 | **`0d` dùng điều kiện quá hẹp** (chỉ bước số CP; phép co cũng xảy ra trên cổ tức tiền, 5/8 ô sửa là DIV-only) | check **`0d2`** mới: ô sửa **không nằm trong rổ**, đo được **0** |
| 6 | **Điểm mù detector giá kẹt** (bất đẳng thức ngặt loại `ratio_d == lo`) | tôi đếm: **0 ô** lọt trên panel này ⇒ vô hại; ghi lại ở §6 |
| 7 | **Chưa có IS/OOS** (§18 `coding_guidelines`) | bảng walk-forward ở §3b: phantom **+16,7pp IS / +20,3pp OOS**, chênh thô **−0,295 / −0,759pp** |
| 8 | **Vi phạm §8**: hai `run_selfcheck.sh` song song ghi đè log + parquet | `flock` + không gian tên theo PID; §6 |

Không phát hiện nào **đảo** kết luận cơ chế; tất cả **thu hẹp phạm vi** và **hạ độ chính xác đã
tuyên bố**. Đó là lý do bản này phát biểu kết luận thành **hai câu có độ mạnh khác nhau**, không
phải một câu.

## 10. File

| File | Nội dung |
|---|---|
| `PREREG.md` | tiền đăng ký, ngưỡng 0,300pp + dự đoán đại số |
| `dump_basket.py` / `run_dump.sh` / `dump.log` | lấy membership + panel + 2 chân engine từ ĐÚNG lệnh pin R3 |
| `dump_ca.py` / `ca_vintage.parquet` | vintage `corporate_action` pin cho job này (7.277 dòng, 204 mã) |
| `replay.py` | bộ tái lập thứ ba (+ 6 mutation knob) |
| `attribute.py` / `attribution.parquet` / `attribute.log` | phân rã name×session + dải carve-out |
| `selfcheck_replay.py` / `selfcheck_replay.log` / `run_selfcheck.sh` | mutation + property, 3 TZ |
| `run_ab.py` / `run_ab.sh` / `ab_*.log` | A/B R3 park 0,30 |
| `ledger_legacy_vs_flat.csv` / `ledger_legacy_by_session.csv` | ledger phantom LEGACY |
| `rights_not_modelled.csv` | 195 sự kiện quyền mua trong cửa sổ, không mô phỏng được |
| `levels_base.parquet` | 4 chuỗi level |
| `resolve_power.py` / `resolve_power.log` | **vòng 3**: bootstrap độ phân giải theo nhãn, IS/OOS, đo lệch ngày chân trọng số |
| `blindspot.py` / `blindspot.log` | **vòng 3**: đếm điểm mù detector giá kẹt (8 ô bắt được / 0 ô lọt) |
| `selfcheck_replay_RACED.log` | log bị TRỘN bởi 2 run song song (sự cố §8) — giữ làm bằng chứng |
| `replay_v1_prefix.py.bak` / `attribute_v1.py.bak` | bản VÒNG 1 (đã bị REFUTED) — giữ để đối chiếu |
| `REPORT.md.v2_bak` / `replay.py.pre_0d2` / `selfcheck_replay.py.pre_unique` | bản VÒNG 2 trước khi vá theo skeptic vòng 3 |
