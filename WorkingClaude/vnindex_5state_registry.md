# VNINDEX 5-State System Registry — "Ngũ Hành"

**Convention:** 5-state market regime system gọi chung là **"Ngũ Hành"** (5 elements). Mỗi major iteration có sub-codename theo phong cách BA series (Song Sinh, Âm Dương, Tinh Tế).

## 🟢 LIVE — đang chạy production

| | |
|---|---|
| **Codename** | **DT5G** (DT 4-gate + Macro gate; base = "Định Tâm" v3.4b) |
| **Tech version** | v3.4b base (ew_v1→dual_v3[BearDvg min_dur=30]→v3.1→v3.4b) → DT 4-gate `DT_10_25_25` → macro gate (Pillar A SBV refi + Pillar B US VIX/SPX + bull-bypass + breadth-decoupling guard) |
| **Deployed** | 2026-06-02 (DT5G); easing floor disabled 2026-06-03 |
| **BQ table** | **`tav2_bq.vnindex_5state_dt5g_live`** (49 transitions) — ⚠️ NOT the no-suffix `vnindex_5state` |
| **Compute / source** | `macro_state_live.py` — production state via `get_gated_state()` (fail-safe → DT4-only when `data/macro_health.json` stale) |
| **Consumers** | `golive_recommend`, `pt_v4_dt5g`, `dna_report.py`, `recommend_tomorrow.py` |
| **Doc** | CLAUDE.md §"VNINDEX 5-State Market System — PRODUCTION = DT5G"; `data/audit_dt5g_events.md` |
| **Validated** | Event audit 2014→2026-05: deviates from DT4 on 49 sessions / 4 de-risk episodes (1.6%), 0 re-risk. Integrated prod-spec (50B): V5 +0.43pp / V4 +0.27pp Full. **FAIL-SAFE RISK GATE, not a return-enhancer.** |

> ⚠️ **Table-label correction (BQ-verified 2026-06-03):** the no-suffix table `tav2_bq.vnindex_5state` is **NOT DT5G**. It is byte-identical to `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (0 diffs / 6291 rows) = the **v3.4b BASE** (~153 transitions, no DT-gate / no macro cap). DT5G lives **only** in `vnindex_5state_dt5g_live`. The old convention "no-suffix = LIVE" below no longer holds — DT5G is served from the `_dt5g_live` table.

## 🟡 STAGING — candidate đang validate (KHÔNG có downstream)

| | |
|---|---|
| **Trạng thái** | _(none currently)_ |
| **BQ table** | `tav2_bq.vnindex_5state_staging` _(created on demand)_ |
| **Local CSV** | `vnindex_5state_staging.csv` _(created on demand)_ |

**Flow để promote staging → live:**
```bash
1. Build candidate     → python build_<candidate>.py
2. Upload to staging   → python deploy_ngu_hanh.py --to-staging
3. Integrated test     → python compare_v11_5state_versions.py
4. ✅ PASS             → python deploy_ngu_hanh.py --promote  # swap staging→live, archive old live
5. ❌ FAIL             → python deploy_ngu_hanh.py --drop-staging
```

## 📦 ARCHIVE — bản cũ giữ rollback

| Codename | BQ table | Local CSVs | Period LIVE | Note |
|---|---|---|---|---|
| **v3.4b base (== live `vnindex_5state`)** | `tav2_bq.vnindex_5state` / `..._tam_quan_v34b_clean` | `vnindex_5state.csv` etc. | base input to DT5G | The v3.4b base ("Định Tâm"). Still daily-refreshed and serves the no-suffix table; consumed by DT5G as its base. NOT the production gated state. |
| **Ngũ Hành — Tinh Tế** | `tav2_bq.vnindex_5state_archive_tinh_te_20260602_*` | `vnindex_5state_archive_*` | 2026-05-21 → 2026-06-02 | v2g_pe3c_s3. Superseded by v3.4b then DT5G. (Also `vnindex_5state_archive_pre_dt5g_20260602` snapshot.) |
| **Ngũ Hành — Cổ Điển** | `tav2_bq.vnindex_5state_archive_co_dien` | `vnindex_5state_archive_co_dien.csv` (+ history + state_history) | until 2026-05-17 | Original smooth+gate60 (EMA0.40→mode(15)→min_stay(7)). Best Mid 18-23 (CAGR 19.52%/Sh 1.30/DD -16.8%). |
| **Ngũ Hành — pe3c_raw** | `tav2_bq.vnindex_5state_archive_pe3c_raw` | `vnindex_5state_archive_pe3c_raw.csv` (+ history + state_history) | 2026-05-21 morning only | v2g_pe3c không smoothing. Integrated FAIL Mid 18-23 (-2.57pp). |
| Ngũ Hành — v2g (legacy) | `tav2_bq.vnindex_5state_archive_v2g_old` | _(not kept locally)_ | 2026-05-12 briefly | Original v2g no-smooth attempt. Reverted same day. |

## Rollback commands

**Rollback to Cổ Điển (safest, proven):**
```bash
bq cp -f tav2_bq.vnindex_5state_archive_co_dien tav2_bq.vnindex_5state
cp vnindex_5state_archive_co_dien.csv vnindex_5state.csv
cp vnindex_5state_history_archive_co_dien.csv vnindex_5state_history.csv
cp vnindex_state_history_archive_co_dien.csv vnindex_state_history.csv
```

**Rollback to pe3c_raw (mid-aggressive):**
```bash
bq cp -f tav2_bq.vnindex_5state_archive_pe3c_raw tav2_bq.vnindex_5state
cp vnindex_5state_archive_pe3c_raw.csv vnindex_5state.csv
# etc.
```

## Naming convention rules

1. **Family name**: "Ngũ Hành" — luôn dùng khi reference 5-state system
2. **Sub-codename**: chữ Việt poetic (Cổ Điển, Tinh Tế, …) cho mỗi major iteration. Avoid technical versions (v1, v2g, pe3c) trong conversation.
3. **Status tag**: LIVE / STAGING / ARCHIVE. LIVE chỉ có 1 tại bất cứ thời điểm.
4. **Tech name** vẫn giữ trong code/file (v2g_pe3c_s3) để traceability.
5. **BQ tables** (updated 2026-06-03 — DT5G era):
   - `vnindex_5state_dt5g_live` = **LIVE production (DT5G)** — read this for the production gated state
   - `vnindex_5state` (no suffix) = **v3.4b BASE only** (== `vnindex_5state_tam_quan_v34b_clean`), DT5G's base input — ⚠️ NOT the production state despite the no-suffix name
   - `vnindex_5state_staging` = STAGING
   - `vnindex_5state_archive_<codename_snake_case>` = ARCHIVE
6. **Khi tạo iteration mới**:
   - Nghĩ codename Việt poetic 2 âm tiết
   - Add row mới ở STAGING
   - Sau khi promote → archive cái LIVE cũ với codename của nó

## Reference

- LIVE doc (DT5G): CLAUDE.md §"VNINDEX 5-State Market System — PRODUCTION = DT5G"; `data/audit_dt5g_events.md`; compute in `macro_state_live.py`
- Predecessor doc (Tinh Tế, archived): [ngu_hanh_tinh_te.md](~/.claude/projects/.../memory/ngu_hanh_tinh_te.md)
- Cổ Điển backtest baseline: original `vnindex_5state_system.py` (in CLAUDE.md notes)
- Integrated test framework: `compare_v11_5state_versions.py`
