# -*- coding: utf-8 -*-
"""lag_forensic_filter_selfcheck.py — self-check cho lag_forensic_filter.lag_filter_forensic_banned.

Chạy:  $DNA_PYEXE lag_forensic_filter_selfcheck.py          # offline, không cần BQ/mạng
       $DNA_PYEXE lag_forensic_filter_selfcheck.py --live   # + rổ ứng viên LAG THẬT hôm nay

Bao gồm cả 2 kiểm tra CƠ HỌC chống trôi lệch danh sách BANNED (nhân bản ở 3 nơi):
  · so khớp với `mike/bin/build_universe_pit_quality.py::BANNED` (danh sách Python, so chính xác)
  · so khớp với dòng "Cổ phiếu BANNED vĩnh viễn" trong `mike/kb/KNOWLEDGE.md` (nguồn chuẩn tắc)
Đây là lý do file này tồn tại thay vì chỉ một dòng ghi chú "nhớ đồng bộ tay".

Không phụ thuộc TZ/ngày hệ thống: mọi mốc thời gian đều truyền tường minh (bài học
coding_guidelines §16 — self-check dính TZ của tác giả thì pass ở đâu cũng vô nghĩa).
"""
import os
import re
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lag_forensic_filter import (BANNED, FORENSIC_CSV, LAG_USER_EXCLUDED,  # noqa: E402
                                 lag_filter_forensic_banned)

WORKDIR = os.path.dirname(os.path.abspath(__file__))
PASS = FAIL = 0


def check(name, ok, extra=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name} {extra}")


def cand_df(rows):
    """rows = [(ticker, release_date|None)]"""
    return pd.DataFrame({"ticker": [r[0] for r in rows],
                         "Release_Date": [pd.Timestamp(r[1]) if r[1] else pd.NaT for r in rows],
                         "tier": ["LAG_HI"] * len(rows)})


def tmp_flags(rows):
    """rows = [(ticker, severity, date)] -> đường dẫn CSV tạm"""
    fd, p = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    pd.DataFrame({"ticker": [r[0] for r in rows], "flag_type": ["t"] * len(rows),
                  "severity": [r[1] for r in rows], "date": [r[2] for r in rows],
                  "source": ["sc"] * len(rows), "note": [""] * len(rows)}).to_csv(p, index=False)
    return p


ASOF = pd.Timestamp("2026-08-03")     # ngày ra quyết định, truyền tường minh (không đọc đồng hồ máy)

print("=== lag_forensic_filter self-check ===")

# --- 1. Đồng bộ danh sách BANNED giữa 3 bản sao (kiểm tra cơ học, không phải văn xuôi) ---
_upq = os.path.join(WORKDIR, "mike", "bin", "build_universe_pit_quality.py")
_src = open(_upq, encoding="utf-8").read()
_m = re.search(r"^BANNED = \[(.*?)\]", _src, re.S | re.M)
_other = set(re.findall(r'"([A-Z0-9]{3})"', _m.group(1))) if _m else set()
check("BANNED khớp build_universe_pit_quality.py", _other == set(BANNED),
      f"chênh: {_other ^ set(BANNED)}")

_kb = open(os.path.join(WORKDIR, "mike", "kb", "KNOWLEDGE.md"), encoding="utf-8").read()
_line = next((l for l in _kb.splitlines() if "BANNED vĩnh viễn" in l), "")
# Bỏ phần trong ngoặc TRƯỚC khi trích mã: chú thích văn xuôi chứa token 3 ký tự IN HOA
# không phải mã ("ROE", "IPO", "CF_OA"...) sẽ bị bắt nhầm nếu quét cả dòng (§28 — chuẩn hoá
# GIÁ TRỊ trước khi so, đừng so chuỗi mô tả).
_kbtxt = _line.split(":**", 1)[-1]
while re.search(r"\([^()]*\)", _kbtxt):
    _kbtxt = re.sub(r"\([^()]*\)", " ", _kbtxt)
_kbset = set(re.findall(r"\b([A-Z]{2}[A-Z0-9])\b", _kbtxt))
check("BANNED khớp mike/kb/KNOWLEDGE.md (nguồn chuẩn tắc)", _kbset == set(BANNED),
      f"chênh: {_kbset ^ set(BANNED)} | dòng KB: {_line[:120]}")

# --- 2. Hành vi lõi ---
p = tmp_flags([("VVS", "exclude", "2026-06-20"), ("BFC", "exclude", "2026-06-20"),
               ("CTF", "watch", "2026-06-20"), ("IJC", "watch", "2026-06-20")])

kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("VHC", "2026-07-23"), ("POW", "2026-07-23")]), ASOF, csv_path=p)
check("mã sạch: không loại gì", len(kept) == 2 and not dropped and err is None)

kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("VVS", "2026-07-23"), ("POW", "2026-07-23")]), ASOF, csv_path=p)
check("VVS bị loại (BANNED thắng trước, dù cũng có cờ forensic)",
      list(kept["ticker"]) == ["POW"] and len(dropped) == 1 and dropped[0]["kind"] == "banned")

kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("BFC", "2026-07-23"), ("POW", "2026-07-23")]), ASOF, csv_path=p)
check("BFC bị loại vì cờ forensic exclude",
      list(kept["ticker"]) == ["POW"] and len(dropped) == 1
      and dropped[0]["kind"] == "forensic" and dropped[0]["flag_date"] == "2026-06-20")

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("HSG", "2026-07-23")]), ASOF, csv_path=p)
check("HSG (BANNED, KHÔNG có cờ forensic) vẫn bị loại", len(kept) == 0 and dropped[0]["kind"] == "banned")

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("CTF", "2026-07-23"),
                                                       ("IJC", "2026-07-23")]), ASOF, csv_path=p)
check("severity=watch KHÔNG loại", len(kept) == 2 and not dropped)

# --- 3. Date-aware theo ASOF (ngày quyết định), KHÔNG theo Release_Date ---
# Đây là cái BẪY mà lần chạy live 2026-08-03 đã bắt được: BFC có cờ 2026-06-20 nhưng event gần
# nhất release 2026-05-04 — dùng Release_Date thì BFC LỌT, dùng asof thì bị chặn (đúng).
kept, dropped, _ = lag_filter_forensic_banned(cand_df([("BFC", "2026-05-04")]), ASOF, csv_path=p)
check("event CŨ hơn ngày cờ nhưng xét ở asof SAU cờ → VẪN bị chặn (ca BFC thật)",
      len(kept) == 0 and len(dropped) == 1)

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("BFC", "2026-05-04")]),
                                              pd.Timestamp("2026-06-19"), csv_path=p)
check("replay asof TRƯỚC ngày cờ → KHÔNG hồi tố (giữ)", len(kept) == 1 and not dropped)

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("BFC", "2026-05-04")]),
                                              pd.Timestamp("2026-06-20"), csv_path=p)
check("asof ĐÚNG ngày cờ → chặn (biên <=)", len(kept) == 0 and len(dropped) == 1)

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("HSG", "2026-05-04")]),
                                              pd.Timestamp("2020-01-01"), csv_path=p)
check("BANNED không phụ thuộc asof (chặn cả ở asof rất cũ)", len(kept) == 0)

kept, dropped, _ = lag_filter_forensic_banned(cand_df([("BFC", "2026-07-23")]), pd.NaT, csv_path=p)
check("asof = NaT → fail-closed (coi mọi cờ đã hiệu lực)", len(kept) == 0 and len(dropped) == 1)

# --- 4. Cùng mã nhiều cờ exclude → lấy ngày SỚM NHẤT ---
p2 = tmp_flags([("BFC", "exclude", "2026-06-20"), ("BFC", "exclude", "2026-01-15")])
kept, dropped, _ = lag_filter_forensic_banned(cand_df([("BFC", "2026-02-01")]),
                                              pd.Timestamp("2026-02-01"), csv_path=p2)
check("nhiều cờ exclude cùng mã → dùng ngày sớm nhất",
      len(kept) == 0 and dropped[0]["flag_date"] == "2026-01-15")

# --- 5. Fail-safe khi nguồn hỏng ---
kept, dropped, err = lag_filter_forensic_banned(cand_df([("BFC", "2026-07-23")]), ASOF,
                                                csv_path="/nonexistent/forensic.csv")
check("CSV thiếu → fail-open cho cờ forensic + trả error string",
      len(kept) == 1 and not dropped and err is not None)

kept, dropped, err = lag_filter_forensic_banned(cand_df([("VVS", "2026-07-23"), ("POW", "2026-07-23")]),
                                                ASOF, csv_path="/nonexistent/forensic.csv")
check("CSV thiếu nhưng BANNED VẪN chặn (fail-closed tuyệt đối)",
      list(kept["ticker"]) == ["POW"] and dropped[0]["kind"] == "banned" and err is not None)

# --- 6. Biên ---
kept, dropped, err = lag_filter_forensic_banned(cand_df([]), ASOF, csv_path=p)
check("cand rỗng → no-op", kept is not None and len(kept) == 0 and not dropped and err is None)
kept, dropped, err = lag_filter_forensic_banned(None, ASOF, csv_path=p)
check("cand None → no-op", kept is None and not dropped and err is None)

src = cand_df([("VVS", "2026-07-23"), ("POW", "2026-07-23")])
kept, _, _ = lag_filter_forensic_banned(src, ASOF, csv_path=p)
check("không mutate DataFrame đầu vào", len(src) == 2)

kept, dropped, _ = lag_filter_forensic_banned(
    pd.DataFrame({"ticker": ["VVS", "POW"], "tier": ["LAG_HI", "LAG_LO"]}), ASOF, csv_path=p)
check("không cần cột Release_Date (gate chỉ dùng asof)", list(kept["ticker"]) == ["POW"])

# --- 7. CSV forensic THẬT trong repo: đọc được + đúng nội dung mong đợi ---
real = os.path.join(WORKDIR, FORENSIC_CSV)
kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("BFC", "2026-07-23"), ("KLB", "2026-07-23"), ("POW", "2026-07-23")]), ASOF,
    csv_path=real)
check("đọc được data/forensic_flags.csv thật; BFC+KLB loại, POW giữ",
      err is None and list(kept["ticker"]) == ["POW"] and len(dropped) == 2)

# --- 8. Bất biến với cửa sổ backtest: 0 event bị chặn trước AUDIT_END=2026-06-19 ---
_ff = pd.read_csv(real)
_min_excl = pd.to_datetime(_ff[_ff["severity"].str.strip() == "exclude"]["date"]).min()
check("mọi cờ exclude đều có ngày > AUDIT_END 2026-06-19 (⇒ 0 event trong cửa sổ pin)",
      _min_excl > pd.Timestamp("2026-06-19"), f"min={_min_excl}")

# --- 8b. LAG_USER_EXCLUDED (nguồn 1b, thêm 2026-08-04 job Taylor_20260804_155443) ---
# Bối cảnh đo được ngày 2026-08-04: IVS VÀ TMG ĐỀU là ứng viên LAG trở lại (nằm trong
# lag_rating_excluded / lag_liq_excluded của golive_v23_status.json), tức "cửa sổ đã đóng" là
# SAI. Hiện mỗi mã chỉ bị chặn bởi ĐÚNG MỘT cổng KHÔNG mang quyết định của user (IVS: rating
# 8L=5; TMG: ADV=0) — các ca dưới kiểm chính cơ chế mang quyết định đó.
check("IVS + TMG có trong LAG_USER_EXCLUDED", set(LAG_USER_EXCLUDED) >= {"IVS", "TMG"})

kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("IVS", "2026-08-03"), ("TMG", "2026-08-03"), ("POW", "2026-08-03")]), ASOF,
    csv_path=p)
check("IVS+TMG bị loại vì user-exclude, POW giữ",
      list(kept["ticker"]) == ["POW"] and len(dropped) == 2
      and all(d["kind"] == "user_exclude" for d in dropped))
check("dropped ghi ngày quyết định + lý do (audit trail đọc được)",
      all(d["flag_date"] == "2026-07-21" and "LAG_USER_EXCLUDED" in d["reason"]
          and len(d["reason"]) > 60 for d in dropped))

# Không hồi tố: replay một ngày TRƯỚC khi user quyết (07-21) phải KHÔNG chặn — nếu không,
# mọi backtest/replay lịch sử sẽ mang hindsight của quyết định 07-21.
kept, dropped, _ = lag_filter_forensic_banned(
    cand_df([("IVS", "2026-05-04")]), pd.Timestamp("2026-07-20"), csv_path=p)
check("asof TRƯỚC ngày user quyết → KHÔNG hồi tố (giữ IVS)",
      list(kept["ticker"]) == ["IVS"] and not dropped)
kept, dropped, _ = lag_filter_forensic_banned(
    cand_df([("IVS", "2026-05-04")]), pd.Timestamp("2026-07-21"), csv_path=p)
check("asof ĐÚNG ngày user quyết → chặn (biên <=)", len(kept) == 0 and len(dropped) == 1)

# Fail-closed: hằng số trong CODE nên KHÔNG phụ thuộc file nào — CSV forensic hỏng vẫn chặn.
kept, dropped, err = lag_filter_forensic_banned(
    cand_df([("IVS", "2026-08-03")]), ASOF, csv_path="/nonexistent/forensic.csv")
check("CSV forensic hỏng nhưng user-exclude VẪN chặn (fail-closed tuyệt đối)",
      len(kept) == 0 and len(dropped) == 1 and err is not None)
kept, dropped, _ = lag_filter_forensic_banned(cand_df([("IVS", "2026-08-03")]), pd.NaT,
                                              csv_path=p)
check("asof = NaT → user-exclude fail-closed (chặn)", len(kept) == 0 and len(dropped) == 1)

# Ưu tiên nguồn: BANNED thắng trước user-exclude (thông điệp mạnh hơn), và một mã user-exclude
# KHÔNG được lẫn vào BANNED (khác phạm vi: BANNED chạm toàn hệ qua universe_pit_quality).
check("IVS/TMG KHÔNG nằm trong BANNED (phạm vi CHỈ LAG, không nới hộ toàn hệ)",
      not (set(LAG_USER_EXCLUDED) & set(BANNED)))
_ff_all = set(pd.read_csv(real)["ticker"].astype(str).str.strip())
check("IVS/TMG KHÔNG nằm trong forensic_flags.csv (tránh đổi bảng 8L + số pin R3)",
      not (set(LAG_USER_EXCLUDED) & _ff_all))

# Bất biến với số pin R3: mọi mục user-exclude phải có ngày > AUDIT_END, nếu không nó sẽ drop
# event TRONG cửa sổ backtest và số pin không còn tái lập được.
_min_ux = min(pd.Timestamp(d) for d, _ in LAG_USER_EXCLUDED.values())
check("mọi mục LAG_USER_EXCLUDED có ngày > AUDIT_END 2026-06-19 (⇒ 0 event trong cửa sổ pin)",
      _min_ux > pd.Timestamp("2026-06-19"), f"min={_min_ux}")

# Đối chiếu CƠ HỌC với nguồn văn xuôi: mọi mã trong file văn xuôi phải có trong hằng số này.
# Đây là lý do §A4 tồn tại — trước đó danh sách CHỈ sống ở văn xuôi.
_pm = open("/home/trido/thanhdt/WorkingClaude/mike/kb/context_planning_mini.md",
           encoding="utf-8").read()
_prose_sec = _pm.split("## LAG entry EXCLUDE list")[1].split("\n## ")[0] if \
    "## LAG entry EXCLUDE list" in _pm else ""
_prose_tk = set(re.findall(r"\*\*([A-Z0-9]{3})\*\*", _prose_sec))
check("mọi mã trong văn xuôi context_planning_mini.md đều có trong LAG_USER_EXCLUDED",
      _prose_tk and _prose_tk <= set(LAG_USER_EXCLUDED),
      f"văn xuôi={sorted(_prose_tk)} hằng số={sorted(LAG_USER_EXCLUDED)}")

# --- 9. Guard nối dây: golive_recommend_v23.py có thật sự gọi gate này không ---
_gl = open(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"),
           encoding="utf-8").read()
check("golive_recommend_v23.py import + gọi lag_filter_forensic_banned(cand, LATEST, …)",
      "from lag_forensic_filter import lag_filter_forensic_banned" in _gl
      and re.search(r"lag_filter_forensic_banned\(\s*\n?\s*cand,\s*LATEST", _gl) is not None)

# --- 10. (--live) rổ ứng viên LAG THẬT hôm nay ---
if "--live" in sys.argv:
    print("--- live ---")
    from lag_live_schedule import live_lag_candidates
    q = live_lag_candidates(workdir=WORKDIR)
    q = q[q["qualify"]]
    kept, dropped, err = lag_filter_forensic_banned(q, ASOF, workdir=WORKDIR)
    names = {d["ticker"] for d in dropped}
    print(f"  rổ qualify {len(q)} → còn {len(kept)}; loại {sorted(names)} (err={err})")
    check("[live] gate chạy được trên rổ thật", err is None)
    check("[live] VVS không còn trong rổ sau gate", "VVS" not in set(kept["ticker"]))
    check("[live] BFC không còn trong rổ sau gate", "BFC" not in set(kept["ticker"]))
    check("[live] không loại nhầm mã sạch (mọi mã bị loại đều BANNED hoặc có cờ exclude)",
          all(d["kind"] in ("banned", "forensic") for d in dropped))

print(f"\n=== {PASS} PASS / {FAIL} FAIL ===")
sys.exit(1 if FAIL else 0)
