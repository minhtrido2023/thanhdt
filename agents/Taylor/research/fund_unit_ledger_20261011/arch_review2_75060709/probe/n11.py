import sys, os, csv, re, glob, datetime as dt, json
os.environ["MIKE_BOT_TEST_MODE"] = "1"
sys.path.insert(0, "/tmp/ar2/WC/mike/bin")
import daily_nav_snapshot as dns
print("import OK; module file:", dns.__file__)
import nav_period_returns as npr
REPORTS = "/home/trido/thanhdt/WorkingClaude/mike/reports"
tot = {}
for acct in ("SpaceX", "ZaloPay"):
    hist = list(csv.DictReader(open(f"/tmp/ar2/WC/data/execution_logs/nav_history_{acct}.csv")))
    same_day = diff_day = same_gl = diff_gl = 0; ex = []
    old_same = 0; n = 0
    for i, row in enumerate(hist):
        date = row["date"]; nav = float(row["nav"])
        prev_nav = float(hist[i-1]["nav"]) if i else 1_000_000_000.0
        day_change = nav - prev_nav
        old1 = f"({day_change:+,.0f} VND, {day_change / prev_nav * 100:+.2f}% so với hôm trước)"
        old2 = f"   Từ go-live: {nav - 1e9:+,.0f} VND ({(nav - 1e9) / 1e9 * 100:+.2f}%)"
        perf, err = dns.unit_price_performance(acct, date, hist[:i+1])
        paren, lines = dns.nav_performance_lines(day_change, perf, err)
        new1 = f"({paren})"; new2 = lines[0]
        n += 1
        if new1 == old1: same_day += 1
        else:
            diff_day += 1; ex.append((date, old1, new1))
        if new2 == old2: same_gl += 1
        else:
            diff_gl += 1
            if diff_gl <= 2 or date == "2026-10-09": ex.append((date, old2, new2))
        if len(lines) != 1: ex.append((date, "EXTRA LINES", lines))
        # cũng thử với TOÀN BỘ lịch sử (kể cả dòng sau `date`) — đường --from-raw backfill
        perf2, err2 = dns.unit_price_performance(acct, date, hist)
        p2, l2 = dns.nav_performance_lines(day_change, perf2, err2)
        if (p2, l2) != (paren, lines): ex.append((date, "KHÁC khi hist có dòng tương lai", (p2, l2)))
    print(f"{acct}: {n} dòng | dòng 'so với hôm trước' y hệt công thức cũ {same_day}, khác {diff_day} | 'Từ go-live' y hệt {same_gl}, khác {diff_gl}")
    for e in ex[:8]: print("   ", e)
    # so với báo cáo ĐÃ GỬI
    hit = miss = 0; bad = []
    by_date = {r["date"]: i for i, r in enumerate(hist)}
    for path in sorted(glob.glob(f"{REPORTS}/{acct}_daily_report_*.md")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})\.md$", path)
        if not m or m.group(1) not in by_date: continue
        date = m.group(1); i = by_date[date]
        text = open(path, encoding="utf-8").read()
        l1 = next((l for l in text.splitlines() if "**NAV " + date in l), None)
        l2 = next((l for l in text.splitlines() if "Từ go-live" in l), None)
        if not l1: continue
        nav = float(hist[i]["nav"]); prev = float(hist[i-1]["nav"]) if i else 1e9
        perf, err = dns.unit_price_performance(acct, date, hist[:i+1])
        paren, lines = dns.nav_performance_lines(nav - prev, perf, err)
        new1 = f"💰 **NAV {date}: {nav:,.0f} VND** ({paren})"
        ok1 = l1.strip().endswith(new1) or new1 in l1
        ok2 = (l2 is None) or (lines[0].strip() in l2)
        if ok1 and ok2: hit += 1
        else:
            miss += 1; bad.append((date, l1.strip()[:120], new1[:120], (l2 or '').strip()[:70], lines[0].strip()[:70]))
    print(f"   báo cáo ngày đã gửi: y hệt {hit}, khác {miss}")
    for b in bad[:4]: print("     ", b)
