# Park-fraction custom30V — VÒNG 2 sau quant-skeptic REFUTED · **KẾT LUẬN: 0 %**

Job `Taylor_20260927_074727` · **paper-only, `trading_rules.json` KHÔNG đổi (vẫn 0.8)** ·
engine **KHÔNG chạy lại** — tái dùng 12 CSV leg của job `Taylor_20260927_064747` (cây `main@f2cfb124`).
PREREG v2 viết **và commit** trước khi đọc bất kỳ số nào: `PREREG_v2.md`, commit `fb6f0aa7`.

## KẾT LUẬN MỘT SỐ — **0 %**

> **Plateau 0–30 %, chọn 0 % vì** đó là mức tối đa hoá **E[Calmar] dưới paired block bootstrap**
> (1,5073) trong tập 4 mức qua cổng rủi ro, và mức 10 % nằm trong dải tie 0,03 nên luật tie-break
> "mức THẤP hơn" giữ nguyên 0 %.

**Nói thẳng, vì đây là phần quan trọng nhất của báo cáo: con số này do LUẬT quyết, không do dữ
liệu phân biệt được.** Ba bằng chứng cho chính câu đó:
- Khoảng cách E[Calmar] giữa 4 mức qua cổng là **0,000 / 0,009 / 0,047 / 0,031** — trong khi dải
  5th–95th của chính Calmar rộng **~1,9** (0,72 → 2,57). Thứ tự xếp hạng nằm hoàn toàn trong nhiễu.
- **30 % bị loại khỏi nhóm tie bởi 0,0012 Calmar** (gap 0,0312 vs ngưỡng khai báo trước 0,0300).
  Nếu ngưỡng khai báo là 0,035 thì luật này trả về vẫn 0 % nhưng nhóm tie có cả 30 % —
  tức con số cuối không đổi, nhưng khoảng cách tới ứng viên số 2 là **1/25 của một bước lưới nhiễu**.
- Head-to-head **cùng 4000 đường bootstrap**: `P(Calmar_30 > Calmar_0) = 0,479` — đồng xu.

**Hai tiêu chí khai báo trước lại chỉ về 30 %** (báo cáo nguyên văn, không che):
`minimax regret CAGR` và `leave-out 4/5 ca`. Xem §4/§2. Đây KHÔNG phải mâu thuẫn dữ liệu — nó là
cùng một sự thật nhìn từ hai phía: parking đổi **+1,07pp CAGR ↔ −1,03pp MaxDD** (trung bình trên
4000 đường). Tỷ lệ ~**1:1**. Cái nào "tốt hơn" là **sở thích rủi ro**, không phải phát hiện định lượng.
PREREG v2 đã khai báo sở thích đó TRƯỚC khi thấy số (thận trọng ⇒ x thấp) ⇒ **0 %**.

**Phần data-backed KHÔNG phụ thuộc sở thích rủi ro, và là hành động thực sự cần làm:**
**80 % (LIVE) phải hạ xuống ≤ 30 %.** 80 % fail cổng DD ở cả 3 ngưỡng (1,5/2,0/3,0pp), E[Calmar]
1,216 thấp nhất trong vùng khả thi, `P(Calmar_80 > Calmar_0) = 0,257`, và không thắng năm nào.
Chênh 0 % vs 30 % là 1pp CAGR đổi 1pp DD; chênh 80 % vs 0–30 % là **8pp đuôi DD**.

## (1) Paired block bootstrap — L=21, B=4000, seed 12345
**Paired = MỘT chuỗi block index cho CẢ 12 leg trên mỗi đường** ⇒ mỗi đường là cùng một thế giới
tái lấy mẫu, nhìn ở 12 mức park. Vòng 1 chạy 12 bootstrap ĐỘC LẬP nên về nguyên tắc không trả lời
được "30 có hơn 0 không" — đó là lỗ hổng phương pháp mà vòng 2 vá. 12 leg đã assert **trùng khít
3107 ngày lịch** (2014-01-02 → 2026-06-19, N_ret=3106, 12,460y calendar) — nếu lệch index thì paired
vô nghĩa, nên nó là `assert`, không phải giả định.

| x | Calmar thực | **E[Calmar]** | Cal 5th | Cal 95th | P(argmax) | P(>x=0) | E[MaxDD] | DD 5th | E[CAGR] | CAGR 5th | cổng 2,0pp |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:--|
| **0 ← CHỌN** | 1,392 | **1,5073** | 0,717 | 2,574 | **0,371** | — | −16,1% | **−24,0%** | 22,44% | 15,15% | ✅ |
| 10 | 1,452 | 1,4983 | 0,715 | 2,542 | 0,126 | 0,508 | −16,5% | −24,3% | 22,82% | 15,29% | ✅ (tie) |
| 20 | 1,496 | 1,4601 | 0,692 | 2,485 | 0,030 | 0,410 | −16,9% | −24,9% | 22,83% | 15,13% | ✅ |
| 30 | 1,628 | 1,4761 | 0,714 | 2,500 | 0,147 | 0,479 | −17,1% | −25,1% | 23,51% | **15,55%** | ✅ |
| 40 | 1,526 | 1,3670 | 0,645 | 2,320 | 0,015 | 0,318 | −18,2% | −26,4% | 23,11% | 14,92% | ❌ |
| 50 | 1,452 | 1,3819 | 0,661 | 2,332 | 0,114 | 0,372 | −18,9% | −27,4% | 24,24% | 15,76% | ❌ |
| 60 | 1,374 | 1,3112 | 0,610 | 2,249 | 0,036 | 0,305 | −20,1% | −28,9% | 24,43% | 15,62% | ❌ |
| 70 | 1,301 | 1,2497 | 0,580 | 2,151 | 0,019 | 0,264 | −21,2% | −30,3% | 24,53% | 15,46% | ❌ |
| 75 | 1,277 | 1,2350 | 0,574 | 2,148 | 0,027 | 0,259 | −21,6% | −31,1% | 24,77% | 15,52% | ❌ |
| **80 ← LIVE** | 1,259 | **1,2164** | 0,562 | 2,117 | 0,051 | **0,257** | −22,2% | **−32,0%** | 25,07% | 15,62% | ❌ |
| 90 | 1,191 | 1,1174 | 0,491 | 1,966 | 0,025 | 0,183 | −24,1% | −34,7% | 24,94% | 15,03% | ❌ |
| 100 | 1,201 | 1,0784 | 0,475 | 1,900 | 0,038 | 0,173 | −25,1% | −36,1% | 25,06% | 15,02% | ❌ |

Neo cổng: 5th-pct MaxDD tại x=0 = **−24,00%** ⇒ trần 2,0pp = **−26,00%** (khớp vòng 1).
Ba điểm đọc ra:
- **E[Calmar] đơn điệu GIẢM theo x từ 30% trở lên, và gần phẳng dưới 30%.** "Đỉnh nội 30%" của
  vòng 1 KHÔNG tồn tại trong kỳ vọng — nó là đặc tính của một đường lịch sử. Xác nhận skeptic.
- `P(argmax)` phân tán khắp lưới (0,371 cho 0%, 0,147 cho 30%, thậm chí 0,114 cho 50%) ⇒ argmax
  của Calmar là **biến ồn**, dùng nó làm tiêu chí chọn (vòng 1) là sai phương pháp.
- **CAGR 5th-pct phẳng 14,9–15,8% trên CẢ lưới** (dải 0,9pp) còn DD 5th-pct chạy 12pp đơn điệu.
  Kết luận vòng 1 ở mục này ĐỨNG: tăng park mua thêm đuôi DD, gần như không mua thêm CAGR tail.

Chẩn đoán bổ sung (`diag_v2.log`, **sau** khi luật đã áp, không dùng để chọn lại): median[Calmar]
cho cùng thứ hạng (argmax 0–30% = 0%, gap 0% vs 10% chỉ **0,0008**) ⇒ kết luận không do đuôi của
phép chia Calmar tạo ra.

## (2) Episode-aware leave-out — **ngược chiều: 4/5 ca chọn 30 %**
| ca | argmax toàn lưới | argmax trong 0–30% | Calmar 0% | 10% | 20% | 30% | 80% |
|---|:--|:--|---:|---:|---:|---:|---:|
| FULL | 30% | 30% | 1,392 | 1,452 | 1,496 | **1,628** | 1,259 |
| bỏ 2019+2020 | **10%** | **10%** | 1,960 | **1,983** | 1,940 | 1,841 | 1,354 |
| bỏ 2018 | 30% | 30% | 1,356 | 1,429 | 1,479 | **1,628** | 1,417 |
| bỏ 2018–2020 | 30% | 30% | 2,079 | 2,142 | 2,172 | **2,191** | 1,802 |
| bỏ 2022 | 30% | 30% | 1,527 | 1,614 | 1,667 | **1,801** | 1,409 |

Đọc đúng: **ưu thế của 30% trên đường lịch sử tập trung ở đợt Covid 2019→03/2020** — bỏ cặp
{2019,2020} là ca DUY NHẤT đảo, và nó đảo về **10%**, không về 0%. Khớp cơ chế vòng 1 đã ghi
(`dd_episodes.txt`): với park ≤30% đợt DD ràng buộc là 2019→24/03/2020 và parking cải thiện nó.
⇒ 30% đứng được trên lịch sử, nhưng **tựa vào một sự kiện đơn lẻ** — đúng lý do E[Calmar] (tính
trên thế giới không có sự kiện đó ở đúng chỗ đó) không thấy đỉnh. **Mọi ca: mức thắng luôn trong
0–30%, 80% không thắng ca nào.**

## (3) Độ nhạy ngưỡng DD — tập qua cổng gần như không đổi
| trần | ngưỡng DD5th | mức qua cổng |
|---|---|---|
| 1,5pp | ≥ −25,50% | 0 / 10 / 20 / 30 |
| **2,0pp (prereg)** | ≥ −26,00% | **0 / 10 / 20 / 30** |
| 3,0pp | ≥ −27,00% | 0 / 10 / 20 / 30 / **40** |

40% chỉ vào tập khi nới tới 3,0pp — và ngay cả khi vào, E[Calmar] của nó (1,367) **thấp hơn cả 4
mức kia**, nên **không mức nào ≥40% thay đổi được kết luận ở bất kỳ ngưỡng nào trong 1,5–3,0pp.**
Phần "mọi mức ≥40% bị loại" là kết luận **bền với ngưỡng**, không phải artefact của số 2,0.

## (4) Minimax regret CAGR trên 0–30 % — **chọn 30 %**
| x | CAGR 5th-pct | regret vs mức tốt nhất | regret per-path (mean) | regret per-path (95th) |
|---:|---:|---:|---:|---:|
| 0 | 15,15% | 0,40pp | 1,20pp | 2,91pp |
| 10 | 15,29% | 0,26pp | 0,82pp | 2,02pp |
| 20 | 15,13% | 0,42pp | 0,80pp | 1,59pp |
| **30** | **15,55%** | **0,00pp** | **0,13pp** | **0,90pp** |

Theo cả hai cách đo regret (trên phân vị tổng hợp, và per-path so với mức tốt nhất trên **cùng**
đường), **30% là mức minimax-regret** ở chân CAGR. Đây là tiêu chí khai báo trước, kết quả ngược
với tiêu chí chọn §1, và tôi báo nguyên văn thay vì bỏ đi. Nó KHÔNG lật kết luận vì PREREG v2 khai
báo tiêu chí chọn là E[Calmar] — regret là phân tích (4), không phải hàm mục tiêu.

## Điều này KHÔNG chứng minh
Không có mức nào trên plateau 0–30% "tốt hơn" theo nghĩa thống kê — plateau phẳng chính là kết
quả, và cả vòng 2 không làm nó bớt phẳng. Bootstrap chỉ là bất định **lấy mẫu** trên phân phối
lịch sử (biên DƯỚI của bất định thật, không mô hình hoá vỡ chế độ); 12 leg cùng vintage
`bq_cache_asof20260729_postrestate`, cùng snapshot corp-action
`data/snapshots/corp_action_share_20260927.parquet`, cùng tham số fill chưa neo (trần 20% ADV/phiên).
Haircut thuế cổ tức vòng 1 (0,000 → 0,083pp/năm, đơn điệu theo x) chỉ làm mức park cao xấu thêm —
không đảo thứ hạng nào ở đây.

## ⛔ KHÔNG ĐỔI GÌ — cần user duyệt
`trading_rules.json` vẫn `neutral_parking.default_park_of_idle_pct = 0.8`, không đụng một byte.
Áp LIVE cần **user duyệt + quant-skeptic**.
- **Số theo PREREG v2: 0 %.** Nếu user muốn một luật khác (ưu tiên minimax-regret CAGR thay vì
  E[Calmar]) thì con số là **30 %** — nói ra ở đây để user chọn LUẬT, không chọn SỐ sau khi xem số.
- **Không phụ thuộc luật nào: hạ 80 % ⇒ ≤ 30 %.** Đó là phần dữ liệu thực sự nói.

**Artifact:** `PREREG_v2.md` (commit `fb6f0aa7`, trước mọi kết quả) · `paired_v2.py` ·
`paired_v2.log` · `paired_v2_results.json` · `diag_v2.py` · `diag_v2.log`. Vòng 1: `PREREG.md`,
`REPORT.md`, 12 CSV leg + 14 log. **Không thay đổi một dòng code production nào.**
