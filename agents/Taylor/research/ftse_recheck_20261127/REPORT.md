# FTSE nâng hạng — kiểm lại mốc 2026-11-26 (làm ngày 27/11, job Taylor_20261127_012110)

**Kết luận: GIỮ NGUYÊN, không đổi tham số. Điều kiện mở prereg KHÔNG chạm.**
- Sau sự kiện: **48 phiên** (2026-09-21 → 2026-11-26; 24/11 nghỉ lễ theo `trading_bot/vn_market.py:42-44`). Trước: 60 phiên. N = 1 sự kiện.
- **1/24 đại lượng ngoài dải**: `T2_top60_pool_names_changed` = 4 mã đổi, dải 5 … 14,75 (66 mốc giả). Lệch về phía **ít** thay đổi hơn thường lệ: pool thanh khoản ổn định hơn, không phải xáo trộn.
  Ra DPM, MBS, SSB, VCK; vào BAF, DGW, FRT, MCH. Giá trị 4 vẫn nằm trong dải 12 mốc mùa vụ (3 … 22).
- Điều kiện mở prereg cần ngoài dải ở **mốc 60 phiên VÀ** mốc kế tiếp. Mốc này mới 48 phiên ⇒ chưa thể chạm.
  Mốc 60 phiên: dữ liệu tới khoảng 14/12 (ước lượng theo lịch ngày làm việc), khớp mốc 15/12 đã đặt.
- 23 đại lượng còn lại không ra ngoài dải (trong đó 1 đại lượng không kiểm được, xem ¹). "Trong dải" không chứng minh là không có đổi cấu trúc: dải rất rộng.

## Bảng 24 đại lượng
Cột "10/13" = số công bố gốc (cắt 10-12, 16 phiên sau, 198 mốc giả; khối ngoại 121/116). "Nay" = cắt 11-26, 48 phiên sau, 66 mốc giả (khối ngoại 40/38).
Dải đổi giữa hai lần vì cửa sổ sau dài hơn (16 → 48). Δ là hiệu số, trừ các đại lượng dạng tỷ lệ (`*_univ_ma200_mean`, `n_in_universe`, `univ_turnover`, `adv_ratio`, `cap_change*`) là % thay đổi (0,10 = 10%).
`T2_top60_pool_names_changed`: "trước → sau" là 60 → số mã còn lại; Δ = số mã đổi. `T3_cap_change_median`: "trước → sau" là trần trung vị (tỷ).

| Đại lượng | 10/13: trước → sau | Δ | Dải p5…p95 (10/13) | Nay: trước → sau | Δ | Dải p5…p95 (nay) | phân vị | Nay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1_b200_mean | 0.2540 → 0.2548 | 0.0008 | -0.1623 … 0.1981 | 0.2539 → 0.2470 | -0.0069 | -0.1541 … 0.2247 | 57.6 | trong |
| T1_univ_ma200_mean | 360.7 → 347.1 | -0.0377 | -0.0740 … 0.1217 | 360.7 → 339.3 | -0.0593 | -0.0908 … 0.1688 | 12.1 | trong |
| T1_guard_true_frac | 0.0000 → 0.0000 | 0.0000 | -0.6096 … 0.6717 | 0.0000 → 0.0000 | 0.0000 | -0.6667 … 0.6604 | 43.9 | trong |
| T1_corr_top30 | 0.3888 → 0.1661 | -0.2227 | -0.2860 … 0.3137 | 0.3889 → 0.3194 | -0.0694 | -0.2587 … 0.3287 | 30.3 | trong |
| T1_foreign_share_median | 0.1404 → 0.1428 | 0.0024 | -0.0324 … 0.0392 | 0.1402 → 0.1451 | 0.0049 | -0.0326 … 0.0402 | 57.5 | trong |
| T1_foreign_net_bn_median | -273.8 → -624.3 | -350.4 | -527.7 … 545.0 | -273.8 → -468.3 | -194.5 | -408.5 … 524.4 | 20.0 | trong |
| T2_n_in_universe_mean | 363.2 → 348.5 | -0.0404 | -0.0628 … 0.1080 | 363.2 → 341.6 | -0.0593 | -0.0824 … 0.1473 | 9.1 | trong |
| T2_n_adv_ge_10bn | 121.0 → 123.0 | 2 | -32 … 34.15 | 121.0 → 127.0 | 6 | -33.75 … 36.5 | 62.1 | trong |
| T2_n_adv_ge_1bn | 257.0 → 240.0 | -17 | -43.3 … 46 | 258.0 → 247.0 | -11 | -55.5 … 61.5 | 39.4 | trong |
| T2_univ_turnover_bn_day | 15,109.5 → 13,203.6 | -0.1261 | -0.3426 … 0.5928 | 15,111.2 → 12,817.4 | -0.1518 | -0.3264 … 0.8195 | 31.8 | trong |
| T2_top60_pool_names_changed | 60 → 57 | 3 | 2 … 7 | 60 → 56 | 4 | 5 … 14.75 | 0.0 | **NGOÀI** |
| T2_top60_adv_ratio_median | 115.6 → 106.3 | -0.2104 | -0.3865 … 0.5279 | 115.6 → 110.3 | -0.1415 | -0.3800 … 0.6569 | 47.0 | trong |
| T2_top10_turnover_share | 0.3656 → 0.3524 | -0.0132 | -0.0451 … 0.0724 | 0.3656 → 0.3291 | -0.0365 | -0.0746 … 0.0721 | 10.6 | trong |
| T2_ftse27_turnover_share | 0.5289 → 0.4844 | -0.0445 | -0.0582 … 0.0736 | 0.5289 → 0.4833 | -0.0455 | -0.0577 … 0.0895 | 9.1 | trong |
| T2_ftse6_turnover_share | 0.2024 → 0.1780 | -0.0244 | -0.0373 … 0.0397 | 0.2024 → 0.1628 | -0.0395 | -0.0442 … 0.0403 | 6.1 | trong |
| T3_quality_set_n | 9 → 8 | 0.0000 | 0.0000 … 0.0000 | 9 → 11 | 0.0000 | 0.0000 … 0.0000 | 0.0 | không kiểm được¹ |
| T3_n_pass_2bn_floor_mean | 9.383 → 7.688 | -1.696 | -3.248 … 3.392 | 9.2 → 9.042 | -0.1583 | -3.677 … 3.493 | 50.0 | trong |
| T3_cap_change_median | 2.249 → 3.459 | -0.1016 | -0.3845 … 0.5225 | 2.249 → 2.182 | -0.0300 | -0.4849 … 0.9771 | 50.0 | trong |
| T3_cap_change_abs_median | — → — | 0.3237 | 0.1200 … 0.5793 | — → — | 0.3849 | 0.2023 … 0.9771 | 31.8 | trong |
| T3_frac_names_cap_stale_gt30pct | — → — | 0.5556 | 0.1950 … 0.7500 | — → — | 0.5556 | 0.3333 … 0.9040 | 27.3 | trong |
| T3_frac_names_cap_too_high_gt30pct | — → — | 0.3333 | 0.0000 … 0.7075 | — → — | 0.3333 | 0.0000 … 0.7644 | 47.0 | trong |
| fgn_share_of_ftse27_turnover | 0.1498 → 0.1441 | -0.0057 | -0.0602 … 0.0506 | 0.1498 → 0.1491 | -0.0007 | -0.0629 … 0.0393 | 57.9 | trong |
| fgn_net_ftse27_bn_day | -177.5 → -475.4 | -297.9 | -404.7 … 314.5 | -177.5 → -333.6 | -156.1 | -376.4 … 307.1 | 15.8 | trong |
| ftse27_share_of_all_foreign_trading | 0.5763 → 0.5064 | -0.0699 | -0.0787 … 0.0708 | 0.5763 → 0.5157 | -0.0606 | -0.0618 … 0.0510 | 5.3 | trong |

¹ `T3_quality_set_n`: `measure.py` ghi cứng cột Δ = 0, nên đại lượng này không bao giờ ra ngoài dải được. Mức thật: 9 → 11 mã (10/13: 9 → 8).

## Bối cảnh (extras của script, không thuộc 24 đại lượng, không có dải)
Nguồn `now/out_measure.txt`, `now/out_fgn27.txt`.
- DT5G (bảng `vnindex_5state_dt5g_live`): state 3 (NEUTRAL) ở cả 60 phiên trước và 48 phiên sau. Breadth guard bật 0 phiên ở cả hai. Breadth MA200 sau: min 0,1621, max 0,2917 (ngưỡng 0,50).
- GTGD/phiên: nhóm 27 mã FTSE −22,5% (7.992 → 6.195 tỷ); phần còn lại −7,0% (7.111 → 6.610 tỷ).
- Khối ngoại luỹ kế 48 phiên: toàn VNINDEX −39.748 tỷ, nhóm 27 mã −32.654 tỷ (gồm thoả thuận). 60 phiên trước: −17.001 / −10.893. Khác độ dài cửa sổ.
- `ftse27_share_of_all_foreign_trading` ở phân vị 5,3, sát mép dưới nhưng còn trong dải.
- custom30V lấy rổ rebal **2026-11-05** (script lấy rổ mới nhất ≤ ngày cắt). Nhãn "(08-05)" trong `now/out_measure.txt` là chữ ghi cứng, SAI cho lần chạy này. So với rổ 08-05: ra DDV, DGC, PAN, VGC, VIX, VND; vào HDG, HHV, HVN, NAB, OCB, POW.

## Chân control (cắt 2026-10-12) so với `results_table.csv` cũ
**Không khớp từng số: 86 ô khác. Nhưng 0 cờ `outside_5_95` đổi, số mốc giả giữ nguyên, lệch phân vị lớn nhất 1,65 điểm.** 3 đại lượng khối ngoại 27 mã in ra trùng bản cũ.
Lệch lớn nhất nhìn thấy: `T1_univ_ma200_mean` p5 −0,0740 → −0,0646, seas_max 0,1101 → 0,0805; `T3_n_pass_2bn_floor_mean` trước 9,38 → 9,20 (Δ −1,70 → −1,51).

Đối chiếu file đầu vào cũ (còn trong git) với bản kéo lại (`control/orig_*` vs `control/*`):
| Đầu vào | Kết quả |
|---|---|
| `custom30v_members.csv` | cùng 30 mã, cùng trọng số; chỉ khác thứ tự dòng |
| `dt5g_live.csv` | bản cũ thừa dòng 10-13 (ngoài ngày cắt) |
| `foreign_vnindex_vndirect.csv` | bản cũ thiếu 2022-08-30 và 08-31, thừa 10-13; các dòng khác trùng |
| `fgn_stock/*` | bản cũ thừa 10-13; buy/sell/net các dòng chung trùng 100%. Vì vậy phần luỹ kế theo mã (extras) lệch: bản cũ cộng cả 10-13 |

Đọc được từ đó:
- Hai ngày 2022 bị thiếu ở bản cũ là một khác biệt đầu vào thật của các đại lượng khối ngoại toàn thị trường. Chưa tách riêng phần đóng góp của nó.
- Dữ liệu khối ngoại các ngày 2026 trùng nhau, mà tỷ trọng khối ngoại ngày 09-21 đổi 19,1% → 19,0%. Đầu vào còn lại của phép chia là GTGD toàn thị trường lấy từ `tav2_bq.ticker` ⇒ bảng này trả số khác so với lúc đo 10/13.
- `universe_pit`/`ticker`/`ticker_prune` đều có `lastModifiedTime` 2026-11-26. Ví dụ lệch: breadth 09-22 0,2890 → 0,2861 (mẫu số 346 không đổi); ADV20 của VNM, SIP, NTC đổi nhẹ.
- **Không đo được**: dòng/mã nào trong BQ đã đổi và vì sao. Ba file parquet của lần 10/13 không có trong commit gốc (danh sách `git ls-tree` không có), nên không so từng dòng được.

## Mục không đo được
| Mục | Lý do / lỗi thật |
|---|---|
| Vốn thụ động vs chủ động trong khối ngoại | script không có nguồn theo loại nhà đầu tư; phiên này không thử nguồn mới (bản 10/13 ghi FiinPro-X hết hạn 09-28) |
| Khối ngoại trước 2018-08-30 | VNDirect trả dòng sớm nhất 2018-08-30 |
| Hành vi breadth guard và ngưỡng state | guard bật 0/48 phiên, 0 chuyển state |
| So 60 phiên vs 60 phiên | mới có 48 phiên |
| 90 mã FTSE Micro Cap | không có danh sách |
| Rổ 27 mã theo văn bản gốc FTSE | vẫn dùng danh sách cũ (nguồn thứ cấp CafeF), chưa đối chiếu |

Lỗi gặp khi chạy lại, đã sửa trong `pull.py`: `KeyError: 'totalPages'` (VNDirect chỉ trả `totalPages` ở trang 1); `AssertionError ('TCX','2018',0,0)` (TCX không có dữ liệu giai đoạn 2018-2022 — do chốt chặn tôi thêm, đã nới cho chunk 2018).

## Dòng đã sửa
`measure.py`, `measure_fgn27.py`: **không sửa byte nào** (`cmp` với bản git). `pull.py` (diff đầy đủ dưới): ngày cắt qua biến `END`; chặn `END` cho custom30V, DT5G, khối ngoại; urllib → curl (README cũ ghi urllib bị 403); sửa phân trang; **thêm** bước kéo `fgn_stock` (script gốc không có bước này).

```diff
--- orig_pull.py	2026-11-27 08:21:20.130131523 +0700
+++ pull.py	2026-11-27 08:23:48.353282329 +0700
@@ -1,8 +1,8 @@
 """Pull panels for FTSE-upgrade re-validation (READ-ONLY, measurement only). Job Taylor_20261013_114456."""
-import json, urllib.request
+import json, os, subprocess, urllib.request
 import pandas as pd
 from google.cloud import bigquery
-PRJ = "lithe-record-440915-m9"; END = "2026-10-12"   # universe_pit max date at run time
+PRJ = "lithe-record-440915-m9"; END = os.environ["END"]
 c = bigquery.Client(project=PRJ)
 q = lambda s: c.query(s).result().to_dataframe()
 # A. PIT universe panel (tav2_bq.ticker JOIN universe_pit per day) — same join as macro_state_live._breadth_sql
@@ -19,18 +19,28 @@
 q(f"""SELECT p.time, p.ticker, COALESCE(p.Price,p.Close)*p.Volume AS turn, p.ROE_Min5Y, p.ROIC5Y, p.FSCORE
 FROM tav2_bq.ticker_prune AS p WHERE p.time BETWEEN DATE '2013-06-01' AND DATE '{END}'""").to_parquet("panel_capit_prune.parquet")
 # D. custom30V current members
-q("""SELECT c.ticker, c.weight, c.liq_rank, c.rebal_date FROM tav2_bq.custom30v_8l AS c
-WHERE c.rebal_date=(SELECT MAX(c2.rebal_date) FROM tav2_bq.custom30v_8l AS c2)""").to_csv("custom30v_members.csv", index=False)
+q(f"""SELECT c.ticker, c.weight, c.liq_rank, c.rebal_date FROM tav2_bq.custom30v_8l AS c
+WHERE c.rebal_date=(SELECT MAX(c2.rebal_date) FROM tav2_bq.custom30v_8l AS c2 WHERE c2.rebal_date<=DATE '{END}')""").to_csv("custom30v_members.csv", index=False)
 # E. DT5G live state
-q("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s WHERE s.time>='2014-01-01' ORDER BY s.time""").to_csv("dt5g_live.csv", index=False)
+q(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s WHERE s.time BETWEEN '2014-01-01' AND '{END}' ORDER BY s.time""").to_csv("dt5g_live.csv", index=False)
+def get(url):   # curl: urllib gets HTTP 403 from VNDirect
+    return json.loads(subprocess.check_output(["curl", "-sSf", "-m", "60", "-A", "Mozilla/5.0", "-H", "Referer: https://dstock.vndirect.com.vn/", url]))
 # F. foreign flow VNINDEX (VNDirect finfo, depth 2018-08-30; includes put-through blocks)
-rows, page = [], 1
+rows, page, total = [], 1, None
 while True:
     url = ("https://api-finfo.vndirect.com.vn/v4/foreigns?q=code:VNINDEX~tradingDate:gte:2018-01-01"
            f"&sort=tradingDate:asc&size=1000&page={page}")
-    r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Referer": "https://dstock.vndirect.com.vn/"}), timeout=40))
+    r = get(url)
     rows += r["data"]
-    if page >= r["totalPages"]: break
+    total = total or r["totalPages"]   # API now returns totalPages on page 1 only
+    if page >= total: break
     page += 1
-pd.DataFrame(rows).to_csv("foreign_vnindex_vndirect.csv", index=False)
+pd.DataFrame(rows).query("tradingDate <= @END").to_csv("foreign_vnindex_vndirect.csv", index=False)
+# G. per-stock foreign flow, 27 FTSE names (fetch step was not in the original script)
+os.makedirs("fgn_stock", exist_ok=True)
+for t in json.load(open("../orig_meta.json"))["ftse27"]:
+    for tag, flt in [("2018", "tradingDate:gte:2018-01-01~tradingDate:lte:2022-09-02"), ("2022", f"tradingDate:gte:2022-09-05~tradingDate:lte:{END}")]:
+        r = get(f"https://api-finfo.vndirect.com.vn/v4/foreigns?q=code:{t}~{flt}&sort=tradingDate:asc&size=1100&page=1")
+        assert r["totalPages"] <= 1 and (r["data"] or tag == "2018"), (t, tag, r["totalPages"], len(r["data"]))
+        json.dump(r, open(f"fgn_stock/{t}_{tag}.json", "w"))
 print("ok", len(rows))
```

## Tái lập
`bash run.sh` (control + nay) → `python compare.py` → `python make_report.py`. Bản gốc: `orig_*` (lấy bằng `git show 60fe58b82^:…`). Chưa commit.
