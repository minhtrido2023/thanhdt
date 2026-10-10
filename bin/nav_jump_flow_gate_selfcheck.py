#!/usr/bin/env python3
"""Selfcheck cho `daily_nav_snapshot.nav_jump_verdict()` — cổng NAV-jump ×
`data/account_cash_flows.json` (job Taylor_20260927_103434).

Import HÀM THẬT từ `daily_nav_snapshot` (không copy logic) nên mutation test có nghĩa.
Mọi file dòng tiền dùng trong test là file TẠM trong /tmp (tham số `flows_path`) ⇒ selfcheck
KHÔNG đọc và KHÔNG sửa `data/account_cash_flows.json` thật, không gọi broker, không gọi BQ.

Chạy:
  $DNA_PYEXE bin/nav_jump_flow_gate_selfcheck.py              # 4 môi trường TZ
  $DNA_PYEXE bin/nav_jump_flow_gate_selfcheck.py --mutations  # + mutation trên file thật
"""
import json
import os
import subprocess
import sys
import tempfile

# §5b: đặt TRƯỚC mọi import có thể kéo Executor vào, dù daily_nav_snapshot hiện không import nó.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "daily_nav_snapshot.py")

# Lịch sử NAV tổng hợp: 1 tỷ tròn để % đọc ra là số tròn, dễ soi ngưỡng.
HIST = [
    {"date": "2026-09-22", "nav": "1000000000", "balance_ts": "2026-09-22T19:10:07"},
    {"date": "2026-09-23", "nav": "1000000000", "balance_ts": "2026-09-23T19:10:12"},
    {"date": "2026-09-24", "nav": "1000000000", "balance_ts": "2026-09-24T19:10:09"},
]
# Lúc chụp số dư của dòng HÔM NAY (dòng sắp ghi) — luật gán dòng tiền so với mốc này.
TODAY_TS = "2026-09-25T19:10:30"
COMP = {"mtm_stock": 9e8, "cash": 1e8, "debt": 0, "egg": 0, "offbook": 0}
TODAY = "2026-09-25"
PREV = 1_000_000_000.0


def flows_file(records, account="SpaceX", tmpdir=None):
    fd, path = tempfile.mkstemp(suffix=".json", dir=tmpdir)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({account: records}, f)
    return path


def build_cases(verdict):
    """-> list (tên, callable()->list[str] các lỗi)."""
    C = []
    raw_verdict = verdict

    def verdict(*a, **k):                     # mọi case mặc định: dòng hôm nay chụp lúc TODAY_TS
        k.setdefault("balance_ts", TODAY_TS)
        return raw_verdict(*a, **k)

    def case(name, fn):
        C.append((name, fn))

    # ---- 1. trong ngưỡng: không tra file, không chặn, không in gì -------------------------
    def c1():
        f = []
        # +14,9% < 15% ⇒ ok, message None. Truyền flows_path trỏ file KHÔNG TỒN TẠI để chứng
        # minh nhánh này thậm chí không cần đọc file.
        ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.149, 15.0, HIST,
                          components=COMP, flows_path="/tmp/__khong_ton_tai__.json")
        if not ok:
            f.append(f"+14,9% phải cho qua, được ok={ok}")
        if msg is not None:
            f.append(f"trong ngưỡng phải im lặng, được message={msg!r}")
        # phía âm
        ok2, msg2 = verdict("SpaceX", TODAY, PREV, PREV * 0.851, 15.0, HIST,
                            components=COMP, flows_path="/tmp/__khong_ton_tai__.json")
        if not ok2 or msg2 is not None:
            f.append(f"-14,9% phải cho qua im lặng, được ok={ok2} msg={msg2!r}")
        return f
    case("trong-nguong-khong-tra-file", c1)

    # ---- 2. vượt ngưỡng, KHÔNG khai dòng tiền ⇒ CHẶN + §29 trích đã đọc gì ---------------
    def c2():
        f = []
        p = flows_file([])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.20, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("+20% không khai dòng tiền PHẢI chặn")
            for need in ("TỰ CHẶN KHÔNG ĐĂNG", "account_cash_flows.json",
                         "0 bản ghi", "KHÔNG có bản ghi nào gán vào 2026-09-25",
                         "CHƯA xác định được nguyên nhân", "market_only"):
                if need not in (msg or ""):
                    f.append(f"thiếu bằng chứng §29 {need!r} trong message")
            if "+20.00%" not in (msg or ""):
                f.append("message không trích đúng biến động đã đo (+20.00%)")
            # KHÔNG được gợi ý nâng env var như lối thoát
            if "chạy lại với NAV_SANITY_MAX_PCT lớn hơn" in (msg or ""):
                f.append("vẫn gợi ý nâng NAV_SANITY_MAX_PCT — đúng lỗi đang sửa")
            if "KHÔNG cần sửa NAV_SANITY_MAX_PCT" not in (msg or ""):
                f.append("không nói rõ khai dòng tiền là cách đi qua đúng")
            if "mtm_stock 900,000,000" not in (msg or ""):
                f.append("không in số thành phần để chẩn đoán nhánh (b)")
        finally:
            os.remove(p)
        return f
    case("vuot-nguong-khong-khai-CHAN", c2)

    # ---- 3. vượt ngưỡng + deposit khai đủ ⇒ CHO QUA, message có vết ----------------------
    def c3():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "sao kê VCB 2026-09-25 ref 998", "timing": "bod", "time_ict": "10:00"}])
        try:
            # nav 1,2B = 1B + 200tr nạp ⇒ phần dư 0%
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"deposit khai đủ phải CHO QUA, được ok={ok} msg={msg!r}")
            if "ĐƯỢC PHÉP GHI" not in (msg or ""):
                f.append("cho qua mà không để lại vết trong message")
            if "+0.00%" not in (msg or ""):
                f.append("không công bố phần dư sau khi trừ dòng tiền")
            if "sao kê VCB 2026-09-25 ref 998" not in (msg or ""):
                f.append("không trích evidence của bản ghi dòng tiền")
            if "+200,000,000" not in (msg or ""):
                f.append("không trích số tiền đã khai")
        finally:
            os.remove(p)
        return f
    case("deposit-khai-du-CHO-QUA", c3)

    # ---- 4. withdraw khai đủ ⇒ CHO QUA (kiểm cả chiều âm) --------------------------------
    def c4():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": -300_000_000, "kind": "withdraw",
                         "evidence": "rút Trứng vàng, email DNSE 2026-09-25", "timing": "bod", "time_ict": "10:00"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 700_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"withdraw khai đủ phải CHO QUA, được ok={ok} msg={msg!r}")
            if "-300,000,000" not in (msg or ""):
                f.append("không trích số rút (âm)")
        finally:
            os.remove(p)
        return f
    case("withdraw-khai-du-CHO-QUA", c4)

    # ---- 5. dòng tiền khai KHÔNG giải thích hết ⇒ VẪN CHẶN ------------------------------
    def c5():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 1_000_000, "kind": "deposit",
                         "evidence": "nạp lẻ 1tr", "timing": "bod", "time_ict": "10:00"}])
        try:
            # khai 1tr nhưng NAV nhảy +50% ⇒ phần dư ~+49,9% ⇒ chặn
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_500_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("khai 1tr mà NAV nhảy +50% PHẢI chặn (bản ghi không phải lời giải thích)")
            if "KHÔNG giải thích hết" not in (msg or ""):
                f.append("không nói rõ dòng tiền không giải thích hết")
            if "+49.90%" not in (msg or ""):
                f.append("không công bố phần dư còn lại sau khi trừ dòng tiền")
            if "nạp lẻ 1tr" not in (msg or ""):
                f.append("không trích bản ghi đã đọc")
        finally:
            os.remove(p)
        return f
    case("dong-tien-khai-thieu-VAN-CHAN", c5)

    # ---- 6. market_only ⇒ CHO QUA dù phần dư vẫn vượt ngưỡng ----------------------------
    def c6():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 0, "kind": "market_only",
                         "evidence": "VNINDEX -6,8% + 4 mã sàn, xác nhận bằng dnse_raw"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 800_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"market_only phải CHO QUA, được ok={ok} msg={msg!r}")
            if "market_only" not in (msg or ""):
                f.append("không nói rõ vì sao cho qua")
            if "VNINDEX -6,8%" not in (msg or ""):
                f.append("không trích evidence của market_only")
        finally:
            os.remove(p)
        return f
    case("market_only-CHO-QUA", c6)

    # ---- 7. bản ghi dòng tiền HỎNG ⇒ CHẶN + in đúng lỗi parser (§29) --------------------
    def c7():
        f = []
        # deposit amount âm = sai schema ⇒ CashFlowError
        p = flows_file([{"date": TODAY, "amount_vnd": -5, "kind": "deposit",
                         "evidence": "x", "timing": "bod", "time_ict": "10:00"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.30, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("bản ghi hỏng PHẢI chặn (không suy 'không có dòng tiền')")
            if "KHÔNG ĐỌC ĐƯỢC" not in (msg or ""):
                f.append("không phân biệt 'không đọc được' với 'không có dòng tiền'")
            if "Lỗi thật:" not in (msg or ""):
                f.append("§29: không in lỗi parser thật")
            if "kind='deposit' phải có amount_vnd>0" not in (msg or ""):
                f.append("§29: không trích nội dung lỗi cụ thể mà parser vừa trả")
            if "KHÔNG nâng NAV_SANITY_MAX_PCT" not in (msg or ""):
                f.append("không cảnh báo lối thoát sai")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-hong-CHAN-va-in-loi-that", c7)

    # ---- 8. dòng tiền của ACCOUNT KHÁC không được tính (§12 tinh thần lọc account) -------
    def c8():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "nạp cho ZaloPay", "timing": "bod", "time_ict": "10:00"}], account="ZaloPay")
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("dòng tiền của ZaloPay KHÔNG được giải thích cho SpaceX")
            if "0 bản ghi cho 'SpaceX'" not in (msg or ""):
                f.append("không nói rõ đã tra bản ghi của ĐÚNG account nào")
        finally:
            os.remove(p)
        return f
    case("dong-tien-account-khac-khong-tinh", c8)

    # ---- 9. biên ngưỡng: đúng 15,00% cho qua, 15,01% chặn -------------------------------
    def c9():
        f = []
        p = flows_file([])
        try:
            ok_eq, msg_eq = verdict("SpaceX", TODAY, PREV, PREV * 1.15, 15.0, HIST,
                                    components=COMP, flows_path=p)
            if not ok_eq or msg_eq is not None:
                f.append(f"đúng 15,00% phải cho qua im lặng (dùng >, không >=): ok={ok_eq}")
            ok_gt, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.1501, 15.0, HIST,
                               components=COMP, flows_path=p)
            if ok_gt:
                f.append("15,01% phải chặn")
        finally:
            os.remove(p)
        return f
    case("bien-nguong-15pct", c9)

    # ---- 10. bản ghi gần ngày (±3) được NÊU nhưng KHÔNG được coi là giải thích ----------
    def c10():
        f = []
        p = flows_file([{"date": "2026-09-18", "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "nạp tuần trước", "timing": "bod", "time_ict": "10:00"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            # 09-18 là BOD, dòng nav đầu tiên >= 09-18 là 09-22 ⇒ KHÔNG gán vào 09-25
            if ok:
                f.append("dòng tiền 09-18 (gán vào 09-22) KHÔNG được giải thích cho 09-25")
            if "không có bản ghi nào trong ±3 ngày" not in (msg or ""):
                f.append("phải nói rõ đã soi cả ±3 ngày và không thấy")
            if "bị đẩy sang phiên sau" in (msg or ""):
                f.append("bản ghi 09-18 đã gán vào phiên 09-22 (không treo) — không được nói nó bị đẩy "
                         f"sang phiên sau: {msg!r}")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-ngay-khac-khong-gan-sai", c10)

    # ---- 11. ngưỡng truyền vào được TÔN TRỌNG (env override vẫn hoạt động) -------------
    def c11():
        f = []
        p = flows_file([])
        try:
            ok, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.20, 25.0, HIST,
                            components=COMP, flows_path=p)
            if not ok:
                f.append("+20% với sanity_max=25 phải cho qua")
            ok2, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.06, 5.0, HIST,
                             components=COMP, flows_path=p)
            if ok2:
                f.append("+6% với sanity_max=5 phải chặn")
        finally:
            os.remove(p)
        return f
    case("nguong-truyen-vao-duoc-ton-trong", c11)

    # ---- 12. file dòng tiền KHÔNG TỒN TẠI + vượt ngưỡng ⇒ chặn, coi như 0 bản ghi ------
    def c12():
        f = []
        ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.30, 15.0, HIST,
                          components=COMP, flows_path="/tmp/__khong_ton_tai_2__.json")
        if ok:
            f.append("thiếu file dòng tiền + vượt ngưỡng PHẢI chặn (không mặc định cho qua)")
        if "0 bản ghi" not in (msg or ""):
            f.append("không nói rõ đã tra và thấy 0 bản ghi")
        return f
    case("thieu-file-dong-tien-CHAN", c12)

    # ---- 13. ngưỡng MẶC ĐỊNH của module phải đúng 15,0 (đo từ N=113 phiên) ------------
    def c13():
        import daily_nav_snapshot as dns
        f = []
        if dns.NAV_SANITY_DEFAULT_PCT != 15.0:
            f.append(f"NAV_SANITY_DEFAULT_PCT = {dns.NAV_SANITY_DEFAULT_PCT} (phải 15.0 — "
                     f"đo từ N=113 cặp phiên, max quan sát 4,148%; đổi thì phải đo lại)")
        # 5% (NAV_JUMP_BLOCK_PCT của cổng công bố) phải KHÁC ngưỡng này — hai câu hỏi khác nhau
        from account_cash_flows import NAV_JUMP_BLOCK_PCT
        if NAV_JUMP_BLOCK_PCT == dns.NAV_SANITY_DEFAULT_PCT:
            f.append("cổng ghi nav_history và cổng công bố đang dùng CÙNG ngưỡng — nếu là chủ ý "
                     "thì phải cập nhật comment §28 trong daily_nav_snapshot.py")
        return f
    case("nguong-mac-dinh-15", c13)

    # ---- 14. NẠP CUỐI TUẦN (arch-review N3): thứ Bảy 09-26 nạp 200tr, dòng thứ Hai 09-28 +20% --
    HIST_FRI = HIST + [{"date": "2026-09-25", "nav": "1000000000", "balance_ts": TODAY_TS}]
    MON, MON_TS = "2026-09-28", "2026-09-28T19:10:11"

    def c14():
        f = []
        for label, rec in (("thứ Bảy 10:00", {"date": "2026-09-26", "time_ict": "10:00"}),
                           ("thứ Sáu 20:00 (sau lần chụp)", {"date": "2026-09-25", "time_ict": "20:00"}),
                           ("thứ Hai 08:30", {"date": MON, "time_ict": "08:30"}),
                           ("thứ Hai 16:00 (sau đóng cửa)", {"date": MON, "time_ict": "16:00"})):
            p = flows_file([dict(rec, amount_vnd=200_000_000, kind="deposit", evidence="sao kê DNSE")])
            try:
                ok, msg = verdict("SpaceX", MON, PREV, 1_200_000_000.0, 15.0, HIST_FRI,
                                  components=COMP, flows_path=p, balance_ts=MON_TS)
                if not ok:
                    f.append(f"nạp {label} phải giải thích dòng thứ Hai, được ok={ok} msg={msg!r}")
                for need in ("ĐƯỢC PHÉP GHI", "+0.00%", "+200,000,000", "sao kê DNSE"):
                    if need not in (msg or ""):
                        f.append(f"nạp {label}: message thiếu {need!r}: {msg!r}")
                want = "[timing=eod]" if "16:00" in label else "[timing=bod]"
                if want not in (msg or ""):
                    f.append(f"nạp {label}: message phải nêu quy ước suy ra {want}: {msg!r}")
            finally:
                os.remove(p)
        return f
    case("nap-cuoi-tuan-giai-thich-dong-thu-hai", c14)

    # ---- 15. tiền vào SAU lần chụp hôm nay KHÔNG giải thích bước nhảy hôm nay ----------------
    def c15():
        f = []
        p = flows_file([{"date": TODAY, "time_ict": "20:00", "amount_vnd": 200_000_000,
                         "kind": "deposit", "evidence": "nạp tối nay"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("tiền 20:00 (sau lần chụp 19:10:30) KHÔNG được giải thích bước nhảy hôm nay")
            for need in ("1 bản ghi cho 'SpaceX'", "KHÔNG có bản ghi nào gán vào 2026-09-25",
                         "gần nhất trong ±3 ngày: 2026-09-25",
                         # L9 (§29): phải nói bản ghi bị đẩy sang phiên sau VÌ giờ khai.
                         "Bản ghi 2026-09-25 time_ict=20:00 +200,000,000 VND ĐÃ khai",
                         f"giờ khai SAU lần chụp số dư của dòng này ({TODAY_TS})",
                         "bị đẩy sang phiên sau"):
                if need not in (msg or ""):
                    f.append(f"message thiếu {need!r}: {msg!r}")
        finally:
            os.remove(p)
        # Không có bản ghi nào treo (không khai gì) ⇒ KHÔNG được in ghi chú "bị đẩy sang phiên sau".
        p = flows_file([])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok or "bị đẩy sang phiên sau" in (msg or ""):
                f.append(f"không có bản ghi treo mà vẫn in ghi chú đẩy phiên: ok={ok} {msg!r}")
        finally:
            os.remove(p)
        return f
    case("tien-sau-lan-chup-khong-giai-thich-hom-nay", c15)

    # ---- 16. file ĐỌC ĐƯỢC nhưng không GÁN được ⇒ chặn, tiêu đề nói ĐÚNG điều đó (§29) -------
    def c16():
        f = []
        p = flows_file([{"date": TODAY, "time_ict": "10:00", "amount_vnd": 200_000_000,
                         "kind": "deposit", "evidence": "sao kê"}])
        try:
            for label, kw, need in (
                    ("dòng hôm nay thiếu balance_ts", {"balance_ts": None},
                     "dòng nav_history 2026-09-25 không có balance_ts (đọc được: None)"),
                    ("dòng hôm nay balance_ts hỏng", {"balance_ts": "tối nay"}, "'tối nay'")):
                ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                                  components=COMP, flows_path=p, **kw)
                if ok:
                    f.append(f"{label}: không gán được bản ghi thì PHẢI chặn")
                for n2 in ("đọc được (1 bản ghi cho 'SpaceX')", "KHÔNG GÁN ĐƯỢC", "Lỗi thật:", need,
                           "KHÔNG nâng NAV_SANITY_MAX_PCT"):
                    if n2 not in (msg or ""):
                        f.append(f"{label}: message thiếu {n2!r}: {msg!r}")
                if "KHÔNG ĐỌC ĐƯỢC" in (msg or ""):
                    f.append(f"{label}: file đọc được mà tiêu đề vẫn nói 'KHÔNG ĐỌC ĐƯỢC'")
            hist_bad = [dict(r) for r in HIST]
            hist_bad[-1]["balance_ts"] = ""
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, hist_bad,
                              components=COMP, flows_path=p)
            if ok or "dòng nav_history 2026-09-24 không có balance_ts" not in (msg or ""):
                f.append(f"dòng lịch sử liền trước thiếu balance_ts phải chặn + nêu đúng dòng: {msg!r}")
            hist_dup = HIST + [dict(HIST[-1])]
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, hist_dup,
                              components=COMP, flows_path=p)
            if ok or "HAI dòng cùng ngày" not in (msg or "") or "KHÔNG GÁN ĐƯỢC" not in (msg or ""):
                f.append(f"nav_history trùng ngày phải chặn bằng thông điệp, không sập: {msg!r}")
        finally:
            os.remove(p)
        return f
    case("doc-duoc-nhung-khong-gan-duoc-CHAN", c16)

    # ---- 17. bản ghi thiếu giờ ⇒ chặn ở bước ĐỌC, tiêu đề 'KHÔNG ĐỌC ĐƯỢC' ------------------
    def c17():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit", "evidence": "x"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("bản ghi thiếu time_ict PHẢI chặn (không còn mặc định timing)")
            for need in ("KHÔNG ĐỌC ĐƯỢC", "Lỗi thật:", "thiếu time_ict"):
                if need not in (msg or ""):
                    f.append(f"message thiếu {need!r}: {msg!r}")
            if "KHÔNG GÁN ĐƯỢC" in (msg or ""):
                f.append("lỗi ở bước ĐỌC mà tiêu đề lại nói 'KHÔNG GÁN ĐƯỢC'")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-thieu-gio-CHAN", c17)

    # ---- 18. main() PHẢI truyền balance_ts của dòng sắp ghi — thiếu thì mọi ngày có dòng tiền
    # đều bị chặn oan ở cron (test hàm không bắt được việc tháo tham số ở chỗ gọi).
    def c18():
        src = open(TARGET, encoding="utf-8").read().split("def main(")[1]
        call = src.split("nav_jump_verdict(")[1].split("if jump_msg:")[0]
        return [] if 'balance_ts=bal["ts"]' in call else [
            f"main() gọi nav_jump_verdict mà không truyền balance_ts của dòng sắp ghi: {call!r}"]
    case("main-truyen-balance_ts", c18)

    # ---- 19. CHẠY LẠI cùng ngày: lịch sử đã có dòng hôm nay (lần chạy trước) ⇒ dòng cũ đó bị
    # thay bằng dòng sắp ghi, không phải thành "hai dòng cùng ngày".
    def c19():
        f = []
        hist_rerun = HIST + [{"date": TODAY, "nav": "1190000000", "balance_ts": "2026-09-25T15:02:00"}]
        p = flows_file([{"date": TODAY, "time_ict": "10:00", "amount_vnd": 200_000_000,
                         "kind": "deposit", "evidence": "sao kê"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, hist_rerun,
                              components=COMP, flows_path=p)
            if not ok or "ĐƯỢC PHÉP GHI" not in (msg or ""):
                f.append(f"chạy lại cùng ngày có dòng tiền đã khai phải CHO QUA, được ok={ok} msg={msg!r}")
        finally:
            os.remove(p)
        return f
    case("chay-lai-cung-ngay", c19)

    # ======================= N11: phần trăm của dòng 💰 NAV lấy từ giá đơn vị quỹ =============
    import csv as _csv
    import datetime as _dtm
    import daily_nav_snapshot as _dns
    FIX = os.path.join(HERE, "fixtures", "nav_unit_ledger_asof_20261009")
    FIX_INC = json.load(open(os.path.join(FIX, "account_inception.json"), encoding="utf-8"))

    def fix_hist(account):
        with open(os.path.join(FIX, f"nav_history_{account}.csv"), encoding="utf-8") as fh:
            return list(_csv.DictReader(fh))

    def loaded(records):
        from account_cash_flows import load_flows as _lf
        p = flows_file(records)
        try:
            return _lf("SpaceX", p)
        finally:
            os.remove(p)

    SYN_INC = {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}
    SYN = [{"date": "2026-07-02", "nav": "1000000000", "balance_ts": "2026-07-02T19:10:00"},
           {"date": "2026-07-03", "nav": "1224000000", "balance_ts": "2026-07-03T19:10:00"}]

    # ---- 20. fixture thật asof 2026-10-09: ZaloPay phải ra mốc 987.865.567 (−4,91%), không phải
    # mốc 1 tỷ (−6,06%); SpaceX (vốn 1 tỷ) giữ NGUYÊN TỪNG KÝ TỰ dòng đã gửi.
    def c20():
        f = []
        for account, want_paren, want_line, old_wrong in (
                ("ZaloPay", "+12,614,629 VND, +1.36% so với hôm trước",
                 "   Từ go-live: -48,470,726 VND (-4.91%)", "(-6.06%)"),
                ("SpaceX", "-643,220 VND, -0.07% so với hôm trước",
                 "   Từ go-live: -13,301,426 VND (-1.33%)", None)):
            hist = fix_hist(account)
            perf, err = _dns.unit_price_performance(account, "2026-10-09", hist, FIX_INC[account], [])
            if err or perf is None:
                f.append(f"{account}: phải tính được, được lỗi {err!r}")
                continue
            day_change = float(hist[-1]["nav"]) - float(hist[-2]["nav"])
            paren, lines = _dns.nav_performance_lines(day_change, perf, err)
            if paren != want_paren:
                f.append(f"{account}: đoạn trong ngoặc phải là {want_paren!r}, được {paren!r}")
            if lines != [want_line]:
                f.append(f"{account}: dòng go-live phải là {[want_line]!r}, được {lines!r}")
            if old_wrong and any(old_wrong in ln for ln in lines):
                f.append(f"{account}: vẫn in số theo mốc 1 tỷ {old_wrong}")
            if perf["inception"]["nav0"] != float(FIX_INC[account]["starting_capital"]):
                f.append(f"{account}: mốc khởi điểm phải lấy từ account_inception.json, được "
                         f"{perf['inception']['nav0']}")
        return f
    case("N11-fixture-2026-10-09-dung-moc-khoi-diem", c20)

    # ---- 21. toàn bộ lịch sử fixture (chưa có dòng tiền): hai dòng mới == công thức tham chiếu
    # (thay đổi NAV / NAV phiên trước; NAV / vốn khởi điểm) từng ngày, từng ký tự.
    def c21():
        f, n = [], 0
        for account in ("SpaceX", "ZaloPay"):
            hist = fix_hist(account)
            cap = float(FIX_INC[account]["starting_capital"])
            inc_date = FIX_INC[account]["inception_date"]
            for i, row in enumerate(hist):
                if row["date"] <= inc_date:
                    continue
                nav = float(row["nav"])
                prev = float(hist[i - 1]["nav"]) if i and hist[i - 1]["date"] > inc_date else cap
                perf, err = _dns.unit_price_performance(account, row["date"], hist[:i + 1],
                                                        FIX_INC[account], [])
                paren, lines = _dns.nav_performance_lines(nav - prev, perf, err)
                # ĐÚNG công thức dòng cũ (làm tròn một lần) ⇒ ngày không dòng tiền, dòng mới == dòng cũ
                want_p = f"{nav - prev:+,.0f} VND, {(nav / prev - 1) * 100:+.2f}% so với hôm trước"
                want_l = [f"   Từ go-live: {nav - cap:+,.0f} VND ({(nav / cap - 1) * 100:+.2f}%)"]
                n += 1
                if (paren, lines) != (want_p, want_l):
                    f.append(f"{account} {row['date']}: được {(paren, lines)!r}, tham chiếu {(want_p, want_l)!r}")
        if n < 130:
            f.append(f"phải kiểm >= 130 (account, ngày) của fixture, chỉ có {n}")
        return f[:5]
    case("N11-toan-lich-su-khong-dong-tien", c21)

    # ---- 22. CÓ dòng tiền: % là tỉ suất giá đơn vị, số VND tách lãi/lỗ với nạp/rút ròng.
    #   1.000 → nạp 200 lúc 10:00 → +2% ⇒ NAV 1.224: lãi 24tr = +2,00% (không phải +22,40%).
    def c22():
        f = []
        fl = loaded([{"date": "2026-07-03", "time_ict": "10:00", "amount_vnd": 200_000_000,
                      "kind": "deposit", "evidence": "sao kê"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-03", SYN, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(224_000_000.0, perf, err)
        want_p = ("+24,000,000 VND lãi/lỗ, +2.00% so với hôm trước; NAV đổi +224,000,000 VND, "
                  "trong đó nạp/rút ròng +200,000,000 VND")
        want_l = ["   Từ go-live: +24,000,000 VND lãi/lỗ (+2.00%); NAV đổi +224,000,000 VND, "
                  "trong đó nạp/rút ròng +200,000,000 VND"]
        if paren != want_p:
            f.append(f"ngày có nạp: ngoặc phải là {want_p!r}, được {paren!r}")
        if lines != want_l:
            f.append(f"ngày có nạp: dòng go-live phải là {want_l!r}, được {lines!r}")
        if "22.40" in paren + "".join(lines):
            f.append("vẫn in +22,40% (tính nạp tiền thành lãi)")
        # rút 100tr sau đóng cửa ngày thị trường −1%: 1.000 → 990 − 100 = 890
        syn_w = [SYN[0], {"date": "2026-07-03", "nav": "890000000", "balance_ts": "2026-07-03T19:10:00"}]
        fl = loaded([{"date": "2026-07-03", "time_ict": "16:00", "amount_vnd": -100_000_000,
                      "kind": "withdraw", "evidence": "sao kê"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-03", syn_w, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(-110_000_000.0, perf, err)
        if paren != ("-10,000,000 VND lãi/lỗ, -1.00% so với hôm trước; NAV đổi -110,000,000 VND, "
                     "trong đó nạp/rút ròng -100,000,000 VND"):
            f.append(f"ngày có rút: ngoặc sai: {paren!r}")
        return f
    case("N11-co-dong-tien-tach-lai-lo-voi-nap-rut", c22)

    # ---- 23. dòng tiền của NGÀY TRƯỚC: hôm nay không nạp ⇒ dòng ngày giữ dạng cũ, dòng go-live
    # tách; dòng tiền TREO thì hiện cảnh báo riêng.
    def c23():
        f = []
        syn3 = SYN + [{"date": "2026-07-06", "nav": "1236240000", "balance_ts": "2026-07-06T19:10:00"}]
        fl = loaded([{"date": "2026-07-03", "time_ict": "10:00", "amount_vnd": 200_000_000,
                      "kind": "deposit", "evidence": "sao kê"},
                     {"date": "2026-07-06", "time_ict": "21:00", "amount_vnd": 50_000_000,
                      "kind": "deposit", "evidence": "nạp tối nay"}])
        perf, err = _dns.unit_price_performance("SpaceX", "2026-07-06", syn3, SYN_INC, fl)
        paren, lines = _dns.nav_performance_lines(12_240_000.0, perf, err)
        if paren != "+12,240,000 VND, +1.00% so với hôm trước":
            f.append(f"ngày KHÔNG nạp phải giữ dạng dòng cũ, được {paren!r}")
        if lines[:1] != ["   Từ go-live: +36,240,000 VND lãi/lỗ (+3.02%); NAV đổi +236,240,000 VND, "
                         "trong đó nạp/rút ròng +200,000,000 VND"]:
            f.append(f"dòng go-live phải tách lãi/lỗ với nạp/rút, được {lines[:1]!r}")
        if len(lines) != 2 or not all(x in lines[1] for x in ("⚠️", "2026-07-06 21:00", "+50,000,000",
                                                              "CHƯA nằm trong số nào", "TREO")):
            f.append(f"dòng tiền treo phải có cảnh báo riêng, được {lines[1:]!r}")
        return f
    case("N11-dong-tien-ngay-truoc-va-treo", c23)

    # ---- 24. không tính được ⇒ nói thẳng + lỗi thật, KHÔNG lùi về công thức mốc 1 tỷ.
    def c24():
        f = []
        for label, kw, need in (
                ("account không có mốc khởi điểm", {"account": "NoSuchAccount"}, "NoSuchAccount"),
                ("bản ghi dòng tiền thiếu giờ", {"account": "SpaceX", "inception": SYN_INC, "flows": [
                    {"date": _dtm.date(2026, 7, 3), "amount_vnd": 2e8, "kind": "deposit",
                     "evidence": "x", "timing": None, "time_ict": None}]}, "không có time_ict")):
            perf, err = _dns.unit_price_performance(kw.pop("account"), "2026-07-03", SYN, **kw)
            if perf is not None or not err or need not in err:
                f.append(f"{label}: phải trả (None, lỗi có {need!r}), được {(perf, err)!r}")
                continue
            paren, lines = _dns.nav_performance_lines(224_000_000.0, perf, err)
            if "%" in paren.replace("tỉ suất", "") or "KHÔNG tính được" not in paren:
                f.append(f"{label}: ngoặc không được in phần trăm nào, được {paren!r}")
            if len(lines) != 1 or "KHÔNG tính được" not in lines[0] or need not in lines[0] or "%)" in lines[0]:
                f.append(f"{label}: dòng go-live phải nêu lỗi thật, không in %, được {lines!r}")
        # ngày chưa có phiên nào sau mốc khởi điểm: không có "hôm trước" để so
        perf, err = _dns.unit_price_performance(
            "SpaceX", "2026-07-01", [{"date": "2026-07-01", "nav": "1000000000", "balance_ts": ""}],
            SYN_INC, [])
        paren, lines = _dns.nav_performance_lines(0.0, perf, err)
        if err or "chưa có phiên nào sau mốc khởi điểm" not in paren or lines != ["   Từ go-live: +0 VND (+0.00%)"]:
            f.append(f"ngày mốc khởi điểm: được {(paren, lines, err)!r}")
        return f
    case("N11-khong-tinh-duoc-thi-noi-thang", c24)

    # ---- 25. main() PHẢI in bằng hai hàm trên, không còn công thức `/ args.starting_capital`.
    def c25():
        src = open(TARGET, encoding="utf-8").read().split("def main(")[1]
        f = []
        for need in ("unit_price_performance(args.account, args.date, hist_rows)",
                     "nav_performance_lines(day_change, perf, perf_err)",
                     'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({paren})"', "] + perf_lines"):
            if need not in src:
                f.append(f"main() thiếu {need!r}")
        if "/ args.starting_capital" in src or "day_change_pct:+.2f" in src:
            f.append("main() vẫn còn công thức phần trăm cũ (mốc --starting-capital / tỉ số NAV thô)")
        return f
    case("N11-main-dung-mot-nguon", c25)

    return C


def run_suite(verbose=True):
    import importlib
    import daily_nav_snapshot
    importlib.reload(daily_nav_snapshot)
    verdict = daily_nav_snapshot.nav_jump_verdict
    cases = build_cases(verdict)
    n = 0
    fails = []
    for name, fn in cases:
        n += 1
        try:
            fs = fn()
        except Exception as exc:  # exception trong case = fail, không im lặng
            fs = [f"case raise {type(exc).__name__}: {exc}"]
        for x in fs:
            fails.append(f"{name}: {x}")
    if verbose:
        for x in fails:
            print("  FAIL " + x)
    return n, fails


MUTATIONS = [
    ("nguong-15->95", lambda t: t.replace(
        "NAV_SANITY_DEFAULT_PCT = 15.0", "NAV_SANITY_DEFAULT_PCT = 95.0")),
    ("nguong-mac-dinh-bang-cong-cong-bo", lambda t: t.replace(
        "NAV_SANITY_DEFAULT_PCT = 15.0", "NAV_SANITY_DEFAULT_PCT = 5.0")),
    ("in-nguong-gt->ge", lambda t: t.replace(
        "    if abs(day_change_pct) <= sanity_max:\n        return True, None",
        "    if abs(day_change_pct) < sanity_max:\n        return True, None")),
    ("khong-co-flow-van-cho-qua", lambda t: t.replace(
        "    today_flows = list(mapped.get(date_d, []))\n    if not today_flows:",
        "    today_flows = list(mapped.get(date_d, []))\n    if False:")),
    ("bo-kiem-phan-du", lambda t: t.replace(
        "    if abs(resid_pct) <= sanity_max:\n        return True, (",
        "    if True:\n        return True, (")),
    ("CashFlowError-cho-qua", lambda t: t.replace(
        "    except CashFlowError as exc:\n        # Bản ghi dòng tiền hỏng",
        "    except CashFlowError as exc:\n        return True, str(exc)\n        # Bản ghi dòng tiền hỏng")),
    ("resid-khong-tru-flow", lambda t: t.replace(
        "    resid_pct = ((nav - net_flow) / prev_nav - 1) * 100 if prev_nav else 0.0",
        "    resid_pct = (nav / prev_nav - 1) * 100 if prev_nav else 0.0")),
    ("market_only-bo-dieu-kien-amount", lambda t: t.replace(
        'if "market_only" in kinds and net_flow == 0:',
        'if "market_only" in kinds or True:')),
    ("net_flow-dao-dau", lambda t: t.replace(
        '    net_flow = sum(f["amount_vnd"] for f in today_flows)',
        '    net_flow = -sum(f["amount_vnd"] for f in today_flows)')),
    ("bo-loi-that-CashFlowError", lambda t: t.replace(
        "Lỗi thật: {exc}", "(không xác định)")),
    ("loi-gan-cho-qua", lambda t: t.replace(
        "    except ValueError as exc:               # CashFlowError (thiếu giờ/balance_ts…) là ValueError",
        "    except ValueError as exc:\n        return True, str(exc)")),
    ("loi-gan-chi-bat-CashFlowError", lambda t: t.replace(
        "    except ValueError as exc:               # CashFlowError (thiếu giờ/balance_ts…) là ValueError",
        "    except CashFlowError as exc:")),
    ("tieu-de-gan-noi-khong-doc-duoc", lambda t: t.replace(
        "nhưng KHÔNG GÁN ĐƯỢC bản ghi vào phiên nào", "KHÔNG ĐỌC ĐƯỢC")),
    ("bo-balance_ts-dong-hom-nay", lambda t: t.replace(
        "+ [NavRow(date_d, nav, balance_ts=balance_ts)])", "+ [NavRow(date_d, nav)])")),
    ("bo-balance_ts-lich-su", lambda t: t.replace(
        '                balance_ts=(r.get("balance_ts") or None)) for r in hist_rows',
        '                balance_ts=None) for r in hist_rows')),
    ("lich-su-lay-ca-dong-hom-nay", lambda t: t.replace(
        'if r.get("date") and r["date"] < date and r.get("nav")]',
        'if r.get("date") and r["date"] <= date and r.get("nav")]')),
    ("main-bo-balance_ts", lambda t: t.replace(
        '"egg": egg_value, "offbook": offbook}, balance_ts=bal["ts"])',
        '"egg": egg_value, "offbook": offbook})')),
    # ---- N11
    ("n11-moc-khoi-diem-1-ty", lambda t: t.replace(
        "inception or load_inception(account), flows), None",
        '{"inception_date": (inception or load_inception(account))["inception_date"], '
        '"starting_capital": 1_000_000_000}, flows), None')),
    ("n11-bo-dong-tien", lambda t: t.replace(
        "inception or load_inception(account), flows), None",
        "inception or load_inception(account), []), None")),
    ("n11-nuot-loi-thanh-so", lambda t: t.replace(
        '        return None, f"{type(exc).__name__}: {exc}"\n\n\ndef nav_performance_lines',
        '        return None, ""\n\n\ndef nav_performance_lines')),
    ("n11-luon-dang-cu", lambda t: t.replace("        if not flow:\n            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"",
                                             "        if True:\n            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"")),
    ("n11-vnd-la-thay-doi-nav", lambda t: t.replace(
        "            return f\"{period['pnl_vnd']:+,.0f} VND{tail}\"",
        "            return f\"{period['nav1'] - period['nav0']:+,.0f} VND{tail}\"").replace(
        "        return (f\"{period['pnl_vnd']:+,.0f} VND lãi/lỗ{tail}; NAV đổi \"",
        "        return (f\"{period['nav1'] - period['nav0']:+,.0f} VND lãi/lỗ{tail}; NAV đổi \"")),
    ("n11-ngay-lay-pct-go-live", lambda t: t.replace(
        "paren = vnd(day, f\", {pct(day):+.2f}% so với hôm trước\")",
        "paren = vnd(day, f\", {pct(inc):+.2f}% so với hôm trước\")")),
    ("n11-lam-tron-hai-buoc", lambda t: t.replace(
        'return (period["unit_price_ratio"] - 1) * 100', 'return period["return_pct"]')),
    ("n11-go-live-lay-pct-ngay", lambda t: t.replace(
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({pct(inc):+.2f}%)\")]",
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({pct(day):+.2f}%)\")]")),
    ("n11-go-live-lay-vnd-ngay", lambda t: t.replace(
        "lines = [\"   Từ go-live: \" + vnd(inc, f\" ({pct(inc):+.2f}%)\")]",
        "lines = [\"   Từ go-live: \" + vnd(day, f\" ({pct(inc):+.2f}%)\")]")),
    ("n11-bo-canh-bao-treo", lambda t: t.replace(
        '    for f in perf["pending_flows"]:\n        lines.append(f"   ⚠️ Dòng tiền đã khai',
        '    for f in []:\n        lines.append(f"   ⚠️ Dòng tiền đã khai')),
    ("n11-dong-tien-rong-dao-dau", lambda t: t.replace(
        "trong đó nạp/rút ròng {flow:+,.0f} VND\")", "trong đó nạp/rút ròng {-flow:+,.0f} VND\")")),
    ("n11-main-in-cong-thuc-cu", lambda t: t.replace(
        'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({paren})"',
        'f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)"')),
    ("n11-main-bo-dong-go-live", lambda t: t.replace("    ] + perf_lines\n", "    ]\n")),
    # ---- arch-review lần 2
    ("l9-bo-ghi-chu-day-phien", lambda t: t.replace(
        '" (không có bản ghi nào trong ±3 ngày)") + "." + late_note + "\\n"',
        '" (không có bản ghi nào trong ±3 ngày)") + ".\\n"')),
    ("l9-ghi-chu-moi-ban-ghi-gan", lambda t: t.replace(
        'late = [f for f in mapped.get(None, []) if f["date"] <= date_d]',
        'late = [f for f in flows if f["date"] <= date_d]')),
    ("bo-so-thanh-phan", lambda t: t.replace(
        "kiểm vị thế thiếu/giá sai ({_comp_line()}).", "kiểm vị thế thiếu/giá sai.")),
]


def child():
    n, fails = run_suite()
    print(f"__RESULT__ cases={n} fails={len(fails)}")
    return 1 if fails else 0


def main():
    args = sys.argv[1:]
    if os.environ.get("_NJF_CHILD") == "1":
        return child()

    tzs = [("ICT", "Asia/Ho_Chi_Minh"), ("UTC", "UTC"),
           ("NY", "America/New_York"), ("no-TZ", None)]
    print(f"target: {TARGET}")
    print(f"môi trường TZ: {[t[0] for t in tzs]}")
    rc = 0
    results = {}
    for tzname, tz in tzs:
        env = dict(os.environ, _NJF_CHILD="1")
        env.pop("TZ", None)
        if tz:
            env["TZ"] = tz
        out = subprocess.run([sys.executable, os.path.abspath(__file__)],
                             capture_output=True, text=True, env=env, timeout=300)
        line = [x for x in out.stdout.splitlines() if x.startswith("__RESULT__")]
        print(f"\n--- TZ={tzname} rc={out.returncode}")
        for x in out.stdout.splitlines():
            if not x.startswith("__RESULT__"):
                print(x if x.startswith("  ") else "  " + x)
        if not line:
            print(f"  FATAL: không đọc được __RESULT__ — stderr={out.stderr[-600:]}")
            rc = 1
            continue
        print("  " + line[0])
        results[tzname] = line[0]
        if out.returncode != 0:
            rc = 1
    if len(set(results.values())) > 1:
        print("\nFAIL: kết quả KHÁC nhau giữa các múi giờ:")
        for k, v in results.items():
            print(f"  {k}: {v}")
        rc = 1
    elif results:
        print(f"\nBẤT BIẾN theo TZ: cả {len(results)} môi trường cho cùng kết quả ✓")

    if "--mutations" in args or "--all" in args:
        orig = open(TARGET, encoding="utf-8").read()
        print(f"\nMUTATION ({len(MUTATIONS)} đột biến trên CHÍNH file thật):")
        killed, survived = 0, []
        try:
            for mname, mfn in MUTATIONS:
                mutated = mfn(orig)
                if mutated == orig:
                    survived.append(f"{mname} (KHÔNG áp được — pattern không khớp code hiện tại)")
                    print(f"  SKIP-NOAPPLY {mname}")
                    continue
                open(TARGET, "w", encoding="utf-8").write(mutated)
                env = dict(os.environ, _NJF_CHILD="1", TZ="Asia/Ho_Chi_Minh")
                out = subprocess.run([sys.executable, os.path.abspath(__file__)],
                                     capture_output=True, text=True, env=env, timeout=300)
                if out.returncode != 0:
                    killed += 1
                    nf = [x for x in out.stdout.splitlines() if x.startswith("__RESULT__")]
                    print(f"  killed   {mname}  ({nf[0] if nf else 'crash'})")
                else:
                    survived.append(mname)
                    print(f"  SURVIVED {mname}")
        finally:
            open(TARGET, "w", encoding="utf-8").write(orig)   # luôn phục hồi file thật
        # chứng minh đã phục hồi đúng
        if open(TARGET, encoding="utf-8").read() != orig:
            print("  FATAL: KHÔNG phục hồi được file thật sau mutation")
            rc = 1
        else:
            print("  (file thật đã được phục hồi nguyên trạng ✓)")
        print(f"\nMUTATION: {killed}/{len(MUTATIONS)} bị giết")
        if survived:
            print("  sống sót: " + "; ".join(survived))
            rc = 1

    print("\n" + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
