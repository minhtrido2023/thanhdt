#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `fund_restatement.py` — cơ chế đính chính số đã công bố (chính sách điểm 4).

KHÉP KÍN: nav_history, mốc khởi điểm, sổ dòng tiền, thư mục báo cáo đều dựng trong tempdir; "thư
mục dữ liệu thật" là một tempdir gán vào `nul.NAV_HISTORY_DIR`. Không broker, không BigQuery,
không đọc/ghi `data/`, không gửi gì đi đâu.

Chạy: python3 mike/bin/fund_restatement_selfcheck.py
      env -u TZ python3 … ;  TZ=America/New_York python3 … ;  TZ=Pacific/Kiritimati python3 …
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

import fund_restatement as fr                         # noqa: E402
import nav_unit_ledger as nul                         # noqa: E402

D = datetime.date
N = 0
FAILS = []
FIELDS = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
          "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
INC = {"SpaceX": {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000},
       "ZaloPay": {"inception_date": "2026-07-01", "starting_capital": 500_000_000}}
# 2026-07-01 thứ Tư. NAV (triệu) theo ngày:
NAV = [("2026-07-02", 1010), ("2026-07-03", 1020), ("2026-07-06", 1015), ("2026-07-07", 1030),
       ("2026-07-08", 1040), ("2026-07-09", 1035), ("2026-07-10", 1050), ("2026-07-13", 1060),
       ("2026-07-14", 1065)]
REPORTS = {
    "SpaceX_daily_report_2026-07-03.md": "NAV 1.020.000.000",
    "SpaceX_daily_report_2026-07-06.md": "💰 NAV 2026-07-06: 1,015,000,000 VND",
    "SpaceX_daily_report_2026-07-07.md": "NAV 1.030.000.000",
    "SpaceX_daily_report_2026-07-10.md": "NAV hôm nay 1.050.000.000\n(đầu tuần 06/07: 1.015.000.000)",
    "SpaceX_weekly_report_2026-07-03.md": "tuần go-live",
    "SpaceX_weekly_report_2026-07-06_to_2026-07-10.md": "| 06/07 | 1015000000 |\n| 07/07 | ... |",
    "SpaceX_weekly_report_2026-07-06_to_2026-07-10_CORRECTION_VIB.md": "bản đính chính VIB",
    "SpaceX_ZaloPay_monthly_report_2026-07.md": "tháng 7",
    "ZaloPay_daily_report_2026-07-06.md": "NAV 1.015.000.000 (tài khoản khác)",
    "paper_programs_daily_report_2026-07-06.md": "không phải báo cáo tài khoản",
    "SpaceX_weekly_report_2026-07-06_to_2026-07-10.md.bak_sent_20260711": "bản sao lưu",
    "SpaceX_daily_report_ngay-la.md": "tên hỏng",
    "ghi_chu.md": "không liên quan",
}


def ok(cond, msg):
    global N
    N += 1
    if not cond:
        FAILS.append(msg)
        print(f"FAIL: {msg}")


def raises(exc_type, fn, msg, needle=None):
    global N
    N += 1
    try:
        fn()
    except exc_type as exc:
        for part in ([needle] if isinstance(needle, str) else (needle or [])):
            if part not in str(exc):
                FAILS.append(f"{msg}: thông điệp thiếu {part!r}: {exc}")
                print("FAIL:", FAILS[-1])
        return exc
    except Exception as exc:                # noqa: BLE001
        FAILS.append(f"{msg}: phải ném {exc_type.__name__}, được {type(exc).__name__}: {exc}")
        print("FAIL:", FAILS[-1])
        return None
    FAILS.append(f"{msg}: phải ném {exc_type.__name__}, không ném gì")
    print("FAIL:", FAILS[-1])
    return None


def md5(data):
    return hashlib.md5(data).hexdigest()


def row(date, nav_m, ts=None, est="False", cash=100_000_000):
    nav = int(round(nav_m * 1_000_000))
    return {"date": date, "nav": str(nav), "mtm_stock": str(nav - cash), "cash": str(cash),
            "margin_debt": "0", "offbook_assets": "0", "egg_assets": "0",
            "balance_ts": ts or f"{date}T19:10:00", "cum_dividend_excl": "0",
            "nav_is_estimate": est, "nav_source": "live"}


class World:
    def __init__(self, tmp, name, nav=NAV, flows=(), terminator="\r\n", account="SpaceX"):
        self.dir = Path(tmp) / name
        self.nav_dir = self.dir / "execution_logs"
        self.reports = self.dir / "reports"
        self.nav_dir.mkdir(parents=True)
        self.reports.mkdir()
        self.account = account
        self.inc = str(self.dir / "account_inception.json")
        self.flows = str(self.dir / "account_cash_flows.json")
        Path(self.inc).write_text(json.dumps(INC), encoding="utf-8")
        self.write_flows(flows)
        self.terminator = terminator
        self.write_nav([row(d, v) for d, v in nav])
        for name_, text in REPORTS.items():
            (self.reports / name_).write_text(text + "\n", encoding="utf-8")

    @property
    def nav_path(self):
        return self.nav_dir / f"nav_history_{self.account}.csv"

    def write_nav(self, rows):
        self.nav_path.write_bytes(fr.write_nav_table(FIELDS, rows, self.terminator))

    def write_flows(self, flows, path=None):
        Path(path or self.flows).write_text(json.dumps({"SpaceX": list(flows), "ZaloPay": []}),
                                            encoding="utf-8")

    def correction(self, items, name="c.json", account=None):
        p = self.dir / name
        p.write_text(json.dumps({"account": account or self.account, "corrections": items},
                                ensure_ascii=False), encoding="utf-8")
        return str(p)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(BIN / "fund_restatement.py"), *args],
                              capture_output=True, text=True)

    def impact(self, correction=None, new_nav_dir=None, out="impact.json", extra=()):
        out_path = str(self.dir / out)
        args = ["impact", "--account", self.account, "--old-nav-dir", str(self.nav_dir),
                "--inception-path", self.inc, "--flows-path", self.flows,
                "--reports-dir", str(self.reports), "--out", out_path, *extra]
        args += ["--correction", correction] if correction else ["--new-nav-dir", new_nav_dir]
        p = self.cli(*args)
        data = json.loads(Path(out_path).read_text(encoding="utf-8")) if p.returncode == 0 else None
        return p, data, out_path

    def apply(self, correction, impact_path, approved_by="user 2026-10-14", extra=()):
        return self.cli("apply", "--account", self.account, "--nav-dir", str(self.nav_dir),
                        "--correction", correction, "--impact-report", impact_path,
                        "--approved-by", approved_by, *extra)


def replace_item(date, old_m, new_m, **kw):
    new = row(date, new_m)
    item = {"op": "replace", "date": date, "expect": {"nav": str(old_m * 1_000_000)},
            "set": {"nav": new["nav"], "mtm_stock": new["mtm_stock"]},
            "reason": "đếm trùng một lô", "evidence": "dnse_raw + journal"}
    item.update(kw)
    return item


def by_name(impact):
    return {r["report"]: r for r in impact["reports"]}


# ------------------------------------------------------------------ R1. bậc
def r1_tier():
    for dev, want in ((0.0, 0), (1e-12, 1), (0.049999, 1), (0.05, 2), (0.0500001, 2), (0.3, 2),
                      (0.5, 2), (0.5000001, 3), (7.0, 3), (float("inf"), 3), (float("nan"), 3)):
        ok(fr.tier(dev) == want, f"R1: tier({dev}) phải = {want}, được {fr.tier(dev)}")
    ok((fr.TIER_NOTE_FROM, fr.TIER_REISSUE_ABOVE) == (0.05, 0.5), "R1: ngưỡng chính sách 0,05 / 0,5")
    ok("ghi chú ở báo cáo kế tiếp" in fr.TIER_ACTION[2] and "cần user duyệt" in fr.TIER_ACTION[3]
       and "không đính chính" in fr.TIER_ACTION[1], "R1: hành động của từng bậc đúng chính sách")


# ------------------------------------------------------------------ R2. tên báo cáo
def r2_report_names(tmp):
    p = fr.parse_report_name
    m = p("SpaceX_daily_report_2026-07-06.md")
    ok(m == {"who": ["SpaceX"], "kind": "daily", "start": D(2026, 7, 6), "end": D(2026, 7, 6),
             "suffix": None}, f"R2 daily: {m}")
    m = p("SpaceX_ZaloPay_weekly_report_2026-07-06_to_2026-07-10_CORRECTION_VIB.md")
    ok(m["who"] == ["SpaceX", "ZaloPay"] and (m["start"], m["end"]) == (D(2026, 7, 6), D(2026, 7, 10))
       and m["suffix"] == "CORRECTION_VIB", f"R2 weekly khoảng + hậu tố: {m}")
    m = p("SpaceX_weekly_report_2026-07-03.md")
    ok((m["start"], m["end"]) == (D(2026, 6, 29), D(2026, 7, 3)), f"R2 weekly một ngày ⇒ từ thứ Hai: {m}")
    m = p("ZaloPay_monthly_report_2026-02.md")
    ok((m["start"], m["end"]) == (D(2026, 2, 1), D(2026, 2, 28)), f"R2 monthly tháng 2: {m}")
    m = p("SpaceX_monthly_report_2028-02.md")
    ok(m["end"] == D(2028, 2, 29), "R2 monthly năm nhuận")
    ok(p("ghi_chu.md") is None and p("SpaceX_daily_report_2026-07-06.md.bak") is None
       and p("SpaceX_plan_2026-07-06.md") is None, "R2: tên không phải báo cáo ⇒ None")
    for bad in ("SpaceX_daily_report_ngay-la.md", "SpaceX_weekly_report_2026-07-10_to_2026-07-06.md",
                "SpaceX_monthly_report_2026-13.md", "SpaceX_daily_report_2026-02-30.md"):
        raises(fr.RestatementError, lambda: p(bad), f"R2: {bad}", "không đọc được kỳ")
    w = World(tmp, "r2")
    found, unparsed, skipped = fr.list_reports(str(w.reports), "SpaceX")
    names = [x["name"] for x in found]
    ok(len(names) == 8 and "ZaloPay_daily_report_2026-07-06.md" not in names
       and "paper_programs_daily_report_2026-07-06.md" not in names
       and "SpaceX_ZaloPay_monthly_report_2026-07.md" in names,
       f"R2 §12: chỉ báo cáo của SpaceX (kể cả báo cáo gộp), được {names}")
    ok(len(unparsed) == 1 and "ngay-la" in unparsed[0], f"R2: tên hỏng phải được NÊU, không bỏ im: {unparsed}")
    ok(skipped == ["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md.bak_sent_20260711"],
       f"R2: file không phải .md phải được liệt kê là bỏ qua: {skipped}")
    z, _, _ = fr.list_reports(str(w.reports), "ZaloPay")
    ok(sorted(x["name"] for x in z) == ["SpaceX_ZaloPay_monthly_report_2026-07.md",
                                         "ZaloPay_daily_report_2026-07-06.md"], "R2 §12: phía ZaloPay khác SpaceX")


# ------------------------------------------------------------------ R3. sửa một dòng giữa
def r3_replace(tmp):
    w = World(tmp, "r3")
    p, imp, _ = w.impact(w.correction([replace_item("2026-07-06", 1015, 1012)]))
    ok(p.returncode == 0 and imp is not None, f"R3: impact phải rc=0: {p.stderr[:300]}")
    rep = by_name(imp)
    ok(imp["n_reports_scanned"] == 8 and imp["n_reports_affected"] == 6,
       f"R3: quét 8, ảnh hưởng 6; được {imp['n_reports_scanned']}/{imp['n_reports_affected']}: {sorted(rep)}")
    d6 = rep["SpaceX_daily_report_2026-07-06.md"]
    want_nav = (1012 / 1015 - 1) * 100
    ok(abs(d6["headline"]["nav"]["dev_pct"] - want_nav) < 1e-9
       and abs(d6["headline"]["day"]["dev_pp"] - (1012 / 1020 - 1015 / 1020) * 100) < 1e-9
       and abs(d6["headline"]["inception"]["dev_pp"] - (-0.3)) < 1e-9
       and abs(d6["headline"]["wtd"]["dev_pp"] - (1012 / 1020 - 1015 / 1020) * 100) < 1e-9,
       f"R3 daily 07-06: độ lệch NAV/ngày/từ đầu/WTD phải đúng số tính tay: {d6['headline']}")
    ok(d6["tier_headline"] == 2 and abs(d6["headline_dev"] - 0.3) < 1e-9
       and d6["action"] == fr.TIER_ACTION[2] and not d6["needs_human_look"],
       f"R3 daily 07-06: bậc 2 (0,3), được bậc {d6['tier_headline']} dev {d6['headline_dev']}")
    d7 = rep["SpaceX_daily_report_2026-07-07.md"]
    ok(d7["headline"]["nav"]["dev_pct"] == 0 and d7["tier_headline"] == 2
       and abs(d7["headline"]["day"]["dev_pp"] - (1030 / 1012 - 1030 / 1015) * 100) < 1e-9
       and "inception" in d7["headline"] and d7["headline"]["inception"]["dev_pp"] == 0,
       f"R3 daily 07-07: NAV không đổi nhưng 'so với hôm trước' lệch ⇒ bậc 2: {d7['headline']}")
    ok("SpaceX_daily_report_2026-07-03.md" in imp["unaffected_reports"],
       "R3: báo cáo trước ngày bị sửa không bị ảnh hưởng")
    wk = rep["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"]
    ok(wk["headline_dev"] == 0 and wk["tier_headline"] == 0 and wk["tier_window"] == 2
       and wk["needs_human_look"] and abs(wk["window_dev"] - (1030 / 1012 - 1030 / 1015) * 100) < 1e-9
       and [x["date"] for x in wk["window"]["days"]] == ["2026-07-06", "2026-07-07"],
       f"R3 weekly: số chính không đổi nhưng số theo ngày lệch bậc 2 ⇒ CẦN NGƯỜI XEM: {wk}")
    ok(wk["literal_hits"] == [{"date": "2026-07-06", "nav_old": 1015000000.0, "lines": [1]}],
       f"R3 weekly: phải thấy dòng trích nguyên NAV cũ (dạng không dấu): {wk['literal_hits']}")
    ok(rep["SpaceX_daily_report_2026-07-06.md"]["literal_hits"][0]["lines"] == [1],
       "R3: NAV cũ dạng 1,015,000,000 cũng phải được tìm thấy")
    d10 = rep["SpaceX_daily_report_2026-07-10.md"]
    ok(d10["headline_dev"] == 0 and d10["window"]["days"] == [] and d10["literal_hits"][0]["lines"] == [2]
       and d10["tier_window"] == 2 and d10["needs_human_look"],
       f"R3 daily 07-10: ngoài kỳ nhưng TRÍCH NGUYÊN NAV cũ (1.015.000.000) ⇒ phải vào danh sách xem: {d10}")
    mo = rep["SpaceX_ZaloPay_monthly_report_2026-07.md"]
    ok(mo["tier_headline"] == 0 and mo["needs_human_look"] and set(mo["headline"]) == {"nav", "mtd", "inception"},
       f"R3 monthly: chỉ đo NAV/MTD/từ đầu; số ngày lệch ⇒ cần người xem: {mo['headline']}")
    ok(set(d6["headline"]) == {"nav", "day", "wtd", "mtd", "inception"}
       and set(wk["headline"]) == {"nav", "wtd", "mtd", "inception"}, "R3: bộ số chính theo loại báo cáo")
    ok(imp["note_next_report"] == ["SpaceX_daily_report_2026-07-06.md", "SpaceX_daily_report_2026-07-07.md"],
       f"R3: bậc 2 ⇒ ghi chú ở báo cáo kế tiếp: {imp['note_next_report']}")
    q = [x["report"] for x in imp["queue_user_decision"]]
    ok(q == ["SpaceX_ZaloPay_monthly_report_2026-07.md", "SpaceX_daily_report_2026-07-10.md",
             "SpaceX_weekly_report_2026-07-06_to_2026-07-10.md",
             "SpaceX_weekly_report_2026-07-06_to_2026-07-10_CORRECTION_VIB.md"],
       f"R3: hàng đợi user = các báo cáo cần người xem: {q}")
    ok(all("người phải xem" in x["why"] for x in imp["queue_user_decision"]),
       "R3: lý do trong hàng đợi phải nói rõ việc của người")
    ok(len(imp["fix_forward_only"]) == 4 and imp["changed_rows"] == [
        {"date": "2026-07-06", "nav_old": 1015000000.0, "nav_new": 1012000000.0}],
       f"R3: changed_rows / fix_forward_only sai: {imp['changed_rows']} {imp['fix_forward_only']}")
    ok(imp["generated_at_ict"].endswith("+07:00") and imp["ledger_binding"] is None
       and imp["old_nav_history_md5"] == md5(w.nav_path.read_bytes()),
       "R3: giờ tạo ICT, md5 nav_history cũ, không gắn sổ khi không truyền --sealed-ledger")
    ok("KHÔNG gửi, KHÔNG sửa, KHÔNG phát hành lại" in p.stdout and "CẦN USER QUYẾT: 4" in p.stdout
       and "⚠ CẦN NGƯỜI XEM" in p.stdout and "KHÔNG đọc được kỳ" in p.stdout
       and "bỏ qua 1 file không phải .md" in p.stdout,
       f"R3: bảng in phải có hàng đợi + cảnh báo tên hỏng + file bỏ qua: {p.stdout[-600:]}")
    ok(w.nav_path.read_bytes() == fr.write_nav_table(FIELDS, [row(d, v) for d, v in NAV], "\r\n"),
       "R3: impact CHỈ ĐỌC — nav_history không đổi byte nào")

    # Bậc 3 và bậc 1.
    _, imp3, _ = w.impact(w.correction([replace_item("2026-07-06", 1015, 1007)], "c3.json"), out="i3.json")
    r3 = by_name(imp3)
    ok(r3["SpaceX_daily_report_2026-07-06.md"]["tier_headline"] == 3
       and r3["SpaceX_daily_report_2026-07-06.md"]["action"] == fr.TIER_ACTION[3]
       and imp3["queue_user_decision"][0]["report"] == "SpaceX_daily_report_2026-07-06.md"
       and "bậc 3" in imp3["queue_user_decision"][0]["why"] and imp3["note_next_report"] == [],
       f"R3 bậc 3: phải vào hàng đợi phát hành lại: {imp3['queue_user_decision'][:2]}")
    _, imp1, _ = w.impact(w.correction([replace_item("2026-07-06", 1015, 1014.9)], "c1.json"), out="i1.json")
    r1 = by_name(imp1)
    ok(r1["SpaceX_daily_report_2026-07-06.md"]["tier_headline"] == 1 and imp1["note_next_report"] == []
       and r1["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"]["tier_window"] == 1
       and not r1["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"]["needs_human_look"],
       "R3 bậc 1: sửa từ nay; số ngày lệch dưới 0,05 không gọi người")
    ok([x["report"] for x in imp1["queue_user_decision"]] == ["SpaceX_daily_report_2026-07-10.md"]
       or imp1["queue_user_decision"] == [],
       f"R3 bậc 1: hàng đợi không có báo cáo tuần/tháng: {imp1['queue_user_decision']}")

    # Sửa DÒNG CUỐI ⇒ báo cáo tháng (asof cuối tháng) đổi số chính.
    _, impl, _ = w.impact(w.correction([replace_item("2026-07-14", 1065, 1062)], "cl.json"), out="il.json")
    mo = by_name(impl)["SpaceX_ZaloPay_monthly_report_2026-07.md"]
    ok(mo["tier_headline"] == 2 and abs(mo["headline"]["inception"]["dev_pp"] + 0.3) < 1e-9
       and abs(mo["headline"]["mtd"]["dev_pp"] + 0.3) < 1e-9 and impl["n_reports_affected"] == 1,
       f"R3: sửa dòng cuối ⇒ MTD/từ đầu của báo cáo tháng lệch 0,3: {mo['headline']}")


# ------------------------------------------------------------------ R4. chèn / xoá dòng, dòng tiền lùi
def r4_insert_delete_flows(tmp):
    w = World(tmp, "r4", nav=[x for x in NAV if x[0] != "2026-07-08"])
    ins = {"op": "insert", "date": "2026-07-08", "row": row("2026-07-08", 1040, est="True"),
           "reason": "thiếu dòng phiên", "evidence": "dnse_raw có balances 19:10"}
    p, imp, _ = w.impact(w.correction([ins]))
    rep = by_name(imp)
    wk = rep["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"]
    ok(p.returncode == 0 and wk["headline_dev"] == 0 and wk["window"]["rows_added_or_removed"] == 1
       and wk["needs_human_look"] and wk["window"]["days"][0] == {
           "date": "2026-07-08", "change": "thêm dòng", "nav_old": None, "nav_new": 1040000000.0},
       f"R4 chèn: báo cáo tuần có dòng thêm ⇒ cần người xem: {wk['window']}")
    ok(abs(wk["window_dev"] - abs((1035 / 1040 - 1035 / 1030) * 100)) < 1e-9 and wk["tier_window"] == 3,
       f"R4 chèn: tỉ suất ngày 07-09 đổi mốc so sánh ⇒ lệch {wk['window_dev']}")
    ok("SpaceX_daily_report_2026-07-10.md" in imp["unaffected_reports"]
       and imp["changed_rows"] == [{"date": "2026-07-08", "nav_old": None, "nav_new": 1040000000.0}],
       "R4 chèn: báo cáo ngày 07-10 không đổi; changed_rows ghi dòng thêm")
    w2 = World(tmp, "r4_del")
    dele = {"op": "delete", "date": "2026-07-08", "expect": {"nav": "1040000000"},
            "reason": "dòng trùng", "evidence": "x"}
    _, imp2, _ = w2.impact(w2.correction([dele]))
    wk2 = by_name(imp2)["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"]
    ok(wk2["window"]["days"][0]["change"] == "bỏ dòng" and wk2["needs_human_look"], "R4 xoá: dòng bị bỏ được nêu")

    # (sổ cũ, sổ mới) bằng hai thư mục — cùng kết quả với file đính chính.
    new_dir = w.dir / "new_logs"
    new_dir.mkdir()
    (new_dir / "nav_history_SpaceX.csv").write_bytes(fr.write_nav_table(
        FIELDS, sorted([row(d, v) for d, v in NAV if d != "2026-07-08"] + [ins["row"]],
                       key=lambda r: r["date"]), "\r\n"))
    p, imp_dir, _ = w.impact(new_nav_dir=str(new_dir), out="impact_dir.json")
    strip = lambda j: {k: v for k, v in j.items()            # noqa: E731
                       if k not in ("generated_at_ict", "correction_md5", "corrections_applied")}
    ok(p.returncode == 0 and strip(imp_dir) == strip(imp),
       "R4: đo bằng (thư mục cũ, thư mục mới) phải ra ĐÚNG kết quả của file đính chính")
    ok(imp_dir["correction_md5"] is None and imp["correction_md5"] is not None, "R4: correction_md5 chỉ có ở chế độ file")

    # Khai dòng tiền LÙI NGÀY (sổ dòng tiền mới) ⇒ tỉ suất các báo cáo sau đó đổi.
    w3 = World(tmp, "r4_flow")
    new_flows = str(w3.dir / "flows_new.json")
    w3.write_flows([{"date": "2026-07-06", "time_ict": "16:00", "amount_vnd": 100_000_000,
                     "kind": "deposit", "evidence": "sao kê"}], new_flows)
    p, imp3, _ = w3.impact(new_nav_dir=str(w3.nav_dir), extra=("--new-flows-path", new_flows))
    r3 = by_name(imp3) if imp3 else {}
    mo = r3.get("SpaceX_ZaloPay_monthly_report_2026-07.md", {})
    # Tính tay: 100tr vào SAU đóng cửa 07-06 ⇒ giá đơn vị 07-06 = (1015 − 100)/1000 × 10.000 (số
    # đơn vị tới đó vẫn là 100.000); sau đó không còn dòng tiền ⇒ giá đi theo NAV: × 1065/1015.
    want = ((915 / 1000) * (1065 / 1015) - 1065 / 1000) * 100
    ok(p.returncode == 0 and mo.get("tier_headline") == 3
       and abs(mo["headline"]["inception"]["dev_pp"] - want) < 1e-9 and imp3["changed_rows"] == [],
       f"R4 dòng tiền lùi: tỉ suất từ đầu của báo cáo tháng phải lệch {want:.4f} điểm %, được {mo.get('headline')}")
    ok("SpaceX_daily_report_2026-07-03.md" in imp3["unaffected_reports"],
       "R4 dòng tiền lùi: báo cáo trước ngày dòng tiền không đổi")


# ------------------------------------------------------------------ R5. file đính chính hỏng
def r5_correction_validation(tmp):
    w = World(tmp, "r5")
    table = [row(d, v) for d, v in NAV]
    good = replace_item("2026-07-06", 1015, 1012)

    def bad(items, needle, account=None, label=""):
        path = w.correction(items, "bad.json", account=account)

        def run():
            parsed, _ = fr.load_correction(path, "SpaceX")
            fr.apply_corrections(FIELDS, table, parsed)
        raises(fr.RestatementError, run, f"R5 {label or needle}", needle)

    bad([good], "của tài khoản 'ZaloPay'", account="ZaloPay", label="§12 file của tài khoản khác")
    bad([], "list không rỗng")
    bad([dict(good, op="update")], "op phải là replace | insert | delete")
    for key in ("reason", "evidence", "date"):
        bad([{k: v for k, v in good.items() if k != key}], f"thiếu {key}")
    bad([dict(good, reason="   ")], "thiếu reason")
    bad([dict(good, date="06/07/2026")], "không phải YYYY-MM-DD")
    bad([good, dict(good)], "xuất hiện hai lần")
    bad([{k: v for k, v in good.items() if k != "expect"}], "cần expect")
    bad([dict(good, set={})], "replace cần set")
    bad([dict(good, expect={"nav": "1014000000"})],
        ["KHÁC expect", "đọc được '1015000000'", "expect '1014000000'"], label="expect lệch")
    bad([dict(good, date="2026-07-15")], "không có dòng ngày này")
    bad([dict(good, set={"nav": "1012000000"})], ["vỡ bất biến", "-3,000,000"], label="vỡ bất biến nav")
    bad([dict(good, set=dict(good["set"], gia_la="1"))], "cột lạ")
    bad([dict(good, set=dict(good["set"], date="2026-07-05"))], "đổi cột date")
    bad([dict(good, set=dict(good["set"], balance_ts="hôm qua"))], "balance_ts 'hôm qua' không đọc được")
    bad([dict(good, set=dict(good["set"], balance_ts=""))], "thiếu balance_ts")
    bad([dict(good, set={"nav": "nan", "mtm_stock": "nan"})], "không hữu hạn")
    ins = {"op": "insert", "date": "2026-07-06", "row": row("2026-07-06", 1012), "reason": "r", "evidence": "e"}
    bad([ins], "ĐÃ có dòng ngày này")
    bad([dict(ins, date="2026-07-15", row=row("2026-07-16", 1070))], "khác date")
    short = row("2026-07-15", 1070)
    del short["cash"]
    bad([dict(ins, date="2026-07-15", row=short)], "thiếu cột ['cash']")
    bad([{"op": "insert", "date": "2026-07-15", "reason": "r", "evidence": "e"}], "insert cần row")
    p = w.dir / "bad.json"
    p.write_text("{", encoding="utf-8")
    raises(fr.RestatementError, lambda: fr.load_correction(str(p), "SpaceX"), "R5 JSON hỏng", "không đọc được file đính chính")
    # Áp lại lên bảng ĐÃ sửa ⇒ `already`, không lỗi, không sửa lần hai.
    items, _ = fr.load_correction(w.correction([good, dict(ins, date="2026-07-15", row=row("2026-07-15", 1070))]), "SpaceX")
    once, ch1 = fr.apply_corrections(FIELDS, table, items)
    twice, ch2 = fr.apply_corrections(FIELDS, once, items)
    ok(once == twice and all(c.get("already") for c in ch2) and not any(c.get("already") for c in ch1)
       and [r["date"] for r in once][-1] == "2026-07-15" and len(once) == len(table) + 1,
       "R5: áp lần hai lên bảng đã sửa phải là không-đổi (already)")
    ok(table == [row(d, v) for d, v in NAV], "R5: apply_corrections không được sửa bảng đầu vào")


# ------------------------------------------------------------------ R6. apply
def r6_apply(tmp):
    w = World(tmp, "r6")
    before = w.nav_path.read_bytes()
    corr = w.correction([replace_item("2026-07-06", 1015, 1012)])
    p, imp, imp_path = w.impact(corr)
    log = w.nav_dir / fr.AUDIT_LOG
    # Báo cáo tác động của bản đính chính KHÁC ⇒ từ chối.
    other = w.correction([replace_item("2026-07-06", 1015, 1011)], "other.json")
    r = w.apply(other, imp_path)
    ok(r.returncode == 2 and "không phải của" in r.stderr and w.nav_path.read_bytes() == before
       and not log.exists(), f"R6: báo cáo tác động của file đính chính khác ⇒ rc=2, không ghi: {r.stderr[:200]}")
    r = w.apply(corr, imp_path, approved_by="  ")
    ok(r.returncode == 2 and "--approved-by" in r.stderr and w.nav_path.read_bytes() == before,
       "R6: thiếu người duyệt ⇒ rc=2")
    junk = w.dir / "junk.json"
    junk.write_text(json.dumps({"account": "SpaceX"}), encoding="utf-8")
    r = w.apply(corr, str(junk))
    ok(r.returncode == 2 and "không phải báo cáo tác động" in r.stderr, "R6: báo cáo tác động thiếu khoá ⇒ rc=2")

    r = w.apply(corr, imp_path)
    after = w.nav_path.read_bytes()
    ok(r.returncode == 0 and "ĐÃ ÁP 1 đính chính" in r.stdout and md5(after) == imp["new_nav_history_md5"],
       f"R6: apply phải rc=0 và ra đúng md5 đã đo: {r.stdout[-200:]} {r.stderr[-200:]}")
    old_lines, new_lines = before.split(b"\r\n"), after.split(b"\r\n")
    changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
    ok(len(old_lines) == len(new_lines) and changed == [3] and b"\r\n" in after
       and new_lines[3].startswith(b"2026-07-06,1012000000,912000000,"),
       f"R6: chỉ ĐÚNG dòng 07-06 đổi, mọi dòng khác giữ nguyên byte (kể cả CRLF): {changed}")
    recs = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    rec = recs[0]
    ok(len(recs) == 1 and rec["account"] == "SpaceX" and rec["approved_by"] == "user 2026-10-14"
       and rec["md5_before"] == md5(before) and rec["md5_after"] == md5(after)
       and rec["correction_md5"] == md5(Path(corr).read_bytes())
       and rec["impact_report_md5"] == md5(Path(imp_path).read_bytes())
       and rec["applied_at_ict"].endswith("+07:00"), f"R6: nhật ký đính chính thiếu trường: {rec}")
    c = rec["changes"][0]
    ok(c["old"]["nav"] == "1015000000" and c["new"]["nav"] == "1012000000" and c["reason"] == "đếm trùng một lô"
       and c["evidence"] == "dnse_raw + journal", "R6: nhật ký giữ dòng cũ + dòng mới + lý do + bằng chứng")
    r = w.apply(corr, imp_path)
    ok(r.returncode == 0 and "ĐÃ ÁP từ trước" in r.stdout and w.nav_path.read_bytes() == after
       and len(log.read_text(encoding="utf-8").splitlines()) == 1,
       "R6: áp lần hai = không làm gì, không thêm dòng nhật ký")

    # nav_history đổi sau khi đo tác động ⇒ từ chối.
    w2 = World(tmp, "r6_stale")
    corr2 = w2.correction([replace_item("2026-07-06", 1015, 1012)])
    _, _, imp2 = w2.impact(corr2)
    w2.write_nav([row(d, v) for d, v in NAV] + [row("2026-07-15", 1070)])
    stale = w2.nav_path.read_bytes()
    r = w2.apply(corr2, imp2)
    ok(r.returncode == 2 and "đã đổi từ lúc đo" in r.stderr and w2.nav_path.read_bytes() == stale
       and not (w2.nav_dir / fr.AUDIT_LOG).exists(),
       f"R6: nav_history đổi sau khi đo ⇒ rc=2, không ghi: {r.stderr[:200]}")

    # File LF (không CRLF) cũng giữ nguyên dấu xuống dòng.
    w3 = World(tmp, "r6_lf", terminator="\n")
    corr3 = w3.correction([replace_item("2026-07-06", 1015, 1012)])
    _, _, imp3 = w3.impact(corr3)
    r = w3.apply(corr3, imp3)
    ok(r.returncode == 0 and b"\r" not in w3.nav_path.read_bytes(), "R6: file LF phải vẫn là LF sau khi áp")

    # Thư mục dữ liệu thật: cần --real-data. Gọi main() trong tiến trình với NAV_HISTORY_DIR giả.
    w4 = World(tmp, "r6_real")
    corr4 = w4.correction([replace_item("2026-07-06", 1015, 1012)])
    _, _, imp4 = w4.impact(corr4)
    kept = w4.nav_path.read_bytes()
    orig = nul.NAV_HISTORY_DIR
    nul.NAV_HISTORY_DIR = str(w4.nav_dir)
    try:
        base = ["apply", "--account", "SpaceX", "--correction", corr4, "--impact-report", imp4,
                "--approved-by", "user"]
        rc = fr.main(base + ["--nav-dir", str(w4.nav_dir)])
        ok(rc == 3 and w4.nav_path.read_bytes() == kept and not (w4.nav_dir / fr.AUDIT_LOG).exists(),
           f"R6: ghi thư mục thật không --real-data ⇒ rc=3, không ghi, được rc={rc}")
        link = w4.dir / "link"
        os.symlink(w4.nav_dir, link)
        ok(fr.main(base + ["--nav-dir", str(link)]) == 3 and w4.nav_path.read_bytes() == kept,
           "R6: thư mục thật qua symlink cũng bị từ chối")
        ok(fr.main(base + ["--nav-dir", str(w4.nav_dir), "--real-data"]) == 0
           and w4.nav_path.read_bytes() != kept, "R6: có --real-data thì áp được (mọi kiểm tra khác vẫn chạy)")
    finally:
        nul.NAV_HISTORY_DIR = orig

    # Chết giữa nhật ký và file ⇒ chạy lại ghi nốt file, không ghi bản ghi nhật ký thứ hai.
    w5 = World(tmp, "r6_crash")
    corr5 = w5.correction([replace_item("2026-07-06", 1015, 1012)])
    _, imp5d, imp5 = w5.impact(corr5)
    args = ["apply", "--account", "SpaceX", "--nav-dir", str(w5.nav_dir), "--correction", corr5,
            "--impact-report", imp5, "--approved-by", "user"]
    real_replace = os.replace
    os.replace = lambda a, b: (_ for _ in ()).throw(OSError("mất điện (giả lập)"))
    try:
        raises(OSError, lambda: fr.cmd_apply(fr.argparse.Namespace(
            account="SpaceX", nav_dir=str(w5.nav_dir), correction=corr5, impact_report=imp5,
            approved_by="user", real_data=False)), "R6: chết khi thay file", "mất điện")
    finally:
        os.replace = real_replace
    log5 = w5.nav_dir / fr.AUDIT_LOG
    ok(len(log5.read_text(encoding="utf-8").splitlines()) == 1
       and md5(w5.nav_path.read_bytes()) == imp5d["old_nav_history_md5"]
       and not [x for x in w5.nav_dir.iterdir() if ".tmp." in x.name],
       "R6 chết giữa chừng: nhật ký có 1 dòng, nav_history chưa đổi, không sót file tạm")
    ok(fr.main(args) == 0 and md5(w5.nav_path.read_bytes()) == imp5d["new_nav_history_md5"]
       and len(log5.read_text(encoding="utf-8").splitlines()) == 1,
       "R6: chạy lại ghi nốt nav_history, KHÔNG thêm dòng nhật ký thứ hai")
    log5.write_text(log5.read_text(encoding="utf-8") + "{hỏng\n", encoding="utf-8")
    w5.write_nav([row(d, v) for d, v in NAV])
    ok(fr.main(args) == 2, "R6: nhật ký hỏng dòng cuối ⇒ rc=2, không ghi tiếp")


# ------------------------------------------------------------------ R7. CLI + bất biến công cụ
def r7_cli_and_guards(tmp):
    w = World(tmp, "r7")
    corr = w.correction([replace_item("2026-07-06", 1015, 1012)])
    base = ["impact", "--account", "SpaceX", "--old-nav-dir", str(w.nav_dir), "--inception-path", w.inc,
            "--flows-path", w.flows, "--reports-dir", str(w.reports)]
    p = w.cli(*base)
    ok(p.returncode == 2 and "ĐÚNG MỘT" in p.stderr, "R7: thiếu cả --correction lẫn --new-nav-dir ⇒ rc=2")
    p = w.cli(*base, "--correction", corr, "--new-nav-dir", str(w.nav_dir))
    ok(p.returncode == 2 and "ĐÚNG MỘT" in p.stderr, "R7: truyền cả hai ⇒ rc=2")
    p = w.cli(*base, "--correction", str(w.dir / "khong_co.json"))
    ok(p.returncode == 2 and "LỖI fund_restatement" in p.stderr, "R7: thiếu file đính chính ⇒ rc=2")
    p = w.cli(*[x if x != "SpaceX" else "NoSuch" for x in base], "--correction", corr)
    ok(p.returncode == 2, "R7: tài khoản không có nav_history ⇒ rc=2")
    os.remove(w.flows)
    p = w.cli(*base, "--correction", corr)
    ok(p.returncode == 2 and "KHÔNG có sổ dòng tiền" in p.stderr,
       f"R7: thiếu sổ dòng tiền ⇒ từ chối (không đoán []), được rc={p.returncode} {p.stderr[:200]}")
    w.write_flows([])
    p = w.cli(*base, "--correction", corr, "--all")
    ok(p.returncode == 0 and "không đổi: SpaceX_daily_report_2026-07-03.md" in p.stdout, "R7: --all in cả báo cáo không đổi")
    # nav_history hỏng.
    w.nav_path.write_bytes(b"date,gia\r\n2026-07-02,1\r\n")
    p = w.cli(*base, "--correction", corr)
    ok(p.returncode == 2 and "thiếu cột date/nav" in p.stderr, "R7: nav_history thiếu cột ⇒ rc=2")
    w.write_nav([row("2026-07-03", 1020), row("2026-07-02", 1010)])
    p = w.cli(*base, "--correction", corr)
    ok(p.returncode == 2 and "không tăng nghiêm ngặt" in p.stderr, "R7: nav_history lộn ngày ⇒ rc=2")
    # Công cụ không có đường GỬI/phát hành nào: không import thứ gì gửi được ra ngoài.
    src = (BIN / "fund_restatement.py").read_text(encoding="utf-8")
    body = src.split('"""', 2)[2]
    ok(not any(x in body for x in ("subprocess", "smtplib", "requests", "urllib", "notify", "discord",
                                   "send_report", "append_event")),
       "R7: mã nguồn công cụ không được chứa đường gửi/thông báo nào")
    ok("--force" not in body, "R7: không có cờ --force")
    # TZ: mọi mốc giờ của công cụ neo ICT tường minh.
    ok("datetime.datetime.now(ICT)" in body and "datetime.now()" not in body
       and "date.today()" not in body, "R7 §16: không có now()/today() trần")


# ------------------------------------------------------------------ R8. các ca bộ mutant chỉ ra còn hở
def r8_gaps(tmp):
    # NAV cuối kỳ lệch bậc 2 trong khi MỌI tỉ suất chỉ lệch bậc 1 (tài khoản đang lỗ sâu: lệch
    # tỉ suất = lệch NAV × giá đơn vị/10.000) ⇒ số chính phải lấy cả lệch NAV.
    deep = NAV[:-1] + [("2026-07-14", 500)]
    w = World(tmp, "r8_deep", nav=deep)
    p, imp, _ = w.impact(w.correction([replace_item("2026-07-14", 500, 500.3)]))
    mo = by_name(imp)["SpaceX_ZaloPay_monthly_report_2026-07.md"] if imp else {}
    ok(p.returncode == 0 and abs(mo["headline"]["nav"]["dev_pct"] - 0.06) < 1e-9
       and abs(mo["headline"]["inception"]["dev_pp"] - 0.03) < 1e-9
       and abs(mo["headline_dev"] - 0.06) < 1e-9 and mo["tier_headline"] == 2,
       f"R8: NAV lệch 0,06% (bậc 2) dù tỉ suất chỉ lệch 0,03 điểm % ⇒ bậc 2: {mo.get('headline')}")

    # Chèn một dòng mà KHÔNG số ngày nào đổi (NAV dòng chèn = NAV phiên trước) ⇒ window = 0,
    # nhưng kỳ báo cáo có thêm một dòng NAV ⇒ vẫn phải có người xem.
    w = World(tmp, "r8_flat_insert", nav=[x for x in NAV if x[0] != "2026-07-08"])
    ins = {"op": "insert", "date": "2026-07-08", "row": row("2026-07-08", 1030),
           "reason": "thiếu dòng phiên", "evidence": "dnse_raw"}
    p, imp, _ = w.impact(w.correction([ins]))
    wk = by_name(imp)["SpaceX_weekly_report_2026-07-06_to_2026-07-10.md"] if imp else {}
    ok(p.returncode == 0 and wk["window_dev"] == 0 and wk["tier_window"] == 0 and wk["headline_dev"] == 0
       and wk["affected"] and wk["needs_human_look"] and wk["window"]["rows_added_or_removed"] == 1
       and any(q["report"] == wk["report"] and "1 dòng NAV thêm/bỏ" in q["why"]
               for q in imp["queue_user_decision"]),
       f"R8: dòng chèn không đổi số nào vẫn phải vào hàng đợi người xem: {wk}")

    # Sửa cột KHÔNG phải nav (balance_ts) ⇒ dòng vẫn phải nằm trong changed_rows; không báo cáo nào lệch.
    w = World(tmp, "r8_ts_only")
    item = {"op": "replace", "date": "2026-07-06", "expect": {"nav": "1015000000"},
            "set": {"balance_ts": "2026-07-06T14:45:00"}, "reason": "giờ chụp", "evidence": "x"}
    p, imp, _ = w.impact(w.correction([item]))
    ok(p.returncode == 0 and imp["changed_rows"] == [
        {"date": "2026-07-06", "nav_old": 1015000000.0, "nav_new": 1015000000.0}]
       and imp["n_reports_affected"] == 0 and imp["old_nav_history_md5"] != imp["new_nav_history_md5"],
       f"R8: sửa riêng balance_ts ⇒ changed_rows có dòng đó, 0 báo cáo lệch: {imp and imp['changed_rows']}")

    # nav_history ngày lộn xộn / trùng ⇒ từ chối, không đo trên dữ liệu hỏng.
    for label, rows in (("lộn xộn", [row("2026-07-03", 1020), row("2026-07-02", 1010)]),
                        ("trùng", [row("2026-07-02", 1010), row("2026-07-02", 1011)])):
        w = World(tmp, f"r8_bad_{label}")
        w.write_nav(rows)
        p, imp, _ = w.impact(w.correction([replace_item("2026-07-02", 1010, 1009)]))
        # Thông điệp phải là của CHÍNH công cụ này (đọc bảng, trước khi áp đính chính lên một bảng
        # có ngày trùng) — tầng dưới (account_cash_flows) cũng chặn nhưng bằng câu khác.
        ok(p.returncode == 2 and "cột date không tăng nghiêm ngặt" in p.stderr,
           f"R8: nav_history ngày {label} phải rc=2, được rc={p.returncode} {p.stderr[-200:]}")

    # apply một lệnh XOÁ hai lần: lần hai nhận ra đã áp, không lỗi, không đổi gì.
    w = World(tmp, "r8_delete_twice")
    c = w.correction([{"op": "delete", "date": "2026-07-08", "expect": {"nav": "1040000000"},
                       "reason": "dòng trùng", "evidence": "x"}])
    _, _, out = w.impact(c)
    a1 = w.apply(c, out)
    after = w.nav_path.read_bytes()
    a2 = w.apply(c, out)
    log = (w.nav_dir / fr.AUDIT_LOG).read_text(encoding="utf-8").splitlines()
    ok(a1.returncode == 0 and b"2026-07-08" not in after and a2.returncode == 0
       and "ĐÃ ÁP từ trước" in a2.stdout and w.nav_path.read_bytes() == after and len(log) == 1,
       f"R8: xoá hai lần — lần hai phải rc=0 'ĐÃ ÁP từ trước', được rc={a2.returncode} {a2.stderr[-200:]}")


def main():
    with tempfile.TemporaryDirectory(prefix="fund_restatement_selfcheck_") as tmp:
        r1_tier()
        r2_report_names(tmp)
        r3_replace(tmp)
        r4_insert_delete_flows(tmp)
        r5_correction_validation(tmp)
        r6_apply(tmp)
        r7_cli_and_guards(tmp)
        r8_gaps(tmp)
    if FAILS:
        print(f"FAIL — {len(FAILS)}/{N} assertion hỏng (fund_restatement_selfcheck.py)")
        return 1
    print(f"OK — {N} assertion PASS (fund_restatement_selfcheck.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
