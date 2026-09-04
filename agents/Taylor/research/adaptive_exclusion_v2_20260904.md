# Adaptive exclusion — vòng 2: sửa lỗi phân loại SBA, kịch bản D (BANNED rỗng), cơ chế hết hạn

Job `Taylor_20260904_054209` (dispatch Mike), tiếp `Taylor_20260904_043943`. Bản v1:
[`adaptive_exclusion_architecture_20260904.md`](adaptive_exclusion_architecture_20260904.md).
**User đã ra quyết định** (2026-09-04): duyệt gỡ 14/16 mã, **PC1 cũng KHÔNG cần ban** (lý do: án
hình sự nhắm cá nhân, không phải công ty; DD kỹ hơn thay vì cấm cứng; xấu thì hệ thống tự loại) ⇒
**BANNED rỗng hoàn toàn**. Vòng này hoàn thiện thiết kế theo quyết định đó, không mở lại câu hỏi
đã chốt. Artifact: `adaptive_exclusion_20260904/v2/`.

## Tóm tắt 4 câu trả lời trực tiếp (đọc trước, chi tiết ở dưới)

1. **IntCov_P0 âm của SBA là DẤU HIỆU MẠNH (tiền ròng), không phải yếu — user ĐÚNG, v1 SAI.**
   Xác nhận bằng dữ liệu BQ trực tiếp (không suy đoán): `IntCov_P0` không đơn thuần là EBIT/lãi
   vay theo quy ước dấu trực quan — mẫu số dường như là **lãi/(chi phí) tài chính RÒNG**, nên khi
   thu nhập tài chính (lãi tiền gửi) vượt chi phí lãi vay thực trả, mẫu số âm và tỷ lệ đảo dấu dù
   công ty đang LÀNH MẠNH. Universe-wide: trong đúng tập ứng viên mà luật gate cũ của tôi
   (`Debt_Eq>3,5 AND IntCov<1,5`) sẽ gắn cờ, **67,6% thực ra CÓ LÃI RÒNG dương và 73,3% có EBITDA
   dương** — tức luật cũ gắn cờ SAI phần lớn thời gian. Đã sửa: gate [A] rule 2 giờ dùng
   `EBITDA_P0 < 0` thay `IntCov_P0 < 1,5` (giữ nguyên điều kiện đòn bẩy `Debt_Eq>3,5` + sustained
   2 quý) — bắt được đúng "đòn bẩy cao THẬT SỰ đang lỗ", loại bỏ false-positive dạng SBA.
2. **Kịch bản D (BANNED rỗng + gate [A] đã sửa) gần như giống hệt C (gate cũ)**: CAGR FULL
   30,20% vs 30,15% (C), vẫn thấp hơn A (không lọc gì, 32,07%) và B (banned tĩnh, 31,41%) —
   **việc sửa lỗi SBA không đổi kết luận backtest tổng thể** vì SBA chưa bao giờ bị luật cũ CHẶN
   thật (Debt_Eq luôn <3,5, không đạt combo). **Chi phí thật của việc thả PC1**: trong scenario D,
   PC1 được chọn 2 lần liên quan giai đoạn gian lận (2026-02-05, 2026-05-05) thay vì (2025-11-05,
   2026-05-05) như ở baseline A — thứ tự dịch do hiệu ứng "ghế trống" khi các mã khác bị gate loại.
   Giữ PC1 từ 2026-02-05→2026-05-05 (1 quý đầy đủ, xuyên ngày bị bắt nằm NGOÀI khoảng này — bắt
   2026-05-15, sau khi đã tái cân bằng): **−25,34% giá cổ phiếu** (Close 25.650→19.150₫). Trên
   trọng số ~1/30 rổ custom30V (~3,3%), đó là **~−0,84pp NAV sleeve** cho riêng lần nắm giữ đó —
   chưa tính hiệu ứng lan (BAL book, w_LAG allocator). Đây là CHI PHÍ THẬT phải chấp nhận, không
   phải lý do phản đối quyết định đã chốt.
3. **`review_by` = `date + 12 tháng`**, gắn vào cron 08:20/12:45 `ops_health_check.sh` có sẵn (không
   đẻ cron mới), escalate bus `question` + Discord Trading Daily theo 2 mức (soft ở −14 ngày, cứng
   khi quá hạn), **FAIL-CLOSED khi quá hạn chưa ai review** (giữ nguyên cờ `exclude`, không tự gỡ)
   — vì chi phí gỡ nhầm 1 mã gian lận thật là KHÔNG GIỚI HẠN trong khi chi phí giữ nhầm 1 mã đã
   sạch chỉ là cơ hội bị bỏ lỡ, có giới hạn.
4. **"DD kỹ hơn"** = khi WebSearch của `fearbuy_weekly_scan.sh` (đã chạy sẵn, quét "khởi tố/bắt
   lãnh đạo") phát hiện sự kiện pháp lý gắn với lãnh đạo/công ty niêm yết → tự động thêm dòng
   `forensic_flags.csv` với `severity=watch` (KHÔNG exclude), `flag_type=leadership_investigation`,
   `review_by = date + 3 tháng` (ngắn hơn mặc định vì diễn biến nhanh) + dispatch
   `fundamental-skeptic` (agent có sẵn) làm DD ngày hôm đó. "Xấu thì tự loại" ĐÃ được gate [A] +
   rating≤3 phủ về mặt CƠ CHẾ (không cần biết NGUYÊN NHÂN xấu) — độ trễ tối đa là 1 chu kỳ báo cáo
   quý (~45 ngày kể từ `Release_Date`). Không tìm được tiền lệ định lượng "bao lâu sau khi lãnh
   đạo bị bắt thì số liệu xấu đi" trong ngân sách effort — case tham chiếu nổi tiếng nhất (FLC,
   Trịnh Văn Quyết bị bắt 2022-03-29) **hoàn toàn KHÔNG có trong `ticker_financial`** (đã verify
   bằng query, 0 dòng) — nói thẳng giới hạn, không đoán con số.

---

## Việc 1 — Sửa lỗi phân loại SBA (làm trước vì phá vỡ luật [A] v1)

### 1a. Ngữ nghĩa `IntCov_P0` — không đoán, đối chiếu số thật

`bigquery_dictionary.json:148` chỉ ghi "Interest Coverage on the current quarter" — không có
công thức. Codebase không có script ETL tính lại `ticker_financial` (nguồn ngoài, vendor).
Grep toàn repo chỉ tìm thấy CONSUMER (`securities_screen.py`, `re_compounder_screen.py`,
`aviation_screen.py`) — không có nơi TÍNH ra cột này. Kết luận buộc phải suy ngược từ dữ liệu.

**Bằng chứng A — SBA cả lịch sử** (`bq query` trực tiếp `ticker_financial`, 2010Q1→2024Q4):
Debt_Eq_P0 giảm dần 1,84 (2010) → 0,12 (2024Q4) — **deleveraging thật, không phải công ty net-cash
tuyệt đối như user mô tả** (SBA vẫn có nợ dài hạn dự án thuỷ điện hàng trăm tỷ, không phải "chỉ
gửi tiền không vay" đúng nghĩa đen). Nhưng: `EBITDA_P0` và `NP_P0` **dương và TĂNG DẦN** suốt giai
đoạn (EBITDA 112 tỷ 2013Q1 → 370 tỷ 2023Q4). `IntCov_P0` **ÂM SUỐT** và **CÀNG ÂM HƠN** khi nợ
càng giảm (−1,47 năm 2013 → −24,26 quý 2024Q4). Dưới quy ước "EBIT/lãi vay, lãi vay dương thông
thường", điều này VÔ LÝ (lợi nhuận tăng + nợ giảm phải làm coverage TỐT hơn, không tệ hơn).

**Bằng chứng B — đối chứng HVN giai đoạn COVID** (2020Q1→2022Q4, distress THẬT): `EBITDA_P0` âm
sâu (−7,99 nghìn tỷ tới −11,35 nghìn tỷ), `IntCov_P0` **cũng âm sâu** (−0,89 tới −23,6) và cả hai
di chuyển CÙNG CHIỀU theo mức độ lỗ — ở đây quy ước trực quan (lỗ nặng → coverage âm) khớp bình
thường.

**Kết luận đối chiếu**: sự khác biệt không nằm ở "công ty này lành mạnh hay không" mà ở **DẤU của
mẫu số**. Với HVN (vay thật, trả lãi thật > thu lãi) mẫu số dương như thường lệ → tỷ lệ theo đúng
trực giác. Với SBA, mẫu số dường như là **chi phí tài chính RÒNG** (chi phí tài chính − doanh thu
tài chính), và khi thu nhập tài chính (lãi tiền gửi, các khoản đầu tư ngắn hạn) VƯỢT chi phí lãi
vay thực trả, mẫu số ÂM → EBIT dương / mẫu số âm = **tỷ lệ âm dù công ty đang tốt lên**. Càng ít
nợ tương đối (mẫu số càng âm hơn vì phần "ròng dương" chiếm tỷ trọng lớn hơn) → tỷ lệ càng âm sâu
hơn — khớp CHÍNH XÁC với xu hướng SBA quan sát được (2013→2024, nợ giảm, IntCov càng âm).

**Bằng chứng C — kiểm chứng ở QUY MÔ UNIVERSE, không chỉ 1 mã** (để không suy diễn từ N=1):

| lev_bucket (Debt_Eq_P0) | n | % IntCov<0 | trong đó % NP_P0>0 |
|---|---:|---:|---:|
| <0,3 (đòn bẩy thấp) | 6.105 | 44,9% | **72,3%** |
| 0,3–1,0 | 15.085 | 40,6% | **83,2%** |
| 1,0–3,5 | 18.644 | 39,3% | **82,4%** |
| ≥3,5 (rất cao) | 4.887 | 44,1% | **71,4%** |

(`v2/universe_financials_v2.csv`, query trực tiếp `ticker_financial` toàn universe 2010→nay.)
IntCov âm xảy ra ở **~40-45% MỌI mức đòn bẩy** (không phải hiện tượng riêng của đòn bẩy thấp), và
**71-83% các trường hợp đó CÓ LÃI RÒNG dương** — tức "IntCov âm" KHÔNG phải một dấu hiệu distress
đáng tin cậy nói chung trong bảng dữ liệu này, đúng như ghi chú đã có sẵn trong
`securities_screen.py:25-27` cho brokerage ("IntCov replaces Debt_Eq... NULL-tolerant vì coverage
patchy") — phát hiện của tôi mở rộng quan sát đó ra TOÀN UNIVERSE, không chỉ ngành chứng khoán.

**Hệ quả trực tiếp cho luật [A] rule 2 của v1** (`Debt_Eq_P0 > 3,5 AND IntCov_P0 < 1,5`, 2 quý
liên tiếp): đo trên đúng tập ứng viên (`Debt_Eq_P0 > 3,5`, n=cả 2 điều kiện):
- Luật CŨ (IntCov<1,5): 3.437 (ticker,quý) bị gắn cờ, trong đó **67,6% có lãi ròng dương, 73,3%
  EBITDA dương**. Tức đa số bị gắn cờ SAI theo đúng cơ chế vừa xác định.
- Luật MỚI (EBITDA<0): chỉ 820 (ticker,quý) — thu hẹp 4,2×, và tách bạch được "lỗ ròng THẬT +
  đòn bẩy cao" (273 dòng, cả IntCov và EBITDA cùng âm — distress chồng distress) khỏi "IntCov âm
  do mẫu số ròng dương nhưng vẫn có lãi" (1.676 dòng — nhóm nghi ngờ SBA-type).

**Rule 2 sửa lại**: `Debt_Eq_P0 > 3,5 AND EBITDA_P0 < 0`, cùng lúc ở quý hiện tại VÀ quý trước
(giữ nguyên yêu cầu sustained-2-quý của v1, chỉ đổi biến điều kiện thứ 2). Universe-wide, luật mới
gắn cờ **1,62%** số (ticker,quý) trong tập `Debt_Eq>3,5`, so với **5,97%** của luật cũ (trên cùng
base dữ liệu 2010→nay, `v2/build_gate_v2.py` output) — thu hẹp đáng kể mà vẫn giữ đúng phần lõi
nguy hiểm (đòn bẩy cao + thực sự đang lỗ ở tầng EBITDA, không chỉ tầng "coverage" mơ hồ dấu).

### 1b. Đo lại flag rate toàn gate [A] (BVPS + rule2 mới + dilution)

| | flag rate any_flag |
|---|---:|
| Gate [A] v1 (rule2 = IntCov) | 15,64% |
| Gate [A] v2 (rule2 = EBITDA) | **12,86%** |

(2 số đo trên CÙNG base dữ liệu mới pull `v2/universe_financials_v2.csv`, 2010→2026-04, khác nhẹ
với con số 17,62% v1 đã trích vì v1 dùng base data 2010→nay khác đợt pull + thiếu vài quý gần
nhất — không so trực tiếp 17,62% với 12,86%, so đúng cặp 15,64% vs 12,86% ở đây.) Rule mới nhẹ
tay hơn ~2,8pp — chủ yếu nhờ bỏ false-positive dạng SBA, KHÔNG phải nới lỏng phần dilution (không
đổi, vẫn 10,62%) hay vốn chủ âm (không đổi, vẫn 1,50%).

### 1c. SBA có bị gắn cờ bởi gate [A] v2 không?

**KHÔNG — 0 episode** (`v2/dynamic_exclude_events_v2final.csv`, lọc `ticker=="SBA"` → rỗng).
Đúng như v1 đã ghi nhận, Debt_Eq_P0 của SBA CHƯA BAO GIỜ vượt 3,5 (đỉnh 1,95 năm 2011) nên luật
combo (dù dùng biến nào cho vế 2) không kích hoạt được với SBA. **Điều cần sửa không phải hành vi
của gate (gate luôn đúng, không chặn SBA) mà là CÁCH TÔI MÔ TẢ nó trong v1 §3** — tôi liệt SBA vào
bảng "lỗ hổng còn mở (đòn bẩy thấp + IntCov âm)" ngụ ý "đây là ca xấu mà gate lẽ ra nên bắt nhưng
bỏ lọt" — **khung diễn giải đó sai bản chất**: SBA không xấu, IntCov âm của nó là dấu hiệu của
DELEVERAGING + tiền ròng dương tương đối, không phải cảnh báo. Xin lỗi vì mô tả sai ở v1; đã sửa ở
đây.

### 1d. Rà lại: còn ca nào khác bị phân loại kiểu SBA (ngành đặc thù, không nên áp ngưỡng chung)?

Trong 16 mã BANNED gốc, kiểm tra Debt_Eq_P0 lịch sử của từng mã (đã có sẵn trong
`banned_financials_history.csv` từ v1): **không mã nào khác trong 16 mã có Debt_Eq luôn thấp +
IntCov âm dai dẳng như SBA** — HVN/NVL/HSG/NKG đều có giai đoạn Debt_Eq vượt 3,5 thật (distress
thật, không phải sign-artifact). Ngành cần lưu ý cho TƯƠNG LAI (không riêng 16 mã này), dựa trên
mẫu hình vừa xác nhận + tiền lệ đã pin trong `data/results_registry.md` ("IntCov replaces Debt_Eq
for brokerage"):
- **Thuỷ điện/hạ tầng BOT/BT** (như SBA): nợ dự án dài hạn lãi suất thấp/ưu đãi + dòng tiền ổn định
  → dễ có thu nhập tài chính ròng dương dù bảng cân đối có nợ. Không nên áp `IntCov` một mình.
- **Chứng khoán/brokerage**: đã ghi nhận trước (`securities_screen.py`), margin debt là by-design.
- **Bảo hiểm**: chưa kiểm tra trong job này (ngoài scope, effort budget) — cờ để dành cho lần sau
  nếu có mã bảo hiểm lọt vào ứng viên gate.
Gate [A] v2 (dùng `EBITDA_P0<0` thay `IntCov`) đã **tự động loại bỏ nhu cầu phân biệt theo ngành**
cho vấn đề CỤ THỂ này, vì EBITDA âm là tín hiệu operating-level không bị méo bởi cấu trúc tài
chính ròng — nhưng KHÔNG loại trừ khả năng có bẫy ngành KHÁC chưa phát hiện; đây là giới hạn đã
biết, không phải đã giải quyết triệt để.

---

## Việc 2 — Kịch bản D (BANNED rỗng + gate [A] đã sửa) so với A/B/C

Cùng engine `custom_basket.build_pit` (fork `custom_basket_dynfork.py`, thay đúng 1 dòng so với
production, giữ nguyên từ v1), `yieldcombo`, `gate_rating≤3`, `namecap`, `q2m5`,
2014-01-01→2026-06-15, walk-forward IS(2014-2019)/OOS(2020+). D dùng episode CSV mới
(`v2/dynamic_exclude_events_v2final.csv`, PIT trên `Release_Date`, đúng cơ chế v1: loại ngay khi
vi phạm, chỉ phục hồi sau 2 quý sạch liên tiếp).

| Scenario | CAGR FULL | Sharpe | MaxDD | Calmar | CAGR IS | CAGR OOS |
|---|---:|---:|---:|---:|---:|---:|
| A — không lọc gì (= hiện trạng backtest, §0 v1) | 32,07% | 1,29 | −40,0% | 0,80 | 24,12% | 39,69% |
| B — BANNED-16 tĩnh (mô phỏng `compute_park_trim.py` LIVE) | 31,41% | 1,29 | −40,2% | 0,78 | 22,77% | 39,83% |
| C — gate động v1 (rule2=IntCov, có lỗi SBA) | 30,15% | 1,29 | −37,1% | 0,81 | 18,31% | 42,01% |
| **D — BANNED rỗng + gate động v2 (rule2=EBITDA, đã sửa)** | **30,20%** | **1,30** | **−38,6%** | **0,78** | **18,56%** | **41,91%** |

**D ≈ C** (chênh 0,05pp CAGR FULL, chiều MaxDD hơi kém đi −38,6% vs −37,1%) — **việc sửa lỗi SBA
không đổi kết luận backtest tổng thể**, vì đúng như 1c đã xác nhận, SBA CHƯA BAO GIỜ bị luật cũ
chặn thật (combo không kích hoạt do Debt_Eq luôn dưới ngưỡng) — sửa rule 2 chủ yếu dọn sạch phần
NGỮ NGHĨA sai (không gắn cờ nhầm ở NƠI KHÁC trong universe mà tôi chưa từng kiểm tra ở v1, vì v1
chỉ nhìn 16 mã) chứ không đổi hành vi trên đúng 16 mã này. D vẫn tốn hơn A/B ở CAGR (đặc biệt IS:
18,56% vs 24,12% A) vì cùng lý do đã nêu ở v1 §3 — gate là bộ lọc TOÀN UNIVERSE, không chỉ 16 tên.

**Must-catch (nhắc lại có kiểm chứng lại với episode v2)**:
- **HVN 2025-05/2025-08** (vốn chủ âm): episode `2020-11-02 → 2026-02-02` — **✅ vẫn chặn đúng**.
- **BAF 2023-11-06** (pha loãng 84%): episode `2022-10-31 → 2027-09-04` (chưa hồi phục) — **✅ vẫn
  chặn đúng** (ngày bắt đầu dịch nhẹ từ 2022-01-28 v1 → 2022-10-31 v2 vì nguồn dữ liệu pull lại,
  không ảnh hưởng must-catch vì ngày chọn 2023-11-06 vẫn nằm trong cả hai).
- **PC1**: vẫn **KHÔNG bị chặn** ở giai đoạn 2025-2026 (episode duy nhất của PC1 là
  `2019-08-01→2020-10-30`, không phủ) — đúng như v1 đã kết luận, gian lận sạch trên số, gate tài
  chính không thể bắt được loại rủi ro này (xem Việc 4).

**Chi phí thật của việc thả PC1 tự do** (đúng yêu cầu dispatch — trình bày minh bạch, không phải
để phản đối quyết định đã chốt):

Trong scenario D, PC1 được `custom30V` chọn ở `2026-02-05` và `2026-05-05` (KHÔNG PHẢI
`2025-11-05` như bảng ở v1 §1b — đó là con số của scenario A/baseline gốc không có gate nào cả;
khi gate [A] loại các mã KHÁC, thứ tự chọn PC1 dịch sang muộn hơn 1 kỳ do hiệu ứng "ghế trống" đã
ghi nhận ở v1 §3 cho scenario C — nêu rõ khác biệt này để không nhầm 2 con số). Giá đóng cửa PC1
(BQ `ticker`, `Close`):

| Ngày | Close (đ) | Ghi chú |
|---|---:|---|
| 2026-02-05 | 25.650 | vào rổ |
| 2026-05-05 | 19.150 | tái cân bằng — **−25,34%** so với 2026-02-05 |
| 2026-05-15 | 17.850 | ngày bị bắt (MPS khởi tố toàn bộ ban lãnh đạo) |
| 2026-06-15 | 19.900 | cuối cửa sổ dữ liệu — hồi phục nhẹ trên cả mức 2026-05-05 |

Giữ PC1 trọn 1 kỳ tái cân bằng (2026-02-05→2026-05-05, ~3 tháng, TRƯỚC khi tin bắt giữ công bố)
đã lỗ **−25,34%** trên chính vị thế đó — đây là tổn thất từ RỦI RO ĐỊNH GIÁ/CHU KỲ bình thường
(không liên quan tin bắt giữ, vì tin ra SAU khi đã tái cân bằng sang kỳ mới). Trên trọng số
namecap (~1/30 rổ ≈ 3,3%), tương đương **≈ −0,84pp NAV sleeve custom30V** cho riêng lần nắm giữ
đó — chưa nhân với tỷ trọng thật của BAL trong NAV tổng (qua w_LAG allocator, ngoài scope backtest
này). Đáng chú ý: **giá đã hồi phục sau tin bắt** (17.850→19.900, +11,5% tính tới cuối dữ liệu),
tức thị trường không phản ứng cực đoan tới mức mất trắng — nhưng đây chỉ là 1 điểm dữ liệu tới
2026-06-15, KHÔNG kết luận được "an toàn", vì hồ sơ hình sự (kế toán bị điều tra) có thể còn diễn
biến xa hơn ngoài cửa sổ dữ liệu hiện có.

**N_TRIALS Việc 1+2**: 1 biến thể mới thử ở rule 2 (EBITDA thay IntCov) — chọn dựa trên bằng
chứng ngữ nghĩa (67,6%/73,3% false-positive rate), KHÔNG dựa trên CAGR (CAGR D gần như không đổi
so C, không phải tiêu chí chọn). DSR/PBO vẫn CHƯA tính chính thức (kế thừa giới hạn v1 §3/§6) —
cần quant-skeptic trước khi wire.

---

## Việc 3 — Cơ chế hết hạn cho `forensic_flags.csv`

### Hiện trạng (đọc trước khi thiết kế)

`data/forensic_flags.csv` (11 dòng, tất cả `date=2026-06-20`) — cột hiện có: `ticker, flag_type,
severity, date, source, note`. Consumer DUY NHẤT áp exclude: `custom_basket.py:307-315` (đọc
`severity=="exclude"`, force `rating=5` từ `date` trở đi, PIT-honest — historical rebal giữ rating
thật). `rating_8l.py:465` tương tự (chưa đọc kỹ dòng chính xác trong job này, ngoài effort budget
— giả định cùng pattern, cần verify nếu wire). `severity=="watch"` (4/11 dòng: CTF, IJC, VRE +
1 khác) hiện KHÔNG bị bất kỳ consumer nào chặn — chỉ là ghi chú.

### Thiết kế `review_by`

**Thêm 1 cột**: `review_by` (date, `YYYY-MM-DD`).

**Quy tắc mặc định**: `review_by = date + 12 tháng`. Lý do chọn 12 tháng (không phải 3/6):
- Cân bằng đúng theo dispatch yêu cầu ("không treo mãi" vs "không gây mệt mỏi cảnh báo"): các vụ
  gian lận/thao túng ở VN (PC1, và tiền lệ FLC 2022) thường mất **nhiều quý tới nhiều năm** để có
  kết luận điều tra/xét xử chính thức — review theo tháng hay theo quý sẽ ra "vẫn chưa có gì mới"
  liên tục, đúng dạng cảnh báo vô nghĩa mà dispatch cảnh báo tránh.
  - 12 tháng cũng khớp nhịp báo cáo thường niên + đủ để quan sát **4 quý báo cáo tài chính** liên
    tiếp — nếu công ty vẫn nộp báo cáo sạch qua 4 quý sau khi bị flag, đó là tín hiệu đáng để
    CON NGƯỜI xem lại có nên hạ `watch`/`exclude` hay không.
- Ngoại lệ: `flag_type=leadership_investigation` (mới, xem Việc 4) dùng `review_by = date + 3
  tháng` vì loại này biến động nhanh hơn nhiều (khởi tố → kết luận điều tra → xét xử, mỗi giai
  đoạn vài tháng, KHÁC pattern related-party/pump vốn ổn định hơn qua thời gian).

### Cơ chế nhắc — gắn vào cron có sẵn, không đẻ job mới

`kb/cron_registry.md:45,60` đã có `ops_health_check.sh` chạy **08:20 và 12:45 (T2-T6)**, post
Discord **Trading Daily**, đã quét "câu hỏi 48h chưa trả lời" — đúng loại cơ chế cần cho việc này.
Đề xuất: thêm 1 check con trong `ops_health_check.sh` (hoặc companion script
`forensic_flag_review_check.py` gọi từ đó, theo đúng pattern `anomaly_scan.py` đã có ở cron 08:20)
đọc `data/forensic_flags.csv`, so `review_by` với ngày hiện tại:

- **`review_by` trong 14 ngày tới, chưa có event đóng** → post Discord Trading Daily (mức FYI, 1
  dòng, không phải `question` — tránh gây mệt mỏi cho việc còn chưa tới hạn).
- **`review_by` đã QUA, chưa có event đóng** → bus `question` (topic
  `forensic-flag-review-due: <ticker>`) + Discord Trading Daily, lặp lại MỖI LẦN chạy check (không
  chỉ 1 lần) cho tới khi có `answer`/`decision` đóng — đúng tinh thần §26 coding_guidelines
  (không để quyết định-cần-người treo im lặng). Dùng `has-event-prefix` (không match tuyệt đối)
  để 1 note tự do vẫn đóng được đúng topic, theo bài học §28.
- **Đóng bằng**: người review ghi `append_event.sh Taylor decision "forensic-flag-review: <ticker>"
  '{"verdict":"vẫn exclude"|"hạ xuống watch"|"gỡ hoàn toàn","review_by_new":"<ngày mới>"}'` — sau
  đó script cập nhật lại `review_by` trong CSV (thủ công hoặc bán tự động, ngoài scope thiết kế
  chi tiết ở đây).

### Hành vi khi quá hạn mà chưa ai review: FAIL-CLOSED (giữ nguyên cờ, KHÔNG tự gỡ)

Đây là lựa chọn có chủ đích, khác với "mặc định fail-open" thường dùng cho lỗi DỮ LIỆU (ví dụ
gate [A] rule 5, thiếu dữ liệu → không tự loại). Lý do bất đối xứng chi phí — **đúng dữ liệu vừa
đo ở Việc 2**: giữ nhầm PC1 bị loại 1 kỳ dù nó có thể đã sạch chỉ tốn CƠ HỘI (~0,84pp NAV sleeve
đo được, có giới hạn trên); nhưng gỡ nhầm một mã ĐANG gian lận thật (không phải PC1 — trường hợp
future) ra khỏi danh sách theo dõi vì "hết hạn không ai review kịp" có thể tốn **KHÔNG GIỚI HẠN**
(toàn bộ vị thế, như user tự nêu case PC1 → −31% giá tính tới lúc bắt theo `forensic_flags.csv`
note gốc). Bất đối xứng này đủ rõ để chọn fail-closed, không cần thêm phân tích định lượng.

### Backfill 11 dòng hiện có

`review_by = date + 12 tháng = 2027-06-20` cho tất cả 11 dòng (kể cả `severity=watch`, vì nguyên
tắc "không treo mãi" nên áp đều, dù watch hiện chưa bind consumer nào). Không rút ngắn riêng cho
PC1 dù mới hơn về mặt tin tức — 12 tháng từ ngày flag (2026-06-20) là đủ thời gian quan sát diễn
biến điều tra ban đầu.

---

## Việc 4 — "DD kỹ hơn" cụ thể hoá thành cơ chế

### Tín hiệu kích hoạt

`kb/cron_registry.md:106-107` đã có `fearbuy_weekly_scan.sh` (Friday 08:10 + Monday 08:00) chạy
**WebSearch quét đúng cụm "tin khởi tố/bắt lãnh đạo DN niêm yết 7-14 ngày"** — cơ chế PHÁT HIỆN đã
tồn tại, KHÔNG cần dựng mới. Hiện phạm vi quét giới hạn ở "mã đang giữ + watchlist 8L≤2"
(`anomaly_scan.py --print-universe`) vì mục đích gốc là bảo vệ phía mua. Đề xuất mở rộng NHẸ: khi
WebSearch trong lượt quét này bắt được 1 sự kiện khởi tố/bắt giữ gắn với TICKER bất kỳ (không chỉ
đang giữ — vì mục tiêu Việc 4 là DD sớm cho MỌI mã có thể vào rổ sau này, không riêng vị thế hiện
tại), gắn nhãn sự kiện đó là trigger — không cần nguồn mới, chỉ mở rộng điều kiện ghi nhận của
nguồn đã có.

### Hành động khi kích hoạt (1 cơ chế rõ, không liệt kê nhiều phương án bỏ ngỏ)

1. **Ngay lập tức**: thêm 1 dòng `forensic_flags.csv` — `flag_type=leadership_investigation`,
   `severity=watch` (KHÔNG exclude — đúng chỉ đạo user "không cần ban, chỉ DD kỹ hơn"),
   `date=<ngày phát hiện>`, `review_by=date+3 tháng` (Việc 3), `source=fearbuy_weekly_scan`,
   `note=<tóm tắt sự kiện từ WebSearch>`.
2. **Cùng ngày**: dispatch `fundamental-skeptic` (agent có sẵn trong danh sách — "Adversarial
   verifier cho due-diligence cơ bản... hunt for scandal-migration risk") — nhiệm vụ cụ thể: xác
   định sự kiện pháp lý là **CÔNG TY** (gian lận báo cáo tài chính, biển thủ tài sản công ty — như
   PC1) hay **CÁ NHÂN không liên quan hoạt động công ty** (như user nêu ví dụ TV1-TV4 — lãnh đạo bị
   bắt vì lý do khác, công ty vẫn vận hành bình thường); đối chiếu chỉ tiêu tài chính gần nhất có
   dấu hiệu bất thường đi kèm không (AR/doanh thu, CFO âm, tập trung giao dịch related-party —
   đúng pattern "5f_forensic" đã dùng cho PC1/KSF/VVS/HHS/L40/KLB/DIG/BFC/IJC/VRE, không phát
   minh tiêu chí mới).
3. **Đầu ra**: `fundamental-skeptic` trả verdict (giống case DGC/TV1 hiện có) → nếu xác nhận rủi ro
   CÔNG TY thật → escalate lên user quyết có nâng `severity` lên `exclude` không (quyết định của
   NGƯỜI, không tự động — đúng chỉ đạo user "không cần ban"); nếu xác nhận CHỈ liên quan cá nhân,
   không ảnh hưởng công ty → giữ `watch`, đóng review sớm hơn `review_by` nếu đã rõ ràng.
4. Post bus `finding` + Discord — route theo đúng convention đã có: nếu mã đang giữ live → Trading
   Daily; nếu là mã ngoài book chính (như case DGC/TV1) → topic "cổ phiếu riêng"
   (`feedback-discretionary-stocks-topic-routing`).

### "Xấu thì tự loại" — đã được gate [A]/rating≤3 phủ tới đâu?

**Đã phủ về CƠ CHẾ, có ĐỘ TRỄ đo được**: gate [A] (BVPS≤0, `Debt_Eq>3,5 AND EBITDA<0` sustained
2 quý — Việc 1, dilution>80%) + rating≤3 gate hiện có đều hoạt động PIT trên số liệu tài chính
QUÝ, anchor bằng `Release_Date` (trung bình lệch ~45 ngày sau kỳ quý theo cách build episode ở
Việc 1/v1). Nghĩa là: nếu một sự kiện pháp lý THỰC SỰ dẫn tới suy giảm tài chính công ty (không
phải trường hợp PC1 — sạch tới tận ngày bắt), gate sẽ tự bắt được **trong vòng tối đa ~1 quý báo
cáo + độ trễ release** (~4,5 tháng kể từ ngày biến cố, worst-case nếu biến cố xảy ra ngay đầu
quý) — KHÔNG cần biết nguyên nhân là gì, đúng tinh thần user muốn ("hệ thống tự loại" = phản ứng
theo SỐ, không theo tin).

**Tiền lệ định lượng — KHÔNG tìm được trong ngân sách effort, nói thẳng thay vì đoán**: đã thử
tra `ticker_financial` cho case tham chiếu nổi tiếng nhất VN (FLC, Trịnh Văn Quyết bị bắt
2022-03-29) — **0 dòng dữ liệu**, mã này hoàn toàn không có trong bảng (khả năng: bị huỷ niêm yết
2023 nên vendor không backfill, hoặc gap dữ liệu khác — chưa điều tra thêm, ngoài effort budget).
Không có tiền lệ sạch thứ hai nào được kiểm trong ngân sách job này. **Kết luận trung thực**: câu
hỏi "sau khi lãnh đạo bị bắt, bao lâu thì chỉ tiêu tài chính suy giảm và gate bắt được" **chưa có
câu trả lời định lượng** — phần "đã phủ tới đâu" ở trên là suy luận CƠ CHẾ (đúng theo thiết kế gate)
chứ không phải verify bằng tiền lệ lịch sử. Nếu user muốn số liệu thật, cần dispatch riêng tìm
case khác còn dữ liệu (gợi ý: ROS/FLC-group liên quan, hoặc các case forensic_flags.csv đã ghi
2026-06-20 — theo dõi CHÍNH các case đó qua các quý tới sẽ tự tạo ra tiền lệ mới).

---

## Việc 5 — Cập nhật kế hoạch triển khai (BANNED rỗng) — ĐỀ XUẤT, KHÔNG TỰ SỬA

Vẫn giữ nguyên khung §5 của v1 (shadow-mode → go/no-go → wire dần, quant-skeptic + user duyệt
trước khi chạm production). Cập nhật CHÍNH XÁC danh sách file/dòng phải đổi khi user duyệt "BANNED
rỗng hoàn toàn" (đã verify lại bằng `grep -n`, không suy đoán):

1. **`lag_forensic_filter.py:90-95`** — hằng số `BANNED = frozenset({"PC1", "VVS", "KSF", "NKG",
   "HSG", "HVN", "VJC", "NVL", "GEG", "SBA", ...})` (16 mã) + `BANNED_TAG`. Đổi thành
   `frozenset()` rỗng (hoặc xoá hẳn logic dùng nó ở dòng 179-181 nếu muốn dọn sạch thay vì để
   hằng số rỗng). Docstring dòng 2-95 (giải thích kiến trúc BANNED) cần viết lại theo tinh thần
   mới — không chỉ đổi hằng số mà để lại văn bản mô tả sai kiến trúc.
2. **`mike/bin/build_universe_pit_quality.py:71-72`** — bản sao y hệt hằng số `BANNED`. Đổi đồng
   thời với (1) — v1 đã cảnh báo đây LÀ 2 bản sao phải khớp nhau, không phải 1 nguồn.
   Cột `banned` sinh ra ở dòng 120,138 (CASE WHEN banned THEN 'BANNED') cũng cần xem lại: nếu
   BANNED rỗng, cột này luôn `false` — cân nhắc XOÁ hẳn cột thay vì giữ cột luôn-false (dọn rác),
   nhưng đây là quyết định của người triển khai thật, không phải job này.
3. **`mike/bin/compute_park_trim.py:427-434`** — khối `if tk in BANNED: dropped.append(...)`. Đây
   là nơi BANNED THỰC SỰ bind cho custom30V/BAL ở tầng LIVE (v1 §0). Nếu `BANNED` rỗng ở (1), khối
   này tự nhiên thành no-op — nhưng nên XOÁ hẳn khối + comment dòng 50-52 (đang tự nhận "lệch có
   chủ đích so với backtest") vì để lại code chết dẫn chiếu 1 khái niệm đã bị loại bỏ dễ gây nhầm
   cho người đọc sau.
4. **`mike/kb/KNOWLEDGE.md:247`** — dòng "Cổ phiếu BANNED vĩnh viễn: PC1, VVS, KSF, ..." là NGUỒN
   CHUẨN TẮC khai báo (theo comment trong `lag_forensic_filter.py:22`). Phải sửa/xoá dòng này
   ĐỒNG THỜI với (1)(2), nếu không nguồn chuẩn tắc trong KB sẽ mâu thuẫn với code thật — đúng loại
   lỗi §28 (so sánh 2 nguồn không chuẩn hoá) mà coding_guidelines cảnh báo.
5. **`LAG_USER_EXCLUDED`** (`lag_forensic_filter.py:103-113`) — **KHÔNG đụng**, đây là cơ chế
   KHÁC (user loại thủ công theo `asof`, đã date-aware, không phải BANNED tĩnh) — v1 đã xác nhận
   đúng mô hình, giữ nguyên.
6. **Gate [A] mới** (nếu wire theo Việc 1 v2): thêm cột `dyn_quality_flag` song song trong
   `build_universe_pit_quality.py` — CHƯA có vị trí dòng cụ thể vì đây là code MỚI chưa viết vào
   production, chỉ tồn tại ở fork `v2/build_gate_v2.py` (nghiên cứu). Khi wire thật, cần viết lại
   thành hàm production-grade (không phải script ad-hoc), đọc `EBITDA_P0`/`Debt_Eq_P0`/`BVPS`/
   `OShares` as-of qua đúng cơ chế PIT `build_universe_pit_quality.py` đã dùng cho golden-floor
   (không viết lại pattern PIT từ đầu).
7. **`forensic_flags.csv`** — thêm cột `review_by` (Việc 3) + backfill 11 dòng. File
   `data/forensic_flags.csv` (root WorkingClaude, KHÔNG phải bản copy trong
   `agents/Taylor/exp_8l_capcheck/data/` — đã liệt kê nhiều bản sao trùng tên nằm trong các
   worktree/thư mục thử nghiệm khi `find`, chỉ bản ở root là canonical, consumer
   `custom_basket.py:307` đọc đúng path này qua `os.path.dirname(__file__)/data/forensic_flags.csv`
   nên các bản trong `agents/Taylor/...` không bị đụng chạm, không cần sửa).

**Chưa làm gì ở trên** — toàn bộ vẫn là ĐỀ XUẤT, cần quant-skeptic verify Việc 1/2 (đặc biệt xác
nhận cách diễn giải ngữ nghĩa `IntCov_P0` không phải suy diễn sai) + user duyệt trước khi chạm bất
kỳ file production nào liệt kê ở trên.

---

## Giới hạn (bổ sung so với v1 §6)

- Ngữ nghĩa `IntCov_P0` (Việc 1) là suy luận từ ĐỐI CHIẾU SỐ (SBA vs HVN + universe-wide
  correlation), KHÔNG phải xác nhận trực tiếp công thức từ vendor/tài liệu gốc — không tìm được
  script ETL nào trong repo tính ra cột này để đọc công thức thật. Độ tin cậy: CAO (nhất quán trên
  3 bằng chứng độc lập — SBA lịch sử, HVN đối chứng, universe-wide 40-45%/70-83%) nhưng KHÔNG phải
  chắc chắn tuyệt đối; nếu wire, nên hỏi thẳng nguồn dữ liệu (`bq_admin` hoặc ai quản lý pipeline
  `ticker_financial`) để xác nhận công thức chính thức trước khi tin hoàn toàn.
- Việc 1d (ngành đặc thù khác thuỷ điện/brokerage — bảo hiểm, BOT/BT khác) chưa kiểm tra, chỉ nêu
  giả thuyết.
- Việc 2: chi phí PC1 (~−0,84pp NAV sleeve cho 1 lần giữ) là ước tính THÔ (trọng số namecap giả
  định 1/30, chưa nhân allocator w_LAG thật, chưa trừ phí giao dịch 0,1%/chiều theo quy ước
  backtest chung) — đủ để MINH BẠCH ĐỘ LỚN, không đủ chính xác để trích dẫn như con số NAV chính
  thức.
- Việc 3/4: thiết kế cơ chế, CHƯA viết code, CHƯA test. `review_by` mặc định 12 tháng /
  `leadership_investigation` 3 tháng là phán đoán hợp lý dựa trên nhịp báo cáo tài chính VN, KHÔNG
  phải số liệu tối ưu hoá — cần user xác nhận trước khi implement.
- Việc 4: câu hỏi định lượng "gate bắt được sau bao lâu" KHÔNG trả lời được (FLC — case tốt nhất
  để kiểm — vắng mặt hoàn toàn trong dữ liệu). Đây là giới hạn thật, không phải bỏ sót.
- Toàn bộ số liệu backtest tính tới `AUDIT_END=2026-06-15` (khớp cache `data/bq_cache`); dữ liệu
  BQ trực tiếp cho Việc 1 (không qua cache, `ticker_financial` live) tới `2026-04-03` theo range
  khai báo trong `bigquery_schema.md`.

---

## Phụ lục — file nguồn v2

`mike/agents/Taylor/research/adaptive_exclusion_20260904/v2/`:
`universe_financials_v2.csv` (BQ pull mới: Debt_Eq_P0, IntCov_P0, EBITDA_P0, NP_P0, BVPS, OShares,
Release_Date, toàn universe 2010→nay), `build_gate_v2.py` (tính rule cũ vs mới, sinh episode),
`dynamic_exclude_events_v2final.csv` (episode PIT gate [A] v2), `step_d_scenario.py` (chạy
scenario D), `scenarioD_metrics.csv`, `cache/nav_scenarioD.csv` + `cache/mem_scenarioD.csv`.
