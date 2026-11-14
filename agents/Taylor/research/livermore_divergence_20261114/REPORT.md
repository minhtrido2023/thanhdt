# Livermore P0 + P1: hồi quy H2, đếm candidate DT, 48 trial phân kỳ RSI, gói κ (14/11/2026)

Job `Taylor_20261114_063556` · kế hoạch `kb/projects/livermore-training-plan-20261114.md` · PAPER-ONLY, không sửa
production, không sửa agent def / pin / registry. PREREG `PREREG.md` md5 **cd943e11b9fbc923221d02812989d007**, chốt trước khi
engine chạy. Self-check **PASS** (`selfcheck.json`). Chưa qua quant-skeptic (Mike sẽ phản biện).

## Kết luận
1. **G1 KHÔNG ĐẠT: 0/48 trial phân kỳ qua tiêu chí §3.3.** Không trial nào có BSS OOS > 0 với CI loại 0 (0/48). 0/48 qua
   BH-FDR. DSR lớn nhất 0,005, PBO 0,74. Ở U2 không trial nào có exR dương với CI loại 0 (0/24), và không trial nào
   dương sau phí (0/24; exR OOS lớn nhất +0,36pp so với chi phí vòng 0,594pp). Kết quả còn NULL hơn nhánh bi quan nhất của
   tiên nghiệm. **Đề xuất: đóng hướng phân kỳ RSI vào `ta-schools-vn` NO-GO, không đề xuất lại.**
2. **U1 (VNINDEX) không kiểm định được.** Mỗi loại chỉ có 0–20 sự kiện trong 13 năm (kế hoạch `ước lượng` 4–8/năm/loại; đo
   được 0–1,65/năm/loại). Có 0–11 ngày OOS mỗi trial, nên MDE hit là 37–88pp. BSS OOS âm ở 23/24 trial. Trial duy nhất
   dương có N=2.
3. **G0, phần Taylor làm được (H2): KHÔNG kích hoạt.** R² giữa call Livermore và (mom20, mom60, rp250) là 0,20–0,29, chỉ
   0,09–0,15 khi chấm LOO, dưới ngưỡng 0,5. Chiều ngược với giả thuyết: Livermore đi **THUẬN** xu hướng (vị trí trong range
   250 là biến mạnh nhất), không phải "mom ngược". Nửa còn lại của G0 là κ: gói đã sẵn ở `kappa/`, Mike chạy.
4. **Hệ quả theo luật user đã duyệt 14/11:** P2 chỉ chạy khi G0/G1 qua. G1 trượt, nên **P2 không chạy**, và đề xuất **thu hẹp
   vai Livermore về 3 việc cơ học ở §9** (trợ lý thực thi lệnh vào, khối Kỹ thuật display, kỷ luật điểm hỏng). Đọc theo mã
   tiếp tục với ENTRY_VERDICT cơ học, chấm riêng. Kết quả κ không còn đổi được quyết định này. Chạy κ chỉ để lưu hồ sơ H4
   (khoảng 60 lượt Livermore, chi phí `ước lượng`); Mike/user chọn.

## A. H2: hồi quy call Livermore lên đặc trưng cơ học (`A_PREDECL.md` md5 fd01a1ca, khai trước khi fit)
N=100 case của battery 05/11. Đặc trưng tính từ chính file case Livermore đã đọc (dấu mom20/mom60 khớp 100% với truth).
| Biến phụ thuộc | R² | R² hiệu chỉnh | R² LOO | Hệ số chuẩn hoá mạnh nhất |
|---|---|---|---|---|
| H20_P_UP (OLS) | 0,288 | 0,266 | 0,147 | rp250 (corr 0,52) |
| H20_DIR (LPM) | 0,204 | 0,179 | 0,089 | rp250 +0,75 |
| H20_DIR (logit) | McFadden 0,164 | — | — | rp250 +1,06σ, mom20 +0,39σ, mom60 −0,24σ |

Luật "mom ngược" (DOWN nếu mom20>0 / mom60>0 / rp250>0,5) chỉ trùng với Livermore ở 33 / 35 / 32 trên 100 case. Hit của các
luật này so với truth là 50 / 52 / 53, của Livermore là 55. RECOGNIZED=true: 0/100, nên tách recognized/không không có
nhóm "true". Đọc kết quả: chỉ khoảng 20–29% phương sai call được giải thích bằng 3 đặc trưng cơ học, và trên mẫu mới thì còn
9–15%. Phần còn lại không mang thông tin về kết cục (resolution 0,0002 đã đo ở §1). Thiên lệch DOWN 60/100 nằm ở hằng số,
không ở đặc trưng.

## B. Candidate DT lịch sử (N cho §6) (`B_result.json`)
Replay `dt_gate_hazard_research.extract_episodes`, cùng hàm mà `dna_report.get_dt_gate_clock` dùng, trên nền v3.4b
(`vnindex_5state_tam_quan_v34b_clean`, 2014-01-02→2026-11-12, 3.208 phiên). **Self-check: DT4 replay so với
`vnindex_5state_dt5g_live.state_raw` lệch 0/3.208 phiên.** Lưu ý: candidate là của DT 4-gate (đồng hồ production). DT5G
có thêm macro cap, lệch ở 50 phiên và có 51 transition. Không dùng bảng không hậu tố.
- 129 episode (need10: 42 commit / 51 revert; need25: 11 commit / 25 revert).
- **Candidate "đáng hỏi" (≥5/10 hoặc ≥15/25): N = 82** (IS 29 / OOS 53), tỉ lệ commit 64,6%. Đây là baseline "luôn commit"
  của §6. MDE cho N=82 quanh 64,6% vào khoảng ±13pp (`ước lượng` theo nhị thức).
- Commit rời BULL/EX-BULL: **11** lần. Quá ít để đo lead time có ý nghĩa.

## C. PREREG (`PREREG.md`, md5 cd943e11)
Giữ nguyên họ 48 trial của §3 (4 loại × H10/20/40 × U1/U2 × RSI14/9), không thêm tham số. Phần làm rõ: pivot k=5 lấy vị trí
đầu tiên, p1 là pivot gần nhất cách 10–60 phiên, ngày tín hiệu t=p2+5, vào tại Close(t+1). RSI Wilder trên Close điều chỉnh.
Chống double-count (dòng 8 quant-skeptic): RSI, pivot và lợi suất đều tính trên CÙNG chuỗi Close điều chỉnh, không nhân với
chuỗi số lượng, không cộng cổ tức riêng. Rào |ret| > 16% loại 0–10 sự kiện mỗi trial. U2 = `universe_pit` `in_universe` ∧
MDV60 thực ≥ 20 tỷ VND-2026 (`kb/data_registry/price-volume/universe_pit.md`: CANONICAL), không dùng `ticker_prune`.
IS 2014–19 / OOS 2020+. Giai đoạn hậu FTSE báo riêng.

## D. 48 trial (`results.csv` md5 2b1cd7f9, bảng đầy đủ `REPORT_table48.md`)
**Tần suất nền đo TRƯỚC phần hiệu quả** (`FREQ.md` md5 eaea6a3b). U2: 399–1.833 sự kiện mỗi trial, **148–528 ngày tín hiệu
độc lập OOS**, MDE hit 5,4–10,2pp. U1: 0–20 sự kiện, 0–11 ngày OOS.

| Tiêu chí §7 | Số trial đạt / 48 |
|---|---|
| (a) BSS OOS > 0 và CI95 khối tháng > 0 | **0** (BSS OOS dương ở điểm ước lượng: 3/48, mọi CI đều chứa 0) |
| (b) BH-FDR q=0,10 trên p_BSS | **0** (p_BSS nhỏ nhất 0,248) |
| (c) LOYO đổi dấu ≤ 2/13 | 37 (tiêu chí này lỏng; một mình nó không có nghĩa) |
| (d) U2 exR ròng sau 0,594% > 0 | **0/24** (kể cả slippage 0,1%: 0/24) |
| **Đạt cả 4** | **0** |

- U2 hit OOS 45,3–54,6% (trung bình 49,1%). BSS OOS trong khoảng −1,85% … +0,13%. exR OOS trong khoảng −1,65pp … +0,36pp.
  Duy nhất 1 trial có CI loại 0, và nó ÂM: RBULL H40 RSI9, exR −1,65pp [−3,20; −0,11]. Phân kỳ tăng thường đi sau giai đoạn
  cổ phiếu thua thị trường.
- IS so với OOS: 10/24 trial U2 có exR IS > 0 (họ hidden, H40 tới +1,6pp), nhưng không trial nào giữ được ở OOS. Đây là
  dạng "edge rớt OOS", bị loại theo quy chuẩn.
- Placebo khối tháng: 1/48 có p < 0,05 (U2 RBEAR H10 RSI14, p = 0,046). Với 48 trial, kỳ vọng ngẫu nhiên khoảng 2,4 trial,
  nên đây là nhiễu.
- DSR (48 trial, SR0 = 1,86 theo phiên OOS): lớn nhất 0,005, nghĩa là RED FLAG ở mọi trial. SR0 bị thổi lên vì các trial
  U1 có N rất nhỏ nên SR nhiễu. Độ nhạy: tính phương sai SR chỉ trên 24 trial U2 thì SR0 = 0,10 và DSR lớn nhất 0,12, vẫn
  dưới 0,95. SR (theo phiên) lớn nhất của U2 là 0,048. PBO (CSCV S=16) = 0,74 ≥ 0,5.
- Hậu FTSE (t ≥ 2026-09-21): 99 sự kiện U2, 0 sự kiện U1. Không kết luận được (N quá nhỏ, H40 chưa đủ cửa sổ).

**So với tiên nghiệm §3:** P(U1 qua) 15%: không qua, và cũng không đủ N để kiểm. P(U2 exR dương CI loại 0 nhưng âm sau
phí) 25%: không xảy ra (0/24 có exR dương với CI loại 0). P(U2 ròng dương) 5%: không xảy ra. **NULL.**

**§8 DT5G, mô tả, NGOÀI họ 48, post-hoc** (`dt5g_lead.json`, `dt5g_baseline.json`): có 13 RBEAR RSI14 trên VNINDEX, 7/13
được theo sau bởi một commit DT đi xuống trong 40 phiên. Tỉ lệ nền của ngày ngẫu nhiên là 27,8% (nhị thức p = 0,043, chưa
hiệu chỉnh). 6/11 lần rời BULL có RBEAR trong 90 ngày trước đó, so với kỳ vọng ngẫu nhiên 2,73 (p = 0,033). Hai số này
**cùng một bộ 13 sự kiện**, được tính SAU khi đã thấy bảng §8, và giá thì không giảm: 8/13 có fwd20 > 0, BSS âm ở mọi
horizon. Nó chỉ cho thấy RBEAR đồng pha với đồng hồ DT (vốn trễ), không dự báo giá. **Không phải bằng chứng.** Nếu muốn
theo dõi, chỉ nên làm forward với PREREG riêng. Với N=11 thì lịch sử không xác nhận được.

## E. Gói κ cho P0 (Mike chạy, Taylor không chạy Livermore) (`kappa/`)
20 case ẩn danh, gồm 15 cổ phiếu U2 (`universe_pit`) và 5 mốc VNINDEX, seed 20261114. As-of 2014-01→2025-09-30, tối đa 1
case/mã, không trùng ±60 ngày với battery 05/11. Gói gồm: `SEALED_truth.json` (md5 trong `SEALED_truth.md5`),
`build_cases.py`, `run{1,2,3}_order.txt`, `kappa_score.py` (`--selftest` PASS; đã chạy thử trên run tổng hợp ngẫu nhiên, ra
κ ≈ −0,04 như mong đợi) và `KAPPA_INSTRUCTIONS.md` (prompt cố định, quy trình cách ly). ⚠️ Livermore có Bash, nên phải chép
`cases/` ra `/tmp` trước khi giao, vì trỏ vào thư mục gói thì nó đọc được truth.

## Đánh giá cổng (§8)
| Mốc | Điều kiện | Kết quả |
|---|---|---|
| G0 (κ) | κ(H20_DIR) < 0,4 | **CHƯA ĐO**: cần Mike chạy 3×20 lượt Livermore |
| G0 (H2) | R² ≥ 0,5 | **Không kích hoạt** (R² 0,20–0,29; LOO 0,09–0,15) |
| G1 | 0/48 đạt §3.3 ở OOS | **KÍCH HOẠT (0/48)**: đóng hướng phân kỳ; theo luật user ⇒ P2 không chạy, thu hẹp vai |
| G1 | U1 đạt / U2 không (hoặc ngược) | Không áp dụng: cả hai đều không đạt |

## Lệch PREREG (đã ghi, không đổi kết luận)
1. Climatology U2 bắt đầu từ 2014, không phải 2013, vì dòng đủ điều kiện U2 được giới hạn t ≥ 2014. Tháng chưa có lịch sử
   dùng c = 0,5. Chỉ ảnh hưởng đầu giai đoạn IS, không chạm OOS.
2. Rào |ret| > 16% ở chân control dùng cửa sổ [t, t+1+H] (control không có p1). Sự kiện dùng [p1−20, t+1+H].
3. Hồi chiêu áp sau bộ lọc đủ điều kiện và trước rào dữ liệu, giống thứ tự của engine ta-model.
4. Control leg: 300.438 so với số pin 300.437. Lệch đúng 1 dòng (VDS 2025-12-31) do vintage cache `universe_pit`/`ticker`
   sau ngày 06/11.
5. DSR để NaN cho trial có < 3 ngày OOS (U1 RBULL RSI9, U1 RBULL RSI14 không có sự kiện).
6. `dt_baseline.py` (baseline §8) được thêm SAU khi thấy output §8, nên là post-hoc và chỉ mô tả.
7. Kế hoạch `ước lượng` U1 có 4–8 sự kiện/năm/loại; đo được 0–1,65. Con số này sai 3–10 lần, ghi lại để sửa §3.

## Tái lập
`/home/trido/thanhdt/wc_venv/bin/python` lần lượt: `a_h2_regression.py` → `b_dt_candidates.py` → `engine.py` (khoảng 20
giây, ghi FREQ trước) → `analyze.py` (khoảng 3 phút, seed 20261114) → `selfcheck.py` (khoảng 45 giây) → `dt_baseline.py`.
Không dùng `now()` hay TZ, mọi seed đều cố định. Dữ liệu: cache `data/bq_cache` (vintage 14/11 09:1x) và
`vnindex_pre2013.csv` (md5 46361d6a).
