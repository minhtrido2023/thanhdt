---
kind: project
owner: Taylor
status: closed
updated: 2026-11-24
title: "Dải tham chiếu chiết khấu holding (HHS) — chốt gọn 0 … +20% (24/11/2026)"
---
# Dải tham chiếu chiết khấu holding (HHS) — chốt gọn 0 … +20% (24/11/2026)

> **Hiển thị / tham chiếu, KHÔNG wire.** Chưa dựng rev8 HHS, chưa ghi `dd_price_zones.json`, chưa email.
> Nguồn số: `agents/Taylor/research/ck_holding_vn_20261124_v5/` (REPORT_CK_HOLDING_v5.md, SKEPTIC_v5.md; skeptic rà phần thay đổi CONFIRMED/medium; merge master c69a7935b).

## Quyết định
- **`decided_by: user` (24/11 15:36 ICT)** — "đồng ý chốt dải đề xuất, nhưng dải không nên quá dài làm mất giá trị đề xuất".
- **`decided_by: user` (24/11 15:48 ICT)** — duyệt luôn mốc đề xuất **0 … +20%** ("Dải hhs duyệt mốc đề nghị"). Dải 0…+20% đã được user chốt.

## Dải: 2 mốc
| Mốc | Là gì | KHÔNG phải là |
|---|---|---|
| **0%** (nhãn "đầu lạc quan") | ≈ trung vị N=12 **−3,24%** (LOO −8,1…+1,6%) cộng đầu trên +1,6% | tâm đo được; chiết khấu = 0 là cận trên có lợi cho HHS |
| **+20%** (= mốc hiện tại; khoảng đo **15–23%**) | một holding PAN, ≈1 quan sát độc lập, xu hướng chưa đảo (19,7% trong v5) | trung tâm dài hạn |

Độ tin **THẤP**: N=12, 1 chế độ thị trường, T_eff≈0,4. Hull trung thực rộng 36,5pp (−16,8…+19,7) — không có dải trung tâm <20pp; dải 0…+20% là lựa chọn đơn giản hoá có chủ đích, không phải khoảng tin cậy.

## Ngoài dải — chỉ ghi chú
- **Stress +33…+38%** (q75 37,7% POSTHOC; 33,5% PREREG gốc): dùng khi HHS có dấu hiệu cấu trúc premium (phân tán một holding).
- **Đầu âm −17%**: chỉ khi HHS có cấu trúc R1/R2 (chưa ai kiểm; brief cấm đọc HHS). **Điều kiện trước khi dùng**: kiểm cấu trúc sở hữu HHS vs R1/R2 bằng việc giao riêng.
- Bỏ +6% (skeptic v5: "bỏ +6% đúng").

## 3 lỗi nhỏ còn lại của v5 (không đổi trung vị/mốc hiện tại/dải a∪d)
- **A**: MSN có 74,58tr CP ưu đãi chuyển đổi 1:1 (CDPS, Bain) nằm trong E_p nhưng không MV_p ⇒ MSN 20/11 45,7→~42,9%.
- **B**: `sweep_v5.py:55-56` bỏ trung gian niêm yết không có giá ⇒ GEX→GEL→VGC+PXL sót, GEX 39,0→~43,3% (đã trên trung vị); chỉ GEX dính.
- **K1**: 2 dòng POSTHOC (stakes_override MCH 66,2% + participation_override MCH 51,28%) khai thiếu; report ghi nhầm 51,28% là "KBS"; hull đúng chữ §C2 đổi −101,4…19,7 → −88,5…30,0, c3_control N 9→10.
- Chưa sửa; sửa chỉ khi user giao việc dựng HHS rev8.

## Cấm (chưa có lệnh)
Dựng rev8 HHS · ghi `dd_price_zones.json` · đọc giá HHS/TCH/CRV · email · wire vào sizing/gate.
