# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

## Status: 2026-06-24

### DONE THIS SESSION
1. **PE_stored bug (Việc 1) — CLOSED: NOT MATERIAL**
   - fa_ratings_8l (production) tier = ROIC/ROE/FSCORE/cashflow/leverage, NO PE
   - score_valuation in fa_ratings (older A-E) averages 0.50 across ALL tiers → PE bias irrelevant to tier
   - Production path custom_basket.py uses fa_ratings_8l exclusively
   - No IS/OOS re-run needed
   - Bus event: decision/pe-stored-bug-impact-assessment ✓

2. **V2.4 go-live formal summary (Việc 2) — DONE**
   - File: data/v24_golive_summary.md created
   - Numbers (snapshot 2026-06-24, 0 VND):
     R3 baseline: 29.00%/Sh1.90/DD-18.5/Cal1.56
     V2.4: 30.63%/Sh1.97/DD-17.5/Cal1.75 (+1.63pp CAGR/-1.0pp DD/+0.19 Calmar)
     OOS: +3.17pp CAGR, Calmar 1.56→1.84
     IS: unchanged (signal dormant IS)
   - Bus event: decision/v24-golive-bundle-ready ✓

### BLOCKING (go-live 2026-06-30)
- **Awaiting: user + Spyros approval** on V2.4 bundle
- Summary doc sent to: Mike, DollarBill, Spyros, Mafee via bus

### Config chốt V2.4
- RECOVERY_PARK=1 RECOVERY_WMAX=0.95 RECOVERY_PBZ_DEEP=-0.5
- RECOVERY_DEP_GATE=1 (DORMANT floor=7.5%)
- trading_rules v1.6 (leverage-free go-live)
- Base: v23a none postbull 0 edge + custompitg/namecap/yieldcombo/NEUTRAL-only

### Post-go-live (separate item, NOT blocking)
- Real-margin 1.3x CAPIT-only: needs Spyros sign-off (đòn bẩy thật, tự-kiểm 0 VND, DD-15.5%)

