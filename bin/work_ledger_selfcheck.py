#!/usr/bin/env python3
"""work_ledger_selfcheck.py — selfcheck fixture-based cho work_ledger.py + work_tree_build.py.

Chạy dưới `env -u TZ` và `TZ=America/New_York` (luật §16): ngày "hôm nay" cố định qua Cfg.today, và
today_ict() phải khớp ICT bất kể TZ host. Cuối cùng build THẬT vào file tạm + secret-grep.
Exit 0 = PASS.
"""
import json
import os
import re
import sys
import tempfile
import threading
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import work_ledger as wl  # noqa: E402
import work_tree_build as wb  # noqa: E402

FAILS = []
SECRET_RX = re.compile(r"0002023347|0001743768|0002023348|availableCash|\bNAV\b|\bCAGR\b")


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ((" — " + str(extra)) if (extra and not cond) else ""))
    if not cond:
        FAILS.append(name)


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text if isinstance(text, str) else json.dumps(text, ensure_ascii=False))


def fixture(tmp):
    kb = os.path.join(tmp, "kb")
    write(kb + "/paper_programs_registry.json", {"updated": "2026-10-26", "programs": [
        {"id": "p_open", "name": "Paper mở", "owner": "Taylor", "start": "2026-07-01", "review_date": "2026-10-20 xem lại",
         "objective": "thử tài khoản 0002023347 có availableCash và NAV tốt", "end_or_trigger": "x"},
        {"id": "p_live", "name": "Paper live", "owner": "Taylor", "status": "graduated-live 2026-08-01"},
        {"id": "p_closed", "name": "Paper đóng", "status": "closed 2026-09-01"}]})
    write(kb + "/dashboard_watchlist.json", {"milestones": [
        {"date": "2026-10-01", "label": "Mốc đã qua hạn phải báo", "source": "kb/projects/proj_new.md và kb/khong_co.md"},
        {"date": "2026-12-01", "label": "Mốc tương lai", "source": ""}],
        "research_backlog": [{"id": "bk1", "priority": 1, "idea": "Ý tưởng backlog một", "source": "kb/x.md"}]})
    write(kb + "/structural_break_watch.json", {"opened": "2026-09-10", "owner": "Mike", "next_review": "2026-11-26",
        "events": [{"id": "ev1", "label": "Sự kiện cấu trúc", "status": "triggered", "conclusion": "Giữ nguyên",
                    "next_checks": ["2026-01-01", "2026-12-15"]}]})
    write(kb + "/projects/INDEX.md",
          "## Dự án đã đóng — x\n"
          "- 2026-10-25 Trường phái kỹ thuật → `proj_closed.md` — **NO-GO** (user đóng)\n"
          "  dòng nối tiếp\n"
          "- 2026-09-07 Overlay oshares → `proj_wire.md` — **KHÔNG WIRE** chốt\n"
          "## Dự án ĐANG MỞ, chi tiết\n"
          "- R&D pipeline → `proj_open.md`\n")
    for n, t in (("proj_closed", "# Trường phái kỹ thuật dài tên"), ("proj_wire", "# Overlay"), ("proj_open", "# R&D"),
                 ("proj_new-20261030", "# Dự án mới ngoài INDEX\nNO-GO ở đây")):
        write(kb + "/projects/%s.md" % n, t + "\n")
    q = {"event_id": "e1", "ts": "2026-10-30T01:00:00Z", "agent_id": "Fix", "event_type": "question",
         "topic": "câu hỏi thử", "payload": {}}
    write(tmp + "/bus/inbox/Fix.jsonl", json.dumps(q) + "\n")
    now = time.time()
    write(tmp + "/bus/jobs/Fix_1.json", {"job_id": "Fix_1", "to": "Taylor", "status": "done", "started_at": str(int(now - 86400)),
                                         "prompt_summary": "làm việc proj_open đi"})
    write(tmp + "/bus/jobs/Fix_old.json", {"job_id": "Fix_old", "to": "Taylor", "status": "done",
                                           "started_at": str(int(now - 90 * 86400)), "prompt_summary": "proj_open cũ"})


def main():
    # ICT anchor, độc lập TZ host
    check("today_ict khớp ZoneInfo ICT", wl.today_ict() == datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat())
    check("now_iso mang offset +07:00", wl.now_iso().endswith("+07:00"), wl.now_iso())

    with tempfile.TemporaryDirectory() as tmp:
        led = os.path.join(tmp, "kb", "work_ledger.jsonl")
        fixture(tmp)
        # ---- ledger CRUD
        wl.upsert("proj:proj_open", path=led, branch="Research/Thực thi", status="active", priority=1, owner="Taylor",
                  summary="x" * 200)
        r = wl.read_records(led)[0]
        check("summary cắt ≤160", len(r["summary"]) <= 160)
        wl.add_note("proj:proj_open", "ghi chú 1", by="user", path=led)
        wl.add_note("proj:proj_open", "ghi chú 2", by="mike", path=led)
        f = wl.fold(path=led)["proj:proj_open"]
        check("notes nối thêm, field sau thắng", len(f["notes"]) == 2 and f["priority"] == 1 and f["status"] == "active")
        for bad in ({"id": "zzz:1"}, {"id": "proj:a", "status": "bogus"}, {"id": "proj:a", "priority": 9},
                    {"id": "proj:a", "verdict": {"label": "??", "text": ""}}, {"id": "proj:a", "due": "31/12/2026"}):
            try:
                wl.upsert(bad.pop("id"), path=led, **bad)
                ok = False
            except ValueError:
                ok = True
            check("từ chối dữ liệu sai %s" % (bad,), ok)
        try:
            wl.add_note("proj:a", "  ", path=led)
            ok = False
        except ValueError:
            ok = True
        check("từ chối ghi chú rỗng", ok)
        wl.close_item("proj:proj_closed", "NO-GO", None, "user chốt", "user", led)
        f = wl.fold(path=led)["proj:proj_closed"]
        check("close NO-GO gắn verdict + note", f["status"] == "NO-GO" and f["verdict"]["label"] == "NO-GO" and f["notes"])
        rec = wl.new_user_item("Research/Thực thi", "Thử ý tưởng mới của anh", "tóm tắt", path=led)
        rec2 = wl.new_user_item("Research/Thực thi", "Thử ý tưởng mới của anh", path=led)
        check("user item: id slug, trùng → -2", rec["id"] == "user:thu-y-tuong-moi-cua-anh" and rec2["id"].endswith("-2"), rec2["id"])
        check("inbox liệt kê 2 item chưa ack", len(wl.inbox_items(led)) == 2)
        wl.ack(rec["id"], path=led)
        check("ack bỏ khỏi inbox", [i["id"] for i in wl.inbox_items(led)] == [rec2["id"]])
        # stale: ops cũ + research cũ + due qua hạn
        wl.upsert("user:ops-cu", path=led, branch="Operation/Cron-hạ tầng-KB", title="Việc ops cũ", status="active",
                  updated="2026-10-01", opened="2026-10-01", type="ops")
        wl.upsert("user:res-cu", path=led, branch="Research/Thực thi", title="Việc research cũ", status="active",
                  updated="2026-09-01", opened="2026-09-01", type="research")
        wl.upsert("user:res-moi", path=led, branch="Research/Thực thi", title="Việc research mới", status="active",
                  updated="2026-10-25", opened="2026-10-25", type="research", links=[{"label": "hỏng", "path": "kb/nope.md"}])
        wl.upsert("user:due-qua", path=led, branch="Watch/Mốc định kỳ", title="Hạn đã qua", status="waiting",
                  updated="2026-10-31", due="2026-10-30", type="watch", needs_user=True)
        # dedup + merge
        wl.upsert("user:dup-a", path=led, title="Báo cáo hiệu suất tuần chuẩn v2", branch="Operation/Báo cáo & cadence", updated="2026-10-31")
        wl.upsert("user:dup-b", path=led, title="Báo cáo hiệu suất tuần chuẩn v2.", branch="Operation/Báo cáo & cadence", updated="2026-10-31")
        wl.upsert("user:secret", path=led, title="Tk 0001743768 availableCash NAV CAGR", branch="Portfolio/Hiệu suất",
                  summary="NAV tăng", updated="2026-10-31")
        wl.merge_ids("proj:proj_wire", "proj:proj_closed", path=led)

        # ---- ghi đồng thời
        errs = []

        def worker(k):
            try:
                for j in range(15):
                    wl.add_note("user:conc", "t%d-%d" % (k, j), path=led)
            except Exception as e:  # noqa
                errs.append(e)
        th = [threading.Thread(target=worker, args=(k,)) for k in range(8)]
        [t.start() for t in th]
        [t.join() for t in th]
        lines = open(led, encoding="utf-8").read().splitlines()
        check("ghi đồng thời 8x15: không hỏng/mất dòng", not errs and all(json.loads(l) for l in lines)
              and len(wl.fold(path=led)["user:conc"]["notes"]) == 120)

        # ---- build fixture
        cfg = wb.Cfg(root=tmp, ledger=led, out=os.path.join(tmp, "state", "merged.json"), bus_root=tmp,
                     today=date(2026, 11, 1))
        out = wb.write_merged(cfg)
        ids = {i["id"]: i for i in out["items"]}
        check("id duy nhất", len(ids) == len(out["items"]))
        check("paper: 3 chương trình, status live/closed/active",
              ids["paper:p_live"]["status"] == "live" and ids["paper:p_closed"]["status"] == "closed"
              and ids["paper:p_open"]["status"] == "active")
        check("paper due lấy từ review_date + quá hạn", ids["paper:p_open"]["due"] == "2026-10-20" and ids["paper:p_open"]["overdue"])
        check("INDEX: NO-GO được ledger/derived bắt", ids["proj:proj_closed"]["verdict"]["label"] == "NO-GO")
        check("merge alias: proj_wire biến mất, thành alias", "proj:proj_wire" not in ids
              and "proj:proj_wire" in ids["proj:proj_closed"]["aliases"])
        check("INDEX mục mở: active", ids["proj:proj_open"]["source"] == "derived:projects_index")
        check("stub ngoài INDEX + NO-GO", ids["proj:proj_new-20261030"]["status"] == "NO-GO"
              and ids["proj:proj_new-20261030"]["confidence"] == "low")
        check("ledger thắng derived (branch)", ids["proj:proj_open"]["branch"] == "Research/Thực thi")
        check("busq pending có mặt, needs_user", ids["busq:Fix/câu hỏi thử"]["needs_user"])
        check("sbw triggered=active, due = next_checks tương lai", ids["sbw:ev1"]["status"] == "active"
              and ids["sbw:ev1"]["due"] == "2026-12-15")
        check("watchlist backlog idea + milestone", ids["wl:bk1"]["status"] == "idea"
              and any(k.startswith("wl:2026-10-01") for k in ids))
        check("stale: ops 31d>14", ids["user:ops-cu"]["stale"])
        check("stale: research 61d>30", ids["user:res-cu"]["stale"])
        check("không stale: research 7d", not ids["user:res-moi"]["stale"])
        check("stale: due đã qua", ids["user:due-qua"]["stale"] and ids["user:due-qua"]["overdue"])
        check("closed/NO-GO không bao giờ stale", not ids["proj:proj_closed"]["stale"])
        a = out["attention"]
        check("attention.need_user chứa due-qua + busq", {"user:due-qua", "busq:Fix/câu hỏi thử"} <= set(a["need_user"]))
        check("attention.inbox = user item chưa ack", a["inbox"] == [rec2["id"]] and rec["id"] not in a["inbox"])
        check("attention.ideas chứa backlog", "wl:bk1" in a["ideas"] and rec2["id"] in a["ideas"])
        check("attention.recent chứa updated ≤7d", "user:due-qua" in a["recent"] and "user:res-cu" not in a["recent"])
        check("link hỏng gắn missing", any(l["missing"] for l in ids["user:res-moi"]["links"]))
        check("watchlist: link thiếu được báo trong warnings", any("kb/khong_co.md" in w for w in out["warnings"]["other"]))
        check("jobs 30d: chỉ job mới, gắn vào item", out["counts"]["jobs_30d"] == 1 and len(ids["proj:proj_open"]["recent_jobs"]) == 1)
        check("dedup warn bắt cặp giống ≥0,85", any({d["a"], d["b"]} == {"user:dup-a", "user:dup-b"} for d in out["warnings"]["dups"]))
        blob = open(cfg.out, encoding="utf-8").read()
        check("sanitize: fixture không lộ số tài khoản/NAV", not SECRET_RX.search(blob), SECRET_RX.findall(blob)[:3])
        check("branches đủ khung 15 nhánh + gốc có thứ tự", len(out["branches"]) >= 15 and out["branches"][0]["root"] == "Research")
        for k in ("generated_at", "counts", "attention", "items", "branches"):
            check("hợp đồng có khoá " + k, k in out)
        need = {"id", "branch", "title", "summary", "detail", "type", "status", "priority", "owner", "opened", "updated",
                "due", "verdict", "waiting_on", "needs_user", "links", "depends_on", "aliases", "notes", "source", "stale"}
        check("mọi item đủ khoá schema", all(need <= set(i) for i in out["items"]))
        check("generated_at ICT", out["generated_at"].endswith("+07:00"))

    # ---- build thật (cây hiện tại) vào file tạm + secret-grep
    with tempfile.TemporaryDirectory() as tmp2:
        t0 = time.time()
        cfg = wb.Cfg(out=os.path.join(tmp2, "merged.json"), ledger=wl.LEDGER)
        out = wb.write_merged(cfg)
        dt = time.time() - t0
        blob = open(cfg.out, encoding="utf-8").read()
        check("build thật <10s (%.1fs)" % dt, dt < 10)
        check("build thật: secret-grep sạch", not SECRET_RX.search(blob), SECRET_RX.findall(blob)[:3])
        check("build thật: ≥1 paper + id duy nhất", sum(i["id"].startswith("paper:") for i in out["items"]) >= 1
              and len({i["id"] for i in out["items"]}) == len(out["items"]))
    print("\nwork_ledger_selfcheck: %s" % ("PASS" if not FAILS else "FAIL (%d): %s" % (len(FAILS), FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
