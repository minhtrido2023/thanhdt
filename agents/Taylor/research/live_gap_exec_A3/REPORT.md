# Luồng A3 — 3 việc quant-skeptic khuyến nghị trước khi đặt mặc định `LIQ_ZERO_BLOCK=lag` + `LAG_ADV_SRC=pit`

Job `Taylor_20261113_021435`. Brief: `brief.md`. ⚠️ PAPER. **KHÔNG merge, KHÔNG đổi production, `trading_rules.json` hay neo sizing −25,2%.**
Mọi số dưới đây đều đo trong job này (log ở `logs/`, ledger ở `ledgers/`). Chưa qua quant-skeptic.

## 1. Kết luận

1. **Dải mới trên đúng cơ sở production** (L3 = cache LAG adj v2, + `LAG_ADV_SRC=pit` + `LIQ_ZERO_BLOCK=lag`):
   - **pin0% (sàn): CAGR 22,91%, DD5 −27,89%** (IS 16,47 / OOS 29,12, năm 2015 5,0%).
   - **pin1M (trần): CAGR 26,61%, DD5 −24,96%** (IS 19,80 / OOS 33,20, năm 2015 8,0%).

   So với L3 dùng `bq` (control trùng byte Luồng A): Δ CAGR −0,48pp ở pin0% (≈2,8 sd tie-break 0,17pp, **vượt nhiễu**) và −0,16pp ở pin1M (≈0,6 sd, trong nhiễu). Δ DD5 −0,32pp / +0,04pp. **Cơ chế của −0,48pp ở sàn CHƯA phân rã** (trên vintage 10-29, A2 đo Δ cùng trục chỉ −0,12pp).
2. **Neo sizing:** DD5 sàn mới −27,89% sâu hơn neo −25,2% là 2,69pp. Chỉ báo, KHÔNG đổi neo — user quyết riêng.
3. **`LAG_ADV_MINP` trơ hoàn toàn.** MINP ∈ {10, 20, 40, 60} cho ledger TRÙNG BYTE ở cả 2 đầu dải × 2 data LAG (16 chân). Knob có vào engine (số key ADV pit 2.180.690 / 2.177.410 / 2.170.850 / 2.164.290 trên adj v2) nhưng **0/7.094 lệnh mua LAG có < 267 dòng lịch sử trước ngày fill** — LAG cần lịch sử BCTC nên mã mới niêm yết không bao giờ vào book. MINP chỉ đổi ADV của những (mã, ngày) LAG không bao giờ chạm tới.
4. **MINP khớp `adv_vnd` live = 60, không phải 20.** Live đọc `Volume_3M_P50` của BQ; trên 643 mã niêm yết sau 2014-06, cột này NULL ở mọi dòng có k < 60 và non-NULL đầu tiên luôn ở k ≥ 60 (p0 = p50 = 60). Engine pit với `min_periods=60` trên cửa sổ t−60..t−1 cũng đòi 60 dòng trước ngày fill ⇒ khớp. Vì trơ, **giữ mặc định 20** để không đổi tên file (`_advsrcpit` ↔ `_advsrcpitmp60`) — đổi sang 60 không đổi một byte nào, là lựa chọn thuần thẩm mỹ/fidelity cho user.
5. **Bootstrap 2 chữ số phân giải chênh DD5 của A2** (§3): ba nguồn ADV dưới `lag` ở pin0% là −27,73 (bq) / −27,68 (fill) / −27,72 (pit) — chênh ≤ 0,05pp, tức bằng nhau trong thực tế; pin1M −25,18 / −25,14 / −25,32.
6. **Cơ chế 2015 đã đính chính** (§5): fill ảo không trần của CẢ HAI loại — ADV ≤ 0 VÀ ngày NULL.
7. **Commit mặc định đã sẵn sàng trên nhánh, chưa merge** (§4): `feat/live-gap-exec-A3-20261113` @ `6bbb4a443`. Lùi `=off`/`=bq` trùng byte với pin cũ và giữ tên file cũ.

## 2. Bảng chân (FULL 2014-01-02 → 2026-06-19, NAV 50B, park 0, AUDIT_END 06-19, threads=1)

Số từ `logs/metrics_L3.log` (cùng `metrics.py` của A2) và `logs/boot2_L3.log` (circular L=21, B=4000, seed 12345).

| Chân | data LAG | ADV | đầu | CAGR | Sharpe | MaxDD | IS / OOS | 2015 | LAG 2015Q4 | Boot CAGR5 | **DD5** | P(DD<−30%) | md5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K_L3 (=L3 Luồng A) | adj v2 | bq | pin0% | 23,39% | 1,81 | −17,1% | 16,77 / 29,77 | 5,7% | 14,2B | 15,14% | −27,57% | 2,55% | `84f796bd` |
| **L3P** | adj v2 | pit | pin0% | **22,91%** | 1,78 | −17,1% | 16,47 / 29,12 | 5,0% | 16,4B | 14,72% | **−27,89%** | 2,73% | `80f509ec` |
| K_L3 (=L3 Luồng A) | adj v2 | bq | pin1M | 26,77% | 2,04 | −14,8% | 20,15 / 33,16 | 8,7% | 14,3B | 18,23% | −25,00% | 0,75% | `35c8968f` |
| **L3P** | adj v2 | pit | pin1M | **26,61%** | 2,04 | −14,8% | 19,80 / 33,20 | 8,0% | 17,2B | 18,13% | **−24,96%** | 0,80% | `e2de0ac4` |

Quét MINP (md5 rút gọn, `logs/*.log` dòng EXIT):

| data LAG | đầu | mp10 | mp20 | mp40 | mp60 |
|---|---|---|---|---|---|
| adj v2 | pin0% | `80f509ec` | `80f509ec` | `80f509ec` | `80f509ec` |
| adj v2 | pin1M | `e2de0ac4` | `e2de0ac4` | `e2de0ac4` | `e2de0ac4` |
| vint 10-29 | pin0% | `87834e98` | `87834e98` (=A2 L2P) | `87834e98` | `87834e98` |
| vint 10-29 | pin1M | `6646c65f` | `6646c65f` (=A2 L2P) | `6646c65f` | `6646c65f` |

Vì trùng byte, CAGR / IS / OOS / 2015 / DD5 của mọi MINP = cột mp20 (bảng trên cho adj v2; A2 §3 + §3 dưới đây cho vint). Bằng chứng trơ: `logs/minp_inert_L3P10.log`, `logs/minp_inert_L3P60.log`; probe live: `logs/minp_probe.log`.

## 3. Bootstrap 2 chữ số — mọi chân A2 (`logs/boot2_A2.log`)

`boot2.py` exec đúng mã `bootstrap_nav.py` (md5 f62f3853, assert L/B/seed), chỉ đổi định dạng in. Làm tròn 1 chữ số khớp bảng A2 ở mọi chân.

| Chân | đầu | CAGR5 | DD med | **DD5** | P(DD<−30%) |
|---|---|---|---|---|---|
| C_L1 (off, bq) | pin0% | 15,07% | −15,27% | −23,56% | 0,55% |
| L1F (off, fill) | pin0% | 14,48% | −15,49% | −24,06% | 0,62% |
| L1P (off, pit) | pin0% | 14,47% | −15,67% | −24,17% | 0,68% |
| C_L2 (lag, bq) | pin0% | 15,24% | −18,11% | −27,73% | 2,55% |
| L2F (lag, fill) | pin0% | 15,14% | −18,10% | −27,68% | 2,55% |
| L2P (lag, pit) | pin0% | 15,10% | −18,14% | −27,72% | 2,65% |
| C_L1 (off, bq) | pin1M | 18,45% | −13,64% | −20,60% | 0,10% |
| L1F (off, fill) | pin1M | 17,93% | −13,79% | −20,96% | 0,15% |
| L1P (off, pit) | pin1M | 17,64% | −14,03% | −21,28% | 0,18% |
| C_L2 (lag, bq) | pin1M | 18,59% | −16,67% | −25,18% | 0,78% |
| L2F (lag, fill) | pin1M | 18,52% | −16,68% | −25,14% | 0,85% |
| L2P (lag, pit) | pin1M | 18,36% | −16,88% | −25,32% | 0,97% |

Đọc: dưới `lag`, nguồn ADV đổi DD5 ≤ 0,05pp ở sàn và ≤ 0,18pp ở trần. Bước `off→lag` mới là bước làm DD5 sâu thêm (~3,6–4,6pp).

## 4. Commit đặt mặc định (CHƯA merge) + control

- Nhánh `feat/live-gap-exec-A3-20261113` = A2 `4f7609c34` + `6bbb4a443` (worktree `/home/trido/thanhdt/wt-livegapA3-1113`, sparse như A2). Diff: `pt_v23_audit_2014.py` +9/−3. Không đặt hoặc rỗng ⇒ `LIQ_ZERO_BLOCK=lag`, `LAG_ADV_SRC=pit`; `LAG_ADV_MINP` giữ 20.
- **Tên file mang trục (§8):** mặc định mới sinh `_liqzblag_advprice_advsrcpit`; lùi `LIQ_ZERO_BLOCK=off LAG_ADV_SRC=bq` sinh lại đúng tên canonical cũ `_wtnamecap_advprice_exp_…`.
- ⚠️ Đổi nghĩa: trước đây `LIQ_ZERO_BLOCK=""` (đặt rỗng) = off; nay rỗng = mặc định `lag`. Muốn off phải ghi `off|none|0`.
- **Control, tất cả chạy trên code `6bbb4a443` (pin0%) hoặc `770393ce2` (pin1M):**

| Chân | env | md5 kỳ vọng | md5 đo | |
|---|---|---|---|---|
| D_L3P_off | KHÔNG đặt (mặc định mới) | = L3P_off | `80f509ec` | ✅ |
| K_L1V_off | off, bq, vint | `2f7739b5` (pin ladderA-L1) | `2f7739b5` | ✅ |
| K_L2V_off | lag, bq, vint | `5ae929c6` (pin ladderA-L2) | `5ae929c6` | ✅ |
| K_L3_off / K_L3_1m | lag, bq, adj | `84f796bd` / `35c8968f` (pin ladderA-L3) | trùng | ✅ |
| K_L2PV_off / _1m | lag, pit, vint | `87834e98` / `6646c65f` (A2 L2P) | trùng | ✅ |

- **Self-check 0 VND: 21/21 chân** (`cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`, EXIT=0). RSS tối đa 4,37G, 4 chân song song, swap 0.
- **Blast radius:** không runtime live nào gọi `pt_v23_audit_2014.py` (mọi hit trong `mike/bin/` chỉ là comment trích dòng). Đổi mặc định chạm các script nghiên cứu gọi pt_v23 không đặt knob: `run_branchC_gates.sh`, `run_park_ablation.sh`, `run_basket_wt.sh`, `run_branchC_decomp.sh`, `run_parkstate_rest.sh`, `run_smallnav.sh`, `run_parkstate_sweep.sh` — sau merge chúng sẽ ra file tên mới (`_liqzblag_advsrcpit`), không đè pin cũ. `pt_v23_lagqual_research.py` có knob riêng, không đổi. `pt_v22_dt5g.py` vốn đã chặn kiểu `lag` (A2 §6).
- **Điều kiện merge (giữ nguyên A2 §5):** quant-skeptic CONFIRMED trên A3; merge cùng nhánh A (`feat/live-gap-exec-A-20261112`) và A2; nhánh research 1m (`770393ce2`) không có commit mặc định — nó chỉ là code đo, không phải đường merge.

## 5. Đính chính cơ chế 2015

Đã ghi vào A2 `REPORT.md` §1.2 (khối "Đính chính 13/11") và mục registry mới: cơ chế là fill ảo KHÔNG TRẦN của **CẢ HAI** loại ngày mà `off` cho mua trọn size — `Volume_3M_P50` ≤ 0 VÀ ngày `Volume_3M_P50` NULL. Cửa sổ 2015H2–2016H1 (`A2/logs/decomp_2015.log`, pin0%): NULL 10 holding / 45,9 tỷ mua / lãi 5,56 tỷ; ≤0 18 / 89,8 / 2,74 tỷ — về lãi, loại NULL lớn hơn. pin1M: NULL 13 / 49,5 / 5,89; ≤0 20 / 95,4 / 3,03. Câu "gần hết chênh đến từ ≤0" chỉ đúng cho TOÀN KỲ (3.757 vs 74 tỷ). Mục registry Luồng A (2026-11-12) không có câu cơ chế 2015 nên không phải sửa.

## 6. Registry + kho

- Mục `## 2026-11-13 — Luồng A3 …` trong `data/results_registry.md`, `ledger_md5: 80f509ec…`; `pin_artifact_gate.py --worktree` OK. Chưa commit (auto-backup/kb_nightly sẽ cuốn như mục Luồng A).
- Pin: `ladderA3-L3P-advsrcpit-pin0pct` (`80f509ec`), `ladderA3-L3P-advsrcpit-pin1M` (`e2de0ac4`), `decided_by: agent`, control = ladderA-L3 byte-identical.
- ⚠️ **Lỗi của tôi lúc pin:** trường `command` chỉ ghi `run_leg.sh … LIQ/SRC/MINP`, thiếu env cố định của script ⇒ `pin_ledger.py compare` với ladderA-L3 báo khác 8 trục (giả) và từ chối. Kho bất biến nên không sửa được dòng gốc; đã `annotate` cả hai pin khai env đầy đủ. Trục thật duy nhất (LAG_ADV_SRC bq→pit) được chứng minh bằng `run_leg.sh` + dòng ARGS trong log + control cùng script trùng byte, KHÔNG bằng `compare`.

## 7. Tái lập

```bash
A3=mike/agents/Taylor/research/live_gap_exec_A3
$DNA_PYEXE $A3/minp_probe.py                      # MINP live (BQ Volume_3M_P50)
$A3/make_sandboxes.sh                              # sb/{m,r}_{vint,adj}; LAG_MD5 vint == A2 sb/m, adj == Luồng A bm_adjv2
cd $A3 && xargs -P4 -L1 ./run_leg.sh < batch.txt   # 21 chân
$DNA_PYEXE ../live_gap_exec_A2/metrics.py <ledgers L3>     # logs/metrics_L3.log
$DNA_PYEXE boot2.py ../live_gap_exec_A2/ledgers/*.csv      # logs/boot2_A2.log ; tương tự L3 → logs/boot2_L3.log
$DNA_PYEXE minp_inert.py ledgers/*_exp_L3P10_off_univpit.csv
```

**Chưa làm:** phân rã −0,48pp sàn L3→L3P; DSR/PBO riêng (N trials = 4 MINP × 2 data × 2 đầu dải + 7 control/default, trục định trước, không chọn trên kết quả — không phải claim edge); BQ cache current chưa đo.
