# Luồng A9: sửa trần bán A7 theo verdict arch-reviewer, đo lại DD5 theo NAV

Job `Taylor_20261113_153627`. ⚠️ PAPER. **KHÔNG đổi production, `trading_rules.json` hay neo sizing. KHÔNG merge. Không pin ledger vào registry.**
Chưa qua quant-skeptic / arch-reviewer (Mike gọi sau).
- Nhánh `research/live-gap-A9-sellcap-fix-20261114` @ `8b5f7fd0d`, cha là `414468bcb` (A7 giữ nguyên, không rewrite).
- Worktree: `/home/trido/thanhdt/wt-livegapA7-1113`. Worktree này được **đổi nhánh tại chỗ** sang A9 để không tốn thêm disk; nhánh A7 vẫn nguyên ở `414468bcb`.
- Log ở `logs/`, ledger gzip ở `ledgers/`. Sandbox đã xoá. Ledger V2 trùng byte pin đã xoá (md5 còn trong `logs/V2_*.log`).

## 0. Kết luận

1. **Đã sửa đủ các mục (b)–(e) của verdict, mặc định vẫn OFF.**
   - Trên cây mới, OFF cho pin0 `80f509ec` và pin1M `e2de0ac4` **trùng byte**.
   - Self-check 0 VND đạt cả BAL lẫn LAG ở **10/10** chân.
2. **Hướng lệch cũ đúng là LẠC QUAN, nhưng ở NAV live thì độ lớn ≈ 0.** DD5 ghép cặp A9 − A7, cùng cấu hình:
   - 1B: **0,00** [−0,03; +0,03]
   - 2B: 0,00 (có sàn) / −0,11 (không sàn)
   - 5B: +0,02 / +0,03
   - 50B: **−0,40** [−0,81; −0,13] (có sàn) / −0,13 (không sàn)
   - Phần sâu thêm chỉ thấy ở 50B, nơi BAL thật sự bị trần bán.
3. **Neo DD5 cho NAV live (≤2 tỷ) KHÔNG đổi: −33,24% [−33,83; −30,28] ở 1B, −33,06 ở 2B.** Hai số này trùng A7 đến 0,01pp.
   - 5B: −31,17.
   - 50B: −26,22, sâu hơn A7 (−25,96) 0,26pp ở trung vị, 0,40pp ở ghép cặp.
   - Nỗi lo "DD thật có thể sâu hơn −33" **không** đến từ lỗi trần bán. Các bất định khác ở §4 vẫn còn mở.

## 1. Việc 1: sửa code (`git diff 414468bcb 8b5f7fd0d`)

| Mục verdict | Sửa |
|---|---|
| (b) trần bán BAL tra as-of trên `liq_map` đã cắt sàn 1e9 | `pt_v23_audit_2014.py`: khi `SELL_ADV_CAP>0`, dựng **bảng ADV pit dày** `SELL_ADV_PIT` = median Volume t-60..t-1 (min 20 phiên) × PxAdv(t-1), PxAdv = `COALESCE(Price, Close)`. Bảng phủ mọi phiên của BAL-universe ∪ LAG/CAPIT (993 mã, 2.663.459 phiên) và **không cắt sàn**. Truyền vào simulate qua kwarg mới `sell_adv_lookup`, dùng cho **cả hai book**. |
| (c) `SIG_ADV_MIN` lọc `sig_f` trước khi dựng `liq_map` | Dựng `liq_map` **trước** bộ lọc. Cổng tín hiệu không còn đục lỗ bảng ADV thực thi (trần mua 20% + slippage bậc). |
| (d) lát cuối tra exact-key, các lát trước tra as-of | Dưới trần bán, lát cuối/lát nguyên dùng **cùng** `_liq_c` as-of. Exact-key chỉ còn ở đường legacy, để OFF vẫn trùng byte. |
| (d) quy ước ngày ADV | **Bảng dày:** giá trị tại d chỉ dùng dữ liệu ≤ d−1 (ADV phiên trước, biết trước Open d) ⇒ tra as-of ≤ d. **Fallback** (không có bảng dày): `liquidity_lookup` tra as-of **< d** (side=left). Ghi trong docstring kwarg và trong comment. |
| (phát hiện thêm) | Lát bị cắt có g_s/ADV tính lại bằng float = 0,2000000001 ⇒ nhảy sang bậc slippage 0,5%. Selfcheck T3a bắt được. Sửa: lát bị cắt dùng đúng `sell_adv_cap` làm tỉ lệ. |
| (e) selfcheck tổng hợp | `sell_adv_cap_selfcheck.py`, xem §2 |
| `run_leg.sh` | Lấy `rev-parse` **lúc bắt đầu** và kiểm lại lúc kết thúc (lệch ⇒ exit 11). Thêm `unset SIG_ADV_MIN SELL_CAP_LOG_OUT`. |

- ADV thiếu mã, ADV ≤0, hoặc không có giá trị trước d ⇒ 0 ⇒ phiên đó không bán được, chờ đến lượt forced ở `maxcarry`.
- Ở cả 8 chân cap: **missing-ADV slices = 0**.

## 2. Việc 2: selfcheck `WorkingClaude/sell_adv_cap_selfcheck.py`

Mẫu extract-and-test như `idle_cash_age_selfcheck` T7–T10. Phần e2e gọi `simulate()` thật trên panel 60 phiên, giá cố định. Phần wiring trích nguyên văn hai khối của `pt_v23_audit_2014.py` rồi `exec` với stub `bq`.

| Test | Nội dung |
|---|---|
| T1 | knob OFF trùng byte nav/trades/events, kể cả khi truyền `sell_adv_lookup` |
| T2 | carry + chia lát: số lát = ceil(gross/0,2·ADV), các lát liên tiếp, mỗi lát ≤ cap, tổng cổ phiếu bán = mua, **0 VND** (cash sau mua + Σ(bán − phí) = cash lát cuối) |
| T3 | slippage theo lát: lát riêng 0,2·ADV ⇒ 0,3%; lát cuối theo ADV **bán**, không theo bảng mua |
| T4 | ép bán ở maxcarry: 3 lát + 1 forced, bán nốt phần còn lại |
| T5 | chống trùng lệnh thoát: mỗi phiên đúng 1 lệnh bán cho mã đang carry |
| T6 | liq=0 và thiếu mã: không bán cho tới phiên forced; `liq_src` đúng |
| T7 | bảng dày tra as-of ≤ d, không lấy d+1 |
| T8 | fallback tra < d: ADV cuối ngày d không ảnh hưởng lệnh khớp Open d |
| T9 | `liq_map` giữ key ADV 1–2 tỷ khi `SIG_ADV_MIN` lọc tín hiệu |
| T10 | bảng pit: đúng công thức; đổi Volume/Price **ngày d** không đổi ADV(d) nhưng đổi ADV(d+1) |

- **31 assertion PASS.**
- **Mutation 9/9 KILLED**, đều bằng assertion ngữ nghĩa, không phải crash:
  - M1: lát cuối exact-key (lỗi A7)
  - M2: bảng dày side=left
  - M3: fallback side=right (nhìn trước)
  - M4: bỏ chống trùng
  - M5: bỏ forced
  - M6: thiếu mã = ADV vô hạn
  - M7: `liq_map` sau bộ lọc (lỗi A7)
  - M8: bảng pit không shift
  - M9: lát không chịu slippage
- PASS dưới `TZ=Asia/Ho_Chi_Minh`, `UTC`, `America/New_York` và `env -u TZ`.
- `idle_cash_age_selfcheck.py` (cùng file simulate) vẫn 104 PASS.
- Lệnh chạy: `$DNA_PYEXE sell_adv_cap_selfcheck.py --mutations` và `--all-tz`.

## 3. Việc 3: OFF trùng byte trên cây mới

`V2_pin0` → `80f509ec3dbbd55233412913407e6f53`, `V2_pin1M` → `e2de0ac45c7c265827fc53ac0a750675`, CODE `8b5f7fd0d` (`logs/V2_pin0.log`, `logs/V2_pin1M.log`).

## 4. Việc 4: chạy lại 8 chân, DD5 theo NAV

Cấu hình: park 0, pin0%, cache asof0729_postrestate, L3P (LIQ_ZERO_BLOCK=lag, ADV pit). `c` = trần bán 0,2; `cF` = trần bán + sàn tín hiệu 2 tỷ.
Metrics lấy từ `../live_gap_exec_A2/metrics.py` (CAGR lịch). DD5 lấy từ `boot_band.py`: 15 cấu hình (L∈{10,21,42} × 5 seed, B=4000), **không độc lập**.

| Chân | md5 | CAGR (IS / OOS) | MaxDD | **DD5 trung vị [min; max]** | A7 DD5 | Δ ghép cặp A9−A7 | trần bán BAL: cắt/max carry/forced (A7) |
|---|---|---|---|---|---|---|---|
| 1B c | `5b27911d` | 27,36 (22,03 / 32,38) | −25,5 | −32,55 [−33,20; −30,03] | −32,56 | +0,00 [−0,05; +0,03] | 9/13/0 (8/1/0) |
| **1B cF** | `0a414a3a` | 28,49 (21,50 / 35,19) | −24,8 | **−33,24 [−33,83; −30,28]** | −33,24 | +0,00 [−0,03; +0,03] | 3/9/0 (1/1/0) |
| 2B c | `61c1eb76` | 27,65 (22,37 / 32,61) | −25,8 | −32,59 [−32,97; −29,68] | −32,55 | −0,11 [−0,17; −0,04] | 17/3/0 (16/1/0) |
| **2B cF** | `ea5fc680` | 28,02 (21,36 / 34,40) | −24,6 | **−33,06 [−33,61; −30,12]** | −33,07 | +0,00 [−0,02; +0,02] | 12/20/1 (12/1/0) |
| 5B c | `6da0861f` | 26,85 (21,30 / 32,09) | −24,1 | −31,37 [−32,02; −29,22] | −31,43 | +0,03 [+0,01; +0,13] | 35/20/1 (35/4/0) |
| **5B cF** | `c7b0a43e` | 27,48 (20,93 / 33,75) | −23,0 | **−31,17 [−31,68; −28,73]** | −31,18 | +0,02 [−0,01; +0,07] | 23/20/1 (22/4/0) |
| 50B c | `8bf950f7` | 23,06 (17,48 / 28,39) | −17,5 | −26,87 [−27,53; −26,49] | −26,79 | −0,13 [−0,26; −0,02] | 156/20/4 (153/20/3) |
| **50B cF** | `763f4e00` | 22,62 (18,04 / 26,94) | −16,5 | **−26,22 [−27,28; −25,94]** | −25,96 | **−0,40 [−0,81; −0,13]** | 147/10/0 (146/20/1) |

- **Cách đọc cột trần bán BAL:** số lệnh thoát BAL bị cắt gần như giữ nguyên, nhưng **max carry** tăng từ 1–4 phiên lên 9–20 ở NAV ≤5B.
  - Nghĩa là ADV thật (pit dày) của các mã BAL lúc bán thấp hơn nhiều so với giá trị as-of cũ. Đúng như verdict: liq_map cũ trả về ADV ở ngày tín hiệu cuối, khi mã còn ≥1 tỷ.
  - Nhưng ở NAV nhỏ, vốn đọng trong các lệnh carry này quá nhỏ để chạm DD5.
- **Trần bán LAG gần như không đổi** (1B: 164/20/1 cả A7 lẫn A9), vì `liq_lag` pit vốn đã dày và cùng định nghĩa.
- **CAGR** đổi ≤0,08pp ở NAV ≤5B. 50B cF giảm 0,56pp (23,18 → 22,62).
- Ghép cặp A9: 1B−2B (cF) −0,16 [−0,32; +0,03]; 1B−50B −6,55 [−7,35; −4,12]; 5B−50B −4,40.
- Tác dụng của sàn 2 tỷ (cF − c): 1B −0,48, 50B +0,56.
- Nguồn: `logs/metrics.log`, `logs/boot_band.log`, `logs/paired.log`, các dòng `[SELL_ADV_CAP=0.2 …]` trong `logs/<chân>.log`.

### Neo DD5 cho NAV live: KHÔNG đổi so với A7

| Mức NAV (dấu chân thị trường) | A7 | **A9** | Đổi? |
|---|---|---|---|
| ≤ 2 tỷ (SpaceX + ZaloPay ≈ 1,55 tỷ) | −33,24 / −33,07 | **−33,24 / −33,06** | không (≤0,01pp) |
| ~5 tỷ | −31,18 | −31,17 | không |
| 50 tỷ | −25,96 | −26,22 | sâu thêm 0,26pp trung vị (ghép cặp −0,40) |

- Lỗi (b)–(d) có hướng lạc quan như arch-reviewer nói, nhưng chỉ có răng khi BAL thật sự bị trần bán, tức ở 50B.
- **Ở NAV live, neo ≈ −33% (cạnh dưới −33,8) giữ nguyên.**
- Bất định của A7 §4.3 **vẫn mở**:
  - pin1M ở NAV nhỏ chưa đo.
  - park 0,3 ở NAV nhỏ chưa đo.
  - Các gate live engine chưa mô phỏng: rating ≤3 LAG, governance, dd_zone, allocator theo plan.
  - Trần ½ share ADV cho từng account.
  - Live chưa phân xử được: N=1 cửa sổ.
- ⇒ Nếu DD thật sâu hơn −33 thì nguồn nằm ở các mục này, **không** ở trần bán.

## 5. Tái lập

```bash
A9=mike/agents/Taylor/research/live_gap_exec_A9   # code: wt-livegapA7-1113 @8b5f7fd0d (git status sạch)
$A9/make_sandboxes.sh                              # sb/c_adj (symlink; đã xoá sau job)
cd $A9 && xargs -P3 -L1 sh -c 'exec $0 "$@"' < batch.txt
$DNA_PYEXE ../live_gap_exec_A2/metrics.py ledgers/v23_*_exp_{S1,S2,S5,B50}_L3Pc{,F}_*.csv.gz
$DNA_PYEXE ../live_gap_exec_A6/boot_band.py a9_<chân>=<ledger A9> a7_<chân>=<ledger A7> ... > logs/boot_band.log
$DNA_PYEXE paired.py logs/boot_band.log a9_X-a7_X ...  > logs/paired.log
cd /home/trido/thanhdt/wt-livegapA7-1113/WorkingClaude && $DNA_PYEXE sell_adv_cap_selfcheck.py --mutations && $DNA_PYEXE sell_adv_cap_selfcheck.py --all-tz
```
