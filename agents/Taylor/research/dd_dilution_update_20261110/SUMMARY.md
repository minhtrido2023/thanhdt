# SUMMARY — cập nhật DD theo pha loãng (10/11/2026, job Taylor_20261110_034232)

Phạm vi: 2 mã có đợt tăng vốn chưa được phản ánh đúng (Mike kiểm kê `tav2_bq.corporate_action` × `kb/dd_price_zones.json`). Định giá **mù giá**, không làm lại mô hình. Bản này dùng phân phối r3 đã qua skeptic CONFIRMED, rồi biến đổi theo số cp và tiền thu (tuyến tính, chính xác). Vụ án / quản trị chỉ WARNING.

Giá dùng (nguồn + ngày):
- HHS: **price_ref ledger = 9.990** (BQ `tav2_bq.ticker` đóng cửa 09/11). DNSE 10/11 10:46 ICT khớp 10.000 (theo skeptic là lệnh đơn 50 cp; chưa lưu bản ghi nên không dùng); tham chiếu 10/11 = 9.990.
- SCL: BQ đóng cửa 06/11 = 29.400 (cum), 09/11 = **28.000** (ex). DNSE 10/11: tham chiếu 28.100, khớp 28.300 lúc 10:18 (690 cp).

| Mã | Đợt | Trạng thái | Kết quả | Nhãn | Đổi kết luận? |
|---|---|---|---|---|---|
| **HHS** | Quyền mua 5:3 (60%) @10.000, 259,19 tr cp, 2.591,9 tỷ → mua 260 tr cp NĐL (dự án I.14); cổ tức CP 7% (48,38 tr cp, trên 691,18 tr) phát hành SAU quyền | **CHƯA thực hiện**: NQ ĐHĐCĐ 01 (24/04), NQ HĐQT 07 (26/08); dự kiến Q4/2026–Q1/2027 sau khi UBCKNN cấp phép; chưa có ĐKCC | CUM: 13.969 / P10 12.422 / P90 15.564 (k=1; quy ước CK-trên-tiền: 13.884 / 12.337 / 15.479). EX dự kiến (đủ): **11.615 / 10.711 / 12.546**, TERP 9.346; độ nhạy k=0,946 (75,41% NĐL, −141 tỷ): 11.428 / 10.525 / 12.360 | DƯỚI (cả cum lẫn ex) — **có điều kiện**: CK holding 0% (errata r3 chờ user) + pha loãng 60% @thị giá là điều kiện trượt §2.5; bản CK holding 27%: giá VƯỢT tâm (r3 −7,2% → r4 TERP +6,1%), vẫn TRONG | **Không**. Thêm WARNING tăng vốn + quản trị bên liên quan; vẫn forensic EXCLUDE |
| **SCL** | Quyền 15,4453% @12.500, GDKHQ 09/11 | **ĐÃ ex**; đăng ký và nộp tiền 17/11–08/12 | EX 5 tỷ: **21.339 / 17.445 / 25.681** (40 tr: 22.146 / 18.104 / 26.651); 44.836.815 cp (6.000.000 cp mới, 75 tỷ — TB 1368/TB-SCL) | TRÊN; giá/P90 cùng cỡ: 40 tr +1,9% (cum) → +5,1% (ex); 5 tỷ +5,7% (cum) → +9,0% (ex) | **Không**. Giá ex cao hơn TERP 3,2% |

Giá trị/cp HHS −16,9% (13.969→11.615) vs TERP −6,5% (10.000→9.346); tâm/giá 1,397→1,243. Luật 4 trên cơ sở EX: điểm hoà vốn k=0,8207, ĐẠT ở k≥0,946, TRƯỢT ở k=0,8 ⇒ "Luật sổ ĐẠT" chỉ có điều kiện.
WARNING quản trị HHS: NQ 06/NQ-HĐQT 21/07 (vay tối đa 100 tỷ từ TCH) đã đọc; tiền thu vào NĐL qua bên liên quan; HHS cần 1.080,6 tỷ ngoài phần TCH vs tiền mặt Q3 181,9 tỷ.

Chi tiết: `HHS_r4.md`, `SCL_r4.md`. Calc: `calc/dilution_calc.py` → `calc/dilution_out.json`, chạy 2 lần trùng byte (vòng 2, sửa kịch bản SCL 40 tr: c=1 khớp r3 22.146). LOCK: `calc/LOCK_md5.txt`.

## Điểm "không xác định được" (nói thẳng)
- **HHS:**
  - Chưa xác định được hạn hiệu lực hay thời hạn phân phối của phương án.
  - Cấu trúc phát hành NĐL lệch giữa 75,41% (công ty nêu) và 79,8% (tự tính).
  - Chưa đọc thuyết minh sự kiện sau kỳ trong BCTC Q3 (bản scan).
- **SCL:** nguồn "ESOP 2,1% announced 07/05" **CHƯA đóng**. 920.000 / (37.916.815 + 6.000.000) = **2,095%** ở cả hai cách đọc (bản trùng vs ESOP riêng sau quyền) ⇒ không phân biệt được. Chưa nên nhờ Winston đóng dòng vendor trước khi đọc NQ 486/NQ-ĐHĐCĐ 24/04/2026 hoặc bản cáo bạch. Độ nhạy nếu là ESOP riêng: tâm 5 tỷ 21.106, nhãn giữ.

## Phát hiện dữ liệu (chuyển Winston)
- BQ `tav2_bq.ticker` SCL: chuỗi `Close` **chưa điều chỉnh lùi** cho quyền ngày 09/11 (06/11 Close = Price = 29.400). Hệ số kỳ vọng 0,9231. Chỉ báo hay lợi suất qua mốc này sẽ thấy cú giảm giả −4,8%.
- BQ `corporate_action` SCL có dòng ISS 2,1% ESOP ở trạng thái `announced` từ 07/05, chưa xác định là bản trùng hay ESOP riêng — chờ đọc NQ 486/NQ-ĐHĐCĐ (xem trên); CHƯA nên đóng.

## Đề xuất entry ledger `kb/dd_price_zones.json` (append-only; KHÔNG tự ghi — Mike nhập sau skeptic)
Chú ý cơ sở:
- **SCL rev 5 là cơ sở EX.** Không so với giá trước 09/11.
- **HHS rev 4 giữ cơ sở CUM.** Entry có thêm khối `ex_basis_pending`, kích hoạt khi có GDKHQ quyền. Tại thời điểm đó công cụ hoặc Mike phải chuyển vùng; không được so giá ex với vùng cum.
- Field `ex_basis_pending` là **field mới**, chưa có trong schema v1. Nếu công cụ không đọc field lạ, có hai cách: (a) Mike chỉ nhập phần cum và ghi một entry rev 5 khi có ĐKCC; hoặc (b) mở rộng schema (việc của Mike).

```json
[
 {
  "ticker": "HHS",
  "dd_date": "2026-11-01",
  "rev": 4,
  "bctc_quarter": "2026Q3",
  "zone_low": 12422,
  "center": 13969,
  "center_kind": "expected_weighted",
  "center_desc": "kỳ vọng trọng số lưới r3 (CK holding 0%), sau CK 5 tỷ; cơ sở CUM (431.985.968 cp) — quyền mua 60% + cổ tức CP 7% CHƯA thực hiện; với k=1 (NPV0, luật 20) giá trị cum của cổ đông thực hiện đủ quyền không đổi",
  "zone_high": 15564,
  "center_range": null,
  "price_ref": 9990,
  "price_date": "2026-11-09",
  "ex_basis_pending": {
   "trigger": "GDKHQ quyền mua 5:3 @10.000 (chưa có ĐKCC/giấy chứng nhận UBCKNN); sau đó GDKHQ cổ tức CP 7%",
   "n_shares_final": 739559976,
   "zone_low": 10711,
   "center": 11615,
   "zone_high": 12546,
   "rule4_threshold": 9873,
   "scenario": "phát hành đủ, k=1, CK 5 tỷ",
   "partial_TCH_only": {
    "zone_low": 10989,
    "center": 12060,
    "zone_high": 13164
   },
   "no_rights_div_only": {
    "zone_low": 11609,
    "center": 13055,
    "zone_high": 14546
   },
   "rule4_note": "ĐẠT chỉ khi k>=0,8207 (điểm hoà vốn trên cơ sở EX); trượt ở k=0,8",
   "k_sensitivity_center": {
    "0.8": 10924,
    "0.946": 11428,
    "1.0": 11615,
    "1.024": 11698
   },
   "warning_governance": "NQ 06/NQ-HĐQT 21/07/2026: vay tối đa 100 tỷ từ TCH (đã đọc, blq.png); tiền thu vào NĐL qua chuỗi bên liên quan; HĐQT tự phân bổ cp dư @10.000 khoá 1 năm; kịch bản chỉ TCH: HHS cần 1.080,6 tỷ vs tiền mặt Q3 181,9 tỷ (thiếu ~898,7 tỷ)"
  },
  "verdict_label": "DƯỚI vùng (headline CK holding 0% — quy ước errata r3 chờ user phán xử): giá 9.990 (BQ 09/11) < P10 cum 12.422; cơ sở ex dự kiến TERP 9.346 < P10 ex 10.711 (tâm/TERP 1,243 vs tâm/giá cum 1,397). Nhãn bền tới k=0,8; k=0,946 (75,41% NĐL công ty nêu, −141 tỷ) tâm ex 11.428 vẫn DƯỚI. Luật sổ ĐẠT CÓ ĐIỀU KIỆN (ex: k>=0,8207; trượt ở k=0,8; điều kiện trượt §2.5: pha loãng 60% @thị giá). forensic_flags EXCLUDE ⇒ loại khỏi candidate plan. Song song CK holding 27%: cum tâm 10.761 (giá −7,2% dưới tâm) → ex tâm 8.808, TERP +6,1% TRÊN tâm, TRONG (≤P90 10.237). WARNING tăng vốn + quản trị bên liên quan (luật 29/10).",
  "skeptic_status": "r4 (10/11) không đổi mô hình — biến đổi pha loãng trên phân phối r3 đã CONFIRMED; CHỜ Mike skeptic/kiểm cơ học",
  "source_file": "agents/Taylor/research/dd_dilution_update_20261110/HHS_r4.md",
  "evidence": [
   {
    "file": "agents/Taylor/research/dd_dilution_update_20261110/HHS_r4.md",
    "quote": "| CUM, **không** áp CK lên phần tiền (= phân phối r3 nguyên bản, dùng cho ledger) | 13.969 | 12.422 | 13.917 | 15.564 | 9.990 (BQ 09/11); DNSE 10/11 10:46 khớp 10.000 — theo skeptic là lệnh đơn 50 cp, tôi CHƯA lưu bản ghi nên ledger dùng 9.990 | **DƯỚI vùng** | ĐẠT (11.874) |",
    "fields": [
     "center",
     "zone_low",
     "zone_high",
     "price_ref"
    ]
   },
   {
    "file": "agents/Taylor/research/dd_dilution_update_20261110/HHS_r4.md",
    "quote": "| **EX cả hai đợt**, phát hành đủ, k = 1, 739,56 tr cp | **11.615** | 10.711 | 11.584 | 12.546 | TERP 9.346 (từ 10.000) | **DƯỚI vùng** | ĐẠT (9.873) |",
    "fields": [
     "ex_basis_pending"
    ]
   },
   {
    "file": "agents/Taylor/research/dd_dilution_update_20261110/src_hhs/nq_dhdcd_2026.pdf",
    "quote": "TT08: 259.191.580 cp, giá chào bán 10.000 đồng/cổ phiếu, tỷ lệ 5:3; mục đích mua 260.000.000 cp NĐL @10.000. TT09: 48.382.428 cp = 7% trên 691.177.548 cp, phát hành sau khi kết thúc chào bán",
    "fields": [
     "ex_basis_pending"
    ]
   }
  ],
  "assumptions_file": "agents/Taylor/research/dd_dilution_update_20261110/calc/LOCK_md5.txt",
  "null_reason": "center_range: nguồn không cho khoảng tâm",
  "expires_on": "2027-03-01",
  "expires_basis": "dd_date+120 (mặc định); công cụ ghi đè bằng ngày công bố BCTC quý mới hơn đọc lúc chạy (PIT)",
  "notes": "Khi có GDKHQ quyền: công cụ/Mike phải chuyển sang ex_basis_pending (KHÔNG so giá ex với vùng cum). Giá chào bán = thị giá ⇒ quyền ~0 theo thị trường ⇒ bao phủ phụ thuộc TCH 58,31%. Tiền vào NĐL/I.14 (NPV0). forensic_flags exclude giữ nguyên. Giá ref 9.990 = đóng cửa BQ 09/11; DNSE 10/11 10:46 khớp 10.000 theo skeptic là lệnh đơn 50 cp (chưa lưu bản ghi).",
  "recorded_at": "<Mike điền lúc nhập>",
  "supersedes": "HHS@2026-11-01#3",
  "correction_reason": "Bổ sung 2 đợt tăng vốn chưa phản ánh (quyền mua 60% @10.000 NQ 01/NQ-ĐHĐCĐ 24/04 + NQ 07/NQ-HĐQT 26/08; cổ tức CP 7% TT09) — vùng cum giữ nguyên (k=1), thêm vùng ex chờ kích hoạt; giá tham chiếu giữ 9.990 (BQ 09/11)."
 },
 {
  "ticker": "SCL",
  "dd_date": "2026-10-29",
  "rev": 5,
  "bctc_quarter": "2026Q3",
  "zone_low": 17445,
  "center": 21339,
  "center_kind": "expected_weighted",
  "center_desc": "kỳ vọng trọng số lưới 108 kết cục r3, cơ sở EX-QUYỀN (44.836.815 cp (6.000.000 cp mới, 75 tỷ, TB 1368/TB-SCL), phát hành đủ), sau CK 5 tỷ",
  "zone_high": 25681,
  "center_range": null,
  "price_ref": 28000,
  "price_date": "2026-11-09",
  "verdict_label": "TRÊN vùng (>P90): giá EX 28.000 (GDKHQ 09/11) cao hơn P90 sau quyền +9,0% ở cỡ 5 tỷ, +5,1% ở sleeve 40tr (P90 26.651); cao hơn TERP 27.139 +3,2%. Luật sổ: KHÔNG đạt (ngưỡng 18.138)",
  "skeptic_status": "r4 (10/11) không đổi mô hình — chỉ đổi cơ sở cum→ex trên phân phối r3 đã CONFIRMED; CHỜ Mike skeptic/kiểm cơ học",
  "source_file": "agents/Taylor/research/dd_dilution_update_20261110/SCL_r4.md",
  "evidence": [
   {
    "file": "agents/Taylor/research/dd_dilution_update_20261110/SCL_r4.md",
    "quote": "| **CK 5 tỷ (cỡ ghi sổ)** | **21.339** | 17.445 | 20.964 | **25.681** | **28.000** (BQ đóng cửa 09/11) | **+9,0%** | +31,2% | **TRÊN** | KHÔNG (ngưỡng 18.138) |",
    "fields": [
     "center",
     "zone_low",
     "zone_high",
     "price_ref"
    ]
   },
   {
    "file": "agents/Taylor/research/dd_redo_20261105/SCL/calc_r3/model_scl_r3_out.json",
    "quote": "post_rights.ck5ty.center_post 21339.47; P_post.p10 17444.9; P_post.p90 25681.2",
    "fields": [
     "center",
     "zone_low",
     "zone_high"
    ]
   }
  ],
  "assumptions_file": "agents/Taylor/research/dd_dilution_update_20261110/calc/LOCK_md5.txt",
  "null_reason": "center_range: nguồn không cho khoảng tâm",
  "expires_on": "2027-02-26",
  "expires_basis": "dd_date+120 (mặc định); công cụ ghi đè bằng ngày công bố BCTC quý mới hơn",
  "notes": "Cơ sở EX (từ 09/11): KHÔNG so với giá cum trước 09/11. Sleeve 40tr: tâm 22.146 · P10 18.104 · P90 26.651. ESOP 0,92tr đã trong 38,84tr; ESOP '2,1%' announced 07/05 không xác định được nguồn (độ nhạy tâm 21.106). BQ ticker.Close chưa điều chỉnh lùi cho quyền (06/11 Close=Price=29.400).",
  "recorded_at": "<Mike điền lúc nhập>",
  "supersedes": "SCL@2026-10-29#4",
  "correction_reason": "GDKHQ quyền mua 15,4453% @12.500 đã xảy ra 09/11 ⇒ chuyển cơ sở cum (22.791/27.803 @29.400) sang ex (21.339/25.681 @28.000); mô hình không đổi."
 }
]
```
