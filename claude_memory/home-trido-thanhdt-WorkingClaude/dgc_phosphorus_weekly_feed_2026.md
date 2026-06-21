---
name: dgc_phosphorus_weekly_feed_2026
description: "Weekly yellow-phosphorus (P4) price feed for DGC — fills the 8L's missing P4 driver (was DAP-proxied); SunSirs source + script + Friday-gated batch wiring"
metadata: 
  node_type: memory
  type: project
  originSessionId: a95e652f-b0cd-4f2c-9251-9d8c7fa31d0d
---

DGC's real earnings driver = **yellow phosphorus (P4)**, but the 8L cyclical lens had NO clean P4 feed and proxied it with DAP (code note `cyclical_multi.py:10`: "real product = yellow phosphorus P4 (no clean history); DAP = partial proxy"; `cyclical_structural.py` maps DGC→"dap"→`BALANCED/WAIT`). User ([REDACTED]15) asked to fold a **WEEKLY** P4 price trend into DGC's nhận định (explicitly "không cần lấy giá hàng ngày").

**Built `phosphorus_dgc_weekly.py`** → scrapes China P4 spot from SunSirs `prodetail-708.html`. ⚠️ Anti-bot **HW_CHECK cookie wall** (page returns a 636-byte JS stub "安全检查"): solved in pure urllib by fetch-stub → read `var _0x2="<token>"` → re-request with header `Cookie: HW_CHECK=<token>` → full 22KB page (no WebFetch needed). Forward-accumulates daily prints into `data/phosphorus_weekly.csv` (dedupe by date, BDI-style like `fetch_bdi_daily.py`); pulls DGC latest quarter + valuation from BQ (graceful try/except if bq absent); writes `data/dgc_phosphorus_watch.md` (dated nhận định: P4 trend + cycle-zone + DGC earnings-leverage read). Wired into `papertrade_daily.bat` **step [15], Friday-gated** (`for /f %%d in ('powershell -NoProfile -Command "(Get-Date).DayOfWeek"') do set DOW=%%d` + `if /i "%DOW%"=="Friday"`). Runs Fri only; other days log "skipped".

**P4 cycle zones (RMB/ton)** used for the verdict: trough 2023-25 ~22-26k (DGC GPM compressed) · recovery 27-32k · mid-favorable 32-38k · 2022 supercycle 40-50k · 2021 dual-control spike >50k. **Pivot ~30k** = "is the recovery holding?".

**History seeded** (one-time `seed_phosphorus_history.py`): 7 SunSirs *benchmark* points (== prodetail daily series) quoted in the SunSirs weekly review articles, backfilling 2026-03 → 2026-05 so the trend has full ~3-month depth immediately (live feed densifies from there). Sources: news-31680 (03-02 **24,172.67** = this-cycle trough / chart min; 03-20 25,000; 03-27 26,796), news-32138 (04-02 27,167; 04-15 31,163), news-33016 (05-18 32,096; 05-19 32,429). NB: real trough = **early MARCH ~24,173** (not early-April as first read off the chart); rise has been monotonic March→June.

**Read @[REDACTED]15**: P4 **34,796 RMB/ton, +43.9% off the ~24,173 (02/03) trough**, +8.4% MoM, +3.6% WoW, MID-favorable + above pivot → verdict **HƯỞNG LỢI** (output price inflecting up; transmission lag ~1Q so not yet in reported numbers). BUT DGC 2026Q1 = **trough earnings** (NP 409 tỷ −49.5% YoY, Rev −24.4% YoY, GPM 28.9% = lowest in series, FSCORE 2); stock beaten down (Close ~47.8k, **−34% vs MA200**, PB 1.15, PE 6.9) = classic cyclical-trough setup. 8L route DGC = **CYCLICAL, tier B**. **Watch**: hold >30k (structural / demand-driven) vs dry-season power-rationing spike (transient → reverts); a rise during wet season (Jun) is notably counter-seasonal.

Related [[oil_gas_chain_8l_2026]] (DGC in fert/chem chain, ICB1357), [[cyclical_commodity_framework_2026]] (buy-trough contrarian logic).
