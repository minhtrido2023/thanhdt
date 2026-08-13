# corporate_action wire — Việc A/B/C (job `Taylor_20260813_041648`, 2026-08-13)

Nguồn: `lithe-record-440915-m9.tav2_bq.corporate_action`.
Đọc kèm: `kb/data_registry/price-volume/corporate_action_bq.md` ·
`kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`.

**Trạng thái: CHỜ quant-skeptic. Việc C ĐÃ ÁP vào 2 report paper (số đang chạy); A/B là
nghiên cứu/thiết kế, KHÔNG bật vào đường tiền thật.**

---

## 0. Freshness — bảng CHƯA refresh như đã hứa

Registry ghi user xác nhận "refresh HÀNG NGÀY từ 2026-08-13". Đo thật hôm nay:

    MAX(ingested_at) = 2026-08-12 15:48:52   (n_ingest_days = 1)
    MAX(public_date) = 2026-08-11            n = 36.149

⇒ vẫn đúng batch nạp một lần 2026-08-12 15:22→15:48, **chưa có lần nạp thứ hai**. Không kết luận
writer hỏng (mới sang ngày 08-13), nhưng **mọi pipeline phải tự kiểm `MAX(ingested_at)` mỗi lần
đọc** — `corp_action_lib.feed_freshness()` có sẵn cho việc đó. Mốc kiểm lại: 2026-08-14.

---

## 1. VIỆC C — bug thật, đang sai trong report gửi user (ĐÃ SỬA)

### Cơ chế
`entry_price` trong `data/alphalens_paper.json` là giá **THÔ, đóng băng** lúc lập sổ; `current` lấy
từ `ticker_1m.Close` là giá **ĐÃ ĐIỀU CHỈNH hồi tố theo vintage hôm nay**. Trộn 2 hệ quy chiếu =
đúng **Bẫy (2)** — mọi sự kiện quyền SAU ngày vào bị tính thành lỗ giá.

MBB: cổ tức tiền 1.000đ (ex 2026-07-09) + quyền mua 10% + cổ tức CP 15% (cùng ex 2026-08-11).
`Close/Price` tại 2026-06-30 = **0,800794** ⇒ giá vào phải quy đổi 25.200 → **20.180**.

### Số đo — A/B thật, cùng ngày dữ liệu 2026-08-12

| | trước (SAI) | sau (ĐÚNG) | lệch |
|---|---:|---:|---:|
| **alphalens** MBB | −18,8% | **+1,3%** | 20,2pp, **đảo dấu** |
| alphalens Portfolio | −3,08% | **+1,96%** | 5,04pp |
| alphalens Alpha vs VNINDEX | +0,51pp | **+5,56pp** | 5,05pp |
| **converge** MBB | −17,4% | **+3,2%** | 20,6pp, đảo dấu |
| converge HAH | −12,4% | **−8,8%** | 3,6pp |
| converge CTR | −9,5% | **+3,2%** | 12,7pp, đảo dấu |
| converge Portfolio | −4,85% | **−0,76%** | 4,09pp |
| converge Alpha vs VNINDEX | −0,65pp | **+3,44pp** | **đảo dấu** |
| converge Alpha vs V2.4 production | −2,80pp | **+1,29pp** | **đảo dấu** |

⚠️ Dòng cuối đáng chú ý nhất: kết luận "DC book THUA production" là **hiện vật của bug**, không
phải kết quả. Đừng trích số cũ.

> **⚠️ CỘT "sau (ĐÚNG)" Ở BẢNG NÀY ĐÃ BỊ THAY THẾ — xem §VÒNG 2/C1 ở cuối file.** Nó theo quy ước
> **TERP** (ngầm giả định holder đã thực hiện hoặc bán quyền mua), mà sổ paper không có tài khoản
> tiền nên không làm được. Số đang chạy hôm nay theo quy ước **accrue-only**: MBB alphalens
> **−2,9%** (không phải +1,3%), portfolio **+0,90%**, converge **−1,24%**. **Mọi đảo dấu ở cột
> "lệch" vẫn đúng** — đổi quy ước, không rút lui.

### Cách sửa — và vì sao chọn hướng này
`paper_entry_adjust.py`: `factor = Close(asof)/Price(asof)` (vintage hôm nay), `entry_adj =
entry_price × factor`, `pct = Close_now/entry_adj − 1`.

Cân nhắc 2 hướng dispatch nêu: (i) rebase `entry_price`, (ii) bỏ hẳn `entry_price`, so
`Close(entry_date)` vs `Close_now`. **Chọn (i)**. Hôm nay hai hướng cho số Y HỆT (vì `entry_price`
== `Price(asof)` đúng 13/13 mã), nhưng (ii) **vứt bỏ `entry_price` đã ghi** — nếu sau này một sổ
paper ghi giá vào không phải giá đóng cửa (khớp trong phiên, giá chọn tay), (ii) sẽ lặng lẽ đo
"mã tăng bao nhiêu" thay vì "vị thế lãi bao nhiêu". (i) giữ đúng bản ghi và chỉ đổi HỆ QUY CHIẾU.
(ii) được giữ lại làm **bộ kiểm**: lệch `entry_price` vs `Price(asof)` > 0,5% ⇒ in cảnh báo.

**KHÔNG cần bảng corp-action để tính** — `Close/Price` đã gộp sẵn mọi loại sự kiện, mà rebase
tổng-lợi-nhuận chỉ cần ĐỘ LỚN chứ không cần LOẠI sự kiện. Bẫy (4) cấm dùng tỉ số để suy **đồng/cp**
(vì không phân biệt được tiền/CP) — không cấm dùng nó để quy đổi thang giá. `corporate_action`
dùng để **KIỂM ĐỘC LẬP**, không dùng để tính.

### Tính an toàn — control property
Mã không có sự kiện ⇒ `factor == 1,0` ⇒ `entry_adj == entry_price` **tuyệt đối** ⇒ số y hệt trước
khi sửa. Xác nhận trên dữ liệu thật: **6/9 mã converge + 3/4 mã alphalens byte-identical**.
Fix chỉ có thể làm đổi số khi có sự kiện quyền thật.

### Đối soát độc lập (`paper_entry_corpaction_crosscheck.py`)
- **T1** `factor < 1` ⟺ có event executed accrue cho cổ đông hiện hữu: **13/13 khớp**.
- **T2** bậc nhảy tỉ số rơi ĐÚNG `exright_date`: **4/4 khớp**.

### Sửa kèm: metadata `alphalens_paper.json`
`entry_date` ghi 2026-07-01 nhưng cả 4 `entry_price` khớp TUYỆT ĐỐI giá thô phiên **2026-06-30**
(và đều lệch giá 07-01; `benchmark_entry` 1860,01 cũng là VNINDEX 06-30). Thêm
`entry_price_asof: "2026-06-30"` — **không đụng `entry_date`/`start_date`** (đó là ngày vào lệnh,
là bản ghi kiểm toán). Không có trường này thì hệ số bị lấy ở sai phiên khi có sự kiện rơi vào giữa.

---

## 2. VIỆC B — `oshares_live.py` (thiết kế, chưa wire)

Thay đường thủ công `update_shares_live.py` → `shares_outstanding_live` (4 dòng, Winston chạy tay).

**Phương pháp**: lấy mốc (anchor) MỚI NHẤT trong hai nguồn — `ticker_financial.OShares` (theo quý)
và `AIS.shares_total_after` — rồi lăn tới bằng `× (1+exercise_ratio)` cho mọi `ISS` có
`exright_date` sau mốc đó.

Chọn mốc theo NGÀY thay vì cố định một nguồn là điểm mấu chốt: **không nguồn nào luôn thắng**.
`AIS` chính xác nhưng trễ (~7 tuần, Bẫy 1), còn `ticker_financial` **đôi khi nhanh hơn hẳn** —
dòng 2025Q2 của FPT (`time` 2025-07-22) đã mang 1.703.507.121, **1 ngày sau ex-right và 7 tuần
trước AIS**.

**Test case bắt buộc (FPT) — ĐẠT:**

| ngày | Oshares | method |
|---|---:|---|
| 2025-07-20 (trước ex) | 1.481.330.122 | AIS_EXACT |
| **2025-07-21 (ex-right)** | **1.703.529.640** | ISS_ESTIMATE (lệch 0,0013%) |
| 2025-07-22 → 09-11 | 1.703.507.121 | ANCHOR_ONLY |
| **2025-09-12 (AIS)** | **1.703.507.121** | **AIS_EXACT — khớp tuyệt đối** |

Chuỗi tăng dần rồi khớp `shares_total_after` đúng yêu cầu. Một bước giảm duy nhất −0,0013%
(07-21→07-22) là **ước lượng nhường chỗ cho số đo**, không phải CP biến mất — selfcheck khẳng định
đúng tính chất đó thay vì giả vờ chuỗi đơn điệu tuyệt đối.

**Phát hiện phụ, quan trọng cho cả A và B — hai câu hỏi KHÁC NHAU** (`corp_action_lib.py`):

| | tăng số CP? | điều chỉnh giá tại ex? |
|---|---|---|
| Cổ tức CP / thưởng CP / quyền mua cổ đông hiện hữu | CÓ | **CÓ** |
| ESOP / riêng lẻ / chuyển đổi TP / đấu giá / sáp nhập | CÓ | **KHÔNG** |

Đo thật: HAH ESOP 1,858% ex **2026-07-28** → tỉ số `Close/Price` **1,000000 → 1,000000** (không
nhảy). *(Đính chính 2026-08-13: bản đầu ghi nhầm ex-date là 2025-07-28 — quant-skeptic bắt. HAH
không có ISS nào vào 2025-07-28; đợt gần nhất trước đó là cổ tức CP 30% ex 2025-08-07.)*
FPT 2 đợt ESOP 2025-05-07 y hệt. ⇒ Oshares phải đếm **MỌI** ISS; rebase giá chỉ được kỳ vọng ở
nhóm trên. Kiểm chứng: lăn qua 2 đợt ESOP của FPT cho 1.481.338.158 vs AIS thật 1.481.330.122 —
**lệch 0,0005%**.

---

## 3. VIỆC A — `dividend_adjusted_return.py` (đã nâng cấp, giữ nguyên thứ bậc tin cậy)

`bq_corp_action()` trước đây tra `shares_outstanding_live` (4 dòng, gần như luôn rỗng) → đổi sang
`corporate_action`: lọc `event_status='executed'` (loại cả `not_executed` lẫn `announced`), dedup
theo `(event_code, issue_method, value_per_share, exercise_ratio)` rồi mới SUM (Bẫy 3 — MBB
2026-08-11 có 2 đợt THẬT cùng ngày, phải giữ cả hai; bản đính chính thì gộp).

**Thứ tự CỐ Ý không đảo**: tiền broker thật giải TRƯỚC (tầng 2 vẫn là nguồn số chính thức), vendor
chạy SAU và làm 3 việc: (1) **phân loại** DIV/ISS dứt khoát — giải Bẫy (4), thay cho dấu hiệu yếu
`openQuantity` vốn vừa bỏ sót thưởng CP vừa dương tính giả khi có lệnh khớp trùng cửa sổ;
(2) **đối soát chéo** nghiệm broker; (3) **lấp** chỗ broker không giải được, nhưng gắn nhãn RIÊNG
`CASH_VENDOR`.

**`CASH_VENDOR` KHÔNG tự động vào báo cáo** (`cash_per_share` vẫn chỉ nhả `CASH_CONFIRMED`). Mở
cổng là **quyết định CHÍNH SÁCH của user**, không phải quyết định kỹ thuật (§22).

### Bằng chứng thực nghiệm cho nguồn vendor — 6/6 KHỚP TUYỆT ĐỐI

Đối chiếu `DIV.value_per_share` với số giải độc lập từ **tiền broker thật** (6 sự kiện tháng 7):

| mã | ex-date | broker | vendor | |
|---|---|---:|---:|---|
| MBB | 07-09 | 1.000 | 1.000 | ✓ |
| BID | 07-17 | 450 | 450 | ✓ |
| CTG | 07-23 | 450 | 450 | ✓ |
| VCB | 07-23 | 450 | 450 | ✓ |
| NCT | 07-27 | 8.000 | 8.000 | ✓ |
| SAB | 07-28 | 3.000 | 3.000 | ✓ |

Khớp tới từng đồng, 5 mã / 5 ex-date khác nhau, **gồm cả ca khó** CTG+VCB trùng ex-date (hệ 2×2).
**Nhưng n=6, cùng một tháng, và mọi sự kiện đều là cổ tức tiền mặt thuần** — chưa nói được gì về
độ trễ công bố của vendor, cũng chưa có ca ISS/hỗn hợp nào để kiểm. Đủ để **đề xuất** mở cổng
`CASH_VENDOR`, chưa đủ để tự mở.

---

## 4. Bug hạ tầng phát hiện dọc đường — `bq` CLI cắt 100 dòng ÂM THẦM

`bq query` mặc định `--max_rows=100`, cắt không lỗi không cảnh báo. `oshares_live` hỏi 2 mã cùng
lúc (~150 dòng quý) → mất các quý mới của PVT → lặng lẽ rơi về anchor **cũ một năm** (AIS
2025-08-01) và vẫn trông hoàn toàn khoẻ mạnh. Đã vá: `corp_action_lib.bq()` luôn truyền
`--max_rows` + RAISE khi chạm trần.

Không phải lỗi mới của fleet: `dividend_adjusted_return.py` đã ghim đúng cạm bẫy này từ
2026-08-02 (`BQ_MAX_ROWS = 200_000`, cắn thật lần đó là batch nhiều mã chỉ nhận 4 mã đầu bảng chữ
cái). **Lần này tái diễn ở file MỚI vì bài học nằm trong một file khác** — ứng viên tốt cho
`coding_guidelines` (mọi wrapper `bq` phải đặt trần + raise), đề xuất chứ chưa tự thêm.

Ca đối chứng "mã không có sự kiện" chính là thứ bắt được bug này — nó cho kết quả sai ở một mã mà
tôi *tưởng* là control. **Giả định control sai lại là thứ có giá trị nhất trong cả job.**

---

## 5. File + selfcheck

| File | Vai trò | Selfcheck |
|---|---|---|
| `paper_entry_adjust.py` | MỚI — rebase giá vào (Việc C) | **21/21 PASS** |
| `corp_action_lib.py` | MỚI — reader + taxonomy accrue/dilute | **7/7 PASS** |
| `oshares_live.py` | MỚI — Oshares tại ngày bất kỳ (Việc B) | **22/22 PASS** |
| `paper_entry_corpaction_crosscheck.py` | MỚI — đối soát độc lập | T1 13/13 · T2 4/4 |
| `alphalens_report.py` | SỬA — dùng rebase | qua A/B thật |
| `converge_report.py` | SỬA — cùng lỗi | qua A/B thật |
| `data/alphalens_paper.json` | SỬA — thêm `entry_price_asof` | — |
| `mike/bin/dividend_adjusted_return.py` | SỬA — Việc A | **58/58 PASS, không hồi quy** |

**Phạm vi hồi quy (§23)**: `resolve_dividends` chỉ có MỘT consumer thật là
`mike/bin/report_return_gate.py`, và nó đọc `cash_per_share` (ngữ nghĩa KHÔNG đổi) — selfcheck
PASS. `daily_nav_snapshot.py` và `corp_actions.py` gọi `detect_adjustments_batch` (tầng 1), không
đi qua đường vừa sửa. `lag_entry_anchor.py` không gọi hàm nào bị đụng.

---

## 6. Việc còn treo / cần quyết

1. **quant-skeptic review** — bắt buộc trước khi coi Việc C là đã đóng, dù nó đang chạy trong
   report (paper, không phải tiền thật).
2. **User quyết**: có mở cổng `CASH_VENDOR` vào báo cáo không? Đề xuất: **chưa**, chờ ≥1 sự kiện
   ISS/hỗn hợp và ≥1 tháng nữa.
3. **Kiểm 2026-08-14**: `MAX(ingested_at)` đã nhích chưa. Chưa nhích ⇒ báo user, đừng xây tiếp
   trên giả định feed sống.
4. **Chưa wire `oshares_live.py`** vào bất kỳ consumer nào (`rating_8l`, market-cap, EPS). Cần
   quyết định riêng + đối soát rộng hơn 1 mã trước khi thay `OShares` ở đường sản xuất.
5. Đề xuất `coding_guidelines`: wrapper `bq` phải đặt `--max_rows` + raise khi chạm trần.

---

# VÒNG 2 — sửa theo quant-skeptic (job `Taylor_20260813_050945`, 2026-08-13)

Vòng 1: Việc B **REFUTED**, Việc C **CONFIRMED** kèm 1 sub-claim overstate + 2 rủi ro fail-silent.

## B. `oshares_live.py` — hai lỗi đã đo, đã vá. **VẪN CHƯA WIRE.**

**B1 — neo "mới nhất giữa hai nguồn" là look-ahead.** `ticker_financial.OShares` bị RESTATE. Đo
lại độc lập hôm nay (dòng quý trùng khít <1cp với `shares_total_after` của một AIS *executed* có
hiệu lực SAU đó): **2.667 dòng / 576 mã**, sớm nhất **2.693 ngày**; lát cắt từ 2024-01-01 là
**626 dòng / 247 mã**, sớm nhất **819 ngày**, trong đó **145 dòng / 75 mã** là look-ahead CỨNG
(có `ISS` đi ex SAU dòng quý). Khớp con số quant-skeptic báo (631/247, 819, ~146) trong sai số
định nghĩa.

Vá: **AIS là neo chính**; dòng quý chỉ được nhận khi **tự giải thích được** — lăn AIS gần nhất
TRƯỚC nó qua các ISS ở giữa, khớp trong `EXPLAIN_TOL=0,1%`. Ngưỡng chọn từ số đo: gap thật lớn
nhất là FPT **0,0013%** (làm tròn cổ phiếu lẻ trên thưởng 15%), còn HAH lệch **+10,06%**.

Không phải "cổng chặn hết cho an toàn" — ca **5b** chứng minh ngược: dòng quý FPT **2025-07-22**
(số sau thưởng, một ngày sau ex-right, 7 tuần trước AIS) **vẫn được nhận**, `rejected_anchors=[]`.
Dữ liệu sớm thật đi qua, restatement bị loại.

**B2 — roll-forward bằng `exercise_ratio` là no-op trên nhóm không-accrue.** `shares_delta` **NULL
100%** trên ISS (0/9.297) nên không cứu được. Vá: ưu tiên `shares_delta` khi có (nhánh chết hôm
nay, giữ vì thứ tự ưu tiên chính là phát biểu về tính đúng), `ratio ∈ {0, NULL}` mà không delta ⇒
**fail CLOSED**: `value=None`, `method="UNKNOWN_RATIO"`, liệt kê `blocking_events`.

**B3 — ca hồi quy có sự kiện thật** (chân đối chứng cũ DHG/PVT/TCB/ACB/HDB không có sự kiện nào ⇒
không bao giờ fail được):

| Ca | Kỳ vọng | Kết quả |
|---|---|---|
| H1/H2 HAH 2026-03-01 | KHÔNG ra 185.840.401; ra 168.861.212 | PASS — loại anchor quý 2026-02-02, lệch +10,06% |
| H3 | lý do loại được NÊU RA | PASS |
| H4 HAH 2025-03-25 & 2026-03-13 | chuyển đổi TP ratio 0,0 ⇒ `UNKNOWN_RATIO`, `value=None` | PASS cả hai |
| P0/P1 NAF 2026-01-06 | "Phát hành riêng lẻ" ex 2026-01-05 ⇒ `UNKNOWN_RATIO` | PASS (mã tự dò từ BQ, không chép cứng) |
| 8d DHG | không có AIS nào ⇒ `ANCHOR_UNVERIFIED`, không giả vờ đã kiểm | PASS |
| 10 | bất biến `value is None ⟺ method ∈ {UNKNOWN_RATIO, NO_ANCHOR}` | PASS |

`oshares_live.py --selfcheck` = **22/22 PASS** (số do máy đếm, xem B4).

**B4 — hai lỗi nhỏ.** (a) HAH ESOP: ex-date đúng là **2026-07-28** (ratio 0,01858), không phải
2025-07-28 — HAH không có ISS nào ngày đó; đã đính chính tại chỗ ở §4. (b) Cả hai selfcheck từng
in tổng số **gõ tay** ("11/11") trong khi thực chạy 12 ca; nay `check()` tự đếm `len(ran)` nên con
số không thể lệch nữa.

**B5 — entry TRAP** (`coding_guidelines` §9, phải có TRƯỚC khi code mới đọc cột này):
`mike/kb/data_registry/fundamentals/ticker_financial_oshares.md` + link từ `index.md` và
`ticker_financial.md`.

**Giới hạn công bố thẳng**: cổng giải thích chỉ loại được restatement khi nó mâu thuẫn với sự kiện
feed ĐÃ CÓ. Dòng bị restate về con số mà AIS hậu thuẫn chưa ingest thì cổng mù — điểm mù chung của
mọi tái dựng point-in-time.

## C. Báo cáo paper — quy ước quyền mua + hai lưới chặn fail-silent

**C1 — sub-claim "MBB thật +1,3%" đã sửa.** `Close/Price` theo quy ước **TERP** (giả định holder
đã mua quyền hoặc bán quyền theo giá lý thuyết). Kiểm bằng nghịch đảo chính bậc nhảy MBB
2026-08-11 (quyền mua 10% @10.000đ + cổ tức CP 15% cùng ngày):

    (24.250 + 0,10×10.000) / (24.250 × 1,25) = 0,832990   — khớp bậc nhảy quan sát tới 6 chữ số

Sổ paper **không có tài khoản tiền**, không thực hiện được quyền ⇒ quy ước đúng là **accrue-only**
(chỉ cổ tức tiền + cổ tức CP/thưởng; quyền mua bị LOẠI, coi như để mất). Đó nay là số headline;
`factor_terp` vẫn được báo kèm ngay trên dòng mang số, không giấu xuống chân trang.

| | trước (TERP) | sau (accrue-only) |
|---|---:|---:|
| MBB alphalens | +1,3% | **−2,9%** |
| alphalens portfolio | +1,96% | **+0,90%** (alpha +4,49pp) |
| converge portfolio | −0,76% | **−1,24%** (alpha vs VNINDEX +2,96pp, vs production +0,81pp) |

Khớp con số quant-skeptic tự tính lại (+0,95% / −1,22% / +4,55 / +2,98 / +0,83pp) trong sai số
ngày giá. **Mọi đảo dấu của bản vá gốc vẫn giữ nguyên** — đây là sửa quy ước, không phải rút lui.

Phần quyền được tách ra như **phần dư** của bậc nhảy ex-date sau khi chia hết mọi sự kiện cùng
ngày (feed không mang giá thực hiện quyền: `value_per_share` NULL trên dòng rights). Không tách
được ⇒ `RIGHTS_UNRESOLVED`, **không** âm thầm rơi về TERP (ca 17).

**C2 — vintage cache.** `stale_years()` + status `VINTAGE_STALE`: `asof` rơi vào một file năm cũ
hơn phần còn lại >2 ngày ⇒ **không rebase**, không under-adjust im lặng.

⚠️ Điều chỉnh so với đề bài: **không** chặn theo "có file năm nào cũ không". Đo thật: **13/14 file
năm (2013-2025) cũ hơn `2026.parquet` ~14 ngày** — đó là trạng thái BÌNH THƯỜNG (sync đêm chỉ ghi
lại năm hiện tại). Chặn theo đó = báo động giả trên MỌI báo cáo, và cổng kêu mỗi ngày là cổng bị
bỏ qua. Việc chặn thuộc về `adjust_entries`, nó gắn cờ đúng vị thế có `asof` rơi vào năm cũ; cổng
chỉ IN ra giao/không-giao giữa "năm cũ" và "năm sổ paper đang dùng".

**C3 — T1 đã WIRE vào `mike/bin/report_return_gate.py`** (`paper_entry_gate()`, chạy TRƯỚC chân
broker vì báo cáo "New deals" mang mục paper nhưng **không** mang nhãn tài khoản nào trong tên
file ⇒ nhánh thoát sớm cũ bỏ qua nó hoàn toàn). Nhận diện theo NỘI DUNG (`PAPER_MARKERS`).

    T1:  factor_terp < 1  ⟺  có DIV/ISS executed điều-chỉnh-giá trong (asof, hôm nay]

T1 neo vào `factor_terp` chứ **không** phải factor dùng để báo cáo — T1 hỏi "chuỗi giá có điều
chỉnh không", đó là câu hỏi về chuỗi giá. Neo vào factor accrue-only sẽ báo động giả ở ca quyền-
mua-đơn-thuần (accrue-only = 1,0 hoàn toàn đúng đắn). Mọi status `degraded` cũng CHẶN. Không tra
được `corporate_action` ⇒ CHẶN (fail-closed).

**Kiểm chứng, hai chiều:**

| | Kết quả |
|---|---|
| `report_return_gate.py --selfcheck` | PASS, **+12 ca mới** (đủ 4 hình dạng T1 + 4 status degraded + no-op) |
| Chạy THẬT trên báo cáo có mục paper (13 vị thế) | **PASS 13/13**, exit 0 |
| **Chứng minh ngược** — cache vintage trước sự kiện (`Close := Price`) | **CHẶN 6 lỗi / 4 vị thế** có sự kiện (MBB×2, HAH, CTR); **9/9 vị thế không sự kiện KHÔNG bị đụng** |

Ca chứng minh ngược là điểm mấu chốt: cắt cụt cache theo NGÀY **không** tái lập được lỗi (giá trị
`Close` đã restate nằm sẵn TRONG dòng, không suy từ dòng sau) — phải dựng lại đúng vintage
`Close = Price`. Ghi lại vì lần sau dễ dựng nhầm ca thử rồi tưởng đã chứng minh.

## Việc còn treo sau vòng 2
1. **quant-skeptic vòng 2** — bắt buộc. Tôi KHÔNG tự nhận đã đóng.
2. `oshares_live.py` vẫn **NOT WIRED** (đã ghi thẳng vào docstring). Wire cần quyết định riêng.
3. Mục 2-5 của §6 ở trên không đổi.
