# ĐỀ XUẤT sổ chấm dự báo chu kỳ — CHƯA TẠO, CHƯA GHI

> Job `Taylor_20261026_045054`. File này chỉ là định dạng đề xuất. Không ghi vào `kb/`. Mike/user duyệt rồi mới tạo.

**Đường dẫn đề xuất:** `mike/kb/data_registry/fundamentals/dd_cycle_reads.md`
(cùng kiểu `market-state/livermore_reads.md`: một nguồn = một file, append-only). Phương án dự phòng nếu không
muốn đưa vào data_registry: `mike/kb/projects/dd-cycle-forecasts.md`.

**Người ghi:** Mike (orchestrator) chép entry từ mục F + `BLIND_ATTESTATION` của mỗi DD. Người viết DD chỉ trả
entry, không tự ghi (giống Livermore). Chấm: Mike, tại `due_date`, chỉ dựa vào `source` đã khai.

## Header file (frontmatter đề xuất)
```
---
kind: registry
status: CANDIDATE
source: khối CHU KỲ của DD sleeve discretionary (mẫu agents/Taylor/research/dd_template_20261026/TEMPLATE.md)
group: fundamentals
writer: Mike ghi; người viết DD chỉ trả entry
role: Sổ append-only các dự báo ngành/biên khoá trước khi đọc BCTC quý mới nhất; chấm sau 2–3 quý.
---
```

## Luật sổ
1. **Append-only.** Không sửa `forecast`. Chỉ được điền `result` và `outcome` một lần khi chấm. Đính chính thì thêm
   dòng `note: ĐÍNH CHÍNH yyyy-mm-dd ...`, không xoá dòng cũ.
2. **Chỉ entry `blind: yes` tính vào cổng.** Entry `blind: no` vẫn ghi (để thấy kỷ luật có được giữ không) nhưng
   bị loại khỏi thống kê.
3. **Mỗi mã tối đa 1 entry mở.** Trong khi entry cũ chưa đến hạn, DD lại của cùng mã không được ghi dự báo mới (tránh
   N giả và tránh "đặt lại" khi thấy dự báo cũ sắp sai).
4. **N độc lập:** nhiều mã cùng ngành, cùng biến chi phối (vd 3 mã phân bón đều ăn theo giá S), cùng tháng tính là
   **1 sự kiện** khi chấm cổng. Cột `driver` dùng để gộp.
5. **Chấm** HIT / MISS / VOID theo `call`. Brier trên `p`. So với 2 baseline: **persistence** (chỉ báo giữ phía
   hiện tại) và **về trung vị 5 năm** (chỉ báo đi về phía trung vị của chính nó).
6. **Cổng đánh giá** (đề xuất, giống cổng giải thể Livermore): sau ≥ 12 sự kiện độc lập `blind: yes` đã chấm, xem
   khối chu kỳ có hơn CẢ HAI baseline (hit VÀ Brier) không. Thua ⇒ khối chu kỳ vẫn giữ làm kỷ luật so sánh, nhưng
   **cấm** viện dẫn "pha chu kỳ" như bằng chứng có sức dự báo trong verdict. Thắng ⇒ vẫn chỉ là ứng viên, cần
   quant-skeptic trước khi coi là edge.

## Định dạng entry
```
### CYC-<MÃ>-<yyyymmdd>
- as_of: yyyy-mm-dd
- created: yyyy-mm-ddTHH:MM+07:00
- report: agents/Taylor/research/dd_<MÃ>_<yyyymmdd>/REPORT.md
- cycle_block_md5: <md5>    cycle_block_commit: <hash>
- blind: yes | no            (no ⇒ lý do: đã đọc BCTC Q / đã đọc DD cũ / biết verdict)
- data_through_quarter: 20xxQ(n-1)
- industry_type: chu kỳ hàng hoá | chu kỳ cầu đầu tư | phân bổ chính sách | annuity hợp đồng | không chu kỳ
- driver: <biến chi phối, vd "spread DAP−S", "Qc/thủy văn", "giá đá ĐNB", "chuyển bay quốc tế TSN→LTH">
- phase_at_asof: ĐÁY | GIỮA-LÊN | ĐỈNH | GIỮA-XUỐNG | KHÔNG XÁC ĐỊNH
- margin_pctile_at_asof: <p biên gộp TTM> / <p biên LNST TTM>   window: 20xxQ1–20xxQn
- verdict_at_report: QUALIFY | AMBIGUOUS | NON      verdict_depends_on_cycle_block: yes | no
- forecast:
    - indicator: ...
    - source: ...
    - baseline: ...
    - call: ...
    - horizon: 20xxQm
    - due_date: yyyy-mm-dd
    - p: 0.xx
    - persistence: ...
    - void_if: ...
- result: CYC|<as_of>|<MÃ>|<call ngắn>|<p>      (dòng máy đọc, giống RESULT| của Livermore)
- outcome:                                       (để trống đến khi chấm: HIT|MISS|VOID, giá trị thực, ngày chấm, người chấm)
```

## Ví dụ minh hoạ (KHÔNG phải entry thật — viết sau khi đã đọc BCTC nên `blind: no`, không ghi vào sổ)
```
### CYC-DDV-20261026 (MINH HOẠ)
- blind: no (người viết đã đọc BCTC Q3/2026 và viết DD cũ)
- driver: spread DAP − lưu huỳnh
- phase_at_asof: GIỮA-XUỐNG (sốc chi phí đầu vào, giá bán vẫn cao)
- forecast:
    - indicator: biên gộp quý theo BCTC riêng DDV (LN gộp / DT thuần)
    - source: BCTC Q2/2027 DDV
    - baseline: 3,7% (Q3/2026, theo REPORT DDV)
    - call: < 8%
    - horizon: 2027Q2
    - due_date: (ngày công bố BCTC Q2/2027 + 10 ngày; chưa tra lịch)
    - p: (bỏ trống — minh hoạ)
    - persistence: < 8% (giữ phía hiện tại)
```
Ví dụ này cho thấy một điểm yếu: với chỉ báo đang ở xa ngưỡng, dự báo "giữ nguyên" trùng với baseline persistence
nên không chứng minh được gì. Dự báo có giá trị là dự báo **đảo chiều** so với persistence, hoặc có ngưỡng gần giá
trị hiện tại.
