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
NAV_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_nav_snapshot.py")
FAILS = []
N_RUN = 0  # đếm THẬT số check() đã chạy — đừng gõ tay con số vào commit message (quant-skeptic
           # verify_20260731_052807 bắt được 2 lần liên tiếp commit message ghi sai: 28/28 rồi
           # 31/31 trong khi thực chạy là 31 rồi 34).


def check(name, cond, extra=""):
    global N_RUN
    N_RUN += 1
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

    # Corporate actions have two different failure modes and therefore two different
    # consumers: live NAV must ALWAYS BLOCK (rc=5, qty_change_block) when quantity changes
    # outside a matched order, EVEN when classify_qty_residual returns share_event_credit
    # (daily_nav_snapshot.py ~1236-1241, ~1323); only --from-raw + a CONFIRMED qty_multiplier can
    # rebuild the pre-event quantity. (early_corp_action_price dropped out of master during the
    # 9311ac03 auto-resolve merge; gate v2 is a parallel design, not a deliberate deletion.)
    # The paper report must rebase a frozen entry before comparing
    # it with BQ's retro-adjusted Close.  Keep this small wiring
    # contract here so a later refactor cannot land one half and silently drop the
    # other (BID broker-early case, 2026-08-14; MBB paper-entry case, 2026-08-11).
    print("== 0. Đồng bộ corporate-action live ↔ paper-report ==")
    report_src = open(SRC, encoding="utf-8").read()
    nav_src = open(NAV_SRC, encoding="utf-8").read()
    check("paper report gọi paper_entry_adjust trước khi tính AlphaLens return",
          "import paper_entry_adjust" in report_src
          and "paper_entry_adjust.adjust_entries(" in report_src)
    check("live NAV giữ cổng corp-action v2: def + call site classify_qty_residual, chặn qty_change_block, lưới 5%",
          "def classify_qty_residual(" in nav_src
          and nav_src.count("classify_qty_residual(") >= 2
          and '"gate_verdict": "qty_change_block"' in nav_src
          and "PRICE_XCHECK_TOLERANCE_PCT = 5.0" in nav_src)

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

    print("== A2. Phạm vi báo cáo ==")
    reg_scope = {"version": "t", "programs": [
        prog("shown"),
        prog("completed", name="completed trial", reporting=False,
             reporting_reason="đã hoàn tất"),
    ]}
    out, _ = run_report(m, root, reg_scope, D, ["--no-state"])
    check("entry reporting=false không render section hoặc tổng quan",
          "**1) shown**" in out and "**2) completed trial**" not in out
          and "**completed trial** —" not in out, out[:900])
    check("entry reporting=false được công khai là đã chuyển khỏi báo cáo",
          "Đã chuyển khỏi báo cáo ngày" in out and "completed trial" in out, out[:500])

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

    # D2b (quant-skeptic verify_20260731_052807 đề xuất) — phiên có CẢ PLACE/FILL thật LẪN vài
    # dòng NO_QUOTE (vd 1 lệnh bị thiếu quote, thử lại xong khớp lệnh khác): NO_QUOTE không được
    # phép ghi đè lên 1 ngày CÓ giao dịch thật. Guard `if not (PLACE or fills)` đã bao NO_QUOTE ở
    # bên trong nên về cấu trúc không thể xảy ra — test này khoá lại bằng chứng, chống hồi quy.
    write(os.path.join(jdir, f"exec_mixed_{D}_journal.csv"),
          "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,note\n"
          f"{D}T09:15:03,NO_QUOTE,P1,VNM,sell,,100,0,0,thieu quote lan 1\n"
          f"{D}T09:15:05,PLACE,P1,VNM,sell,C1,100,61200,0,retry ok\n"
          f"{D}T09:15:09,FILL,P1,VNM,sell,C1,100,61200,100,x\n")
    reg_d2b = {"version": "t", "programs": [
        act("mixed", {"mode": "journal", "account": "mixed"}),
    ]}
    outd2b, _ = run_report(m, root, reg_d2b, D, ["--no-state"])
    # Dòng đầu tiên của khối chi tiết chương trình mang badge THẬT; phần dưới report luôn có chú
    # thích cuối trang liệt kê nghĩa của "🔴 RED" nên KHÔNG được grep "🔴 RED" trên toàn bộ đuôi.
    header_line = outd2b.split("── **")[1].split("\n")[0]
    check("D2b: có NO_QUOTE NHƯNG cũng có PLACE/FILL thật → vẫn báo lệnh khớp, KHÔNG bị NO_QUOTE ghi đè",
          "1 lệnh khớp" in outd2b and "SELL VNM" in outd2b and "🔴 RED" not in header_line,
          outd2b[:400])

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

    # ---- E. `_terp_factor_stale` — cái neo bắt lỗi HỒI TỐ CỦA VENDOR (thêm 2026-09-23) ----
    # `Close/Price` = tích hệ số của các sự kiện CÒN Ở TƯƠNG LAI ⇒ phải KHÔNG-GIẢM theo ngày.
    # Ba ca dưới pin đúng cái quyết định dễ sai nhất về sau: NGƯỠNG. Ca E2 là ca đã báo động
    # giả thật khi ngưỡng còn là FACTOR_EPS=1e-6 — nó ở đây để ngưỡng không bị siết lại.
    import duckdb

    def _mkcache(sub, rows):
        d = os.path.join(root, sub, "ticker")
        os.makedirs(d, exist_ok=True)
        con = duckdb.connect()
        vals = ",".join(f"('{t}', DATE '{dd}', {c}, {pp})" for t, dd, c, pp in rows)
        con.execute(f"COPY (SELECT * FROM (VALUES {vals}) AS t(ticker, time, Close, Price)) "
                    f"TO '{os.path.join(d, '2026.parquet')}' (FORMAT PARQUET)")
        con.close()
        return os.path.join(root, sub)

    # E1 — ca FPT thật: r=1,0 tại ngày vào lệnh, 0,909066 về sau (CP thưởng 10% chỉ hồi tố 3 phiên)
    c1 = _mkcache("cache_e1", [("FPT", "2026-06-30", 70200, 70200),
                               ("FPT", "2026-09-11", 72700, 72700),
                               ("FPT", "2026-09-18", 65180, 71700)])
    v1 = m._terp_factor_stale([("FPT", "2026-06-30", 70200.0)], cache_dir=c1)
    hit = v1.get(("FPT", "2026-06-30"))
    check("E1: chuỗi hệ số GIẢM thật (1,0 → 0,909) ⇒ bị bắt, kèm ngày gãy + chặn trên",
          hit is not None and hit[0] == "2026-09-18" and abs(hit[1] - 1.0) < 1e-9
          and abs(hit[2] - 65180 / 71700) < 1e-9, v1)

    # E2 — ca MBB thật: chỉ rung do LÀM TRÒN bước giá (giảm 4,0e-4). KHÔNG được báo động.
    c2 = _mkcache("cache_e2", [("MBB", "2026-06-30", 20180, 25200),
                               ("MBB", "2026-07-08", 20820, 26000)])
    v2 = m._terp_factor_stale([("MBB", "2026-06-30", 25200.0)], cache_dir=c2)
    drop = (20180 / 25200 - 20820 / 26000) / (20180 / 25200)
    check("E2: rung làm tròn (giảm ~4e-4) KHÔNG bị bắt — ngưỡng FACTOR_EPS từng báo động giả ở đây",
          v2 == {} and 0 < drop < m._TERP_DROP_TOL, (v2, drop))

    # E3 — hệ số phẳng (không có sự kiện nào) và ca thiếu dữ liệu: không bắt, không nổ.
    c3 = _mkcache("cache_e3", [("HDB", "2026-06-30", 25850, 25850),
                               ("HDB", "2026-09-18", 27550, 27550),
                               ("ACB", "2026-06-30", 22650, 22650)])
    v3 = m._terp_factor_stale([("HDB", "2026-06-30", 25850.0), ("ACB", "2026-06-30", 22650.0),
                               ("XXX", "2026-06-30", 1000.0)], cache_dir=c3)
    check("E3: hệ số phẳng / <2 dòng / mã không có trong cache ⇒ rỗng, không exception", v3 == {}, v3)

    # E4 — ngưỡng phải tách được HAI mốc đo thật (nhiễu 4,01e-4 vs hỏng 9,09e-2), không kẹp biên.
    check("E4: ngưỡng nằm GIỮA nền nhiễu và tín hiệu thật đã đo (4,01e-4 < tol < 9,09e-2)",
          4.01e-4 < m._TERP_DROP_TOL < 9.09e-2, m._TERP_DROP_TOL)

    # ---- E5/E6 — PHƯƠNG ÁN B: chặn trên PHẢI được ÁP vào chính số dẫn dắt (2026-09-23) ----
    # E1-E4 chỉ pin cái NEO (phát hiện). E5 pin cái HÀNH ĐỘNG: sau khi user duyệt phương án B,
    # tỉ suất dẫn dắt phải tính bằng giá vốn ĐÃ nhân chặn trên, và nhãn phải nói rõ đó là CHẶN
    # DƯỚI. E6 là ca ĐỐI CHỨNG: mã không lệch hệ số thì tuyệt đối không được đụng vào số.
    import shutil
    shutil.copy(os.path.join(os.path.dirname(SRC), "..", "..", "paper_entry_adjust.py"),
                os.path.join(root, "paper_entry_adjust.py"))
    _mkcache("data/bq_cache", [("FPT", "2026-06-30", 70200, 70200),
                               ("FPT", "2026-09-11", 72700, 72700),
                               ("FPT", "2026-09-18", 65180, 71700),
                               ("ACB", "2026-06-30", 22650, 22650),
                               ("ACB", "2026-09-18", 22000, 22000)])
    write(os.path.join(root, "data/alphalens_e5.json"), json.dumps({
        "meta": {"benchmark_entry": 1860.01, "entry_price_asof": "2026-06-30"},
        "positions": [{"ticker": "FPT", "entry_price": 70200.0, "entry_date": "2026-07-01",
                       "lens": "L", "weight_paper": 1.0}]}, ensure_ascii=False))
    write(os.path.join(root, "data/alphalens_e6.json"), json.dumps({
        "meta": {"benchmark_entry": 1860.01, "entry_price_asof": "2026-06-30"},
        "positions": [{"ticker": "ACB", "entry_price": 22650.0, "entry_date": "2026-07-01",
                       "lens": "L", "weight_paper": 1.0}]}, ensure_ascii=False))
    _con = duckdb.connect()
    _con.execute("COPY (SELECT ticker, time, CAST(Close AS DOUBLE) AS Close, "
                 "CAST(VNINDEX AS DOUBLE) AS VNINDEX FROM (VALUES "
                 "('FPT', DATE '2026-09-22', 66600.0, 1816.93), "
                 "('ACB', DATE '2026-09-22', 22000.0, 1816.93)) "
                 "AS t(ticker, time, Close, VNINDEX)) TO "
                 f"'{os.path.join(root, 'data/alphalens_e5_px.parquet')}' (FORMAT PARQUET)")
    _con.close()

    r_min = 65180 / 71700
    # `paper_entry_adjust.DEFAULT_CACHE` neo vào WORKDIR (mặc định cây canonical), KHÔNG vào thư
    # mục chứa module ⇒ copy file vào `root` không đổi cache. Không vá thì E5 đọc cache BQ THẬT:
    # khi vendor hồi tố FPT (entry_adj 70.200→63.820) chặn trên bị áp lên giá vốn đã sửa ⇒ +14,79%
    # thay vì +4,36% — đỏ từ 2026-09-29 (sweep selfcheck-red 2026-10-09). Cùng mẫu với khối F.
    from pathlib import Path as _PathE5
    sys.path.insert(0, root)
    import paper_entry_adjust as _pea_e5
    _old_cache_e5 = _pea_e5.DEFAULT_CACHE
    _pea_e5.DEFAULT_CACHE = _PathE5(root) / "data" / "bq_cache"
    e5 = m.probe_alphalens({"json_path": "data/alphalens_e5.json",
                            "prices_parquet": "data/alphalens_e5_px.parquet"}, {}, D)
    want5 = (66600 / (70200 * r_min) - 1) * 100
    check("E5: có lệch hệ số ⇒ số DẪN DẮT tính bằng giá vốn đã áp chặn trên (+4,36%, không -5,13%)",
          f"{want5:+.2f}%" in e5["headline"] and "≥" in e5["headline"]
          and "CHẶN DƯỚI" in e5["body"] and f"{-5.13:+.2f}%" not in e5["headline"],
          (want5, e5["headline"]))
    check("E5b: body nêu rõ giá vốn cũ→mới và giữ nguyên bằng chứng ngày gãy",
          f"{70200 * r_min:,.0f}" in e5["body"] and "2026-09-18" in e5["body"]
          and "phương án B" in e5["body"], e5["body"][-400:])
    e6 = m.probe_alphalens({"json_path": "data/alphalens_e6.json",
                            "prices_parquet": "data/alphalens_e5_px.parquet"}, {}, D)
    want6 = (22000 / 22650 - 1) * 100
    check("E6 (đối chứng): mã hệ số phẳng ⇒ KHÔNG áp chặn, không có nhãn ≥/CHẶN DƯỚI",
          f"{want6:+.2f}%" in e6["headline"] and "≥" not in e6["headline"]
          and "CHẶN DƯỚI" not in e6["body"], (want6, e6["headline"]))
    _pea_e5.DEFAULT_CACHE = _old_cache_e5

    print("== F. close_repair self_computed KHÔNG bị cap hai lần (Việc nhỏ 2, 2026-09-29) ==")
    # Regression cho commit 2f6ee508/8a9d3ac3 (finding paper-report-fpt-double-adjust-fix-20260929,
    # quant-skeptic CONFIRMED x2): khi close_repair đã tự sửa Close cho MỘT entry
    # (adj_source="self_computed"), `_terp_factor_stale`'s Phương án B (chặn trên) PHẢI bị gate
    # tắt (`already_repaired`) — nếu không, tỉ suất bị sửa HAI LẦN (ca thật FPT 2026-09-29:
    # entry_adj ĐÚNG 63.818,18 bị chặn trên kéo xuống 58.015, báo +9,80% thay vì đúng ~-0,19%).
    # Chạy `close_repair.py` THẬT (không mock công thức) — chỉ mock `corp_action_lib.events()` để
    # không phụ thuộc BQ sống, giữ test hermetic/deterministic (khác các con số "hôm nay" thật sẽ
    # đổi mỗi ngày). File này TRƯỚC batch vá (2f6ee508 lùi lại) fail — headline in "+9.80%".
    from pathlib import Path as _Path
    import types as _types

    _outer_root = os.path.join(os.path.dirname(SRC), "..", "..")
    if _outer_root not in sys.path:
        sys.path.insert(0, _outer_root)

    _fpt_bonus_event = {"ticker": "FPT", "exright_date": "2026-09-21", "event_code": "ISS",
                        "issue_method_name_vi": "Cổ phiếu thưởng", "exercise_ratio": 0.1}

    def _stub_is_price_adjusting(event):
        code = event.get("event_code")
        if code == "DIV":
            return True
        if code != "ISS":
            return False
        return (event.get("issue_method_name_vi") or "").strip() in {
            "Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng", "Quyền mua CP cho Cổ đông hiện hữu"}

    def _stub_events(tickers, since=None, until=None, codes=("DIV", "ISS"), executed_only=True):
        return [e for e in (_fpt_bonus_event,) if e["ticker"] in tickers]

    _cal_stub = _types.ModuleType("corp_action_lib")
    _cal_stub.is_price_adjusting = _stub_is_price_adjusting
    _cal_stub.events = _stub_events
    _old_cal = sys.modules.get("corp_action_lib")
    sys.modules["corp_action_lib"] = _cal_stub
    sys.modules.pop("close_repair", None)   # force reimport under the stub above

    import paper_entry_adjust as _pea_mod
    _old_default_cache = _pea_mod.DEFAULT_CACHE
    _pea_mod.DEFAULT_CACHE = _Path(root) / "data" / "bq_cache"
    try:
        # `_mkcache` (4 cột) không đủ — `_repair_close` cần High/Low để chạy band-guard của
        # close_repair; 0 tắt guard đó một cách hợp lệ (xem `_band_lifted_suspect`). Volume=1
        # (bất kỳ giá trị dương nào, không ảnh hưởng ca này — không có bar nào ở đây chained) chỉ
        # để khớp schema thật (`tav2_bq.ticker` LUÔN có cột Volume — Việc A, dispatch
        # Taylor_20260929_042515); thiếu cột này làm `_repair_close`'s SQL ném BinderException,
        # Layer 2 rơi vào nhánh lỗi im lặng, và cap an toàn cũ bị bật nhầm lại.
        _fcache_dir = os.path.join(root, "data/bq_cache/ticker")
        os.makedirs(_fcache_dir, exist_ok=True)
        _fconn = duckdb.connect()
        _fconn.execute(
            "COPY (SELECT * FROM (VALUES "
            "('FPT', DATE '2026-06-30', 70200, 70200, 0, 0, 1), "   # r=1,0 tại asof — chưa hồi tố
            "('FPT', DATE '2026-09-18', 65180, 71700, 0, 0, 1), "   # r=0,909066 — CÙNG bằng chứng E1
            "('FPT', DATE '2026-09-22', 63700, 63700, 0, 0, 1)) "   # sau ex-date thật, đã hội tụ (r=1,0)
            "AS t(ticker, time, Close, Price, High, Low, Volume)) TO "
            f"'{os.path.join(_fcache_dir, '2026.parquet')}' (FORMAT PARQUET)")
        _fconn.close()
        write(os.path.join(root, "data/alphalens_f.json"), json.dumps({
            "meta": {"benchmark_entry": 1860.01, "entry_price_asof": "2026-06-30"},
            "positions": [{"ticker": "FPT", "entry_price": 70200.0, "entry_date": "2026-07-01",
                          "lens": "L", "weight_paper": 1.0}]}, ensure_ascii=False))
        _conf = duckdb.connect()
        _conf.execute("COPY (SELECT ticker, time, CAST(Close AS DOUBLE) AS Close, "
                     "CAST(VNINDEX AS DOUBLE) AS VNINDEX FROM (VALUES "
                     "('FPT', DATE '2026-09-22', 63700.0, 1780.68)) "
                     "AS t(ticker, time, Close, VNINDEX)) TO "
                     f"'{os.path.join(root, 'data/alphalens_f_px.parquet')}' (FORMAT PARQUET)")
        _conf.close()

        f_entry_adj = 70200.0 / 1.1   # r_pred = 1+exercise_ratio (no cash leg), Close_self = Price/r_pred
        f_want = (63700.0 / f_entry_adj - 1) * 100

        ef = m.probe_alphalens({"json_path": "data/alphalens_f.json",
                                "prices_parquet": "data/alphalens_f_px.parquet"}, {}, D)
        check("F1: close_repair self_computed + raw-cache stale detector CẢ HAI fire ⇒ CHỈ MỘT "
              "lần sửa (ret ≈ -0,19%, KHÔNG +9,80%)",
              f"{f_want:+.2f}%" in ef["headline"] and "+9.80%" not in ef["headline"]
              and "≥" not in ef["headline"], (f_want, ef["headline"]))
        check("F2: body xác nhận cap bị gate tắt (đã sửa qua close_repair, không áp thêm chặn trên)",
              "KHÔNG áp thêm chặn trên" in ef["body"] and "ĐÃ ÁP CHẶN TRÊN" not in ef["body"],
              ef["body"][-400:])
    finally:
        _pea_mod.DEFAULT_CACHE = _old_default_cache
        if _old_cal is not None:
            sys.modules["corp_action_lib"] = _old_cal
        else:
            sys.modules.pop("corp_action_lib", None)
        sys.modules.pop("close_repair", None)

    n_pass = N_RUN - len(FAILS)
    status = f"ALL PASS ({n_pass}/{N_RUN})" if not FAILS else f"FAILED {len(FAILS)}/{N_RUN}: " + ", ".join(FAILS)
    print(f"\n{status}  (tmp: {root})")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
