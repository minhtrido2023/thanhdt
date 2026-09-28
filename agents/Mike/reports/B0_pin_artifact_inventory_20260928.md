# B0 — Kiểm kê artifact của mọi số đã pin

*Sinh tự động bởi `bin/pin_artifact_inventory.py` lúc 2026-09-28 15:15 ICT. Script CHỈ ĐỌC.*

Nguồn: `data/results_registry.md` · cây quét: `data/`, `mike/research/`, `mike/agents/`, `mike/kb/`

| | số lượng | nghĩa |
|---|---|---|
| ✅ trong kho bất biến | 2 | an toàn, không ghi đè được |
| 🟡 chỉ có file rời | 24 | có thể bị ghi đè bất cứ lúc nào |
| ⚠️ trong đó chỉ ở worktree TẠM | 0 | xoá worktree là mất |
| ❌ MẤT DẤU | 2 | **không còn tái lập được** |
| **tổng** | **28** | |

## ❌ Mất dấu — số nào trích các md5 này là số KHÔNG tái lập được

- `a953d4bb06f7e429bd55837aebcdaefc` (32 hex)
- `f30a5beadde2bc5e117eca47021aabef` (32 hex)

## 🟡 File rời (nên pin vào kho)

- `1d2f8cad366cc538a1844def6fd06a2d` → `data/custom30v_8l_publish_CAND_20260927pm.csv`
- `2f9c3702524391f5538d262edb17515d` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_pinR3_20260927pm_univpit.csv` (+3 bản trùng)
- `32659b23856448b4f566fb3d3fd834a1` → `data/custom30v_8l_publish.csv`
- `3f836927c0df82915c4cfb973d8f4af3` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_c30vnopark_univpit.csv` (+7 bản trùng)
- `454f40c0a6846c260e34439f98a58d71` → `mike/agents/Taylor/research/custom30v_selector_20260909/PREREG.md` (+2 bản trùng)
- `4d736d9169c32f1055ea6c54ee5c6dac` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_dropMOMN-MOMS.csv` (+18 bản trùng)
- `518651bf3c6b86fe814acc68daab14d6` → `data/custom30v_8l_publish_expwexdate2_exdate.csv` (+1 bản trùng)
- `5f1013c0ea2a6b03d2fb1b5ab088c6e2` → `mike/agents/Taylor/research/custom30v_placebo_20260910/report.md` (+2 bản trùng)
- `6c11b1bc908cc74d18bda86b44b3e243` → `mike/agents/Taylor/research/custom30v_placebo_20260910/PREREG.md` (+2 bản trùng)
- `7d053e6201c9d107685ff4d1dd9d2d2a` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_dyn_ctrl_univpit.csv` (+40 bản trùng)
- `7de1daf4874bb062d87e16897a1db277` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_c30vctl_univpit.csv` (+2 bản trùng)
- `8eb19acfd3c18392da23eaca6a5404dd` → `data/custom30v_8l_publish_expwexdate2_quarter.csv` (+1 bản trùng)
- `a90e87c093873028ac2cd19f71c1780e` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-80_wtnamecap_advprice_exp_parkgrid_080q_univpit.csv` (+1 bản trùng)
- `c24f39071a400cff5d956a2fc5288af9` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_ekexit_univpit.csv`
- `d6ac4be1294cc26650af9b61ea20dd1e` → `data/lag_edge_health.csv.bak_20260927_prefailc`
- `dc4ce3a9bd35152c5a344a4fe90d0554` → `data/lag_edge_health_exp_causal.csv` (+1 bản trùng)
- `ff0d3a37d2ba682ca9b1244b2e36125d` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_exp_pinR3_20260927_park030_univpit.csv` (+2 bản trùng)
- `2cea9626` → `mike/research/dsr_family_manifest_20260927/man_2026_07_recon.json` (+2 bản trùng)
- `51a1ec0f` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_repin0803_close_univpit.csv` (+7 bản trùng)
- `58208ffa` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_pc_ovf_fixtable_univpit.csv`
- `c6d56907` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_pc_ovf_oldtable_univpit.csv`
- `c774418c` → `mike/research/dsr_family_manifest_20260927/man_today.json` (+2 bản trùng)
- `d73f983d` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_etfcreatpit_exp_rp_21sfifo_re2_univpit_idledep1m_21sfifo.csv` (+1 bản trùng)
- `f4421a17` → `data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_depgate_ctlSb.csv` (+1 bản trùng)

---

Pin một artifact vào kho:

```bash
mike/bin/pin_ledger.py add <file.csv> --label <nhãn> \
    --command "<lệnh chạy đầy đủ>" --audit-end <YYYY-MM-DD>
```
