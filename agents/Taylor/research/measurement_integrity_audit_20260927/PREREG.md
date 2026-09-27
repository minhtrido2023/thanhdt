# PREREG — Audit "lỗi đo cơ bản" toàn diện
job=Taylor_20260927_043544 · viết 2026-09-27 ~11:40 ICT · **TRƯỚC khi đọc bất kỳ kết quả nào**

## Vì sao có job này
custom30V lộ lỗi: chuỗi return của rổ park nhân `Close` (ĐÃ điều chỉnh) với `OShares` (đổi theo
quý) ⇒ cộng tăng trưởng số CP (~13,5%/năm) vào lợi nhuận. R3 28,86% → 24,38% CAGR. Merge
`a808a613`. Câu hỏi user: **"còn sai sót cơ bản về cách tính nào còn tồn tại không?"**

Đây là audit **ĐỌC-CHỈ**. Không sửa code. Sản phẩm = danh sách FAIL có bằng chứng dòng-code,
xếp theo mức ảnh hưởng.

## 6 bất biến cơ học (ký hiệu dùng trong bảng REPORT)
- **(a) RETURN-ADJ** — chuỗi return chỉ từ giá ĐÃ điều chỉnh (`Close`); không nhân/chia thêm số
  CP; không trộn `Close` với `Price` thô trong CÙNG một chuỗi return.
- **(b) HỆ QUY CHIẾU** — adj vs thô dùng đúng mục đích: return = adj; mcap/ADV/weight/notional =
  giá THÔ × số CP CÙNG NGÀY. (Ngược lại cũng là FAIL: dùng `Close` adj × OShares hôm nay làm mcap.)
- **(c) KHÔNG ĐẾM 2 LẦN CORP-ACTION** — test "holder tổng hợp": P&L của người giữ nguyên cổ phần
  qua 1 sự kiện (cổ tức tiền / CP thưởng / tách / quyền mua) phải ≈ 0 net. Cấm cộng cổ tức lên
  chuỗi vốn đã dùng giá adj.
- **(d) SỐ CP ĐÚNG NGÀY** — `OShares`/shares lấy theo ex-date (hoặc as-of PIT), KHÔNG phải ngày
  quý/ngày restate; nếu xấp xỉ thì phải khai rõ sai số.
- **(e) KHÔNG LOOK-AHEAD** — chuỗi weight/level/gate as-of PIT: mọi cột dùng để chọn/cân ở ngày t
  phải khả dụng tại t (gồm `Release_Date`, universe membership, restate).
- **(f) ĐƠN VỊ / TẦN SUẤT** — CAGR theo thời gian LỊCH (không theo số phiên); annualize đúng
  (√252 cho daily, √12 cho monthly); bps vs % không lẫn; VND vs tỷ VND không lẫn.

## Danh sách chuỗi sẽ quét (khai TRƯỚC)
Mỗi dòng = 1 "chuỗi" (một đường đi từ dữ liệu thô → một con số được báo cáo/dùng để quyết định).

### Nhóm 1 — rổ park custom30V (chân đã sửa + chân weight CHƯA quét)
1. `custom_basket.py` chân RETURN (sau fix `1b89881b`) — tái kiểm (a)(c)(f).
2. `custom_basket.py` chân WEIGHT/selection (`BASKET_WT`, ey/mcap/liq) — (b)(d)(e).
3. `custom_basket.py` `build_pit()` vs `build()` — (e).

### Nhóm 2 — engine R3
4. `pt_v23_audit_2014.py` ledger BAL — (a)(b)(c)(f).
5. `pt_v23_audit_2014.py` ledger LAG — (a)(b)(c)(f).
6. `pt_v23_audit_2014.py` parking leg (xe custom30V) — (a)(c).
7. `pt_v23_audit_2014.py` gated-overflow — (e)(f).
8. `pt_v22_dt5g.py` (engine CAPIT/park) cùng 6 bất biến.
9. Chuỗi NAV tổng + self-check 0 VND — (c)(f).
10. Chuỗi ADV/thanh khoản dùng để cap size — (b).

### Nhóm 3 — thống kê hậu kỳ
11. `bootstrap_nav.py` — (f) + đơn vị chuỗi đầu vào.
12. `dsr_pbo_annex.py` — (f) + N độc lập.
13. `regime_size_overlay.py` — (e)(f).
14. `edge_health_monitor.py` (gồm chân LAG edge health) — (a)(e).

### Nhóm 4 — rating & báo cáo tiền thật
15. `rating_8l_history.py` — PE/PB/PCF/PS dùng `Price` hay `Close`, OShares nào — (b)(d)(e).
16. `mike/bin/dividend_adjusted_return.py` — (c) là trọng tâm.
17. `mike/bin/nav_period_returns.py` — (c)(f) + mốc inception.
18. `mike/bin/compute_active_nav.py` — (b)(c) + off-book/egg.
19. `backtest_recovery_alloc.py` + `backtest_recovery_alloc_2011.py` (2 file backtest_* DUY NHẤT
    còn được trích trong `data/results_registry.md`).

## Quy tắc phán (khai trước để không co giãn sau)
- **FAIL** = có dòng code cụ thể vi phạm bất biến, ảnh hưởng tới một con số được BÁO CÁO hoặc
  dùng để QUYẾT ĐỊNH.
- **FAIL-hiển-thị** = vi phạm nhưng chỉ ảnh hưởng nhãn/hiển thị, không ảnh hưởng số quyết định.
- **PASS** = đọc được dòng code chứng minh bất biến được giữ.
- **N/A** = chuỗi này không có khái niệm đó.
- **CHƯA XÁC MINH** = không đọc đủ để phán → ghi thẳng, KHÔNG suy từ tên hàm.
- Với mỗi FAIL: đo độ lớn bằng 1 chân đối chứng nếu RẺ (≤1 lần chạy). Không rẻ ⇒ ghi
  "chưa đo, cần job riêng" — KHÔNG ước lượng bằng trực giác.
- Không suy từ tên biến/tên hàm. Mọi phán quyết kèm `file:line`.

## Giới hạn đã biết trước (sẽ ghi lại trong REPORT)
- Không quét: `trading_bot/` (đường thực thi live, thuộc Mafee), `webui/`, ~44 file `backtest_*.py`
  KHÔNG được registry trích (legacy, không ai đọc số).
- Không chạy lại backtest đầy đủ (tốn giờ); chỉ chân đối chứng rẻ.
