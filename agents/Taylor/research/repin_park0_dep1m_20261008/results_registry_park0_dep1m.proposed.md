<!-- ĐỀ XUẤT — CHƯA GHI VÀO data/results_registry.md. Chờ Mike/user duyệt (§13 + ranh giới dispatch
     job Taylor_20261008_155435: "KHÔNG pin vào data/pinned_ledgers và KHÔNG sửa
     data/results_registry.md trực tiếp").

     Cách áp (Mike, sau khi user duyệt):
       (0) pin 2 ledger mới vào kho bất biến TRƯỚC (cổng pin-artifact-gate đòi ledger_md5 resolve
           được trong PINS.jsonl) — lệnh đúng ở cuối khối;
       (A) append NGUYÊN KHỐI "## 2026-10-08 — ..." dưới đây vào CUỐI file registry.
     Tiêu đề không trùng mục nào hiện có (đã grep "2026-10-08" trong data/results_registry.md = 0). -->

## 2026-10-08 — ⭐ **R3 ĐO Ở KNOB LIVE park=0: `pin0%` 22,12% (SÀN) … `pin1M` 25,42% (TRẦN)** · neo DD sizing **GIỮ −25,2%** (park 0 đo −23,9%) — job `Taylor_20261008_155435` ⚠️ PAPER + REGISTRY, `trading_rules.json` KHÔNG ĐỔI

ledger_md5: a6ba34d83a4d374a73293d897c0b43d9

> **ĐỔI KNOB ĐO, KHÔNG ĐỔI MÔ HÌNH.** Mục septies (2026-09-28) đo ở `PARK_STATES=3:0.3`. Live park
> = **0** từ 2026-10-01 10:26 ICT (user chốt). Mục này đo lại ĐÚNG knob live, đổi đúng **1 biến**
> `PARK_STATES=3:0.0`, mọi thứ khác y lệnh septies (code worktree `wt-repin-dep1m-2809` @ `f66dab18`,
> branch `research/repin-dep1m-2709`, knob carry CHƯA ở main).
> Quy ước tiền nhàn rỗi (user, 08/10/2026 22:53 ICT): lãi huy động **1 tháng Big-4 cá nhân PIT**
> (`idle_rate_proxy.py` tier `dep1m`), trả **theo ngày** (`IDLE_CARRY_PAY_MODE=daily`, không gate
> tuổi) — đúng cơ chế Trứng vàng DNSE (rút trong ngày, không phạt rút trước hạn). KHÔNG dùng 8,543%
> egg spot. Báo cáo đầy đủ: `mike/agents/Taylor/research/repin_park0_dep1m_20261008/REPORT.md`.

**Chân CONTROL (cổng §8c, chạy trước):** `PARK_STATES=3:0.3 IDLE_CARRY_TIER=off` → md5
`4707bcbeb7e801d49a4a851ffd91d5e7` **byte-identical** anchor sexies; `…=dep1m` → `bcd0469f42c2f76937a6ebb10aae9b40`
**byte-identical** pin1M septies; cùng lệnh chạy trên **code MAIN canonical** → `4707bcbe`, và park0/off trên main → `537e349b` = `p0_off` (lệch
worktree↔main = INERT cho cấu hình này: chỉ khác forensic-flags mà mọi cờ ngày 2026-06-20 > AUDIT_END).

| Đại lượng | `pin0%` @park0 — **SÀN** | **`pin1M` @park0 — TRẦN** (quy ước user chọn cho egg) | *(tham chiếu)* pin0% @0,3 | *(tham chiếu)* pin1M @0,3 |
|---|---|---|---|---|
| CAGR | **22,12%** | **25,42%** | 23,37% | 25,71% |
| Sharpe(252) | 1,93 | 2,17 | 1,88 | 2,06 |
| MaxDD | −16,2% | −13,9% ¹ | −14,6% | −14,0% |
| Calmar | 1,36 | 1,84 | 1,60 | 1,83 |
| Final NAV | 603,06B | 840,62B | 684,52B | 864,86B |
| IS 2014-19 / OOS 2020+ | 20,06% / 23,98% | 23,21% / 27,43% | 20,00% / 26,50% | 22,47% / 28,71% |
| **Bootstrap DD 5th** | −23,9% *(số đo)* | −21,5% | **−25,2%** ⬅ **NEO SIZING GIỮ NGUYÊN** ² | −23,6% |
| Bootstrap CAGR 5th | 14,9% | 18,0% | 15,5% | 17,8% |
| P(DD < −30%) | 0,7% | 0,1% | 1,1% | 0,5% |
| self-check | 0 VND (BAL+LAG, tiền + NAV identity) | 0 VND | 0 VND | 0 VND |
| ledger md5 | `537e349b5589408c994f8aceafeb9a39` | `a6ba34d83a4d374a73293d897c0b43d9` | `4707bcbe…` | `bcd0469f…` |

Cửa sổ 2014-01-02 → 2026-06-19 (12,46 năm), NAV 50B, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`, threads=1,
bootstrap circular L=21 B=4000 seed=12345 annualize theo lịch.

¹ **~1,6pp của MaxDD −13,9% là ĐƯỜNG ĐI, không phải carry** (overlay số học thuần = −15,5%). Δ
pin0%→pin1M @park0 = +3,30pp = **2,51pp số học** (57,6% NAV nhàn rỗi × ~3,5%/năm) + **0,79pp đường
đi** (vượt sàn W2b 0,46pp đo trên chân có park; không có cơ chế ⇒ biến thiên chưa giải thích, KHÔNG
phải edge).

² **Neo DD giữ −25,2%** = đầu sàn ở mức park XẤU HƠN trong {0; 0,3}. Luật park của user có điều kiện lãi suất
(có thể quay lại 0,3) ⇒ neo phải phủ cả hai; paired test sàn P(MaxDD₀ tốt hơn) chỉ 0,68 (5th ΔMaxDD −1,9pp),
MaxDD thực tế park 0 sâu hơn (−16,2 vs −14,6). −23,9% là số đo park 0, KHÔNG phải neo (quant-skeptic 2026-10-08).

**A/B park 0 vs 0,3 dưới CÙNG dep1m (paired block bootstrap, 1 chuỗi index chung):**
P(CAGR₀>CAGR₃₀) **0,40** (ΔCAGR −0,29pp, 90% [−2,17; +1,66]) · P(MaxDD₀ tốt hơn) **0,79** ·
P(Calmar₀>Calmar₃₀) **0,72** (E[Calmar] 1,854 vs 1,695). Chỉ số học: P(Calmar) 0,565. Carry 0%:
P(CAGR) 0,13, P(Calmar) 0,49. ΔCAGR −0,286pp = −1,248 (park, carry 0%) + 0,459 (carry số học trên
tiền không park) + 0,503 (đường đi). ⇒ **Park 0 KHÔNG bị dữ liệu phản bác, cũng KHÔNG được chứng
minh tốt hơn — vẫn là khẩu vị rủi ro; carry 1M làm nó RẺ (−0,29pp thay vì −1,25pp).**

**Caveat bắt buộc:** 53/150 tháng proxy DỰNG LẠI (FiinPro không có ≤2018-12) · chưa có sàn nhiễu đo
cho chân park 0 · DSR/PBO không chạy (không có chọn lựa trên dữ liệu này — knob do user chốt trước)
· quant-skeptic 2026-10-08 **CONFIRMED-with-changes** (5 sửa đổi đã áp) · proxy ≠ carry egg thật · CAGR thật ≈ backtest − 1,5pp.

**Pin (Mike chạy, sau duyệt):**
```bash
cd /home/trido/thanhdt/WorkingClaude
D=data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp
CMD_BASE="mike/agents/Taylor/research/repin_park0_dep1m_20261008/run_leg.sh <TAG> BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0"
python3 mike/bin/pin_ledger.py add ${D}_p0_off_univpit.csv --label R3-park0-pin0pct-SAN \
  --command "${CMD_BASE/<TAG>/p0_off} IDLE_CARRY_TIER=off" --audit-end 2026-06-19 \
  --control-md5 4707bcbeb7e801d49a4a851ffd91d5e7 --control-byte-identical --decided-by user
python3 mike/bin/pin_ledger.py add ${D}_p0_1m_univpit_idledep1m.csv --label R3-park0-pin1M-SO-CHINH \
  --command "${CMD_BASE/<TAG>/p0_1m} IDLE_CARRY_TIER=dep1m" --audit-end 2026-06-19 \
  --control-md5 bcd0469f42c2f76937a6ebb10aae9b40 --control-byte-identical --decided-by user
```
