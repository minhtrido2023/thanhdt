---
name: capit-selection-study-2026
description: CAPIT per-name selection study — golden PB_z is the only robust within-event discriminator; momentum/rebound-history are 2022 artifacts
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ef717ab-5c78-4933-9acd-888a2ecf9450
---

CAPIT "chọn mã nào trong rổ" study ([REDACTED]12, user hỏi nhóm nào hiệu quả nhất + ý: dùng momentum-book knowledge? technical chọn golden eggs? sức-bật-lịch-sử của chính mã?). Method: 141 vị thế CAPIT thực hiện từ ledger audit (`data/capit_positions.csv`, 50 mã/16 event, all closed) → join đặc trưng tại lúc mua từ BQ + earnings_px → **within-event rank IC** (demean theo event = tách chọn-mã khỏi chọn-thời-điểm). Scripts: `data/capit_selection_study.py` + `data/capit_selection_features.csv`.

**KẾT LUẬN: chọn-mã trong CAPIT YẾU; EVENT (regime) chi phối, không phải name.** Within-event IC hầu hết |IC|<0.2 và KHÔNG robust.

**Robustness killer (IC all-events vs EXCLUDING event9=2022-04, rổ 30 mã):**
| feature | IC all | IC ex-2022 | verdict |
|---|---|---|---|
| **PB_z** | −0.106 | **−0.212** (MẠNH lên, đúng dấu) | ✅ DUY NHẤT robust — golden valuation |
| C_L1W (oversold vs đáy tuần) | −0.214 | −0.122 | ⚠️ yếu nhưng giữ dấu |
| rebound (sức-bật lịch sử, ý user) | +0.224 | **−0.076** (LẬT dấu!) | ❌ artifact 2022 |
| ROE_Min5Y / FSCORE / ROIC5Y | −0.13..−0.22 | giữ SAI dấu | ❌ quality KHÔNG giúp trong rổ |
| PE | +0.311 | +0.043 (sụp) | ❌ spurious |
| own_dd52 / D_CMF | +0.06/+0.10 | −0.35/−0.31 (lật loạn) | ❌ noise |
| D_RSI/D_MACDdiff/D_CMB | ~0 | ~0 | ❌ momentum vô dụng (mã đã crash) |

**Trả lời 3 ý user**: (1) momentum-book/technicals (RSI/MACD/CMF/CMB) = near-0, KHÔNG giúp (cổ phiếu đã sập → momentum vô nghĩa). (2) technical chọn golden egg: chỉ **C_L1W** (gần đáy-tuần/oversold) có tín hiệu nhẹ thật — tercile oversold nhất +10.1% vs ~5%. (3) **sức-bật-lịch-sử: looked promising (+0.224) nhưng LÀ artifact 2022** (ex-2022 → −0.076), KHÔNG survive → đừng dùng. **Quality-trong-rổ KHÔNG thêm** (ROE/FSCORE/ROIC sai dấu) vì rổ ĐÃ quality-screened; trong nhóm sống sót, quality không phân biệt thêm.

**Survivor DUY NHẤT = golden PB_z** (mạnh lên ex-2022, xác nhận prior [[cheap_pb_floor_quality_crisis]]): mã rẻ-vs-lịch-sử-chính-nó (z<−1) hồi tốt hơn TRONG rổ. → **Rổ playbook hiện tại (quality screen ROE_Min5Y≥12%/ROIC5Y≥10%/FSCORE≥6, rank theo PB_z, lấy golden z<−1) ĐÃ là selection đúng**; thêm momentum/rebound/technical overlay = overfit 2022. Tinh chỉnh nhẹ tùy chọn: nghiêng về mã oversold nhất (C_L1W thấp) trong nhóm golden. Lại một lần nữa: 1 event (2022) tạo tín hiệu giả, chỉ prior kinh tế (golden value) sống sót robustness. Liên quan [[v23_audit_2014_now_deliverable]].
