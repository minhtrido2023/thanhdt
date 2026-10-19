# AIS lock-up stale-base — PARKED 2026-10-19 (user: "Park")

**Trạng thái:** KHÔNG làm tiếp. `oshares_live` giữ fail-closed (`AIS_UNCERTIFIED`) cho 10 mã (ELC, DCF, HKT, HMS, KSH, PSD, TAL, TCB, TLG, VTK ngày 19/10). Tác động tiền ≈ 0.

**Cơ chế thật (đừng chẩn đoán lại là "vendor sai ngày"):** với AIS của ESOP / phát hành riêng lẻ, `effective_date` = ngày hết lock-up = `listing_date` của ISS tương ứng (70/73 dòng); `shares_total_after` là tổng cộng dồn lúc PHÁT HÀNH (stale-base), không phải mức niêm yết tại `effective_date`. Sắp theo `effective_date` ⇒ chuỗi gãy ⇒ cổng chứng nhận từ chối (đúng thiết kế). Ca ELC: ESOP 4,9tr ex 2025-08-22, listing 2026-08-24.

**Nhánh đã thử, BỊ BÁC:** `feat/ais-chain-order-20261019` @`c22ce4c60` (worktree `wt-Taylor_20261019_052148`, Taylor job `Taylor_20261019_052148`). Rule `_chain_redate` (sắp theo total, dời ngày về public_date, `chain_certified`) bị arch-review NEEDS_CHANGES + quant-skeptic REFUTED: bỏ `_delta_predates_anchor` ⇒ `AIS_EXACT` sai ở SFI 2019 (−3,5%), NAF 2020 (−20,6%), CTD, HAX@2023-02 (−13%→+26%); TCB/PSD live mở khoá nhờ bypass đó.

**Nếu làm lại:** loại dòng lock-up lệch thứ tự + total thấp khỏi chọn anchor/prev (không dời ngày); đo thử cho ELC 117.748.108, SFI vẫn None. Kèm: re-freeze 8 ca legacy (AAA, HHV, TCB, HAH, EVF, IDC, FPT, KHP) có `public_date`; SFI@2019-01-01 làm ca âm; audit toàn bộ ô None→số vs BCTC xuất bản ≤ asof; ghi vào data_registry `corporate_action_bq.md` (§9); NAF = bug `_dedup_iss` có sẵn (hai tranche cùng ngày ratio 0 bị gộp). Số đo: `agents/Taylor/research/ais_chain_order_20261019/`.
