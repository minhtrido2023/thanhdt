# ARCH-REVIEW — `feat/fund-cashflow-detect-20261012` @ `ea9d6969a` (base `fa6d36c8b`)

Chép từ báo cáo arch-reviewer (Mike gọi 2026-10-12 ~20:45 ICT, một lần toàn nhánh). Tái lập:
`repro.py`, `mutants.py`, `run.py`, `results.json` (cùng thư mục — bản gốc ở `/tmp/archrev_fcf/`);
bảng phần dư thật `ci_real_SpaceX.txt`, `ci_real_ZaloPay.txt`.

## VERDICT: NEEDS_CHANGES — 2 CHẶN, 9 NÊN SỬA, 8 GHI CHÚ; 33/70 mutant mới còn sống

Phần đúng, GIỮ NGUYÊN: đúng field §25 (`totalCash − totalDebt + egg + off-book`), lọc tài khoản ở
mọi lần đọc `dnse_raw` (§12); đường cron 19:10 an toàn (mọi lỗi đẳng thức hạ thành 1 dòng cảnh báo,
SAU khi `nav_history` đã ghi); K2/K3/K5 đóng thật; cổng tỉ suất fail-closed đúng ở các nhánh đã
nêu; không thêm `now()`/`today()` trần; không chạm surface tiền thật.

## CHẶN

**C1 — Nạp/rút đi kèm lệnh đặt NGOÀI bot lọt im lặng.** `bin/cash_identity.py:266-287`, `:388-389`.
- Nguồn lệnh khớp duy nhất là bản ghi `orders`/`place_order` trong `dnse_raw`. Ngày bot không giao
  dịch thì không có bản ghi nào: SpaceX 54/77 ngày phiên, ZaloPay 47/77 (vd 10-08, 10-09, 10-12).
- Đối chiếu số lượng vị thế (`_fill_evidence`) chỉ chạy khi cửa sổ ĐÃ bị nghi ⇒ không bao giờ tự
  phát hiện.
- Tái hiện (`repro.py`): R1 nạp 50tr + mua tay 50tr (AAA +5.000, NAV +5,0%) → ΔK −48.500, 0 cảnh
  báo. R2 bán tay 60tr + rút 60tr (NAV −6,0%) → 0 cảnh báo.
- Giảm nhẹ: cổng `qty_unexplained` (rc=5) của `daily_nav_snapshot.py` chặn ghi NAV đêm đó, nhưng nó
  hỏi về cổ phiếu; sau khi người xử lý xong, đẳng thức vẫn báo sạch.
- required_change: (1) chạy đối chiếu số lượng vị thế cho MỌI cửa sổ; (2) số lượng đổi mà lệnh đã
  đọc không giải thích được ⇒ cửa sổ "không kết luận được" + 1 dòng nêu mã, số lượng, giá trị ước
  tính; (3) thêm R1, R2 vào `cash_identity_selfcheck.py`, cả hai phải ra ≥1 dòng cảnh báo; (4) ghi
  điểm mù vào `cash_identity.md.proposed` mục "Không phủ".

**C2 — Báo cáo ngày SpaceX (gửi nhà đầu tư) sẽ in hai đoạn cảnh báo thô MỖI TỐI.**
`bin/daily_nav_snapshot.py:1578-1579`, `bin/cash_identity.py:446-461`,
`bin/eod_trading_report.sh:280-288`, `:327-352`.
- Đường đi: stdout `daily_nav_snapshot.py` → `NAV_SECTION` → `_investor_polish` (không lọc dòng
  `⚠️`) → file báo cáo → Discord + email. Hai dòng dài 1.280 và 1.150 ký tự (báo cáo SpaceX 10-12
  hiện 497 ký tự), mang tên nội bộ (`dnse_raw`, `data/account_cash_flows.json`,
  `cashDividendReceiving`, `market_only`), khẳng định "nghi RÚT ra" và "Tỉ suất các kỳ chứa ngày
  này CHƯA khử khoản đó" — với 08-28 điều đó SAI. Lặp vô hạn (module không trạng thái).
- required_change: (1) trước merge hai cửa sổ lịch sử phải được đóng, bằng chứng 08-28 sửa lại;
  (2) chi tiết cảnh báo đi kênh vận hành (Trading Daily); báo cáo nhà đầu tư không mang tên nội bộ,
  không khẳng định "nghi RÚT" khi chưa xác minh; (3) chỉ in đầy đủ cửa sổ kết thúc đúng ngày đang
  chụp; cửa sổ cũ chưa đóng gộp 1 dòng đếm.

## NÊN SỬA

- **S1** `cash_identity.py:365`, `:370` — `market_only` tắt cảnh báo KHÔNG giới hạn số tiền. R3: nạp
  200tr chưa khai (+20% NAV) cùng ngày có `market_only` → 0 cảnh báo; bản ghi đó cũng mở cổng bước
  nhảy NAV 5%. Sửa: lời xác nhận mang số tiền đã xem (vd `acked_residual_vnd`), chỉ tắt khi phần dư
  lệch ≤ ngưỡng; nên ở FILE RIÊNG, không nằm trong sổ dòng tiền.
- **S2** `cash_identity.py:32-36` — báo động giả chắc chắn tới, đều in "nghi RÚT/NẠP". R5: rút hết
  Trứng vàng ZaloPay 319tr, khấu trừ 0,2013% → −0,077% NAV (vượt ngưỡng khi rút từ ~231tr ZaloPay /
  ~245tr SpaceX). R6: lãi vay post dồn, dư nợ 400tr một tháng → −0,417%. R8: cổ tức 80tr ghi và trả
  trong một cửa sổ → "nghi NẠP +7,6%". Quyền mua: ca thật 08-28. Sửa: đưa khấu trừ Trứng vàng đã đo
  vào đẳng thức; khi ghi chú nội bộ giải thích được phần lớn phần dư thì đổi nhãn "cần xác nhận
  khoản nội bộ".
- **S3** `cash_identity.py:77-82`, `:370` — không phát hiện trôi tích luỹ, không cơ chế báo hằng số
  cũ. R10: rút 450k × 10 phiên = −0,451% NAV, 0 cảnh báo. R11: lãi Trứng vàng thật 6,5%/năm trên
  500tr → −27.944 đ/cửa sổ, 20 cửa sổ −559.824 đ, 0 cảnh báo. Sửa: tổng phần dư trượt 20 cửa sổ
  chưa xác nhận; vượt ngưỡng ⇒ 1 dòng "phần dư trôi có hệ thống — đo lại hằng số hoặc tìm khoản nhỏ
  lặp lại"; thêm ca selfcheck.
- **S4** `report_delivery_gate.py:186-191` — còn fail-open khi dòng có mặt nhưng số không đọc được
  (`+nan%`, `n/a`, `—`, `−1.330,5%` ⇒ `_parse_inception_return_pct` trả None ⇒ WARN rồi gửi). Sửa:
  tách "không có dòng" (WARN) khỏi "có dòng nhưng ô số không parse được" (BLOCK, trích nguyên ô).
- **S5** `report_delivery_gate.py:307-310`, `:393`, `:426` — đường "chỉ cảnh báo" có thể chặn giao
  báo cáo bằng crash: 3 import ngoài `try`; `cash_identity` không import được ⇒
  `ModuleNotFoundError` không thuộc `except` của `deliver()`. Sửa: import vào `try`; bọc
  `_warn_cash_flows(report)` bằng `except Exception` in stderr.
- **S6** `cash_identity.py:198-199`, `:203-224`, `:274`, `:469-471` — một bản ghi `dnse_raw` sai
  kiểu ở bất kỳ ngày nào làm chết đẳng thức cả tài khoản (`payload` là list ⇒ AttributeError không
  nêu file/dòng, §29; `fillQuantity: "abc"` tương tự; JSON hỏng bị bỏ qua im lặng không đếm). Sửa:
  bắt lỗi theo từng bản ghi, ghi (file, số dòng, lỗi), chỉ đánh dấu cửa sổ liên quan là không kiểm
  được, in số bản ghi bị bỏ.
- **S7** `cash_identity.py:453` — chuỗi `… 1,107,515 VND (-0.112% NAV)` khớp
  `report_return_gate._near_signed_pct(line, "VND")` ⇒ khi tài khoản giữ mã VND, dòng bị đọc thành
  tỉ suất của VND và chặn báo cáo ngày. Sửa: viết "đ" thay "VND", hoặc bỏ dấu ± trước phần trăm.
- **S8** chẩn đoán 08-28 sai ở 3 chỗ (§29): `cash_identity.py:103-105`, `proposed_acks.json` bản ghi
  thứ hai, `cash_identity.md.proposed` Bẫy 1 — đều ghi "DNSE trừ dồn". Sửa theo bảng dưới.
- **S9** lỗ hổng test — 33 mutant sống. Tối thiểu thêm ca cho: nhiều bản ghi cùng một lệnh
  `fillQuantity` tăng dần (N22); `price` ≠ `averagePrice` (N03); nhiều bản ghi `balances` trong ngày
  (N08, N31); khai withdraw làm hết cảnh báo (N27, N28); NAV `nan` (N14); một cửa sổ THẬT đóng băng
  để ghim `EGG_DAILY_RATE` (N36 — fixture hiện tự sinh từ chính hằng số); import `cash_identity`
  hỏng ở `daily_nav_snapshot` và `nav_period_returns` (S01, P01); lỗi khi kiểm dòng tiền treo phải
  hiện ra (G07); bản ghi `positions` không gắn tài khoản (N23).

## GHI CHÚ
- G1 `nav_unit_ledger_selfcheck.py` không khép kín: phần A2 đọc `data/` sống (4716 ↔ 4734 = +9
  assertion mỗi dòng nav_history mới mỗi tài khoản); `nav_jump_flow_gate_selfcheck.py` ca N11 cần
  `data/account_inception.json` thật. Có từ bước 1.
- G2 mỗi lần gọi đọc lại toàn bộ `dnse_raw` (264 MB, 101 file): 2,1 giây, RSS 143/230 MB, tăng
  tuyến tính; nếu sau này archive `dnse_raw` thì mọi cửa sổ cũ có giao dịch thành cảnh báo giả.
- G3 cửa sổ mốc khởi điểm → dòng đầu không được liệt kê "không kiểm được" (cần cho tài khoản mới).
- G4 mã lệnh DNSE không duy nhất qua các ngày (58481, 58471, 94311 ở cả 07-02 và 09-29) — code khoá
  theo ngày nên đúng; đừng dedupe theo mã toàn cục.
- G5 subprocess `nav_period_returns.py` trong cổng không có timeout và giữ `flock` (có từ trước).
- G6 `report_delivery_gate.py:230-231` còn comment "khác `_check_period_returns` ở trên
  (fail-open)", nay sai.
- G7 "gấp 3,3 lần nhiễu thường nhật lớn nhất (0,0152%)" không đúng: hai cửa sổ dưới ngưỡng đạt
  0,0294% (SpaceX 07-31→08-03) và 0,0217% (ZaloPay 08-27→08-28) ⇒ biên thật ~1,7 lần.
- G8 dòng lỗi chứa "[Errno 2]" sẽ khớp pattern của `cron_health_check.py` ⇒ ERRORS_FOUND hằng ngày.

## Cửa sổ 08-28 giải thích được tới từng đồng (Mike đã tự kiểm số lượng + giá vốn MBB trên dnse_raw)
| | SpaceX | ZaloPay |
|---|---|---|
| MBB | 1.565 → 1.675 (+110) | lô 232 → 252 (+20) |
| Số lượng × `costPrice` | 33.500.000 → 34.600.000 (+1.100.000 = 110 × 10.000) | +200.000 = 20 × 10.000 |
| `totalCash` đổi | −1.264.731 | −311.405 |
| Phân rã | −165.000 thuế cổ tức − 1.100.000 + 269 lãi không kỳ hạn | −111.600 − 200.000 + 195 |
| Phần dư đẳng thức | −1.107.515 = −1.100.000 − 7.763 (`totalDebt`) + 269 − 21 | −206.656 = −200.000 − 6.842 + 195 − 9 |

Tiền đổi thành cổ phiếu (mua 110 và 20 MBB giá 10.000 đ/cp), KHÔNG phải rút tiền, KHÔNG phải "DNSE
trừ dồn". Chưa xác minh bằng nguồn ngoài rằng đây là quyền mua phát hành thêm — chỉ có số học trên
sổ broker.

## Mutant mới: 70 áp được, 37 bị giết, 33 sống (`mutants.py`, `run.py`, `results.json`)
Sống, có ý nghĩa (file:dòng — đổi gì):
N03 `cash_identity.py:285` fill lấy `price` trước `averagePrice` · N08 `:238` phải thu lấy `balances`
sớm nhất trong ngày · N31 `:233` chỉ xét `balances` đầu ngày · N22 `:222` giữ bản ghi lệnh đầu tiên
thay vì mới nhất · N21 `:176` bỏ `place_order` khỏi bộ lọc · N27 `:363` dòng tiền đã khai lấy trị
tuyệt đối · N28 `:325` bỏ withdraw đã khai · N14 `:119` bỏ kiểm số hữu hạn · N36 `:82`
`EGG_DAILY_RATE` 0,00023397 → 0,00018 · N23 `:209` bỏ lọc `accountNo` từng vị thế · N05 `:280` lệnh
không đọc được giờ gán 00:00 · N06 `:278` lấy `createdDate` trước `modifiedDate` · N10 `:243` thiếu
`cashDividendReceiving` coi là 0 · N12 `:336` NAV = 0 không còn "không kiểm được" · N13 `:333` hai
lần chụp cùng giây vẫn kiểm · N15 `:127` bỏ quy đổi `balance_ts` có múi giờ về ICT · N19 `:542` CLI
rc luôn 0 · N20 `:529` CLI bỏ bắt `KeyError` · N25 `:150` dòng thiếu `nav` không bị bỏ · N33 `:371`
ghi chú dư nợ lấy `min` · N39 `:400` ghi chú thiếu orders tính cả cuối tuần · N40 `:224` đếm bản ghi
orders của tài khoản khác · G07 `report_delivery_gate.py:325` lỗi khi kiểm dòng tiền treo bị nuốt ·
S01 `daily_nav_snapshot.py:922` `except Exception` → `except ValueError` · S02 `:1578` không truyền
`nav_dir`/`raw_dir` · P01 `nav_period_returns.py:281` `except Exception` → `except ValueError` · P02
`:285` không in cảnh báo ra stderr.
Sống, tương đương/biên: N01 (`:370` `>`→`>=`), N02 (`:283` bỏ `.upper()`), N16 (`:137` bỏ phần lẻ
giây), N26 (`:168` bỏ sort), N34 (`:357` `>=`→`>`), G06 (`report_delivery_gate.py:220` `>=`→`>`).
Bị giết: toàn bộ K3/K2 (A01–A09), K5 (U01, U02), cổng fail-closed (G01–G05, G08–G10, G13), G11, G12.

## Sau merge (bản HIỆN TẠI) báo cáo nào in gì
| Nơi | In gì | Tần suất |
|---|---|---|
| Báo cáo ngày SpaceX (Discord + email) | 2 dòng "DÒNG TIỀN CHỜ KHAI … nghi RÚT ra", ~2.430 ký tự | mỗi tối phiên, vô hạn |
| Báo cáo ngày ZaloPay | không (lớn nhất −0,0217%) | — |
| `nav_snapshot_SpaceX_<ngày>.json` | trường `cash_flow_warnings` | mỗi tối |
| `nav_sync_retry.sh` khi bù NAV | nguyên khối vào topic Trading report | khi có bù |
| `nav_period_returns.py` (tuần/tháng SpaceX) | 2 dòng ở stderr và JSON; docstring bảo "chép nguyên văn" | mỗi lần gọi |
| `report_delivery_gate` | cảnh báo stderr, không chặn | mỗi lần giao có validation |
- Không có đường "đã xem, không phải dòng tiền" nào ngoài `market_only` trong sổ dòng tiền thật.
- Chép `proposed_acks.json` vào sổ KHÔNG đổi số (thử trên bản sao: 70 ngày báo cáo SpaceX, 3.920
  trường số, 0 lệch) nhưng đổi hình dạng JSON (`net_flow_vnd: 0.0` + `cash_flows` 2 phần tử, vĩnh
  viễn với `inception`). Bản ghi thứ hai có evidence SAI (S8) — đừng chép như hiện có.

## Cổng fail-closed — đã kiểm
Chặn đúng: rc≠0 (trích 600 ký tự cuối stderr), stdout rỗng, JSON thiếu khoá, `inception` không phải
object, `return_pct` null/NaN/chuỗi. Còn fail-open: ô số không parse được (S4); không suy được ngày
từ tên file; không đọc được file báo cáo. Không chặn oan báo cáo ngày SpaceX/ZaloPay.

## Reviewer CHƯA kiểm
Sao kê DNSE tháng 07 (bằng chứng 07-03) và kết quả dò email mục B; `report_return_gate.py` đầu-cuối
(cần BigQuery) và giao Discord/email thật với báo cáo có dòng cảnh báo; `daily_nav_snapshot.py
main()` và `eod_trading_report.sh` trên dữ liệu thật; quét rộng 27 selfcheck của tác giả; tỉ lệ khấu
trừ rút Trứng vàng 0,2013% (lấy theo số tác giả đo).
