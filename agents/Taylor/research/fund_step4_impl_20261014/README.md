# Quỹ mở bước 4 phần 2 — CÀI ĐẶT (job Taylor_20261014_060642, 2026-10-14)

Nhánh `feat/fund-step4-benchmark-20261014` (worktree `agents/Taylor/wt-step4-1014`), **CHƯA merge, CHƯA cài cron,
data/ thật KHÔNG đổi**. Đặc tả: `../fund_step4_20261014/SPEC.md`; quyết định user Q1–Q10 (2026-10-14): mặc định,
riêng Q2 = cột có cổ tức hiển thị `tr_net` (sau thuế 5%), `tr_gross` vẫn lưu, cờ `data/benchmark/benchmark_config.json`.

## Commit (theo SPEC § Thứ tự làm)
| Bước | Commit | Nội dung |
|---|---|---|
| 1 | `b58064f4f` | A1–A4: `vnindex_total_return.py` (chuỗi có cổ tức, cổng G1–G8), `hose_membership_refresh.py`, selfcheck 63 |
| 2 | `a51b7cb18` | B1–B3: `nav_sleeve.py` (chuỗi "phần bot quản lý", đề xuất dòng tiền, cổng S1–S7), selfcheck 37 |
| 3 | `7aeae5999` | `nav_period_returns.py`: khối `benchmark` mỗi kỳ (mốc = dòng sổ kỳ — Q1; cờ Q2), `--sleeve bot` (rc=3 khi chưa có số); selfcheck 56 |
| 4 | `461dd1077` | `period_table_32.py` (render bảng 3.2 + `check_report`), `report_delivery_gate._check_benchmark_table`; selfcheck 39 |
| 5 | (commit này) | CHỈ SOẠN: `proposed_kb/` — registry, cron, thư bq_admin (Q10), bổ sung §31 |

## Bằng chứng (MEASURED)
- **Số danh mục giữ nguyên từng byte**: `byte_proof.sh` — CLI master (sandbox `/tmp/step4_ctl`, md5 code = `git show
  master:`) vs nhánh (`/tmp/step4_sbx`) trên CÙNG bản sao dữ liệu thật, 2 TK × 6 ngày: 11/11 cặp có số BẰNG từng byte sau
  khi bỏ khối `benchmark`; ZaloPay 07-03 rc=1 ở cả hai (trước mốc).
- **Khớp nguyên mẫu**: chuỗi b ZaloPay 06/07→13/10 = **−0,790%**, mốc 525.365.567, dòng vào 76.000.000 (= `zalopay_bot_series.py`);
  chuỗi có cổ tức: 2023 y=1,680 · 2025 1,623 · 07-01→10-13 giá −7,915 / gộp −7,276 / ròng −7,308 (= `tr_build.py`, chênh 0,64).
- **Q1**: bảng ZaloPay weekly 10-09 render lại: VN-Index giá "từ khi bắt đầu" −5,88% (mốc 06/07) thay −6,82% (03/07 trong
  báo cáo đã gửi); chênh +0,97pp thay +1,91pp — đúng con số README phần 1. `e2e/step4_t32_*.md`.
- **Selfcheck khép kín**, mỗi cái chạy dưới `env -u TZ`, `Pacific/Kiritimati`, `America/Los_Angeles`: vnindex 63, nav_sleeve 37,
  nav_period_benchmark 56, period_table_32 39 — PASS.
- **Mutation** (`mutants.py`, TZ gỡ): **58/58 mutant chết** (A1–A20, B1–B17, C1–C10, D1–D11) — `mutants_final.txt`.
- **§23 quét rộng** (đụng `nav_period_returns.py` + `report_delivery_gate.py`): 16 selfcheck phụ thuộc, nhánh vs worktree
  master tạm (`e2e/step4_sweep_{branch,master}.txt`) — kết quả trùng nhau. `report_delivery_ledger_selfcheck` FAIL 5 ca ở
  CẢ HAI (chạy từ worktree ⇒ ca "ROOT = cây canonical"); ở cây canonical master 40/40 ⇒ lỗi môi trường, không do nhánh.
  `failopen_batch1_selfcheck` cần git ⇒ chạy trong worktree: 39 PASS.
- data/ thật: md5 `nav_history_*.csv` + `account_cash_flows.json` trước/sau quét — không đổi.

## Hành vi cổng giao báo cáo sau merge (cần biết TRƯỚC khi merge)
- Weekly/monthly SpaceX + ZaloPay: khi `data/benchmark/vnindex_tr_daily.csv` ĐÃ tồn tại, bảng 3.2 định dạng cũ (1 cột
  VN-Index) bị **CHẶN**. Thứ tự rollout đúng: merge → dựng chuỗi (`--update`) → cập nhật prompt/mẫu soạn weekly theo §31
  bổ sung (`period_table_32.py`) → mới bật cron. Chuỗi chưa có ⇒ chỉ WARN.
- Cổng gọi `nav_period_returns.py` của **cây canonical** (cùng chỗ cổng period-return cũ) ⇒ phải merge trước khi có hiệu lực.

## Chưa làm / chưa kiểm được
- So sánh SpaceX ↔ ZaloPay cùng cửa sổ từ 06/07 (báo cáo tháng, SPEC B4): CLI chưa có cờ mốc tuỳ chọn — chưa cài.
- Biểu đồ "lợi nhuận lũy kế so với VN-Index" thêm đường có cổ tức (SPEC A5) — chưa cài (`report_charts.py`).
- `hose_membership_refresh.py` chỉ in diff ra log, chưa post Trading Daily (SPEC A3).
- `sleeve_scope.json` / `sleeve_transfers.json` thật chưa tạo; bản ghi cổ tức DGC trong sandbox mang `confirmed_by: SANDBOX`
  — cần user xác nhận thật (Q6) trước khi dựng chuỗi b trên cây thật.
- Số "5 phiên" provisional→sealed vẫn là đề xuất, chưa đo độ trễ DIV (SPEC § Chưa kiểm được).
- Không chạy qua `deliver()` thật (Discord/email) — chỉ gọi `_check_benchmark_table` trực tiếp + kiểm vị trí gọi trong `deliver()`.
