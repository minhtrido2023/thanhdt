#!/usr/bin/env python3
"""One-off: trim kb/current_ops.md + kb/canonical.md by MOVING line ranges verbatim to
kb/projects/*.md (job Wags_20261008_133659). Spec is keyed to the line numbers of master
ea5c066d; the script asserts the source md5 so it cannot silently run on a drifted file.

Ops per source file, in order, must cover every line exactly once:
  ("keep", a, b)               lines a..b stay
  ("move", a, b, dest, title)  lines a..b go verbatim to kb/projects/<dest> under a section
  ("new", text)                pointer line(s) inserted in the source (verbatim fragments + path)
"""
import hashlib, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
JOB = "Wags_20261008_133659"
SRC_MD5 = {"kb/current_ops.md": None, "kb/canonical.md": None}  # filled by --print-md5 run

P = "kb/projects/"
TRIM = "context-pack-trim-20261008.md"
RND = "rnd-pipeline-tracker.md"
EGG = "dnse-trung-vang-legal-review-20260927.md"
DEP = "deposit-rate-effective-rate-20261001.md"
CORP = "corp-action-nav-chain-20260922.md"
MIA = "measurement-integrity-audit-20260927.md"
R3 = "r3-pin-history.md"
SCR = "screen-sort-direction-bug-20260927.md"
BRD = "breadth-tercile-axis-20260822.md"

NEW_HEADERS = {
    EGG: "# Trứng vàng DNSE — bản chất pháp lý (legal-vn 2026-09-27)\n"
         "> Chuyển nguyên văn từ `kb/current_ops.md` (trim context_pack 2026-10-08). Trạng thái quyết định\n"
         "> (user chốt 2026-10-05: Trứng vàng = tương đương tiền) vẫn ở `kb/current_ops.md`.\n",
    DEP: "# Effective rate (Big-4 12M vs CCTG) cho rating_8l/DCF — LIVE 2026-10-01\n"
         "> Chuyển nguyên văn từ `kb/current_ops.md` (trim context_pack 2026-10-08). Dòng tóm tắt hành vi\n"
         "> + trigger xem lại vẫn ở `kb/current_ops.md`.\n",
    CORP: "# Chuỗi corp-action NAV/ex-date 2026-09-22→09-28 — chi tiết vòng review\n"
          "> Chuyển nguyên văn từ `kb/current_ops.md` + `kb/canonical.md` (trim context_pack 2026-10-08).\n"
          "> Tên feature + ngày + commit + hành vi chính + mọi mục CÒN MỞ/CHƯA vá/CẦN USER vẫn ở file gốc.\n",
    MIA: "# Measurement integrity audit — bối cảnh mở cadence (2026-09-27)\n"
         "> Chuyển nguyên văn từ `kb/current_ops.md` (trim context_pack 2026-10-08). Lịch review quý vẫn ở file gốc.\n",
    R3: "# R3 / V2.4 — lịch sử pin, số SUPERSEDED, diễn giải đo lường\n"
        "> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Dải pin hiện hành\n"
        "> 23,37%…25,71%, neo DD −25,2%, luật cấm trích 1 số vẫn ở `kb/canonical.md`. Nguồn chuẩn: `data/results_registry.md`.\n",
    SCR: "# `*_screen.py` sort-direction bug (\"8L top-25\" = 25 mã xấu nhất) — vá 2026-09-27\n"
         "> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Mục CÒN PHẢI LÀM vẫn ở file gốc.\n",
    BRD: "# Trục 2 mặc định = breadth-tercile PIT — bằng chứng + định nghĩa tính chuẩn\n"
         "> Chuyển nguyên văn từ `kb/canonical.md` (trim context_pack 2026-10-08). Quy ước + ranh giới vẫn ở file gốc.\n",
    TRIM: "# Trim context_pack 2026-10-08 (job Wags_20261008_133659) — mục lục di chuyển\n"
          "> Quy tắc: CHỈ DI CHUYỂN nguyên văn, không viết lại sự thật. Mỗi khối dưới đây/ở file đích\n"
          "> mang tiêu đề `Chuyển từ kb/<file> L<a>-<b>` (số dòng theo master ea5c066d).\n"
          "> Kiểm: `python3 bin/kb_move_verify.py --base ea5c066d`.\n",
}

CO = "kb/current_ops.md"
CA = "kb/canonical.md"

SPEC = {
CO: [
    ("keep", 1, 2),
    ("move", 3, 4, TRIM, "header current_ops cũ"),
    ("new", "> Cập nhật lần cuối: 2026-10-08 (trim context_pack #5 — CHỈ DI CHUYỂN nguyên văn sang `kb/projects/*.md`, để pointer 1 dòng; mục lục `kb/projects/context-pack-trim-20261008.md`)."),
    ("keep", 5, 15),
    ("move", 16, 16, RND, "AlphaLens Paper (đã đóng)"),
    ("new", "- **AlphaLens Paper**: FPT/ACB/MBB/HDB — **ĐÃ ĐÓNG 2026-10-01** (user chọn A: không wire live) → `kb/projects/rnd-pipeline-tracker.md`."),
    ("move", 17, 30, EGG, "Trứng vàng — dòng trạng thái đầy đủ + đính chính bản chất 2026-09-27"),
    ("new", "- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,9tr / ZaloPay ~102,2tr (đo 09-27), đã cộng NAV tự động — KHÔNG phải `availableCash`. ⚠️ **RÚT VỀ TRONG NGÀY, KHÔNG phải T+1**. ⚠️ **KHÔNG phải tiền gửi ngân hàng**; lãi đo thật **8,543%/năm** và DNSE **tự khấu trừ TNCN trước khi trả** nên số đó đã là net. \"Tài khoản Không Ngủ\" là SẢN PHẨM KHÁC (trần 30 tỷ), đừng lẫn. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23."),
    ("new", "  ⚠️ **ĐÍNH CHÍNH BẢN CHẤT 2026-09-27 (legal-vn, bus `dnse-trung-vang-legal-review-20260927`) — KHÔNG phải repo.** khách **SỞ HỮU THẬT** trái phiếu niêm yết, **lưu ký tại VSDC**; **Việt Nam KHÔNG CÓ Quỹ bảo vệ nhà đầu tư**. Ba rủi ro THẬT + thuế + căn cứ: `kb/projects/dnse-trung-vang-legal-review-20260927.md`."),
    ("keep", 31, 33),
    ("move", 34, 35, EGG, "Trần đề xuất (chưa user chốt) — đã bị user chốt 2026-10-05 thay thế (dòng ✅ ở current_ops)"),
    ("keep", 36, 43),
    ("move", 44, 44, DEP, "rating_8l/DCF effective rate — dòng đầy đủ"),
    ("new", "- ✅ **rating_8l NEUTRAL tilt + chuỗi DCF (dcf_valuation, dcf_refresh_gate, custom30_yield_labels, due_diligence) DÙNG effective rate = max(Big-4 12M, CCTG 6M)** — LIVE trên WC main từ 2026-10-01 (merge `d87a6f89`, user duyệt 12:40, quant-skeptic vòng 2 CONFIRMED). **Fail-closed**: CCTG stale >45 ngày hoặc lỗi ⇒ cả 5 consumer rơi về Big-4 6,8% + WARNING (không phải ARMED). **Knob lùi**: env `DEPOSIT_RATE_CCTG_OVERLAY=0` (chỉ nhận đúng chuỗi \"0\"; lan tới mọi launcher source `wc_env.sh`, NGOẠI LỆ cron `dcf_refresh_gate` không source). `golive_recommend_v23.py:~991` (cổng CAPIT margin PIT, ngưỡng 9,0%) CỐ Ý vẫn Big-4-only — user chốt 2026-10-01 16:42: GIỮ Big-4, chỉ THÊM dòng hiển thị \"effective vs 9%\". **TRIGGER XEM LẠI đổi sang effective** = CCTG có ≥3 tháng dữ liệu + cron tuần chạy ổn, HOẶC effective ≥ ~8% (lúc đó dispatch Taylor đo khoảng cách CCTG−Big-4 lịch sử rồi quant-skeptic + user duyệt riêng). Tác động đo, dòng hiển thị PIT, follow-up: `kb/projects/deposit-rate-effective-rate-20261001.md`."),
    ("keep", 45, 67),
    ("move", 68, 68, CORP, "close_repair.py Layer 2 — dòng đầy đủ"),
    ("new", "- **close_repair.py — Layer 2 self-computed back-adjustment khi vendor backfill kẹt vĩnh viễn** (`MIKE_CLOSE_REPAIR` mặc định ON) — LIVE từ **2026-09-28**, commit `3c55c249`. Tự tính hệ số (xác nhận 2 nguồn độc lập, lệch <0,006%), fail-closed khi không đủ bằng chứng. Vòng review + VND/VNM: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("keep", 69, 70),
    ("move", 71, 71, CORP, "NAV corp-action gate v2 — nhánh cổ tức tiền"),
    ("keep", 72, 72),
    ("move", 73, 74, CORP, "NAV corp-action gate v2 — nhánh --from-raw / không giải thích được"),
    ("move", 75, 75, CORP, "Ex-date price-frame — dòng đầy đủ (sự cố gốc VPB)"),
    ("new", "- **Ex-date price-frame — KL và GIÁ phải CÙNG hệ quy chiếu** (`bin/exdate_frame.py` + wire vào `compute_active_nav.py` / `park_holdings.py` / `compute_park_trim.py` / `compute_jit_unpark.py`) — LIVE từ **2026-09-24**, commit `508bb607`, **3 vòng arch-review**. Sự cố gốc + nhánh định giá: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("move", 76, 76, CORP, "Ex-date price-frame — nhánh marketPrice"),
    ("keep", 77, 77),
    ("move", 78, 78, CORP, "Ex-date price-frame — rc=7"),
    ("keep", 79, 79),
    ("move", 80, 80, CORP, "Ex-date price-frame — selfcheck/replay"),
    ("keep", 81, 84),
    ("move", 85, 90, CORP, "dividend_adjusted_return qty_entitled — chi tiết vá, Q1, broker_qty (sau đã LIVE 4b59c6d1)"),
    ("keep", 91, 91),
    ("move", 92, 92, CORP, "Vendor mismatch ⇒ UNVERIFIED — dòng đầy đủ"),
    ("new", "- **LỆCH NGUỒN VENDOR ⇒ hạ UNVERIFIED + cảnh báo ĐÚNG NGƯỜI (Winston)** (`bin/dividend_adjusted_return.py` + `bin/report_return_gate.py` + `bin/vendor_mismatch_alert.sh` MỚI) — LIVE từ **2026-09-24**, commit `dc147859` và `6b751298` (nhánh con D1). Chỉ đạo user 2026-09-24: *\"vendor mismatch thì hạ về unverified rồi raise warning lên để tôi kêu winston xử lý.\"* Nhánh D1, hợp đồng dòng máy đọc 7 trường, đường phát lại, selfcheck: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("keep", 93, 93),
    ("move", 94, 99, CORP, "Vendor mismatch — D1, SANITY_REL, hợp đồng 7 trường, alert, đường phát lại, selfcheck"),
    ("move", 100, 105, CORP, "lookup_failed (206dd348) — dòng đầy đủ + chi tiết"),
    ("new", "  · **ĐÃ VÁ 2026-09-24, commit `206dd348`**: `bq_corp_action` NÉM LẠI exception thay vì `except Exception: return None`; nhãn **`lookup_failed`** tách khỏi `unavailable`."),
    ("move", 106, 107, CORP, "broker_qty gộp TỔNG lô + vá a56203f2 — dòng đầy đủ"),
    ("new", "  · **`broker_qty()` gộp TỔNG lô** — LIVE từ 2026-09-24, merge `4b59c6d1`. §21: **KHÔNG số công bố nào đổi**."),
    ("new", "  · **VÁ 2026-09-24, commit `a56203f2`**: gap test-only `report_return_gate.py:732` đã bịt. ⚠️ arch-reviewer tìm thêm 3 nhánh anh em CÙNG lớp vacuous-anchor CHƯA vá: `:723` (`cash_mismatch`), `:727` (`stock_leg_ignored`), `:737` (`reasons_present - {...}`) — chi tiết: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("keep", 108, 108),
    ("move", 109, 109, CORP, "Bẫy đường dẫn selfcheck — dòng đầy đủ"),
    ("new", "- **Bẫy đường dẫn selfcheck — MỌI selfcheck import module qua `load_module()`/`sys.path.insert` phải TỰ ĐỔI theo worktree, không hardcode canonical** (phát hiện 2026-09-24 khi verify C2, commit `a56203f2`). Ca gốc + bản vá: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("keep", 110, 112),
    ("move", 113, 116, CORP, "4 call-site còn lại — chi tiết Việc 4/3/1/2"),
    ("new", "  · **Việc 4 `report_return_gate.py:558-573` unmatched — APPROVED, LIVE, commit `569be662`.** · **Việc 3 `verify_account_snapshot.py:307` `broker_positions_from_raw()` — APPROVED vòng 2, LIVE, commit `96ee1bb8`+`7700582d`.** · **Việc 1 `discretionary_accumulation_inject.py` `broker_filled_qty()` — APPROVED vòng 2, LIVE, commit `5e6fb9af`+`642d4f5a`.** (⚠️ **Lưu ý docstring** — chưa sửa docstring (không chặn)) · **Việc 2 `discretionary_margin_gate.py` arm_price — APPROVED vòng 12, LIVE, merge `c5247def` (12 commit vòng 3→12, từ `26ef0c58` tới `bc22bed2`).** Chi tiết từng việc: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("move", 117, 117, CORP, "Sự cố phụ arm giả VPB — dòng đầy đủ"),
    ("new", "  ⚠️ **Sự cố phụ phát sinh khi verify vòng 5** (Mike tự gây ra): ghi lọt 1 arm giả (`ticker=VPB, note=\"seed\"`) vào LIVE canonical `data/discretionary_margin_arms.json` — **CẦN USER TỰ DỌN hoặc cấp quyền**, xem tin nhắn Discord thread này ~17:53 ICT 2026-09-24. Chi tiết: `kb/projects/corp-action-nav-chain-20260922.md`."),
    ("keep", 118, 122),
    ("move", 123, 128, MIA, "Lý do mở cadence"),
    ("new", "Lý do: bug custom30V double-count (`mcap = Close_adj × OShares`, −4,48pp CAGR) sống trong production nhiều tháng, KHÔNG bị bắt bởi self-check 0 VND LẪN quant-skeptic → `kb/projects/measurement-integrity-audit-20260927.md`."),
    ("keep", 129, 153),
],
CA: [
    ("keep", 1, 17),
    ("move", 18, 36, R3, "Dải pin — điểm thận trọng 25,24%, chân maturity 25,34%, min_age, giới hạn pin1M"),
    ("new", "  xấu, neo thực tế KHÔNG đổi. Điểm THẬN TRỌNG trong dải = chân `dep1m_21s` FIFO = **25,24%** — **GIỮ 25,24% làm số chính, KHÔNG re-pin**; ⚠️ **KHÔNG gọi là \"điểm thực tế\"**. Chân maturity, min_age, giới hạn `pin1M`: `kb/projects/r3-pin-history.md`."),
    ("keep", 37, 41),
    ("move", 42, 89, R3, "Pin quinquies SUPERSEDED, đính chính 24,42%, ba rail park 0,30, bối cảnh 24,42%, sửa lỗi đo 09-27, LAG_ADV_BASIS, số lịch sử khác vintage, MIXED-universe, fidelity liq<=0"),
    ("new", "  ✅ **Ba rail park ĐÃ ĐỒNG BỘ = 0,30** (commit mike `1f15139b`). Cổng cơ học `bin/park_rail_consistency_selfcheck.py` đọc giá trị 3 rail bằng AST, rc=1 khi lệch. ⚠️ R3 vẫn CHƯA có code path nào đọc (văn bản chính sách); việc wire R2 đọc R3 chờ arch-review."),
    ("new", "  Lịch sử pin (quinquies, 24,42%, 28,86%, 27,x%), `LAG_ADV_BASIS`, fidelity `liq<=0` → `kb/projects/r3-pin-history.md` — **KHÔNG trích +1,62pp như \"edge mới\"**; **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng**. ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho CAPIT pool/maturity. LAG fidelity: Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không"),
    ("keep", 90, 92),
    ("move", 93, 99, R3, "Bootstrap 5th-pct (quinquies) + chuỗi SUPERSEDED"),
    ("new", "- Bootstrap 5th-pct + P(DD<−30%) + chuỗi số SUPERSEDED: `kb/projects/r3-pin-history.md`."),
    ("keep", 100, 101),
    ("move", 102, 105, R3, "DSR/PBO — họ gốc 68 file + caveat mtime"),
    ("new", "  68 file (manifest `mike/research/dsr_family_manifest_20260927/`) — caveat phục dựng theo `mtime`: `kb/projects/r3-pin-history.md`."),
    ("keep", 106, 115),
    ("move", 116, 118, R3, "FAIL-C đóng — A/B"),
    ("new", "- ✅ **FAIL-C ĐÓNG 2026-09-27** (A/B: `kb/projects/r3-pin-history.md`). Anchor R3"),
    ("keep", 119, 122),
    ("move", 123, 124, R3, "Ghi chú bootstrap/FAIL-F branch/PBO 2 cây (viết trước merge 3c944443/f2cfb124)"),
    ("new", "  (Ghi chú cũ FAIL-F branch + PBO 2 cây — xem FAIL-F merge `3c944443` và `DSR_FAMILY_MANIFEST` merge `f2cfb124` ở trên; nguyên văn: `kb/projects/r3-pin-history.md`.)"),
    ("keep", 125, 128),
    ("move", 129, 135, R3, "Parking @0,7 SUPERSEDED + +7.4pp Full SUPERSEDED"),
    ("new", "  Bản @park 0,7 + \"+7.4pp Full\" SUPERSEDED: `kb/projects/r3-pin-history.md`. Giữ/bỏ parking là **quyết định của user**, Taylor không tự đảo."),
    ("keep", 136, 139),
    ("move", 140, 158, SCR, "Lỗi + mức độ sai + hệ quả nghiên cứu"),
    ("new", "Lỗi `ascending=False` trên thang 1-5 (1 = TỐT NHẤT), **16/20 file**, merge `ec9750f2`; chi tiết + mức sai: `kb/projects/screen-sort-direction-bug-20260927.md`. 🔴 **HỆ QUẢ NGHIÊN CỨU — đừng trích số cũ nữa**: **kết luận \"sleeve này bổ sung alpha mới, không lặp 8L\" KHÔNG còn suy được từ những con số cũ.**"),
    ("keep", 159, 211),
    ("move", 212, 216, R3, "Quy chuẩn #5 — cập nhật DSR/PBO 2026-09-27 (bis), trước manifest"),
    ("new", "   DSR/PBO — xem mục **DSR/PBO** ở trên (họ trial GHIM bằng `DSR_FAMILY_MANIFEST`, merge `f2cfb124`); bản cập nhật 2026-09-27 (bis): `kb/projects/r3-pin-history.md`."),
    ("keep", 217, 256),
    ("move", 257, 262, BRD, "Bằng chứng 0/27 ô, job E 0/4"),
    ("new", "- **KHÔNG có bằng chứng trục này tách tín hiệu.** (0/27 ô BH FDR 08-22; job E 09-27 0/4 — `kb/projects/breadth-tercile-axis-20260822.md`)"),
    ("keep", 263, 265),
    ("move", 266, 289, BRD, "Trục khác 0/12, lý do 08-22, cách tính breadth chuẩn"),
    ("new", "- Không trục nào khác qua được cùng chuẩn (0/12). Lý do chọn + **cách tính breadth chuẩn (3 chi tiết từng làm tái lập lệch)**: `kb/projects/breadth-tercile-axis-20260822.md`."),
    ("keep", 290, 291),
    ("move", 292, 294, BRD, "Nguồn quyết định + tái kiểm"),
    ("new", "Quyết định gốc 2026-08-22 + tái kiểm 2026-09-27 (verdict **A — quy ước ĐỨNG, không đổi trục**): `kb/projects/breadth-tercile-axis-20260822.md`."),
    ("keep", 295, 316),
    ("move", 317, 324, CORP, "QUY TẮC DNSE ex-date — bản nháp expected_exdate_adjustment bị gỡ 09-12"),
    ("new", "  (`expected_exdate_adjustment`) bị arch-review gỡ, lý do: `kb/projects/corp-action-nav-chain-20260922.md`. **tự động hoá SAI ở đây còn tệ hơn tự tay xử lý mỗi quý vài lần.**"),
    ("keep", 325, 346),
],
}


def main():
    out_src = {}
    moved = {}  # dest -> list of blocks
    for src, ops in SPEC.items():
        path = os.path.join(ROOT, src)
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        if lines and lines[-1] == "":
            lines = lines[:-1]
        n = len(lines)
        seen = []
        new_lines = []
        for op in ops:
            if op[0] == "new":
                new_lines.append(op[1])
                continue
            a, b = op[1], op[2]
            seen.extend(range(a, b + 1))
            chunk = lines[a - 1:b]
            if op[0] == "keep":
                new_lines.extend(chunk)
            else:
                dest, title = op[3], op[4]
                moved.setdefault(dest, []).append((src, a, b, title, chunk))
        assert seen == list(range(1, n + 1)), f"{src}: coverage broken (n={n}, seen {len(seen)})"
        out_src[src] = "\n".join(new_lines) + "\n"
    for src, txt in out_src.items():
        open(os.path.join(ROOT, src), "w", encoding="utf-8").write(txt)
    for dest, blocks in moved.items():
        dpath = os.path.join(ROOT, P, dest)
        exists = os.path.exists(dpath)
        with open(dpath, "a", encoding="utf-8") as f:
            if not exists:
                f.write(NEW_HEADERS[dest] + "\n")
            else:
                f.write("\n")
            for src, a, b, title, chunk in blocks:
                f.write(f"## Chuyển từ {src} L{a}-{b} (trim 2026-10-08, {JOB}) — {title}\n")
                f.write("\n".join(chunk) + "\n\n")
    # index of moves
    tpath = os.path.join(ROOT, P, TRIM)
    with open(tpath, "a", encoding="utf-8") as f:
        f.write("\n## Bảng di chuyển\n")
        for dest, blocks in moved.items():
            for src, a, b, title, chunk in blocks:
                f.write(f"- {src} L{a}-{b} → `kb/projects/{dest}` — {title}\n")
    print("ok")


if __name__ == "__main__":
    main()
