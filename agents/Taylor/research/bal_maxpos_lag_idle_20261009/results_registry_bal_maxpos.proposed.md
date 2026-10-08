## 2026-10-09 — BAL MAX_POS 12→16/20 khi LAG idle: NO-GO (job Taylor_20261008_163222)
no_ledger: kết quả NO-GO, không pin số mới; 4 ledger treatment là thí nghiệm (tên `_exp_bmx_*`), không thay mẫu số.
- Control tái lập byte-identical: 537e349b (pin0% 22,12%) và a6ba34d8 (pin1M 25,42%), code research bb700ab6 (knob mặc định + log trơ).
- ΔCAGR FULL vs control cùng carry: m16_off −1,19pp · m20_off −1,55pp · m16_1m −1,14pp · m20_1m −2,09pp; âm ở cả IS và OOS, LOO-năm âm ở mọi năm bỏ, DSR excess ≤0,013.
- Cơ chế: BAL/LAG sổ cái độc lập → nới trần chỉ tiêu cash dư BAL (trung vị 0,7% NAV BAL lúc bị chặn), không chạm cash LAG (LAG navT 426,8135B ở mọi chân); ứng viên ngoài top-12 yếu hơn (excess 45d trung vị OOS −2,6%, hit 44%) + hiệu ứng đường đi (vị thế vụn <5% 14%→29%, STOP 29→51, BAL 2021 +122%→+65/84%).
- Báo cáo: mike/agents/Taylor/research/bal_maxpos_lag_idle_20261009/REPORT.md · PREREG 7f7ff730.
