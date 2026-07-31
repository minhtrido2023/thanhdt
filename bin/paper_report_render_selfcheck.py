#!/usr/bin/env python3
"""Selfcheck cho TẦNG RENDER của paper_programs_daily_report.py (redesign 2026-07-31).

Chạy hoàn toàn trên fixture trong tmpdir (WC_ROOT/CHARTER_DIR/STATE_PATH bị trỏ lại) — không
đụng dữ liệu thật, không gọi probe thật. Kiểm 3 nhóm tính chất mà redesign hứa:
  A. "Giao dịch hôm nay" phân biệt được CÓ / KHÔNG CÓ / n/a-chưa-đo-được (không nhập nhèm)
  B. Cảnh báo không bao giờ trần: có giải thích → WATCH, không giải thích → RED; phiên lỗi
     toàn tập (0 lệnh + N lỗi) → RED chứ không phải "ngày yên ả"
  C. Không lặp lại nội dung tĩnh: charter tách file, gate chỉ in đầy đủ khi ĐỔI

Usage: python3 mike/bin/paper_report_render_selfcheck.py   (exit 0 = PASS hết)
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_programs_daily_report.py")
FAILS = []


def check(name, cond, extra=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  <<< ' + str(extra)[:400]}")
    if not cond:
        FAILS.append(name)


def load_module(root):
    spec = importlib.util.spec_from_file_location("ppdr_selfcheck", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.WC_ROOT = root
    m.CHARTER_DIR = os.path.join(root, "charter")
    m.CHARTER_REL = "charter"
    m.STATE_PATH = os.path.join(root, "state.json")
    return m


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def run_report(m, root, registry, date, extra=()):
    p = os.path.join(root, "registry.json")
    write(p, json.dumps(registry, ensure_ascii=False))
    argv = ["x", "--registry", p, "--date", date, *extra]
    old = sys.argv
    sys.argv = argv
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = m.main()
        return buf.getvalue(), rc
    finally:
        sys.argv = old


def main():
    root = tempfile.mkdtemp(prefix="ppdr_selfcheck_")
    m = load_module(root)
    D = "2026-07-31"

    # ---- fixtures ----
    jdir = os.path.join(root, "data/execution_logs")
    write(os.path.join(jdir, f"exec_ok_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          f"{D}T09:15:03,PLACE,P1,HPG,sell,C1,100,21750,0,x\n"
          f"{D}T09:15:09,FILL,P1,HPG,sell,C1,100,21750,100,x\n")
    write(os.path.join(jdir, f"exec_broken_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          + "".join(f"{D}T10:46:0{i},PLACE_FAIL,P{i},HPG,buy,,100,21750,0,TypeError\n" for i in range(5)))
    write(os.path.join(jdir, f"exec_quiet_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          f"{D}T09:15:03,GHOST_ORDER,P1,HPG,sell,C1,100,21750,0,x\n")
    write(os.path.join(root, "data/sleeve.csv"),
          "date,turnover,ret\n2026-07-30,0.0,1.5\n" + f"{D},0.0,2.0\n")
    write(os.path.join(root, "data/sleeve_traded.csv"),
          f"date,turnover,ret\n{D},0.12,2.0\n")
    write(os.path.join(root, "data/sleeve_stale.csv"), "date,turnover,ret\n2026-07-29,0.0,1.5\n")
    write(os.path.join(root, "data/sleeve_lag1.csv"), "date,turnover,ret\n2026-07-30,0.0,1.5\n")

    def prog(pid, **kw):
        base = {"id": pid, "name": pid, "owner": "Taylor", "objective": f"MỤC-ĐÍCH-{pid}-DÀI-DÒNG",
                "start": "2026-07-01", "end_or_trigger": "mốc X",
                "probe": {"type": "command", "cmd": ["true"]},
                "today_activity": {"mode": "static", "text": "**Không có giao dịch** — static"},
                "gate_criteria": [{"text": "g1", "status": "pending"},
                                  {"text": "g2", "status": "pass"}]}
        base.update(kw)
        return base

    def act(pid, spec):
        return prog(pid, today_activity=spec)

    print("== A. Giao dịch hôm nay: CÓ / KHÔNG / n-a ==")
    reg = {"version": "t", "programs": [
        act("has_fill", {"mode": "journal", "account": "ok"}),
        act("outage", {"mode": "journal", "account": "broken"}),
        act("quiet", {"mode": "journal", "account": "quiet"}),
        act("missing_journal", {"mode": "journal", "account": "nofile"}),
        act("csv_no_trade", {"mode": "csv_row", "path": "data/sleeve.csv",
                             "zero_when": {"col": "turnover", "zero_value": 0.0},
                             "template": "turnover {turnover:.2%}"}),
        act("csv_traded", {"mode": "csv_row", "path": "data/sleeve_traded.csv",
                           "zero_when": {"col": "turnover", "zero_value": 0.0},
                           "template": "turnover {turnover:.2%}"}),
        act("csv_stale", {"mode": "csv_row", "path": "data/sleeve_stale.csv",
                          "template": "turnover {turnover:.2%}"}),
        act("csv_lag1", {"mode": "csv_row", "path": "data/sleeve_lag1.csv", "lag_days": 1,
                         "template": "turnover {turnover:.2%}"}),
        prog("no_decl", today_activity=None),
    ]}
    out, rc = run_report(m, root, reg, D, ["--no-state"])
    sec = {p["id"]: s for p, s in zip(reg["programs"], out.split("── **")[1:])}
    check("exit 0", rc == 0, rc)
    check("MỌI chương trình đều có dòng 'Giao dịch hôm nay'",
          out.count("💱 Giao dịch hôm nay:") == len(reg["programs"]),
          out.count("💱 Giao dịch hôm nay:"))
    check("có fill → '1 lệnh khớp' + chi tiết mã", "1 lệnh khớp" in sec["has_fill"]
          and "SELL HPG" in sec["has_fill"], sec["has_fill"][:200])
    check("phiên lỗi toàn tập → KHÔNG nói 'Không có giao dịch'",
          "0 lệnh đặt / 5 sự kiện LỖI" in sec["outage"]
          and "**Không có giao dịch**" not in sec["outage"], sec["outage"][:250])
    check("phiên yên thật (0 lệnh, 0 lỗi) → 'Không có giao dịch'",
          "**Không có giao dịch**" in sec["quiet"], sec["quiet"][:200])
    check("thiếu file journal → n/a, KHÔNG suy diễn thành 'không có giao dịch'",
          "n/a — chưa đo được" in sec["missing_journal"]
          and "**Không có giao dịch**" not in sec["missing_journal"], sec["missing_journal"][:250])
    check("csv turnover=0 → 'Không có giao dịch'", "**Không có giao dịch**" in sec["csv_no_trade"])
    check("csv turnover>0 → 'CÓ giao dịch'", "**CÓ giao dịch**" in sec["csv_traded"])
    check("csv thiếu dòng hôm nay → n/a (không mượn dòng cũ để nói 'không có giao dịch')",
          "CHƯA có dòng cho phiên" in sec["csv_stale"]
          and "**Không có giao dịch**" not in sec["csv_stale"], sec["csv_stale"][:250])
    check("lag_days=1 → dòng T-1 là ĐÚNG thiết kế, không báo động",
          "vintage T-1 theo thiết kế" in sec["csv_lag1"]
          and "CHƯA có dòng" not in sec["csv_lag1"], sec["csv_lag1"][:250])
    check("thiếu khai báo today_activity → nói rõ thiếu + badge WATCH",
          "registry chưa khai báo `today_activity`" in sec["no_decl"]
          and "⏳ WATCH" in sec["no_decl"], sec["no_decl"][:250])
    check("phiên lỗi toàn tập → badge RED", "🔴 RED" in sec["outage"], sec["outage"][:120])
    check("header liệt kê chương trình RED", "**CẦN CHÚ Ý NGAY**" in out and "outage" in out.split("\n")[2])

    print("== B. Cảnh báo có ngữ cảnh mức độ ==")
    warn_cmd = ["python3", "-c", "print('journal FAIL/ERROR events: 431')"]
    reg = {"version": "t", "programs": [
        prog("explained", probe={"type": "command", "cmd": warn_cmd},
             attention_notes=[{"match": "journal FAIL/ERROR events", "severity": "watch",
                               "note": "GIẢI-THÍCH-CỦA-REGISTRY"}]),
        prog("unexplained", probe={"type": "command", "cmd": warn_cmd}),
    ]}
    out, _ = run_report(m, root, reg, D, ["--no-state"])
    sec = {p["id"]: s for p, s in zip(reg["programs"], out.split("── **")[1:])}
    check("cảnh báo có giải thích → in note + WATCH",
          "GIẢI-THÍCH-CỦA-REGISTRY" in sec["explained"] and "⏳ WATCH" in sec["explained"],
          sec["explained"][:250])
    check("cảnh báo chưa giải thích → 'CHƯA CÓ GIẢI THÍCH' + RED",
          "CHƯA CÓ GIẢI THÍCH" in sec["unexplained"] and "🔴 RED" in sec["unexplained"],
          sec["unexplained"][:250])

    print("== C. Không lặp nội dung tĩnh (charter + gate) ==")
    en = ("=== EXECUTION-QUALITY REVIEW ===\\n   journal ft-notes: 154 placements\\n"
          "=== GO/NO-GO CHECKLIST (30-06) ===\\n  [ ] BUY window adherence high\\n"
          "  -> if mechanics clean: flip gate")
    reg = {"version": "t", "programs": [
        prog("p1", probe={"type": "command", "cmd": ["python3", "-c", f"print('{en}')"],
                          "drop_regex": [r"ft-notes"]}),
    ]}
    out1, _ = run_report(m, root, reg, D, ["--force-state"])   # lần đầu: có ghi state
    check("charter được sinh ra file riêng",
          os.path.exists(os.path.join(root, "charter", "p1.md")))
    charter = open(os.path.join(root, "charter", "p1.md"), encoding="utf-8").read()
    check("charter chứa mục đích + tiêu chí đầy đủ", "MỤC-ĐÍCH-p1-DÀI-DÒNG" in charter and "g1" in charter)
    check("report KHÔNG paste mục đích đầy đủ nữa", "MỤC-ĐÍCH-p1-DÀI-DÒNG" not in out1)
    check("report link tới charter", "charter/p1.md" in out1)
    check("checklist GO/NO-GO tiếng Anh bị lược",
          "BUY window adherence high" not in out1 and "checklist GO/NO-GO tiếng Anh" in out1, out1[-800:])
    check("drop_regex bỏ đúng dòng", "ft-notes" not in out1 and "lược 1 dòng phụ lục" in out1)

    # Regression: 1 dòng có thể VỪA là nguồn headline VỪA bị drop_regex bỏ khỏi phần chi tiết
    # (bỏ vì đã lặp lại ở dòng headline). headline phải khớp trên output GỐC — nếu khớp trên body
    # đã cắt thì con số quan trọng nhất của mục âm thầm rơi mất, thay bằng dòng tiêu đề vô nghĩa.
    reg_h = {"version": "t", "programs": [
        prog("ph", probe={"type": "command", "cmd": ["python3", "-c", f"print('{en}')"],
                          "drop_regex": [r"ft-notes"]},
             headline={"regex": r"journal ft-notes:\s*(.+)$", "template": "ft-notes {0}"}),
    ]}
    outh, _ = run_report(m, root, reg_h, D, ["--no-state"])
    check("headline khớp trên output GỐC dù dòng nguồn bị drop_regex bỏ",
          "ft-notes 154 placements" in outh and "EXECUTION-QUALITY REVIEW ===\n" not in outh.split("📈")[1][:60],
          outh.split("📈")[1][:160] if "📈" in outh else outh[:200])
    check("lần đầu: in gate đầy đủ", "bản đầy đủ" in out1 and "  ⏳ g1" in out1)

    out2, _ = run_report(m, root, reg, D, ["--force-state"])   # lần 2, không đổi gì
    check("ngày thường (gate không đổi): chỉ 1 dòng badge",
          "không đổi từ" in out2 and "bản đầy đủ" not in out2 and "  ⏳ g1" not in out2, out2[:600])
    check("ngày thường: đếm đúng số gate PASS", "**1/2 PASS**" in out2, out2[:600])
    check("charter không bị ghi lại khi registry không đổi", "Charter vừa cập nhật" not in out2)

    reg["programs"][0]["gate_criteria"][0]["status"] = "pass"
    out3, _ = run_report(m, root, reg, D, ["--force-state"])   # đổi status 1 gate
    check("gate ĐỔI → in lại đầy đủ + đánh dấu mục đổi",
          "Gate **ĐỔI hôm nay**" in out3 and "🔔" in out3 and "(trước: pending)" in out3, out3[:900])
    check("charter cập nhật theo registry", "Charter vừa cập nhật" in out3)

    st = json.load(open(os.path.join(root, "state.json"), encoding="utf-8"))
    check("state lưu trạng thái gate để so sánh lần sau",
          st["programs"]["p1"]["gates"]["g1"] == "pass", st)
    before = open(os.path.join(root, "state.json"), encoding="utf-8").read()
    reg["programs"][0]["gate_criteria"][0]["status"] = "fail"
    run_report(m, root, reg, D, ["--no-state"])
    check("--no-state KHÔNG ghi đè state production",
          open(os.path.join(root, "state.json"), encoding="utf-8").read() == before)
    out4, _ = run_report(m, root, reg, D, ["--no-state"])
    check("gate FAIL → badge RED", "🔴 RED" in out4, out4[:300])

    print("== D. 3 lỗ hổng quant-skeptic bắt được (verify_20260731_051111, REFUTED trước fix) ==")
    # D1 — idx==0 (dòng ĐẦU TIÊN của chuỗi unchanged_vs_prev) không có phiên trước để đối chiếu:
    # trước đây rơi vào nhánh else, tuyên bố "CÓ giao dịch" từ 0 bằng chứng.
    write(os.path.join(root, "data/sleeve_firstrow.csv"), f"date,nav\n{D},1000000000\n")
    reg_d1 = {"version": "t", "programs": [
        act("first_row", {"mode": "csv_row", "path": "data/sleeve_firstrow.csv",
                          "zero_when": {"col": "nav", "unchanged_vs_prev": True},
                          "template": "NAV {nav}"}),
    ]}
    outd1, _ = run_report(m, root, reg_d1, D, ["--no-state"])
    check("D1: dòng đầu tiên chuỗi unchanged_vs_prev → n/a, KHÔNG tuyên bố 'CÓ giao dịch'",
          "n/a — chưa so sánh được" in outd1 and "**CÓ giao dịch**" not in outd1, outd1[:400])

    # D2 — phiên chỉ toàn NO_QUOTE (mất quote, không FAIL/ERROR literal trong tên event): trước
    # đây lọt qua check `bad` (chỉ soi substring FAIL/ERROR) và bị coi là "ngày yên ả" y hệt calm
    # thật, dù executor không hề quan sát được giá để hành động.
    write(os.path.join(jdir, f"exec_noquote_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          + "".join(f"{D}T10:{i:02d}:00,NO_QUOTE,P{i},HPG,buy,,100,0,0,thieu quote\n" for i in range(20)))
    reg_d2 = {"version": "t", "programs": [
        act("noquote", {"mode": "journal", "account": "noquote"}),
    ]}
    outd2, _ = run_report(m, root, reg_d2, D, ["--no-state"])
    check("D2: phiên toàn NO_QUOTE → RED + KHÔNG tuyên bố 'Không có giao dịch' như ngày calm thật",
          "NO_QUOTE" in outd2 and "🔴 RED" in outd2 and "**Không có giao dịch**" not in outd2,
          outd2[:400])

    # D3 — probe chính kiểu journal_scan (dùng bởi extreme_regime/vol_scale_chase_cap trong
    # registry thật) có marker bắn HÔM NAY (vd EXTREME_SELL/EXTREME_DOWN) phải đẩy qua
    # res["flags"] để badge_of thấy — trước đây probe_journal_scan không set "flags" nên marker
    # bắn thật (10 hit) vẫn hiện badge XANH bình thường, không ai chú ý.
    write(os.path.join(jdir, f"exec_markers_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          + "".join(f"{D}T10:{i:02d}:00,EXTREME_SELL,,HPG,sell,,100,0,0,x\n" for i in range(5))
          + "".join(f"{D}T10:{i:02d}:10,EXTREME_DOWN,,HPG,sell,,100,0,0,x\n" for i in range(5)))
    reg_d3 = {"version": "t", "programs": [
        prog("markers", probe={"type": "journal_scan", "account": "markers",
                               "markers": ["EXTREME_SELL", "EXTREME_DOWN", "EXTREME_PAUSE"]},
             today_activity={"mode": "static", "text": "**Không có giao dịch** — static"}),
    ]}
    outd3, _ = run_report(m, root, reg_d3, D, ["--no-state"])
    check("D3: probe journal_scan marker bắn hôm nay → badge RED (không lọt qua thành XANH)",
          "🔴 RED" in outd3 and "bắn hôm nay" in outd3, outd3[:500])

    print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)}  (tmp: {root})")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
