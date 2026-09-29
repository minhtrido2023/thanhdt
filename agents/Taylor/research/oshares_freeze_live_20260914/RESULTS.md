# Đóng băng check selfcheck OShares đọc BQ sống — job Taylor_20260914_164512

Branch `test/oshares-freeze-live-selfchecks` commit `ce123789` (từ `bc86963e`), worktree `/home/trido/thanhdt-wt-oshares-freeze-live`.
Mike repo: `5c931f08` (usage `corp_action_daily_selfcheck.py`).

## 1. Kiểm kê — check chạm BQ trên bc86963e (đo bằng capture.py, không suy đoán)
Chạy selfcheck gốc với `corp_action_lib.bq` bị ghi lại: **oshares_live 65 truy vấn, oshares_pit 16 (+1 truy vấn lỗi T3)**.
Chặn BQ ⇒ oshares_live CRASH ngay check đầu (rc=98), oshares_pit FAILED ("L1-L3. gọi được BQ").

**oshares_live** (cổng publish chạy file này):
| Check | Đường chạm BQ |
|---|---|
| 1–7, 5b (FPT) | `_fetch(["FPT"], "2026-08-13")` |
| H1–H5b (HAH) | `_fetch(["HAH"], "2026-08-19")` |
| P0, P1 | `bq()` SQL chọn ca "Phát hành riêng lẻ" mới nhất (→ NAF 2026-01-05) + `oshares_at(NAF)` không cache |
| 8, 8b, 8c, 8d, N6 | `oshares_at(DHG/PVT/TCB/ACB/HDB)` lô + từng mã, không cache |
| 9 (MBB) | `oshares_at(MBB)` không cache |
| N1, N1b / N2, N2b, N2c / N7 / N8 | `_fetch` IDC 2021-02-05, FPT, FPT, IDC 2026-08-13 |
| N3, N3b | `oshares_at` IDC ×2 + FPT không cache (khi vá cổng) |
| N4 / N5, F2 | `oshares_at(TCB)` 2026-08-12 / 2025-12-05 không cache |
| F1, F1b, F1c (VRE) · F3 (FPT 2001) · F5, F5b (CC1) | `oshares_at` không cache |
| AB1, AB1b (HHV) · AB1c (VCI) | `oshares_at(..., live=True)` không cache (comment ghi "cố ý chạm BQ") |
| F6 (ABB/NVL) · F6b (KBC) | `oshares_at` không cache |
| 10 | gián tiếp (bất biến trên kết quả các check trên) |
| 10b | `_corp_of` → `_fetch([tk], "2026-08-13")` cho FPT/HAH/VRE/KHP |

**oshares_pit** (không nằm trong cổng, kiểm kê theo yêu cầu): T3 (`fetch_cache` → BQ lỗi cú pháp), L1–L4, A1–A15 (`fetch_cache` IDC/AAA/FPT/VNM 2026-06-16, FPT 2026-06-16; `oshares_reconciled/oshares_pit` cache=None; `oshares_at(DHG)`).

**Sạch sẵn**: `corp_action_lib` selfcheck (1–7 thuần Python); `corp_action_daily_selfcheck.py` (hermetic, tầng `--live` opt-in không nằm trên cổng); `oshares_wire_selfcheck.py` (monkeypatch `R.bq`).
`gate_selfcheck` chỉ chạy `corp_action_lib` + `oshares_live` (`_model_files()`).

## 2. Fixture + tương đương
- `WorkingClaude/oshares_selfcheck_fixture.py` (mới): dòng `_fetch` NGUYÊN VĂN (chuỗi bq CLI) của 20 mã, **74 dòng quý + 177 dòng corp** (feed đầy đủ của 20 mã: 1.032 quý + 656 corp; từng mã ở `windows.json`). Cửa sổ liền ngày tối thiểu/mã do `freeze.py` dò: trần = asof lớn nhất; sàn corp rồi sàn quý = ngày muộn nhất còn tái lập khít.
- Replay (freeze.py): 76 lời gọi mã thật với feed ĐẦY ĐỦ tái lập 100% trước khi dò (độ trung thực replay), rồi 76/76 trên fixture.
- **Chạy thật** (capture.py): code mới + BQ BỊ CHẶN vs code gốc + BQ sống ⇒ **126/126 lời gọi tầng ngoài trùng khít full JSON** (96 live + 30 pit, gồm các lượt vá cổng N3/F1c/N4/A6/A11/A13/K1b), dòng PASS/FAIL trùng từng byte. Bảng: `equivalence_table.md`.
- P0 giữ nghĩa: cùng tiêu chí SQL áp lên feed NAF đóng băng (không hằng số). 8c chỉ còn kiểm tách mã trong cache lô ⇒ bù bằng `corp_action_lib` check 8 mới: `bq()` luôn gửi `--max_rows` + ném lỗi khi chạm trần (subprocess giả lập).
- Guard mới: `_selfcheck()` của oshares_live/oshares_pit thay `_fetch`/`bq` bằng hàm NÉM LỖI trong lúc chạy (thân cũ đổi tên `_selfcheck_body`) ⇒ check nào quên cache sẽ đỏ.
- Số kỳ vọng: KHÔNG đổi một số nào. Logic model: không đụng.

## 3. Hermetic
| Chặn | Kết quả |
|---|---|
| capture.py mode=blocked (`bq` + CLI `bq` ném lỗi) | live 102/102, pit 49/49, 0 lần chạm BQ |
| `CLOUDSDK_CONFIG=/tmp/no_gcloud_cfg_x` (bq CLI lỗi auth, cả tiến trình con của cổng) | xem §5 — xanh; code gốc bc86963e cùng env: rc=1 (`control_orig_bc86963e_bq_blocked_env.log`) |
Không còn check nào buộc chạm BQ trên đường cổng.

## 4. Mutation — 22/22 bị giết (`mutate.py`, `mutation_result.json`)
| id | module | mutation | check phải đỏ | kết quả |
|---|---|---|---|---|
| FPT | live | `C.FPT[2025-09-12].col8: 1703507121 -> 1703507122.0` | 4. | ĐỎ ✓ |
| HAH | live | `Q.HAH[2026-07-30].col1: 1.91840401E8 -> 191840402.0` | H5. | ĐỎ ✓ |
| NAF | live | `C.NAF[2026-01-05].col5: -7083933 -> 7083933` | P1. | ĐỎ ✓ |
| DHG | live | `Q.DHG[2026-07-20].col0: 2026-07-20 -> 2026-08-13` | 8d. | ĐỎ ✓ |
| PVT | live | `Q.PVT[2026-07-29].col1: 5.16918938E8 -> 517918938.0` | N6. | ĐỎ ✓ |
| ACB | live | `Q.ACB[2026-07-22].col1: 5.804421957E9 -> 5904421957.0` | N6. | ĐỎ ✓ |
| HDB | live | `Q.HDB[2026-07-31].col1: 5.005276323E9 -> 5105276323.0` | N6. | ĐỎ ✓ |
| TCB | live | `C.TCB[2025-12-01].col8: 7064851739 -> 7164851739.0` | N5. | ĐỎ ✓ |
| MBB | live | `C.MBB[805499990].col5: 805499990 -> 805499991.0` | 9. | ĐỎ ✓ |
| IDC | live | `C.IDC[2020-05-28].col7: 108000000 -> 2700000000` | N1. | ĐỎ ✓ |
| VRE | live | `Q.VRE[2026-07-29].col1: 2.27231841E9 -> 2272318411.0` | F1. | ĐỎ ✓ |
| CC1 | live | `Q.CC1[2026-07-31].col1: 4.746561E8 -> 474656101.0` | F5. | ĐỎ ✓ |
| HHV | live | `Q.HHV[2026-07-31].col1: 5.74511888E8 -> 574511889.0` | AB1. | ĐỎ ✓ |
| VCI | live | `Q.VCI[2026-02-02].col1: 8.501E8 -> 722600000.0` | AB1c. | ĐỎ ✓ |
| ABB | live | `Q.ABB[2026-02-02].col1: 1.397208685E9 -> 1397208686.0` | F6. | ĐỎ ✓ |
| NVL | live | `Q.NVL[2026-02-02].col1: 2.234496474E9 -> 2234496475.0` | F6. | ĐỎ ✓ |
| KBC | live | `Q.KBC[2026-02-02].col1: 9.41754759E8 -> 941754760.0` | F6b. | ĐỎ ✓ |
| KHP | live | `C.KHP[2026-09-14].col8: 62215739 -> 72215739.0` | 10b. | ĐỎ ✓ |
| AAA | pit | `C.AAA[2019-06-03].col8: 58664988 -> 58664989.0` | A6. | ĐỎ ✓ |
| VNM | pit | `C.VNM[2016-07-11].col5: 8887731 -> 0` | A4b. | ĐỎ ✓ |
| LEAK_no_cache_CC1 | live | `bỏ _cache= ở F5 (CC1)` | hermetic guard | ĐỎ ✓ |
| LEAK_no_cache_DHG_pit | pit | `bỏ _cache= ở A15 (DHG)` | L1-L3 | ĐỎ ✓ |

Lượt đầu 7 mutation ±1 SỐNG (HAH ESOP2, NAF ratio, ACB/HDB +1e6, TCB/KHP AIS +1, CC1 ISS +1): đều do dung sai thiết kế (EXPLAIN_TOL 0,1%, AIS OK trong dung sai) hoặc đường số không đi qua dòng đó (HAH H5 nay phục vụ từ dòng quý 07-30; NAF còn ca riêng lẻ 2025-08-29) — đổi sang mutation đi qua đúng đường số, không đổi check.

## 5. Verify (`verify_matrix.sh` → `verify_matrix.log`; không source wc_env.sh; module in từ worktree)
Mọi ô dưới đây: env -u TZ và TZ=America/New_York × BQ mở và BQ chặn (env) = 4 lượt:
- oshares_live **102/102** · oshares_pit **49/49** · corp_action_lib **PASS (8/8)** · oshares_wire **11/11**
- cổng thật `gate_driver_wt.py` (`cad.gate_selfcheck()`, WC_ROOT=worktree): **ok=true**, 2 module rc=0 (`gate_driver_bqblock.log`)
- corp_action_daily_selfcheck: **201/201** khi WORKDIR_8L trỏ symlink `/tmp/wt_freeze_live_wc`; với đường worktree thật **200/201 — SC2 đỏ do ARTIFACT**: SC2 giả lập lỗi bằng `"oshares" in path`, mà tên thư mục worktree chứa "oshares" ⇒ cả 2 module bị giả lập FAIL. Không liên quan thay đổi này (bc86963e cũng vậy); SC2 dễ vỡ theo tên thư mục — ghi để Mike quyết.

## Cái giá / cần Mike quyết
1. Cổng publish **mất khả năng bắt BQ đổi shape/lược đồ** (docstring `corp_action_daily.gate_selfcheck` vẫn nói "bộ hồi quy truy vấn BQ thật… thay đổi lược đồ phía vendor sẽ làm cổng đỏ" — nay SAI; file đó ngoài phạm vi được sửa). Nếu cần canary lược đồ: job riêng không chặn publish.
2. `oshares_selfcheck_fixture.py` không nằm trong `_model_files()` ⇒ không vào `model_version` (đúng về nghĩa: không định nghĩa số). Thiếu file ⇒ ImportError ⇒ cổng đỏ (fail-closed). oshares_live.py đổi ⇒ model_version đổi (đằng nào cũng đổi cùng bc86963e).
3. SC2 phụ thuộc tên thư mục (trên).
