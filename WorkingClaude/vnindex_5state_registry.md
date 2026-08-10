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


---

# Phụ lục — kiến trúc & lịch sử DT5G (tách khỏi `CLAUDE.md` 2026-08-10)

> `CLAUDE.md` giữ phần LUẬT (bảng nào là production, đọc qua `get_gated_state()`, cảnh báo
> nhãn bảng, "đừng re-tune"). Toàn bộ diễn giải kiến trúc, số liệu audit và changelog nằm đây.

### VNINDEX 5-State Market System — PRODUCTION = **DT5G** (`macro_state_live.py`)

**5 states** (shared by all versions): CRISIS(0%), BEAR(20%), NEUTRAL(70%), BULL(100%), EX-BULL(130%).

The LIVE production market-regime source as of 2026-06-02 is **DT5G**, computed by `macro_state_live.py` and published to BQ table **`tav2_bq.vnindex_5state_dt5g_live`**. Production consumers read DT5G via `get_gated_state()` (e.g. `golive_recommend`, `pt_v4_dt5g`, `dna_report.py`, `recommend_tomorrow.py`).

> ⚠️ **Table-label correction (verified by BQ, 2026-06-03):** the no-suffix table `tav2_bq.vnindex_5state` is **NOT DT5G**. It is byte-identical to `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (0 diffs / 6291 rows) = the **v3.4b BASE** (TQ34b, ~153 transitions, **no DT-gate, no macro cap**, only light base smoothing). Real DT5G (49 transitions, DT-gate + macro) lives **only** in `vnindex_5state_dt5g_live`. Distribution gap (2014+): `vnindex_5state` has EX-BULL 194 / CRISIS 748 days; `dt5g_live` has EX-BULL 59 / CRISIS 525 (the DT-gate clamps the extremes hard). Many research scripts read bare `vnindex_5state` assuming it is DT5G — **it is the base only**; this is a known research trap. (An earlier note claimed the 2026-06-02 swap put DT5G into `vnindex_5state` — that was wrong; the no-suffix table still serves the v3.4b base. Archives `vnindex_5state_archive_pre_dt5g_20260602` / `vnindex_5state_archive_tinh_te_20260602_*` exist from that episode.)

**DT5G architecture** (do not change without explicit instruction — source: `macro_state_live.py`):
1. **Base state** = v3.4b ("Định Tâm"), read from BQ `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (== the no-suffix `vnindex_5state` table), warmed up from 2014. (v3.4b itself = the ew_v1 → dual_v3 → v3.1 → v3.4b chain — the `dual_v3` stage carries the v2g **BearDvg gate, `min_dur=30`**; plus bull-aware US-override bypass + RSI/concentration gates.) This base alone runs ~153 transitions.
2. **DT 4-gate** (`_dt_4gate`, = `DT_10_25_25`) — **the primary smoother now** (replaces the Cổ Điển `mode(15) → min_stay_filter(7)` pipeline). Asymmetric causal commitment: a new state must persist `enC=25` sessions to commit INTO CRISIS and `enX=25` INTO EX-BULL (slow to panic / slow to euphoria), but only `exC=10`/`exX=10` to leave them, `default=10` for NEUTRAL/BEAR/BULL moves. Cuts whipsaw from the ~155 base transitions down to ~49–53.
3. **Macro gate** (fuses three rule families into ONE causal cap, no rule-sprawl):
   - **Pillar A — domestic money**: SBV refi-rate 6m momentum (`SBV_REFI_EVENTS` from `sbv_macro_overlay`), lagged 5d. Rising-rate → cap. (The cut-from-peak easing FLOOR is still *computed* but **no longer applied** — see `EASING_FLOOR_ENABLED=False`, changelog 2026-06-03.)
   - **Pillar B — US panic**: VIX + SPX 1y drawdown (`us_market_history.csv`, aligned to VN T-1). Thresholds: VIX>35 / SPX-DD<-25% → CRISIS cap, etc.
   - **v3.4b bull-aware bypass**: in a confirmed VN bull (6m return >15% AND Close>MA200), ignore Pillar B, keep Pillar A.
   - **Defensive action = CAP** the state ceiling on stress (the only active macro action). **Re-risk is now PURELY price-based** via the DT base (slow, price-confirmed) — the macro overlay no longer floors the state back up on a monetary-easing signal (asymmetry; easing FLOOR disabled 2026-06-03, was dormant in the live era since 2014-06 anyway).
   - `cap_commit=7`: a defensive cap must persist 7 sessions before committing (debounces VIX flicker).
4. **Breadth-decoupling guard** on Pillar B (added 2026-05-29, free insurance): suppress the US-panic cap ONLY when VN breadth is broadly healthy while the US panics (genuine US-VN decoupling, e.g. 2025 VIC-led). Fail-safe: weak/missing/small-universe breadth → NO suppression → US cap fires as usual. Breadth = % of the breadth universe above MA200, causal (T-1), needs ≥100 names. **Breadth universe = `tav2_mike.universe_pit` (point-in-time, per-day membership) since 2026-07-29** — module constant `BREADTH_SOURCE="pit"` in `macro_state_live.py`; setting it to `"prune"` restores the legacy `ticker_prune` universe exactly (one-word rollback).

**Production state source = `get_gated_state()`** (fail-safe wrapper): returns the DT5G macro state ONLY when `data/macro_health.json` is fresh (<1440 min) and says feeds are trustworthy (`recommended_state_source == "DT5G_macro"`); otherwise fails CLOSED to **DT4-only** (base + DT 4-gate, no macro cap). Consume the `state` column. `state_dt4` = base-without-macro is retained for ablation.

**BQ tables** (labels corrected 2026-06-03 — see ⚠️ note above):
- `tav2_bq.vnindex_5state_dt5g_live` — **DT5G production** (DT-gate + macro, 49 transitions). Read by `get_gated_state` consumers: `golive_recommend`, `pt_v4_dt5g`, `dna_report.py`, `recommend_tomorrow.py`.
- `tav2_bq.vnindex_5state` — **v3.4b BASE, NOT DT5G** (light base smoothing, ~153 transitions). Byte-identical to `vnindex_5state_tam_quan_v34b_clean`. Bare reads of this table get the base, not the production gated state.
- `tav2_bq.vnindex_5state_tam_quan_v34b_clean` — v3.4b base spec (== `vnindex_5state`; daily-refreshed; DT5G reads this as its base input).

**DT5G performance** (event-level audit, 2014→2026-05; source `data/audit_dt5g_events.md`): DT5G == DT4 in benign windows; it deviates on only **49 sessions / 4 de-risk episodes (1.6%)**, 0 re-risk. Integrated prod-spec ablation (DT4 vs DT5G, 50B): **V5 (Kelly) +0.43pp Full** (DT4 23.23% → DT5G 23.67%), **V4 (V121_ENS) +0.27pp Full**; **IS 2014-19 = +0.00pp exactly** (overlay dormant in-sample → walk-forward IS/OOS is the wrong tool here); OOS 2020-now V5 +0.88pp / V4 +0.54pp. Per-year LOO: the entire net edge = the single 2023 tightening (+5pp/yr V5); the 2025 bull COSTS −0.89pp. **Verdict: DT5G is a FAIL-SAFE RISK GATE (insurance), not a return-enhancer** — deploy via `get_gated_state`, do not re-tune to history (params are a robust plateau).

**Changelog**:
- **2026-07-29** — `macro_state_live.py`: breadth-decoupling guard (§4) switched from `ticker_prune` → `universe_pit` (`BREADTH_SOURCE="pit"`, `_breadth_sql()`). Reason: the old SQL joined `IN (SELECT DISTINCT ticker FROM ticker_prune)` with **no time condition** — a name admitted today was counted on every historical breadth date (look-ahead), and the 2026-07-29 `ticker_prune` TRUNCATE+rebuild silently dropped 58 names from the whole series (Winston_20260729_132257). Measured A/B 2014-01-02→2026-07-29 (3135 sessions): breadth series differs on 3132 days, guard flips 229 (7,3%), macro cap differs 13 (2016-01-26→02-18, pit side MORE conservative, non-binding), **final DT5G state differs on 0**, DT4 base 0, today unchanged NEUTRAL(3). Thresholds unchanged (data-source migration, not a re-tune). quant-skeptic CONFIRMED (high); post-merge self-check 6/6 PASS on the merged module. Job `Taylor_20260729_152031` / merge `Taylor_20260729_160020`, report `mike/agents/Taylor/research/dt5g_breadth_guard_universe_pit_20260729.md`.
- **2026-06-03** — `macro_state_live.py`: set `EASING_FLOOR_ENABLED=False` — disabled the monetary-easing recovery floor (asymmetry: re-risk only via the price-based DT base, never on rate cuts alone). Dormant in the discrete live state since 2014-06 → zero live-behavior change; full-history backtest improved marginally (Full CAGR 19.93→20.05%, Sharpe 1.36→1.37, same MaxDD). `vnindex_5state_dt5g_live` re-published.
- **2026-06-03** — repointed `dna_report.py` (Telegram bot NOW-regime block) and `recommend_tomorrow.py` from bare `vnindex_5state` → `vnindex_5state_dt5g_live` so they report the true DT5G production regime instead of the v3.4b base.
- **2026-06-03** — doc fix: corrected the table labels above (`vnindex_5state` is the v3.4b base, not DT5G).

> **Cổ Điển (archived, NOT live)** — `vnindex_5state_system.py` is the original baseline ("Cổ Điển"), kept for historical reference only. Its smoothing pipeline was **EMA(0.40) → mode(15) → min_stay_filter(7)** over 7 expanding-percentile factors with BearDvg/BullDvg gates. It was superseded by Tinh Te (v2g_pe3c_s3), then v3.4b, then DT5G. The "EMA(0.40) → mode(15) → min_stay_filter(7)" pipeline and its ~16.1%/-62.3% full-period numbers describe this archived version, **not** current production. See [vnindex_5state_registry.md](vnindex_5state_registry.md) for the full lineage.

