# HẬU KIỂM SAU MERGE ĐỢT AUDIT 27/09 — job `Taylor_20260927_064745` → `Taylor_20260927_071001`

Chạy trên **main canonical** (WC `f2cfb124`+, mike `8525d2d8`) sau khi user duyệt 8 mục lúc 13:38 ICT.
Nguồn số chuẩn tắc: `data/results_registry.md` mục **"2026-09-27 (quater)"**.

## Kết quả một dòng mỗi mục

| # | Việc | Trạng thái | Số / bằng chứng |
|---|---|---|---|
| 1 | Tái lập pin R3 trên main | ✅ | **24,42% / 1,69 / −18,8% / 1,30 / 761,11B**, md5 `2f9c3702…`, self-check **0 VND** cả 2 book. Trùng khít bản worktree ⇒ merge không đổi số. `pinR3_20260927pm.log` |
| 2 | Bootstrap + DSR/PBO trên ledger pin | ✅ | Bootstrap (theo LỊCH): 5th-pct **CAGR 15,5% / DD −30,3%**. **DSR 1,0000**. **PBO(68) = 0,2085** (số pin) · **PBO(today,486) = 0,5013** (chỉ báo sức ép multiple-testing tích luỹ). `bootstrap_pin.log`, `annex_recon68.log`, `annex_today486.log` |
| 3 | `DSR_FAMILY_MANIFEST` BẮT BUỘC | ✅ code, ⏳ merge | WC branch `fix/dsr-manifest-mandatory` @ `9bb40de8`, annex fail-closed `rc=2`; **13/13 assertion × 4 TZ × 2 interpreter**, 2/2 mutation killed. KHÔNG merge (Mike merge). `dsr_mandatory/` |
| 4 | custom30_history với snapshot CA | ✅ cổng, ⛔ load | Rebal hiệu lực **2026-08-05: 0/30 tên đổi weight, max\|Δw\| = 0,0**; 17/49 rebal lịch sử đổi. `cp` + `bq load` bị permission classifier chặn ⇒ **cần Mike/user chạy**. CAND md5 `1d2f8cad…` |
| 5 | KB `.proposed` | ✅ | `mike/kb/canonical.md.proposed`, `mike/kb/KNOWLEDGE.md.proposed` — §13, chờ Mike duyệt |
| 6 | Hồi quy selfcheck + reconcile thật | ⚠️ | 4/8 selfcheck sạch mọi ô; 3 FAIL đã phân lập là **ENV / control-leg cũ**; **1 FAIL THẬT** (`asof_label`). reconcile thật: SpaceX **+0,0281%** / ZaloPay **+0,0107%** NAV |

## Phát hiện quan trọng nhất — FAIL-C đã merge nhưng CÒN VÔ HIỆU

`data/lag_edge_health.csv` chưa được sinh lại nên vẫn không có cột `known_date`; engine rơi về
`label_col=entry` (`pt_v23_audit_2014.py:2064`, thấy trong log pin). `bin/asof_label_selfcheck.py`:
**5.488/5.488 dòng vi phạm, sớm tối đa 25 phiên**. ⇒ **24,42% vẫn đo trên nhãn look-ahead**
(A/B trước ticket 1: 24,38 → 24,44, ~+0,06pp). Cần người duyệt việc sinh lại file dữ liệu
production rồi re-pin — Taylor không tự làm.

## Phân lập 3 selfcheck FAIL "giả" — đo, không đoán

| Selfcheck | Mặc định | Biến đổi 1 thứ | Kết luận |
|---|---|---|---|
| `basket_oshares_step_exdate` | FAIL py3.10 | PASS `$DNA_PYEXE` | ENV: `merge_asof` pandas 2.3 `M8[ns]` vs `M8[us]` |
| `basket_price_basis` | FAIL 6/6 | `BASKET_OSHARES_STEP=quarter` → **PASS toàn bộ** | Chân control so bit-for-bit với module tiền-sửa (không có ex-date) |
| `basket_return_leg_oshares` | FAIL 6/6 | `PREREF=2c098c1a`+`quarter` → **PASS**; cùng PREREF + `exdate` → **FAIL** | Cùng gốc; biến phân biệt là bước OShares, không phải chân return |

Sửa đề xuất (1 dòng mỗi file, CHƯA làm): chân control của 2 selfcheck `basket_*` phải tự pin
`BASKET_OSHARES_STEP=quarter` khi nạp module tiền-sửa, nếu không chúng sẽ FAIL vĩnh viễn dưới
mặc định production mới.
