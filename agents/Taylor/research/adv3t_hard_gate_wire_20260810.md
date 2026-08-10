# Wire sàn ADV3T 2 tỷ/phiên thành GATE CỨNG cho LAG + BAL — **ĐÃ VIẾT, CHƯA ÁP**

- **Job**: `Taylor_20260810_081207` · 2026-08-10 · Taylor
- **Trạng thái**: patch nằm ở `mike/agents/Taylor/pending_adv3t_hard_gate_20260810/`,
  **production sạch 0 dòng** (đã `git checkout` sau khi test — xác nhận bằng `git status` rỗng
  trên cả 5 file). Chờ quant-skeptic + Mike duyệt.
- **Cơ sở quyết định**: user chốt sau finding `Taylor_20260810_073541` — **hiệu quả vốn**, KHÔNG
  phải edge. Điều này được ghi thẳng vào comment code (xem §3) vì backtest nói NGƯỢC LẠI và người
  đọc sau sẽ tưởng là lỗi.

---

## §0 — TL;DR

| Việc dispatch | Kết quả |
|---|---|
| 1. Ngưỡng đang enforce ở `lag_filter_illiquid()` | **`> 0` (nhị phân), KHÔNG có ngưỡng độ lớn** — trích dòng ở §1 |
| 2. Bỏ 1 ứng viên thì vốn có tự dồn sang deal to hơn không? | **KHÔNG dồn size. LAG: không có hàng đợi, vốn rơi về cash → parking custom30V. BAL: CÓ lấp slot (26/47 phiên có hàng đợi >12) nhưng trọng số/slot CỐ ĐỊNH 10%** — §2 |
| 3. Wire gate cứng ở tầng chọn mã | **XONG** — `ADV_MIN_VND=2e9`, 2 hàm, loại trước `select_book`/trước plan; KHÔNG đụng executor, KHÔNG đụng sleeve discretionary — §3 |
| 4. Selfcheck có ca chứng minh ngược | **XONG — 50/50 PASS** (40 unit + 10 live), mọi ca "chặn được" đều kèm ca "bỏ gate ⇒ lọt qua" — §4 |
| 5. Dọn câu chữ `due_diligence.py` | **KHÔNG phải dead code** (đã verify cơ chế, không đoán) — §5 |
| 6. quant-skeptic + pending_ | patch + README theo convention — §6 |

**Cái giá đo được ngay hôm nay: rổ ứng viên LAG 176 → 58 mã (loại 118, trong đó 101 mã là do
sàn mới).** Trong nhóm bị sàn mới chặn có **TRC** — đúng mã user duyệt mua 07-24.

---

## §1 — Việc 1: ngưỡng ĐANG enforce (trích dòng, không suy đoán)

`lag_liquidity_filter.py::lag_filter_illiquid()`, 3 nhánh loại duy nhất, nguyên văn:

```python
:170        if r is None:
:171            dropped.append({"ticker": tk,
:172                            "reason": f"không có dòng giá nào trong {LOOKBACK_DAYS} ngày gần nhất"})
:174        stale = (asof_d - pd.Timestamp(r.time).date()).days
:175        if stale > max_stale_days:                      # LAG_ADV_MAX_STALE_DAYS = 30
:179        if not (pd.notna(r.adv_vnd) and float(r.adv_vnd) > 0):
:180            dropped.append({... "reason": f"Volume_3M_P50={r.Volume_3M_P50} → ADV ≤ 0, ..."})
```

⇒ **Ngưỡng độ lớn đang enforce = 0 VND.** Phép thử là `adv_vnd > 0` — nhị phân "đo được và dương
hay không", không có sàn nào. So với 2 tỷ đề xuất: **khoảng cách là toàn bộ băng (0; 2e9)**, và
đó chính là băng job trước đo được là 1,6% vốn / 93,4% bỏ dở.

ADV dùng đúng công thức PIT của audit (`:156-161`):
`Volume_3M_P50 × COALESCE(Price, Close)` trên dòng MỚI NHẤT có `time <= asof`. Cùng một công thức
xuất hiện ở 3 nơi và **cả 3 đều khớp** — `signal_v11_sql.py:95` (cột `liq`),
`trading_bot/due_diligence.py::adv_vnd`, và hàm này. Patch không đẻ công thức thứ tư.

**Phạm vi thật của hàm** (docstring `:133-138`, đã verify lại): CHỈ book LAG. BAL đi đường khác —
`signal_v11_sql.py:143` `FROM classified WHERE liq >= 1e9` **cứng trong SQL**. CAPIT pool đã lọc
`>= 2` tỷ; PARK custom30V min ADV 13,1 tỷ. ⇒ **hai book cần sửa là LAG (sàn 0) và BAL (sàn 1e9)**.

---

## §2 — Việc 2 (CÂU HỎI QUYẾT ĐỊNH): vốn có tự dồn sang deal to hơn không?

**Trả lời ngắn: KHÔNG. Trọng số mỗi vị thế là HẰNG SỐ ở cả hai book — không có cơ chế nào tăng
size khi một ứng viên bị loại.** Hai book hỏng theo hai kiểu khác nhau:

### BAL — CÓ lấp slot, KHÔNG tăng size

```python
golive_recommend_v23.py:90   MAX_POS = 12; POS_PCT = 0.10; WEAK_PCT = 0.05
:663  today["weight"] = np.where(today["weak"] & half_in_state, WEAK_PCT, POS_PCT)
:669  def select_book(cand):
:670      c = cand.sort_values(["prio", "ta"], ascending=[True, False])
:672      for _, r in c.iterrows():
:673          if len(picked) >= MAX_POS: break
```

`select_book` là **hàng đợi có trần**: loại 1 mã ⇒ mã xếp sau được xét, **nếu hàng đợi dài hơn 12**.
Trọng số thì lấy từ `today["weight"]` đã gán TRƯỚC đó và **không phụ thuộc số mã được chọn** ⇒ mã
còn lại không to lên một đồng nào.

Hàng đợi có thật sự dài hơn 12 không — đo 365 ngày (SIGNAL_V11, TIER_BAL, 47 phiên có tín hiệu):

| Số dòng eligible/phiên | trung vị **14** · max 35 · **26/47 phiên (55%) có >12** |
|---|---|
| Băng `[1e9, 2e9)` = phần sàn 2 tỷ THÊM vào | **80/720 dòng = 11,1%**, 16 tên riêng (ABW, ADS, AFX, BCC, D2D, HHP, LBM, MVC, OGC, PHC, PVP, SJD, SJE, SJS, TCI, TVS) |
| Số phiên có ít nhất 1 dòng bị cắt | 36/47 |

⇒ **~55% số phiên sẽ có mã xếp sau lấp chỗ; ~45% còn lại vốn rơi ra ngoài.**

### LAG — KHÔNG có hàng đợi nào để lấp

LAG không đi qua `select_book`. Ứng viên = các sự kiện PEAD tới hạn vào T+5 (`:718-728`); **mọi**
ứng viên qualify đều thành mục tiêu, trọng số cố định `LAG_TW = {"LAG_HI": 0.10, "LAG_LO": 0.08}`
(`:303`) của `NAV_book_LAG`. Không có `MAX_POS` nào ở đường LIVE — chính docstring của module ghi
nhận khe hở này (`lag_liquidity_filter.py:113-119`: *"đường LIVE … KHÔNG có trần vị thế nào cho
book LAG"*). ⇒ loại 1 ứng viên = **1 slot biến mất, không ai thế chỗ**.

### Vậy vốn đi đâu?

Về **cash nhàn rỗi**, rồi bị `mike/bin/compute_park_trim.py` hút vào **rổ parking custom30V** theo
tỷ lệ `PARK_TARGET` (state NEUTRAL: `ETF_PARK = {3: 0.8}` — 80% cash nhàn rỗi;
`compute_park_trim.py:17` `pool = (totalCash − totalDebt) + park_mv`).

⇒ **Lợi ích user kỳ vọng — "dồn lực vào deal thanh khoản cao/size lớn hơn" — KHÔNG tự xảy ra ở
tầng sizing.** Cái xảy ra thật là: (a) BAL lấp slot bằng mã xếp sau ở ~55% phiên, (b) phần vốn
còn lại chuyển từ "rót vào deal mỏng" sang "nằm trong rổ parking custom30V". Đó vẫn là một sự
chuyển dịch có thật và nhất quán với lý do *hiệu quả vốn* của user (custom30V parking là cấu phần
đo được tin cậy nhất của V2.4: +7,4pp Full), nhưng **nó KHÔNG phải "deal to hơn"**.

**Tôi KHÔNG thêm logic dồn vốn** — dispatch nói rõ chỉ báo cáo hiện trạng. Nếu user muốn size to
hơn thật thì đó là thay đổi RIÊNG ở `POS_PCT`/`LAG_TW` và phải qua backtest + quant-skeptic riêng.

---

## §3 — Việc 3: gate đã wire (5 file, 310 dòng thêm / 29 xoá)

| File | Sửa gì |
|---|---|
| `lag_liquidity_filter.py` | `ADV_MIN_VND = 2e9`; `lag_filter_illiquid(..., min_adv_vnd=ADV_MIN_VND)` thêm nhánh loại thứ 4; hàm mới `bal_filter_thin()`; `_thin_reason()` sinh chuỗi lý do chung |
| `deploy_golive_dt5g_v4/golive_recommend_v23.py` | gọi `bal_filter_thin(today)` **ngay trước `select_book`** (`:671`, `select_book` ở `:680`, `bal = select_book(today)` ở `:692`); 4 field mới trong `status.json`; 1 dòng mới trong report MD |
| `lag_liq_ledger.py` | thêm regex `adv_thin` **đứng trước** `_RE_VOL` |
| `trading_bot/due_diligence.py` | câu chữ (§5) |
| `lag_liq_signal_filter_selfcheck.py` | 40 → 50 case (§4) |

### Ba quyết định thiết kế đáng chất vấn nhất

**(a) KHÔNG sửa `signal_v11_sql.py:143` `liq >= 1e9` → `2e9`.** Đó là chỗ "hiển nhiên" nhất và
là chỗ **sai nhất**: `pt_v23_audit_2014.py:48` `from signal_v11_sql import SIGNAL_V11` — engine
backtest đã pin R3 **import thẳng cùng chuỗi SQL đó**. Sửa 1e9→2e9 ở đó = **lặng lẽ đổi nền
R3 28,86% đã pin** mà không ai thấy, đúng loại lỗi §8 coding_guidelines. Sàn BAL vì vậy áp ở
**tầng live**, trên cột `liq` đã có sẵn của mỗi dòng tín hiệu — cùng công thức, cùng ngày,
**không thêm một truy vấn BQ nào**, và backtest giữ nguyên bit-for-bit.

**(b) Sàn là THAM SỐ, mặc định = hằng số.** `min_adv_vnd=0` tái lập hành vi trước 2026-08-10
bit-for-bit ⇒ rollback một chữ, và chân control của selfcheck dùng đúng đường đó (không phải
một nhánh code riêng chỉ tồn tại cho test).

**(c) Fail-safe khác chiều nhau, có chủ ý.**

| Hỏng kiểu gì | LAG | BAL |
|---|---|---|
| Cả truy vấn/nguồn hỏng | **fail-OPEN** (giữ nguyên + cờ lỗi) — giữ nguyên hành vi có sẵn, `cap_lag_orders` ở executor vẫn fail-closed | **fail-OPEN** (thiếu cột `liq`) — nền `liq >= 1e9` vẫn nằm trong chính SQL nên không có mã "không đo được" nào lọt tới đây |
| Từng dòng thiếu số | **fail-CLOSED** (loại) | **fail-CLOSED** (`NaN` → loại) |

Chặn sạch một book vì một lỗi mạng là thiệt hại lớn hơn nhiều lần thiệt hại của việc để lọt một
phiên — đây là lập luận đã có sẵn trong module, patch chỉ giữ nguyên chứ không phát minh.

### Phạm vi — grep lại lần 2 trước khi giao patch (dispatch yêu cầu)

- `trading_bot/discretionary_accumulation.py`: **0 dòng** khớp
  `lag_filter_illiquid|bal_filter_thin|lag_liquidity_filter|SIGNAL_V11` ⇒ **sleeve fear-buy
  (TV1/DGC) KHÔNG đi qua gate này**, đúng như job trước kết luận.
- `git diff --stat signal_v11_sql.py trading_bot/plan.py` = **rỗng** ⇒ **KHÔNG đụng `plan.py`**
  (module lõi 21 selfcheck) và **KHÔNG đụng SQL dùng chung với backtest**. Vì vậy §23 KHÔNG kích
  hoạt quét rộng cho `plan.py`. File lõi duy nhất bị chạm là `due_diligence.py` (2 selfcheck phụ
  thuộc) — đã chạy cả 2, xem §4.
- Không đụng `executor.py`: gate nằm ở khâu **chọn mã**, đúng như dispatch yêu cầu.

---

## §4 — Việc 4: selfcheck **50/50 PASS**, mọi ca chặn đều có ca chứng minh ngược

`lag_liq_signal_filter_selfcheck.py` (mở rộng file có sẵn, không đẻ file mới), 4 khối:

| Khối | Nội dung | Số ca |
|---|---|---|
| **A** | 3 nhánh cũ, chạy với `min_adv_vnd=0` — vừa giữ nguyên ý nghĩa gốc, vừa là **chân control** chứng minh rollback tái lập đúng hành vi cũ | 14 |
| **B** | sàn 2 tỷ trên LAG: TRC số thật bị loại + **B1' bỏ sàn ⇒ TRC LỌT**; biên `<` (đúng 2,000 tỷ giữ / thiếu 1đ loại); sàn không nuốt 3 nhánh cũ; stale đi trước sàn; BQ lỗi vẫn fail-open | 9 |
| **C** | `bal_filter_thin`: chặn + **C1' bỏ sàn ⇒ cả 3 lọt**; biên; NaN fail-closed vs thiếu cột fail-open; `liq` kiểu chuỗi; rỗng/None; không mutate đầu vào | 12 |
| **D** | chuỗi lý do parse được bởi `lag_liq_ledger.parse_liq_reason` → `adv_thin`, và **`adv_zero`/`stale_adv`/`no_price_row` KHÔNG bị regex mới nuốt** | 5 |
| **live** | BQ thật: TRC bị loại; **min ADV của rổ giữ lại = 2,08 tỷ ≥ sàn** (đo lại độc lập bằng query riêng, không tin danh sách `dropped`) | 10 |

**Chạy lại đủ biến thể môi trường** (§16 + skill `verify-before-done`):
`env -u TZ` · `TZ=America/New_York` · `TZ=UTC` · `$DNA_PYEXE` (pandas 3) · `python3` hệ thống
(pandas 2.3) ⇒ **40/40 unit ở cả 5 tổ hợp**, `--live` 50/50 dưới `$DNA_PYEXE`.

**Quét theo phạm vi (§23)** — file lõi duy nhất bị chạm là `due_diligence.py`
(`bin/selfcheck_scope_map.sh` ⇒ 2 selfcheck phụ thuộc):
`due_diligence_selfcheck.py` **35/35 OK** · `lag_adv_cap_selfcheck.py` **29/29 PASS**.
`golive_recommend_v23.py` không có selfcheck nào import → `py_compile` + kiểm AST xác nhận 4 tên
mới có mặt; **CỐ Ý không chạy script thật** vì nó ghi đè artifact canonical
(`data/golive_v23_status.json`, `out/*.csv|md`) — §8.

### Một ca test cũ đã bị ĐẢO, có chủ ý

`live: TRC (ADV ~1,4 tỷ) KHÔNG bị loại` → `live: TRC (ADV ~1,44 tỷ < sàn 2 tỷ) BỊ LOẠI`.
Giữ nguyên ở dạng ngược (thay vì xoá) để lần sau ai đọc log thấy ngay là **đảo có chủ ý**.

---

## §5 — Việc 5: cảnh báo trong `due_diligence.py` **KHÔNG phải dead code** (verify, không đoán)

Dispatch dự đoán cảnh báo `⚠ thanh khoản mỏng` sẽ thành code chết. **Sai** — verify bằng cơ chế:
`mike/bin/send_plan_report.sh:601-611` chạy `run_due_diligence` cho **MỌI lệnh MUA trong plan**,
mà có những đường vào plan **không** đi qua 2 gate mới:

- **sleeve discretionary/fear-buy** (`discretionary_accumulation.py` — 0 hit khi grep, đã nêu §3);
- vị thế legacy/excluded và các book có gate thanh khoản RIÊNG (CAPIT/PARK).

⇒ Giữ cảnh báo, nhưng **sửa câu chữ để 2 nguồn không nói khác nhau**: nói rõ 2 tỷ nay là sàn CỨNG
của LAG/BAL, và *lệnh tới được đây nghĩa là nó KHÔNG đi qua gate đó*. Comment tại `ADV_THIN_VND`
ràng buộc hai hằng số phải đổi cùng nhau; selfcheck có 1 ca đóng đinh `ADV_MIN_VND == 2e9`.

---

## §6 — Rủi ro & những gì tôi KHÔNG khẳng định

1. **Số backtest nói NGƯỢC với quyết định này và tôi không làm nó mềm đi.** Phần gia tăng của
   sàn 2 tỷ = **−0,26pp CAGR / −0,02 Sharpe / −0,92pp OOS**, thang liều **phẳng** 0,5→5 tỷ,
   **PBO 0,916** (`Taylor_20260804_080547`, quant-skeptic CONFIRMED cao). Wire vì hiệu quả vốn —
   **không được trích ngược lại như edge**, và ai định tinh chỉnh ngưỡng phải đọc PBO trước.
2. **Cái giá cụ thể, đã đo hôm nay**: LAG 176 → 58 ứng viên (−67%). Trong 101 mã bị sàn mới chặn
   có **TRC** (ADV 1,44 tỷ) — chính mã user duyệt mua 07-24 theo phương án C. Nếu user muốn
   TRC-like vẫn qua được thì sàn phải < 1,44 tỷ, và đó là quyết định CHÍNH SÁCH của user, không
   phải điều tôi tự chỉnh.
3. **BAL chỉ lấp slot ở ~55% số phiên** (§2). Ở 45% còn lại, sàn = giảm số vị thế BAL thật.
4. **Ledger `lag_liq_ledger.py` chỉ ghi book LAG.** Dòng BAL bị sàn loại nằm ở
   `bal_liq_excluded` trong `status.json` nhưng **chưa vào ledger** — cố ý (khác book, khác đơn vị
   thống kê); nếu sau này muốn theo dõi cả BAL thì phải thêm `GATES` entry, không tự xảy ra.
5. **Kích thước mẫu**: mọi số ở §2 đo trên 47 phiên có tín hiệu BAL trong 365 ngày. Đủ để nói về
   *cơ chế* (hàng đợi dài hơn trần hay không), **không** đủ để nói về *lợi nhuận*.
6. **Chưa chạy `golive_recommend_v23.py` thật** (§4) ⇒ tích hợp end-to-end mới được kiểm ở mức
   compile + AST + hàm cô lập. Phiên chạy thật đầu tiên sau khi áp cần soát log
   `[bal-liq]`/`[lag-liq]` và `n_bal_liq_excluded` trong `status.json`.

---

## §7 — Cách tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
patch -p1 --forward < mike/agents/Taylor/pending_adv3t_hard_gate_20260810/adv3t_hard_gate.patch
$DNA_PYEXE lag_liq_signal_filter_selfcheck.py          # 40/40
$DNA_PYEXE lag_liq_signal_filter_selfcheck.py --live   # 50/50
$DNA_PYEXE due_diligence_selfcheck.py && $DNA_PYEXE lag_adv_cap_selfcheck.py
git checkout -- lag_liquidity_filter.py lag_liq_ledger.py lag_liq_signal_filter_selfcheck.py \
                deploy_golive_dt5g_v4/golive_recommend_v23.py trading_bot/due_diligence.py
```

Số đo §2 tái lập bằng `mike/agents/Taylor/exp_adv2t_gate_20260810/probe_impact_today.py`
(chỉ đọc, không ghi gì).
