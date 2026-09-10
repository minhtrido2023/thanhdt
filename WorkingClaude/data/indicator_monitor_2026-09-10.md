# Indicator Monitor — 2026-09-10


Universe: `tav2_bq.ticker_1m` ngày mới nhất, lọc `liq = Volume_3M_P50*Price >= 1e9` (sàn thanh khoản SIGNAL_V11 đã dùng) — 256 mã. Công cụ audit thuần — KHÔNG đổi logic rating/filter. Xem `kb/coding_guidelines.md` §9/§29.


47/256 mã thiếu ≥1 cột cần cho BAL (SIGNAL_V11) hoặc 8L rating (rating_8l.py, `['CF_OA_3Y', 'ROE_Min3Y']` = golden floor).


_Lưu ý đọc bảng: index/ETF (VNINDEX, VN30, E1VFVN30...) thiếu toàn bộ cột tài chính là BÌNH THƯỜNG (không có BCTC) — không phải data gap. `UnearnRev_P0` thiếu ở NGÂN HÀNG cũng vậy (không có doanh thu chưa thực hiện). Cả hai vẫn được liệt kê nguyên văn (tool không tự loại trừ theo ngành) — người đọc tự lọc theo ICB khi cần._


| Ticker | Golden floor? | Thiếu (BAL/SIGNAL_V11) | Thiếu (8L rating) |

|---|---|---|---|

| E1VFVN30 | ⚠️ CÓ | ['PE', 'PE_MA5Y', 'PE_SD5Y', 'FSCORE', 'NP_P0', 'NP_P1', 'NP_P4', 'ICB_Code'] | ['ROIC3Y', 'ROIC_Min3Y', 'ROE_Min3Y', 'ROIC_Trailing', 'ROIC5Y', 'ROIC_Min5Y', 'ROE_Min5Y', 'ROE5Y', 'Debt_Eq_P0', 'FSCORE', 'PB', 'PE', 'PCF', 'EVEB', 'OShares', 'CF_OA_3Y', 'CF_OA_5Y', 'ROE_Trailing', 'ROE3Y', 'STLTDebt_Eq_P0', 'GPM_P0', 'Revenue_P0', 'UnearnRev_P0', 'totalAsset_P0'] |

| VNINDEX | ⚠️ CÓ | ['PE', 'PE_MA5Y', 'PE_SD5Y', 'FSCORE', 'NP_P0', 'NP_P1', 'NP_P4', 'ICB_Code'] | ['ROIC3Y', 'ROIC_Min3Y', 'ROE_Min3Y', 'ROIC_Trailing', 'ROIC5Y', 'ROIC_Min5Y', 'ROE_Min5Y', 'ROE5Y', 'Debt_Eq_P0', 'FSCORE', 'PB', 'PE', 'PCF', 'EVEB', 'OShares', 'CF_OA_3Y', 'CF_OA_5Y', 'ROE_Trailing', 'ROE3Y', 'STLTDebt_Eq_P0', 'GPM_P0', 'Revenue_P0', 'UnearnRev_P0', 'totalAsset_P0'] |

| VN30 | ⚠️ CÓ | ['PE', 'PE_MA5Y', 'PE_SD5Y', 'FSCORE', 'NP_P0', 'NP_P1', 'NP_P4', 'ICB_Code'] | ['ROIC3Y', 'ROIC_Min3Y', 'ROE_Min3Y', 'ROIC_Trailing', 'ROIC5Y', 'ROIC_Min5Y', 'ROE_Min5Y', 'ROE5Y', 'Debt_Eq_P0', 'FSCORE', 'PB', 'PE', 'PCF', 'EVEB', 'OShares', 'CF_OA_3Y', 'CF_OA_5Y', 'ROE_Trailing', 'ROE3Y', 'STLTDebt_Eq_P0', 'GPM_P0', 'Revenue_P0', 'UnearnRev_P0', 'totalAsset_P0'] |

| F88 |  | ['ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y', 'FSCORE', 'NP_P4'] | ['FSCORE'] |

| VCK |  | ['MA200', 'ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| VPX |  | ['MA200', 'ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| TCX |  | ['ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| VPL |  | ['ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| MZG |  | ['ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| AIG |  | ['ID_HI_3Y', 'PE_MA5Y', 'PE_SD5Y'] |  |

| TSA |  | ['PE_MA5Y', 'PE_SD5Y'] |  |

| DSE |  | ['PE_MA5Y', 'PE_SD5Y'] |  |

| BIG |  | ['PE_MA5Y', 'PE_SD5Y'] |  |

| MBS |  |  | ['ROIC_Trailing', 'ROE_Trailing'] |

| SBS |  |  | ['ROIC_Trailing', 'ROE_Trailing'] |

| BVS |  |  | ['ROIC_Trailing', 'ROE_Trailing'] |

| BMS |  |  | ['ROIC_Trailing', 'ROE_Trailing'] |

| DCL |  | ['PE'] | ['PE'] |

| THD |  |  | ['PCF', 'EVEB'] |

| TRC |  |  | ['ROE_Trailing'] |

| TNG |  |  | ['ROE_Trailing'] |

| DIG |  |  | ['ROE_Trailing'] |

| TIN |  |  | ['UnearnRev_P0'] |

| KLB |  |  | ['UnearnRev_P0'] |

| VPB |  |  | ['UnearnRev_P0'] |

| TCB |  |  | ['UnearnRev_P0'] |

| EVF |  |  | ['UnearnRev_P0'] |

| LPB |  |  | ['UnearnRev_P0'] |

| ABB |  |  | ['UnearnRev_P0'] |

| ACB |  |  | ['UnearnRev_P0'] |

| VIB |  |  | ['UnearnRev_P0'] |

| VAB |  |  | ['UnearnRev_P0'] |

| BVB |  |  | ['UnearnRev_P0'] |

| VCB |  |  | ['UnearnRev_P0'] |

| CTG |  |  | ['UnearnRev_P0'] |

| NVB |  |  | ['UnearnRev_P0'] |

| OCB |  |  | ['UnearnRev_P0'] |

| MBB |  |  | ['UnearnRev_P0'] |

| NAB |  |  | ['UnearnRev_P0'] |

| SSB |  |  | ['UnearnRev_P0'] |

| TPB |  |  | ['UnearnRev_P0'] |

| EIB |  |  | ['UnearnRev_P0'] |

| SHB |  |  | ['UnearnRev_P0'] |

| MSB |  |  | ['UnearnRev_P0'] |

| HDB |  |  | ['UnearnRev_P0'] |

| BID |  |  | ['UnearnRev_P0'] |

| STB |  |  | ['UnearnRev_P0'] |
