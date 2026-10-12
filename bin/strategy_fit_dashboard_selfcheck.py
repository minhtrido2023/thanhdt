#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
strategy_fit_dashboard_selfcheck.py — selfcheck cho bin/strategy_fit_dashboard.py

KHÔNG chạm BigQuery / mạng / file thật trong data/: mọi nguồn sống được tiêm bằng provider giả,
mọi file đọc từ fixture trong thư mục tạm. Chỉ ĐỌC code thật ở WC_ROOT để kiểm neo trích dẫn (T8).

Phụ thuộc môi trường (verify-before-done): TZ. Chạy đủ 3 kiểu:
    python3 bin/strategy_fit_dashboard_selfcheck.py
    env -u TZ python3 bin/strategy_fit_dashboard_selfcheck.py
    TZ=America/New_York python3 bin/strategy_fit_dashboard_selfcheck.py
T6 còn tự đổi TZ bên trong tiến trình (tzset) để không phụ thuộc người chạy có nhớ hay không.
"""
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import strategy_fit_dashboard as D  # noqa: E402

PASS, FAIL = [], []
NOW = datetime(2026, 10, 12, 9, 0, tzinfo=D.ICT)       # Thứ Hai — cố định để test tất định
REAL_CITER = D.Citer(D.WC_ROOT)


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  ← {detail}" if (detail and not cond) else ""))


# ───────────────────────────────────────────────────────────────── fixture
def mk_ledger(prices, end="2026-10-09", est=(), off=()):
    """Sổ đơn vị giả: dòng 0 = mốc khởi điểm; `est` = chỉ số dòng có NAV ước tính; `off` = chỉ số dòng chụp lệch giờ."""
    days = pd.bdate_range(end=end, periods=len(prices))
    return [dict(date=d.date(), nav=p * 1e5, unit_price=float(p), nav_is_estimate=(i in est),
                 snap_off=(f"balance_ts {d.date()}T09:15:00" if i in off else None))
            for i, (d, p) in enumerate(zip(days, prices))]


def ledger_prov(prices, end="2026-10-09", est=(), jumps=(), pending=(), off=(), n_flows=0, raw_pct=None):
    """Provider giả cùng hợp đồng với `default_providers()["unit_ledger"]`: (account, data_dir) → dict."""
    def prov(account, data_dir=None):
        led = mk_ledger(prices[account] if isinstance(prices, dict) else prices, end, est, off)
        raw = None
        if len(led) >= 2:
            raw = dict(prev_date=led[-2]["date"], date=led[-1]["date"],
                       change_pct=(led[-1]["nav"] / led[-2]["nav"] - 1) * 100 if raw_pct is None else raw_pct)
        return dict(ledger=led, pending=list(pending), dropped=[], jumps=list(jumps), block_pct=5.0,
                    n_flows=n_flows, raw_last=raw)
    return prov


LEDGER_OK = {"SpaceX": [10000, 10100, 9900, 10050], "ZaloPay": [10000, 9800, 9700, 9900]}
JHDR = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"


HYB_IN, HYB_OUT = "ft:in-window hyb:blk left=2", "ft:out×4 hyb"      # nhãn thật của trading_bot/executor.py


def write_journal(data, account, day, rows):
    """rows: (event, side, book[, note]) — note mặc định = lệnh hybrid TRONG block."""
    d = os.path.join(data, "execution_logs"); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"exec_{account}_{day}_journal.csv"), "w", encoding="utf-8") as f:
        f.write(JHDR + "".join(f"{day}T11:00:00,{r[0]},P,AAA,{r[1]},1,100,10000,0,{r[2]},X,{r[3] if len(r) > 3 else HYB_IN}\n"
                               for r in rows))


def write_real(data, account, navs, capital, *, flows=(), start="2026-10-05", inception="2026-10-02", ts=None):
    """Fixture cho provider THẬT: nav_history_<account>.csv + mục của account trong account_inception.json và
    account_cash_flows.json (flows=None ⇒ KHÔNG đụng sổ dòng tiền). `ts`: {chỉ số dòng: balance_ts} ghi đè."""
    ex = os.path.join(data, "execution_logs"); os.makedirs(ex, exist_ok=True)
    days = [d.date() for d in pd.bdate_range(start, periods=len(navs))]
    with open(os.path.join(ex, f"nav_history_{account}.csv"), "w", encoding="utf-8") as f:
        f.write("date,nav,balance_ts,nav_is_estimate\n")
        for i, (d, n) in enumerate(zip(days, navs)):
            f.write(f"{d},{n},{(ts or {}).get(i, f'{d}T19:10:00')},False\n")
    for name, val in (("account_inception.json", {"inception_date": inception, "starting_capital": capital}),
                      ("account_cash_flows.json", None if flows is None else list(flows))):
        if val is None:
            continue
        path = os.path.join(data, name)
        cur = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
        cur[account] = val
        json.dump(cur, open(path, "w", encoding="utf-8"))
    return days


def write_registry(kb, *, count=0, target=10, review="fill-vs-open hybrid = +13,4 bps (se 14,4, n=6) x", lm=True, loo=True):
    prog = {"id": "fill_timing", "status": "graduated-live 2026-08-26", "review_short": review, "progress": {},
            "gate_criteria": [{"text": "a", "note": "x"}, {"text": "b", "note": "leave-one-out cho sigma tu 1,59 toi 3,34, "
                               + ("mean tu +2,9 den +23,7 bps." if loo else "khong ghi khoang.")}]}
    if lm:
        prog["progress"]["live_monitoring"] = {
            "target_sessions": target, "count_current_measured": count, "measured_sessions": [],
            "since": "2026-08-26", "note_2026-09-02": "0/10", "criterion": "phien LIVE co >=1 lenh MUA hybrid",
            "rollback_condition": "mean fill-vs-open > +22 bps (1 tick) ben vung -> rollback flip"}
    json.dump({"programs": [{"id": "other"}, prog]}, open(os.path.join(kb, "paper_programs_registry.json"), "w"))


def write_fixture(root, *, mean12=-0.59, mom_verdict="DECAYED", status="watching",
                  next_review="2026-11-26", nan=False):
    data = os.path.join(root, "data"); kb = os.path.join(root, "kb")
    os.makedirs(data, exist_ok=True); os.makedirs(kb, exist_ok=True)
    x = float("nan") if nan else 0.05
    pd.DataFrame([
        dict(signal="mom_200", label="Mom: Close/MA200", scope="ALL", prior=0, n=151, full=0.064,
             recent=x, tstat=3.8, verdict=mom_verdict),
        dict(signal="mom_200", label="Mom: Close/MA200", scope="CYCLICAL", prior=0, n=151, full=x,
             recent=-0.01, tstat=x, verdict="FLIPPED"),
        dict(signal="PE", label="Val: PE", scope="ALL", prior=-1, n=151, full=-0.05, recent=-0.09,
             tstat=-6.1, verdict="STRENGTH"),
    ]).to_csv(os.path.join(data, "edge_health_matrix.csv"), index=False)
    idx = pd.date_range("2022-08-01", "2026-07-01", freq="MS")
    ic = pd.DataFrame({"mom_200": [0.01 * (i % 7 - 3) for i in range(len(idx))],
                       "PE": [-0.02] * len(idx)}, index=idx)
    if nan:
        ic.iloc[-2, 0] = float("nan"); ic.iloc[5, 1] = float("nan")
    ic.to_csv(os.path.join(data, "edge_health_ic.csv"))
    kd = pd.date_range("2025-01-02", periods=300, freq="B")
    lag = pd.DataFrame({"entry": kd - pd.Timedelta(days=35), "known_date": kd, "ret": 1.0,
                        "mean12": [mean12] * 300, "win12": 35.6, "n12": 567.0})
    if nan:
        lag.loc[lag.index[-1], ["mean12", "win12"]] = float("nan")
    lag.to_csv(os.path.join(data, "lag_edge_health.csv"), index=False)
    pd.DataFrame({"date": ["2025-04-09", "2026-03-09"], "FIX60_ret": [12.0, -1.2]}).to_csv(
        os.path.join(data, "bt_capitulation_STRONG.csv"), index=False)
    json.dump({"date": "2026-10-09", "w_lag_target": 0.5}, open(os.path.join(data, "golive_v23_status.json"), "w"))
    json.dump({"capit_margin_lever": {"enabled": True}}, open(os.path.join(data, "trading_rules.json"), "w"))
    json.dump({"opened": "2026-09-10", "next_review": next_review, "events": [
        {"id": "a", "label": "Nang hang", "status": status, "effective_date": None, "revalidate": ["DT5G"]},
        {"id": "b", "label": "KRX", "status": "watching", "effective_date": None, "revalidate": ["fill"]}]},
        open(os.path.join(kb, "structural_break_watch.json"), "w"))
    write_registry(kb)
    return data, kb


def fake_providers(*, last="2026-10-09", source="DT5G_macro", ks=None, big4=6.8, clock=None,
                   vr_asof="2026-10-09", nan=False):
    days = pd.bdate_range(end=last, periods=300)

    def gated_state(start, end):
        st = [3] * 200 + [4] * 40 + [3] * 60
        df = pd.DataFrame({"time": days, "state": st, "base_state": st, "macro_state": st,
                           "source": source, "stale": False})
        return df, f"[get_gated_state] {source}: health=HEALTHY -> {source}\n"

    def breadth(start, end):
        b = [0.30 + 0.001 * (i % 50) for i in range(300)]
        if nan:
            b[100] = float("nan")
        return pd.DataFrame({"time": days, "b200": b, "univ": 349})

    def neg_streak(d):
        mo = d.set_index("known_date")["mean12"].resample("ME").last().dropna()
        return 1, mo

    return dict(
        gated_state=gated_state, breadth=breadth, neg_streak=neg_streak,
        dt_clock=lambda: clock or {"active": False, "committed": 3, "asof": last, "badzone": None},
        dt_line=lambda: f"Gate DT5G: ✓ ổn định (NEUTRAL)  [dữ liệu tới {last}]",
        value_radar=lambda: dict(score=22.4, label="CHEAP", score_expanding=31.9, pe_cap10=11.1,
                                 p_pe=float("nan") if nan else 5.8, pb_cap10=1.87, p_pb=23.0,
                                 spread=1.6, p_sp=38.5, deposit_rate=7.4,
                                 deposit_rate_source="cctg_6m", asof=vr_asof),
        killswitch=lambda: ks or dict(armed=False, rate=0.074, threshold=0.075, stale=False,
                                      last_update="2026-10-03", age_days=8, rate_source="cctg_6m(2026-10-05)",
                                      reason="cctg_6m(2026-10-05) 7.40% <= 7.5% -> CLEAR"),
        big4_rate=lambda: big4,
        unit_ledger=ledger_prov(LEDGER_OK, end=last),
        is_session=lambda d: d.weekday() < 5,
        crontab=lambda: "10 12 * * 1-5 /x/mike/bin/eod_trading_report.sh\n# 0 13 * * 1-5 python3 risk_monitor.py\n",
        code_refs=lambda needle: (387, ["mike/agents/Spyros/risk_monitor.py"] if needle == "recovery_episode_state" else []),
        capit=lambda: dict(n=12, full_mean=14.2, full_hit=0.75, rec_mean=10.0, rec_hit=0.75,
                           last=-1.2, verdict="HEALTHY", max_carve=0.70),
    )


def raising_providers():
    def boom(*a, **k):
        raise ConnectionError("BQ không kết nối được (giả lập)")
    return {k: boom for k in fake_providers()}


def build(root, prov, now=NOW, **fx):
    data, kb = write_fixture(root, **fx)
    cells, ct = D.build_cells(now, wc_root=D.WC_ROOT, data_dir=data, kb_dir=kb, providers=prov,
                              citer=D.Citer(D.WC_ROOT))
    return cells, D.render_page(cells, now, ct.misses), ct


def by(cells):
    return {c.key: c for c in cells}


class _Strict(HTMLParser):
    def error(self, message):       # py<3.10
        raise ValueError(message)


def parses(page):
    try:
        p = _Strict(); p.feed(page); p.close()
        return True
    except Exception:
        return False


# ───────────────────────────────────────────────────────────────── các ca
def t1_full():
    print("\n[T1] fixture đầy đủ")
    with tempfile.TemporaryDirectory() as r:
        cells, page, ct = build(r, fake_providers())
        c = by(cells)
        check("T1a đủ 12 ô, không ô nào lỗi", list(c) == D.CELL_KEYS and all(x.error is None for x in cells),
              {k: v.error for k, v in c.items() if v.error})
        check("T1b bất biến trang đạt", D.validate_html(page) == [], D.validate_html(page))
        check("T1c html.parser đọc được", parses(page))
        check("T1d không có http(s)://", "http://" not in page and "https://" not in page)
        check("T1e < 1 MB", len(page.encode()) < D.MAX_BYTES)
        check("T1f mọi ô có as_of khác 'không xác định'", all(x.as_of != D.UNKNOWN_ASOF for x in cells),
              {k: v.as_of for k, v in c.items()})
        check("T1g không ô nào CŨ", not any(x.stale is True for x in cells),
              {k: v.stale_why for k, v in c.items() if v.stale})
        check("T1h câu trễ 3 tháng nằm NGAY TRONG ô IC", D.LAG_NOTE in c["edge_ic"].body)
        check("T1i ô IC hiện 3 giá trị IC tháng gần nhất", "05/2026" in c["edge_ic"].body
              and "06/2026" in c["edge_ic"].body and "07/2026" in c["edge_ic"].body)
        check("T1j ô mô tả ghi đúng câu chuẩn", page.count(D.DESCRIPTIVE) == 3, page.count(D.DESCRIPTIVE))
        check("T1k không có chuỗi profit_", "profit_" not in page)
        check("T1l mean12 −0,59 < 4 ⇒ chạm ngưỡng w_LAG", any("w_LAG mục tiêu 0,50" in t for t in c["edge_lag"].touched))
        check("T1m số kiểu VN (dấu phẩy, dấu trừ U+2212)", "−0,59" in c["edge_lag"].body and "-0.59" not in page)
        check("T1n có viewport + lang=vi + một cột", 'name="viewport"' in page and 'lang="vi"' in page)


def t2_missing():
    print("\n[T2] thiếu file + mọi nguồn sống hỏng")
    with tempfile.TemporaryDirectory() as r:
        os.makedirs(os.path.join(r, "data")); os.makedirs(os.path.join(r, "kb"))
        cells, ct = D.build_cells(NOW, data_dir=os.path.join(r, "data"), kb_dir=os.path.join(r, "kb"),
                                  providers=raising_providers(), citer=D.Citer(D.WC_ROOT))
        page = D.render_page(cells, NOW, ct.misses)
        c = by(cells)
        data_cells = [x for x in cells if x.key != "book_map"]
        check("T2a không crash, đủ 12 ô", list(c) == D.CELL_KEYS)
        check("T2b 11 ô dữ liệu đều báo lỗi", all(x.error is not None for x in data_cells),
              [x.key for x in data_cells if x.error is None])
        check("T2c lỗi THẬT được in ra (tên file / thông điệp exception)",
              "edge_health_matrix.csv" in (c["edge_ic"].error or "")
              and "BQ không kết nối được" in (c["env_dt5g"].error or ""),
              (c["edge_ic"].error, c["env_dt5g"].error))
        check("T2d trang vẫn đạt bất biến (as_of + ngưỡng vẫn hiện)", D.validate_html(page) == [], D.validate_html(page))
        check("T2e có đủ 11 thông báo KHÔNG CÓ DỮ LIỆU", page.count("nodata-msg") >= 11, page.count("nodata-msg"))
        check("T2f ngưỡng của ô lỗi KHÔNG biến mất", "golive_recommend_v23.py:" in D.render_cell(c["edge_lag"]))
        out = os.path.join(r, "out")
        rc, path = D.run(NOW, out, data_dir=os.path.join(r, "data"), kb_dir=os.path.join(r, "kb"),
                         providers=raising_providers())
        check("T2g không ô dữ liệu nào ⇒ rc=1, không ghi file", rc == 1 and path is None and not os.path.exists(out))
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r)
        out = os.path.join(r, "out")
        rc, path = D.run(NOW, out, data_dir=data, kb_dir=kb, providers=raising_providers())
        check("T2h còn ô dựng được ⇒ rc=0, có file", rc == 0 and path and os.path.exists(path), (rc, path))
        check("T2i ghi nguyên tử, không sót .tmp", not any(f.endswith(".tmp") for f in os.listdir(out)))


def t3_stale():
    print("\n[T3] dữ liệu cũ ⇒ huy hiệu CŨ")
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r, next_review="2026-09-01")
        old = (NOW - timedelta(days=12)).timestamp()
        for f in ("edge_health_matrix.csv", "lag_edge_health.csv"):
            os.utime(os.path.join(data, f), (old, old))
        prov = fake_providers(last="2026-09-25", vr_asof="2026-09-25",
                              ks=dict(armed=True, rate=0.068, stale=True, last_update="2026-08-01",
                                      rate_source="big4_12m", reason="feed stale (72d > 45d) -> fail-closed (armed)"))
        cells, ct = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=prov, citer=D.Citer(D.WC_ROOT))
        c = by(cells)
        for k in ("edge_ic", "edge_lag", "env_dt5g", "env_breadth", "env_value", "env_rates", "env_structural",
                  "live_dd_spacex", "live_dd_zalopay"):
            check(f"T3 {k} gắn CŨ", c[k].stale is True and 'class="bdg stale"' in D.render_cell(c[k]), c[k].stale_why)
        check("T3 edge_capit KHÔNG gắn CŨ (nguồn không có nhịp)", c["edge_capit"].stale is None)
        page = D.render_page(cells, NOW)
        check("T3 khối đầu trang liệt kê nguồn CŨ", page.count("<b>Nguồn CŨ</b>") == 9, page.count("<b>Nguồn CŨ</b>"))
        check("T3 kill-switch ARMED-do-cũ lên khối đầu trang", "Kill-switch A lãi suất đang ARMED" in page)
        check("T3 bất biến vẫn đạt", D.validate_html(page) == [])
    # biên: Thứ Hai đọc dữ liệu Thứ Sáu = bình thường; Thứ Ba đọc Thứ Sáu = CŨ
    fri = datetime(2026, 10, 9).date()
    check("T3 biên: Thứ Hai/Chủ Nhật đọc T6 không CŨ",
          not D.session_stale(fri, datetime(2026, 10, 12).date())[0] and not D.session_stale(fri, datetime(2026, 10, 11).date())[0])
    check("T3 biên: Thứ Ba đọc T6 là CŨ", D.session_stale(fri, datetime(2026, 10, 13).date())[0])


def t4_empty():
    print("\n[T4] CSV rỗng")
    for kind in ("0 byte", "chỉ header"):
        with tempfile.TemporaryDirectory() as r:
            data, kb = write_fixture(r)
            for f, hdr in (("edge_health_matrix.csv", "signal,label,scope,prior,n,full,recent,tstat,verdict\n"),
                           ("edge_health_ic.csv", ",mom_200,PE\n"),
                           ("lag_edge_health.csv", "entry,known_date,ret,mean12,win12,n12\n")):
                open(os.path.join(data, f), "w").write("" if kind == "0 byte" else hdr)
            open(os.path.join(kb, "structural_break_watch.json"), "w").write('{"events": []}')
            cells, ct = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=fake_providers(), citer=D.Citer(D.WC_ROOT))
            c = by(cells)
            check(f"T4 ({kind}) edge_ic / edge_lag / structural báo lỗi, không crash",
                  all(c[k].error for k in ("edge_ic", "edge_lag", "env_structural")),
                  {k: c[k].error for k in ("edge_ic", "edge_lag", "env_structural")})
            check(f"T4 ({kind}) ô khác không bị kéo theo", c["env_dt5g"].error is None and c["edge_capit"].error is None)
            check(f"T4 ({kind}) bất biến đạt", D.validate_html(D.render_page(cells, NOW)) == [])


def t5_nan():
    print("\n[T5] giá trị NaN")
    with tempfile.TemporaryDirectory() as r:
        cells, page, ct = build(r, fake_providers(nan=True, big4=float("nan")), nan=True)
        c = by(cells)
        check("T5a không ô nào crash", all(x.error is None for x in cells), {k: v.error for k, v in c.items() if v.error})
        low = page.lower()
        check("T5b không rò chữ 'nan'/'inf' ra trang", ">nan<" not in low and " nan" not in low and "nan%" not in low
              and "inf" not in low.replace("info", ""), [low[i - 30:i + 10] for i in [low.find("nan")] if i >= 0])
        check("T5c NaN hiện thành '—'", "—" in c["edge_ic"].body and "—" in c["edge_lag"].body)
        check("T5d mean12 NaN ⇒ ghi rõ luật live rơi về 0,50 (đúng nhánh pd.notna trong code)",
              any("NaN" in t and "0,50" in t for t in c["edge_lag"].touched), c["edge_lag"].touched)
        check("T5e Big-4 NaN không bị coi là chạm ngưỡng margin", not any("margin" in t for t in c["env_rates"].touched))
        check("T5f bất biến đạt", D.validate_html(page) == [], D.validate_html(page))
    check("T5g vn(): None/NaN/inf/chuỗi rác → '—'",
          [D.vn(None), D.vn(float("nan")), D.vn(float("inf")), D.vn("abc")] == ["—"] * 4)
    check("T5h vn(): dấu phẩy + dấu trừ + dấu cộng", (D.vn(-0.5937, 2, True), D.vn(0.018, 3, True), D.vn(7.4, 2))
          == ("−0,59", "+0,018", "7,40"))


def t6_tz():
    print("\n[T6] múi giờ — neo ICT tường minh")
    saved = os.environ.get("TZ")
    try:
        for tz in (None, "America/New_York", "UTC", "Asia/Tokyo"):
            if tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = tz
            time.tzset()
            inst = datetime(2026, 10, 11, 18, 30, tzinfo=timezone.utc).astimezone(D.ICT)   # = 01:30 12/10 ICT
            check(f"T6 TZ={tz}: tên file theo NGÀY ICT", os.path.basename(D.out_path(inst, "/x")) == "strategy_fit_2026-10-12.html")
            check(f"T6 TZ={tz}: tiêu đề in giờ ICT", "2026-10-12 01:30 ICT" in D.render_page([], inst))
            with tempfile.TemporaryDirectory() as r:
                data, kb = write_fixture(r)
                ts = datetime(2026, 10, 9, 17, 30, tzinfo=timezone.utc).timestamp()             # = 00:30 10/10 ICT
                for f in ("edge_health_matrix.csv", "edge_health_ic.csv"):
                    os.utime(os.path.join(data, f), (ts, ts))
                cells, _ = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=fake_providers(), citer=D.Citer(D.WC_ROOT))
                check(f"T6 TZ={tz}: mtime quy về ICT", "file ghi 2026-10-10 00:30 ICT" in by(cells)["edge_ic"].as_of,
                      by(cells)["edge_ic"].as_of)
                # 01:30 ICT Thứ Ba 13/10 (= 18:30 UTC Thứ Hai): theo ngày ICT thì dữ liệu T6 09/10 đã CŨ;
                # code lấy nhầm ngày UTC/NY (12/10) sẽ báo KHÔNG cũ.
                late = datetime(2026, 10, 12, 18, 30, tzinfo=timezone.utc).astimezone(D.ICT)
                c3, _ = D.build_cells(late, data_dir=data, kb_dir=kb, providers=fake_providers(), citer=D.Citer(D.WC_ROOT))
                dd = by(c3)["live_dd_spacex"]
                check(f"T6 TZ={tz}: ô drawdown tính CŨ theo ngày ICT", dd.as_of == "2026-10-09" and dd.stale is True,
                      (dd.as_of, dd.stale, dd.stale_why))
        off = datetime.now(D.ICT).utcoffset()
        check("T6 datetime.now(ICT) lệch UTC đúng +7h", off == timedelta(hours=7), off)
    finally:
        if saved is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = saved
        time.tzset()
    src = open(D.__file__, encoding="utf-8").read()
    check("T6 nguồn không gọi datetime.now() trần", "datetime.now()" not in src and "date.today()" not in src)


def t7_mutation():
    print("\n[T7] đột biến — selfcheck phải ĐỎ khi mất ngưỡng / as_of")
    with tempfile.TemporaryDirectory() as r:
        cells, page, ct = build(r, fake_providers())
        assert D.validate_html(page) == []
        # (a) xoá ĐÚNG 1 dòng ngưỡng ở ô DT5G
        sec = page[page.index('<section class="cell" id="env_dt5g"'):]
        sec = sec[:sec.index("</section>")]
        thr = sec[sec.index('<div class="thr">'):]
        li = thr[thr.index("<li>"):thr.index("</li>") + 5]
        bad = D.validate_html(page.replace(li, "", 1))
        check("T7a xoá 1 dòng ngưỡng ⇒ đỏ", any("env_dt5g" in b and "dòng ngưỡng" in b for b in bad), bad)
        # (b) xoá cả khối ngưỡng của 1 ô
        s2 = page[page.index('<section class="cell" id="env_value"'):]
        s2 = s2[:s2.index("</section>")]
        t2 = s2[s2.index('<div class="thr">'):]
        # (khối mô tả giống nhau từng byte giữa các ô ⇒ phải thay TRONG đúng section, không thay lần gặp đầu)
        bad = D.validate_html(page.replace(s2, s2.replace(t2, "", 1), 1))
        check("T7b xoá khối «Ngưỡng hành động» ⇒ đỏ", any("env_value" in b and "Ngưỡng hành động" in b for b in bad), bad)
        # (c) as_of rỗng
        bad = D.validate_html(page.replace(f'id="edge_lag" data-asof="{D.esc(by(cells)["edge_lag"].as_of)}"',
                                           'id="edge_lag" data-asof=""', 1))
        check("T7c as_of rỗng ⇒ đỏ", any("edge_lag" in b and "as_of" in b for b in bad), bad)
        # (d) ô có ngưỡng thật bị đổi thành câu mô tả
        c = by(cells)["env_rates"]; saved = c.thr; c.thr = []
        bad = D.validate_html(D.render_page(cells, NOW)); c.thr = saved
        check("T7d ô có ngưỡng thật bị hạ thành «chỉ để mô tả» ⇒ đỏ", any("env_rates" in b for b in bad), bad)
        # (e) ô mô tả bị gắn ngưỡng tự đặt
        c = by(cells)["env_breadth"]; c.thr = ["breadth &lt; 30% ⇒ giảm tỷ trọng"]
        bad = D.validate_html(D.render_page(cells, NOW)); c.thr = []
        check("T7e ô mô tả bị bịa ngưỡng ⇒ đỏ", any("env_breadth" in b for b in bad), bad)
        # (f) dòng ngưỡng không có trích file:dòng
        c = by(cells)["env_structural"]; saved = c.thr; c.thr = ["status đổi ⇒ re-validate"]
        bad = D.validate_html(D.render_page(cells, NOW)); c.thr = saved
        check("T7f ngưỡng không trích file:dòng ⇒ đỏ", any("env_structural" in b and "file:dòng" in b for b in bad), bad)
        # (g) tài nguyên ngoài, (h) thẻ lệch, (i) thiếu hẳn 1 ô, (j) cột nhìn trước
        check("T7g chèn URL ngoài ⇒ đỏ", any("http" in b for b in D.validate_html(page.replace("<main>", '<main><img src="https://x.y/z.png">', 1))))
        check("T7h thẻ không đóng ⇒ đỏ", D.validate_html(page.replace("</section>", "", 1)) != [])
        cut = page[page.index('<section class="cell" id="env_structural"'):]
        cut = cut[:cut.index("</section>") + len("</section>")]
        check("T7i mất hẳn 1 ô ⇒ đỏ", any("thiếu ô env_structural" in b for b in D.validate_html(page.replace(cut, "", 1))))
        check("T7j lọt chuỗi profit_ ⇒ đỏ", any("profit_" in b for b in D.validate_html(page.replace("<main>", "<main>profit_3M", 1))))
        # (k) run() trả rc=4 và KHÔNG ghi file khi bất biến vỡ
        orig = D.cell_env_rates
        try:
            def broken(*a, **k):
                c = orig(*a, **k); c.thr = c.thr[:1]; return c
            D.cell_env_rates = broken
            data, kb = write_fixture(r)
            out = os.path.join(r, "out_k")
            rc, path = D.run(NOW, out, data_dir=data, kb_dir=kb, providers=fake_providers())
            check("T7k code đánh rơi 1 dòng ngưỡng ⇒ run() rc=4, không ghi file", rc == 4 and not os.path.exists(out), rc)
        finally:
            D.cell_env_rates = orig


def t8_anchors():
    print("\n[T8] neo trích dẫn trên code THẬT (chỉ đọc)")
    with tempfile.TemporaryDirectory() as r:
        cells, page, ct = build(r, fake_providers())
        check("T8a mọi neo file:dòng định vị được", ct.misses == [], ct.misses)
        check("T8b trang không có 'KHÔNG ĐỊNH VỊ ĐƯỢC'", "KHÔNG ĐỊNH VỊ ĐƯỢC" not in page)
        import re
        n = len(set(re.findall(r'<code class="cite">([^<]+:\d+)</code>', page)))
        check("T8c có ≥ 25 trích dẫn file:dòng khác nhau", n >= 25, n)
        thr, _ = REAL_CITER.const("deploy_golive_dt5g_v4/golive_recommend_v23.py", r"^EDGE_THR\s*=\s*([0-9.]+)")
        m, _ = REAL_CITER.const("deploy_golive_dt5g_v4/golive_recommend_v23.py", r"^CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD\s*=\s*([0-9.]+)")
        a, _ = REAL_CITER.const("deposit_rate_vn.py", r"^\s*THRESHOLD\s*=\s*([0-9.]+)")
        check("T8d hằng số đọc từ code là số hữu hạn", all(D._isnum(v) for v in (thr, m, a)), (thr, m, a))
    ct = D.Citer(D.WC_ROOT)
    h = ct.cite("edge_health_monitor.py", r"NEO_KHONG_TON_TAI_xyz")
    check("T8e neo mất ⇒ in rõ + ghi misses, không im lặng", "KHÔNG ĐỊNH VỊ ĐƯỢC" in h and len(ct.misses) == 1)
    h = ct.cite("file_khong_co.py", r"x")
    check("T8f file mất ⇒ in rõ + lỗi thật", "KHÔNG ĐỊNH VỊ ĐƯỢC" in h and "file_khong_co.py" in ct.misses[-1])
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r)
        cells, ct2 = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=fake_providers(), citer=D.Citer(r))
        bad = D.validate_html(D.render_page(cells, NOW, ct2.misses))
        check("T8g repo nguồn không đọc được ⇒ bất biến đỏ (không ra trang thiếu trích dẫn)",
              any("file:dòng" in b for b in bad), bad[:2])


def t9_touch_logic():
    print("\n[T9] khối «đáng chú ý» chỉ theo ngưỡng thật")
    with tempfile.TemporaryDirectory() as r:
        cells, page, _ = build(r, fake_providers(), mean12=5.2)
        check("T9a không gì chạm ⇒ đúng câu «Không ô nào chạm ngưỡng»", "Không ô nào chạm ngưỡng." in page
              and not any(c.touched for c in cells), {c.key: c.touched for c in cells if c.touched})
    with tempfile.TemporaryDirectory() as r:
        clock = {"active": True, "cand": 2, "k": 8, "need": 10, "committed": 3, "asof": "2026-10-09",
                 "badzone": {"n": 16, "ret": -0.06, "review": True}}
        prov = fake_providers(source="DT4_only", big4=9.5, clock=clock,
                              ks=dict(armed=True, rate=0.078, stale=False, last_update="2026-10-03",
                                      rate_source="big4_12m", reason="big4_12m 7.80% > 7.5% -> SUSPEND new recovery deploy"))
        cells, page, _ = build(r, prov, mean12=5.2, mom_verdict="FLIPPED", status="effective")
        t = {c.key: c.touched for c in cells}
        check("T9b mom_200·ALL FLIPPED ⇒ chạm", len(t["edge_ic"]) == 1, t["edge_ic"])
        check("T9c mean12 ≥ 4 ⇒ ô LAG KHÔNG chạm", t["edge_lag"] == [], t["edge_lag"])
        check("T9d DT4_only + đồng hồ ≥70% + ngưỡng xem lại ⇒ 3 dòng", len(t["env_dt5g"]) == 3, t["env_dt5g"])
        check("T9e kill-switch ARMED + Big-4 ≥ 9,0 ⇒ 2 dòng", len(t["env_rates"]) == 2, t["env_rates"])
        check("T9f sự kiện cấu trúc khác 'watching' ⇒ chạm", len(t["env_structural"]) == 1, t["env_structural"])
        check("T9g2 ô tầng 3 không chạm khi không có điều kiện thật", t["live_dd_spacex"] == [] and t["live_slippage"] == [])
        check("T9g ô mô tả không bao giờ chạm", t["env_breadth"] == [] and t["env_value"] == [] and t["book_map"] == [])
        check("T9h Không còn câu «Không ô nào chạm ngưỡng»", "Không ô nào chạm ngưỡng." not in page)
    check("T9i tercile: thấp nhất 252 phiên ⇒ LOW (pct=0 không bị ném mất)",
          D.breadth_tercile([0.5] * 252 + [0.1]) == (0.0, "LOW"))
    check("T9j tercile: cao nhất ⇒ HIGH", D.breadth_tercile([0.5] * 252 + [0.9])[1] == "HIGH")
    check("T9k tercile: thiếu 252 phiên trước ⇒ không xếp", D.breadth_tercile([0.5] * 100) == (None, None))


def t10_tier3():
    print("\n[T10] tầng 3 — drawdown thật + trượt giá")
    import inspect
    s = D.drawdown_stats(mk_ledger([10000, 11000, 9900, 10450, 12000, 11400], est=(2,)))
    check("T10a N = số phiên sau mốc khởi điểm", s["n"] == 5, s["n"])
    check("T10b drawdown lớn nhất −10% (đỉnh dòng 1 → đáy dòng 2)", abs(s["max_dd"] + 0.10) < 1e-12
          and s["max_peak"]["unit_price"] == 11000 and s["max_trough"]["unit_price"] == 9900, s["max_dd"])
    check("T10c drawdown hiện tại −5% từ đỉnh MỚI NHẤT, 1 phiên kể từ đỉnh", abs(s["cur_dd"] + 0.05) < 1e-12
          and s["peak"]["unit_price"] == 12000 and s["since_peak"] == 1, (s["cur_dd"], s["since_peak"]))
    check("T10d phiên giảm mạnh nhất −10%, phiên gần nhất −5%", abs(s["worst_day"] + 0.10) < 1e-12 and abs(s["day_ret"] + 0.05) < 1e-12)
    check("T10e đếm đúng phiên NAV ước tính", [r["unit_price"] for r in s["est"]] == [9900])
    flat = mk_ledger([10000, 10000, 10000])
    flat[1]["nav"] *= 3; flat[2]["nav"] /= 2                     # nạp rồi rút lớn: nav nhảy, giá đơn vị đứng yên
    s = D.drawdown_stats(flat)
    check("T10f nạp/rút (nav nhảy, giá đơn vị không đổi) KHÔNG tạo drawdown", s["max_dd"] == 0 and s["cur_dd"] == 0 and s["total"] == 0, s)
    check("T10g drawdown_stats không đọc cột nav thô", '"nav"]' not in inspect.getsource(D.drawdown_stats))
    gap = mk_ledger([10000, 10100, 10200]); gap[2]["date"] += timedelta(days=4)   # T6 09/10 → T3 13/10: thiếu T6 + T2
    check("T10h ngày Thứ 2–6 thiếu dòng được liệt kê (bỏ T7/CN), không nội suy",
          [str(d) for d in D.drawdown_stats(gap)["missing"]] == ["2026-10-09", "2026-10-12"], D.drawdown_stats(gap)["missing"])
    for bad, why in (([10000], "1 dòng"), ([10000, float("nan"), 9000], "NaN"), ([10000, 0, 9000], "giá 0")):
        try:
            D.drawdown_stats(mk_ledger(bad)); ok = False
        except ValueError:
            ok = True
        check(f"T10i sổ hỏng ({why}) ⇒ từ chối, không ra số", ok)

    def cells_with(r, ul, **reg):
        data, kb = write_fixture(r)
        if reg:
            write_registry(kb, **reg)
        prov = fake_providers(); prov["unit_ledger"] = ul
        cells, ct = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=prov, citer=D.Citer(D.WC_ROOT))
        return by(cells), D.render_page(cells, NOW, ct.misses), data, kb

    with tempfile.TemporaryDirectory() as r:
        c, page, data, kb = cells_with(r, ledger_prov(LEDGER_OK))
        a, b = c["live_dd_spacex"], c["live_dd_zalopay"]
        check("T10j hai tài khoản ra hai kết quả KHÁC nhau (§12)", a.error is None and b.error is None and a.body != b.body)
        check("T10k số đúng: SpaceX max −1,98% · ZaloPay hiện tại −1,00%", "−1,98%" in a.body and "−1,00%" in b.body, a.body[:400])
        check("T10l mốc tham chiếu đọc từ CLAUDE.md, ghi rõ KHÔNG phải ngưỡng", "−25,2%" in a.body and "KHÔNG phải ngưỡng" in a.body)
        check("T10l2 (M35) có đoạn GIẢI THÍCH mốc −25,2%: không phải ngưỡng hành động, N phiên chưa đủ để so",
              "không phải ngưỡng hành động" in a.body and "3 phiên live chưa đủ để nói drawdown thật" in a.body, a.body[-900:])
        check("T10m ô ZaloPay ghi rõ chuỗi TOÀN tài khoản; SpaceX không", "TOÀN tài khoản" in b.body and "TOÀN tài khoản" not in a.body)
        check("T10m2 (N3) caveat ZaloPay đứng TRƯỚC bảng, kèm độ lớn DGC trích từ chính sách fund-unit (file:dòng)",
              0 <= b.body.find("TOÀN tài khoản") < b.body.find("<table") and "36% NAV" in b.body
              and "fund-unit-performance-policy-20261010.md:" in b.body, b.body[:500])
        check("T10m3 (N3) ô ZaloPay KHÔNG mang mốc backtest −25,2%", "−25,2%" not in b.body and "Mốc tham chiếu" not in b.body)
        check("T10m4 (N2) nguồn ghi «đã loại nạp/rút ĐÃ KHAI», số bản ghi và giới hạn cổng 5%",
              "ĐÃ KHAI" in a.source and "hiện <b>0 bản ghi</b>" in a.source and "nhỏ hơn 5% NAV" in a.source, a.source)
        check("T10n không in NAV bằng tiền / số tài khoản", "1.000.000.000" not in page and "0002023347" not in page
              and "0001743768" not in page and "1005000000" not in page)
        check("T10o bất biến đạt, không neo nào mất", D.validate_html(page) == [], D.validate_html(page))
    with tempfile.TemporaryDirectory() as r:
        c, page, *_ = cells_with(r, ledger_prov([10000, 10100, 9900, 10050]))
        check("T10p hai tài khoản ra số GIỐNG HỆT ⇒ cả hai báo lỗi, không công bố",
              all("giống hệt" in (c[k].error or "") for k in ("live_dd_spacex", "live_dd_zalopay")))
        check("T10p2 … trang vẫn đạt bất biến", D.validate_html(page) == [])
    with tempfile.TemporaryDirectory() as r:
        j = [dict(date="2026-10-08", prev_date="2026-10-07", nav0=1e9, nav1=1.2e9, change_pct=20.0)]
        c, page, *_ = cells_with(r, lambda acc, d=None: ledger_prov(LEDGER_OK, jumps=j if acc == "SpaceX" else ())(acc, d))
        a = c["live_dd_spacex"]
        check("T10q cổng NAV-jump chặn ⇒ ô báo lỗi thật, KHÔNG in drawdown", "NAV-jump" in (a.error or "") and "Drawdown hiện tại" not in a.body, a.error)
        check("T10r … tài khoản kia không bị kéo theo, ngưỡng của ô lỗi vẫn hiện", c["live_dd_zalopay"].error is None
              and "trading_rules.json:" in D.render_cell(a) and D.validate_html(page) == [])
    with tempfile.TemporaryDirectory() as r:
        c, page, *_ = cells_with(r, ledger_prov({"SpaceX": [10000, 10200, 9690], "ZaloPay": [10000, 10200, 9700]}, est=(1, 2)))
        check("T10s phiên đóng cửa −5,0% ⇒ chạm phanh lỗ trong ngày", len(c["live_dd_spacex"].touched) == 1, c["live_dd_spacex"].touched)
        check("T10t −4,9% ⇒ KHÔNG chạm", c["live_dd_zalopay"].touched == [], c["live_dd_zalopay"].touched)
        check("T10s2 ngưỡng drawdown-từ-đỉnh 25% đọc từ code thật, kèm trạng thái đầu vào của luật",
              "25%" in c["live_dd_spacex"].thr[0] and "risk_monitor.py:" in c["live_dd_spacex"].thr[0]
              and "không có file nào" in c["live_dd_spacex"].thr[0], c["live_dd_spacex"].thr[0])
        check("T10u đỉnh/đáy rơi vào ngày NAV ước tính ⇒ gắn nhãn ngay cạnh ngày", c["live_dd_spacex"].body.count("(NAV ước tính)") >= 2
              and "2/2 phiên có NAV" in c["live_dd_spacex"].body)
    with tempfile.TemporaryDirectory() as r:
        c, page, *_ = cells_with(r, ledger_prov({"SpaceX": [10000, float("nan"), 9000], "ZaloPay": [10000, 9900, 9950]},
                                               pending=[dict(date="2026-10-09")]))
        check("T10v giá đơn vị NaN ⇒ ô lỗi, không rò 'nan%' ra trang", c["live_dd_spacex"].error and "nan%" not in page.lower())
        check("T10w dòng tiền TREO được nêu trong ô", "TREO" in c["live_dd_zalopay"].body)

    with tempfile.TemporaryDirectory() as r:
        os.makedirs(os.path.join(r, "data"), exist_ok=True)
        open(os.path.join(r, "data", "eod_account_20260702.json"), "w").write("{}")
        c, page, *_ = cells_with(r, ledger_prov({"SpaceX": [10000, 9000, 8000, 7500], "ZaloPay": [10000, 9000, 8000, 7501]}))
        check("T10w2 drawdown −25,00% ⇒ chạm ngưỡng HALT của risk_monitor; −24,99% ⇒ không",
              any("25% của luật HALT" in t for t in c["live_dd_spacex"].touched)
              and not any("25% của luật HALT" in t for t in c["live_dd_zalopay"].touched),
              (c["live_dd_spacex"].touched, c["live_dd_zalopay"].touched))
        check("T10w3 ngày của file đầu vào eod_account được ĐỌC ra, không viết cứng", "20260702" in c["live_dd_spacex"].thr[0])
    # ── trượt giá
    with tempfile.TemporaryDirectory() as r:
        c, page, data, kb = cells_with(r, ledger_prov(LEDGER_OK))
        sl = c["live_slippage"]
        check("T10x registry 0 phiên + journal 0 phiên ⇒ không CŨ, không chạm", sl.error is None and sl.stale is False and sl.touched == [])
        check("T10y nói thẳng «Chưa có nguồn định kỳ» + số LIVE «chưa có»", "Chưa có nguồn định kỳ" in sl.body and "<b>chưa có</b>" in sl.body)
        check("T10z ngưỡng +22 bps đọc từ KB thật, có trích file:dòng", "+22 bps" in sl.thr[0] and "current_ops.md:" in sl.thr[0]
              and "paper_programs_registry.json:" in sl.thr[0], sl.thr[0])
        check("T10A số PAPER ghi rõ không phải live", "+13,4 bps" in sl.body and "không phải live" in sl.body)
        check("T10A2 (N5) số PAPER ghi «không so với ngưỡng +22 bps» + khoảng leave-one-out đọc từ registry",
              "không so với ngưỡng +22 bps" in sl.body and "+2,9 … +23,7 bps" in sl.body, sl.body[-900:])
        check("T10A3 (N4) nhãn bộ đếm khớp thứ đang đếm + trích tiêu chí registry", "MUA hybrid trong block" in sl.body
              and "paper_programs_registry.json:" in sl.body and "hyb:blk" in sl.body)
        write_registry(kb, loo=False)
        check("T10A4 (N5) registry không có khoảng leave-one-out ⇒ ghi «không đọc được», không bịa",
              "khoảng leave-one-out: không đọc được từ registry" in D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW).body)
        write_registry(kb)
        write_journal(data, "SpaceX", "2026-09-17", [("PLACE", "buy", "LAG"), ("FILL", "buy", "LAG")])
        write_journal(data, "SpaceX", "2026-08-28", [("PLACE", "buy", "CORP_ACTION")])        # quyền mua: không tính
        write_journal(data, "SpaceX", "2026-08-20", [("PLACE", "buy", "LAG")])                # trước `since`: không tính
        write_journal(data, "SpaceX", "2026-09-21", [("PLACE", "sell", "LAG"), ("HYBRID_DEFER", "buy", "LAG")])  # không có PLACE mua
        write_journal(data, "ZaloPay", "2026-09-17", [("PLACE", "buy", "BAL")])
        write_journal(data, "ZaloPay", "2026-09-14", [("PLACE", "buy", "BAL")])
        write_journal(data, "ZaloPay", "2026-09-15", [("PLACE", "buy", "DISCRETIONARY_SPECIAL", HYB_OUT)] * 2)  # hybrid NGOÀI block
        write_journal(data, "ZaloPay", "2026-09-16", [("PLACE", "buy", "BAL", "ft:in-window")])                  # không hybrid
        write_journal(data, "STRESSTEST_P1SPACEX", "2026-09-22", [("PLACE", "buy", "LAG")])   # nhãn khác: không tính
        write_journal(data, "main", "2026-09-23", [("PLACE", "buy", "LAG")])                  # paper: không tính
        f = D.hybrid_block_buy_sessions
        check("T10B đếm theo TỪNG tài khoản (§12): SpaceX 1 phiên, ZaloPay 2 phiên",
              f(data, "SpaceX", "2026-08-26") == ["2026-09-17"] and f(data, "ZaloPay", "2026-08-26") == ["2026-09-14", "2026-09-17"],
              (f(data, "SpaceX", "2026-08-26"), f(data, "ZaloPay", "2026-08-26")))
        check("T10B2 (N4) lệnh hybrid NGOÀI block (ft:out×N hyb) và lệnh không hybrid KHÔNG tính là phiên",
              "2026-09-15" not in f(data, "ZaloPay", "2026-08-26") and "2026-09-16" not in f(data, "ZaloPay", "2026-08-26"))
        sl = D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW)
        check("T10C registry 0 ≠ journal 2 phiên (hợp, không cộng trùng ngày) ⇒ CŨ kèm lý do thật",
              sl.stale is True and "registry ghi 0 phiên, journal đếm được 2 phiên" in sl.stale_why and "<b>2/10</b>" in sl.body, sl.stale_why)
        check("T10D chưa đủ 10 phiên ⇒ không ghi «đến hạn đo»", "đến hạn đo" not in sl.stale_why)
        write_registry(kb, count=0, target=2)
        sl = D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW)
        check("T10E đủ số phiên mục tiêu ⇒ ghi «đến hạn đo»", "đến hạn đo" in sl.stale_why, sl.stale_why)
        write_registry(kb, count=2)
        check("T10F registry khớp journal ⇒ không CŨ", D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW).stale is False)
        write_registry(kb, review="khong co so nao")
        check("T10G registry không còn số PAPER ⇒ ghi «không đọc được», không bịa",
              "không đọc được từ registry" in D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW).body)
        write_registry(kb, lm=False)
        sl = D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW)
        check("T10H registry mất khối live_monitoring ⇒ ô lỗi, ngưỡng vẫn hiện", "live_monitoring" in (sl.error or "")
              and "current_ops.md:" in D.render_cell(sl))
        open(os.path.join(kb, "paper_programs_registry.json"), "w").write("{hỏng")
        sl = D.cell_live_slippage(data, kb, D.Citer(D.WC_ROOT), NOW)
        check("T10I registry hỏng JSON ⇒ ô lỗi kèm lỗi thật", "JSONDecodeError" in (sl.error or ""), sl.error)
    # ── đột biến + chỉ đọc
    with tempfile.TemporaryDirectory() as r:
        c, page, *_ = cells_with(r, ledger_prov(LEDGER_OK))
        cells = list(c.values())
        x = c["live_dd_spacex"]; saved = x.thr; x.thr = x.thr[:1]
        bad = D.validate_html(D.render_page(cells, NOW)); x.thr = saved
        check("T10J ô drawdown rơi 1 dòng ngưỡng ⇒ đỏ", any("live_dd_spacex" in b for b in bad), bad)
        x = c["live_slippage"]; saved = x.thr; x.thr = []
        bad = D.validate_html(D.render_page(cells, NOW)); x.thr = saved
        check("T10K ô trượt giá bị hạ thành «chỉ để mô tả» ⇒ đỏ", any("live_slippage" in b for b in bad), bad)
        x = c["live_dd_zalopay"]; saved = x.thr; x.thr = saved + ["drawdown &lt; −25,2% ⇒ giảm tỷ trọng"]
        bad = D.validate_html(D.render_page(cells, NOW)); x.thr = saved
        check("T10L bịa ngưỡng −25,2% cho drawdown ⇒ đỏ", any("live_dd_zalopay" in b for b in bad), bad)
        cut = page[page.index('<section class="cell" id="live_slippage"'):]
        cut = cut[:cut.index("</section>") + len("</section>")]
        check("T10M mất hẳn ô tầng 3 ⇒ đỏ", any("thiếu ô live_slippage" in b for b in D.validate_html(page.replace(cut, "", 1))))
        check("T10N trang có tiêu đề Tầng 3 và KHÔNG có ô «NAV so dải backtest»", "Tầng 3 — Thực tế so với kỳ vọng" in page
              and len(D.CELL_KEYS) == 12 and not any("backtest_band" in k or "nav_vs" in k for k in D.CELL_KEYS))
    src = "".join(inspect.getsource(f) for f in (D.drawdown_stats, D.cell_live_dd, D._enforce_status, D.nav_expected_date,
                                                 D.hybrid_block_buy_sessions, D.cell_live_slippage))
    prov_src = inspect.getsource(D.default_providers)
    check("T10O code tầng 3 chỉ ĐỌC (không mở file để ghi, không chốt sổ, không gọi tiến trình con)",
          not any(t in src + prov_src for t in ('"w"', "'w'", '"a"', "os.replace", "seal(", "--seal", "to_csv"))
          and "subprocess" not in src)
    check("T10O2 tiến trình con DUY NHẤT của provider là `crontab -l` (chỉ đọc), có timeout",
          prov_src.count("subprocess.") == 1 and 'subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10)' in prov_src)


def _cells(r, ul, now=NOW, ct=None, **over):
    data, kb = write_fixture(r)
    prov = fake_providers(); prov["unit_ledger"] = ul; prov.update(over)
    cells, ct = D.build_cells(now, data_dir=data, kb_dir=kb, providers=prov, citer=ct or D.Citer(D.WC_ROOT))
    return by(cells), D.render_page(cells, now, ct.misses), data


def _rows(body):
    """Bảng của ô → {nhãn: (giá trị, ghi chú)} (text thuần)."""
    import re
    out = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        td = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<td>(.*?)</td>", tr, re.S)]
        if len(td) == 3:
            out[td[0]] = (td[1], td[2])
    return out


def t11_enforcement():
    print("\n[T11] C1 — ba phanh lỗ: luật trên giấy + trạng thái thực thi ĐỌC lúc chạy")
    import re
    with tempfile.TemporaryDirectory() as r:
        c, page, data = _cells(r, ledger_prov(LEDGER_OK))
        thr = c["live_dd_spacex"].thr
        txt = [re.sub(r"<[^>]+>", "", t) for t in thr]
        check("T11a cả 3 dòng: «Luật trên giấy» + «Trạng thái thực thi», không dòng nào ghi «→ HALT»",
              all("Luật trên giấy" in t and "Trạng thái thực thi" in t and "→ HALT" not in t for t in txt), txt)
        check("T11b dòng 25%: crontab có 0 dòng BẬT gọi risk_monitor (dòng bị # không tính) ⇒ nói thẳng chưa có tiến trình định kỳ",
              "0 dòng đang bật" in txt[0] and "hiện chưa có tiến trình định kỳ nào đánh giá luật trên NAV live" in txt[0], txt[0])
        check("T11c dòng −5%: quét code 0 file nhắc khoá ⇒ «chưa có code nào đọc khoá này, luật chưa được thực thi»",
              "quét 387 file" in txt[1] and "0 file nhắc tới daily_loss_limit_pct" in txt[1]
              and "chưa có code nào đọc khoá này, luật chưa được thực thi" in txt[1], txt[1])
        check("T11d dòng episode: file vắng ⇒ «không tồn tại», KHÔNG suy ra «không có episode nào đang được theo dõi»",
              "không tồn tại" in txt[2] and "không có episode nào đang được theo dõi" not in page
              and "file vắng KHÔNG cho biết có episode hay không" in txt[2] and "0 dòng đang bật" in txt[2], txt[2])
        check("T11e dòng episode nêu file code nhắc tới file trạng thái (đọc từ lượt quét)", "mike/agents/Spyros/risk_monitor.py" in txt[2])
        check("T11f trang đạt bất biến", D.validate_html(page) == [], D.validate_html(page))
        # đột biến câu chữ ở TẦNG TRANG: xoá / đổi phần trạng thái thực thi ⇒ bất biến đỏ
        cells = list(c.values()); x = c["live_dd_zalopay"]; saved = x.thr
        for i in range(3):
            x.thr = [t.replace("<b>Trạng thái thực thi</b>", "Ghi chú") if k == i else t for k, t in enumerate(saved)]
            bad = D.validate_html(D.render_page(cells, NOW))
            check(f"T11g{i + 1} dòng ngưỡng {i + 1} mất cụm «Trạng thái thực thi» ⇒ bất biến đỏ", any("live_dd_zalopay" in b for b in bad), bad)
        x.thr = [saved[0].replace("thì HALT", "→ HALT")] + saved[1:]
        bad = D.validate_html(D.render_page(cells, NOW)); x.thr = saved
        check("T11h dòng ngưỡng ghi lại «→ HALT» như phanh đang chạy ⇒ bất biến đỏ", any("→ HALT" in b for b in bad), bad)
    with tempfile.TemporaryDirectory() as r:
        c, page, data = _cells(r, ledger_prov(LEDGER_OK),
                               crontab=lambda: "0 13 * * 1-5 python3 /x/mike/agents/Spyros/risk_monitor.py\n",
                               code_refs=lambda needle: (10, ["trading_bot/halt.py"]))
        t = [re.sub(r"<[^>]+>", "", x) for x in c["live_dd_spacex"].thr]
        check("T11i crontab CÓ dòng risk_monitor ⇒ «1 dòng đang bật», không còn câu «chưa có tiến trình»",
              "1 dòng đang bật" in t[0] and "chưa có tiến trình định kỳ" not in t[0] and "có lịch chạy" in t[0], t[0])
        check("T11j có file nhắc khoá ⇒ liệt kê file, KHÔNG nói «chưa có code nào đọc», không khẳng định là đã thực thi",
              "1 file nhắc tới daily_loss_limit_pct" in t[1] and "trading_bot/halt.py" in t[1]
              and "chưa có code nào đọc" not in t[1] and "không xác minh được" in t[1], t[1])
        open(os.path.join(data, "recovery_episode_state.json"), "w").write("{}")
        open(os.path.join(data, "eod_account_20261009.json"), "w").write("{}")
        t = [re.sub(r"<[^>]+>", "", x) for x in D.cell_live_dd("SpaceX", data, D.Citer(D.WC_ROOT), NOW,
                                                               dict(fake_providers(), unit_ledger=ledger_prov(LEDGER_OK))).thr]
        check("T11k file episode CÓ ⇒ «có»; ngày file eod_account đọc ra từ thư mục", "recovery_episode_state.json: có" in t[2]
              and "20261009" in t[0], (t[0][-200:], t[2][:300]))

    def boom(*a, **k):
        raise PermissionError("crontab: không được phép (giả lập)")
    with tempfile.TemporaryDirectory() as r:
        c, page, data = _cells(r, ledger_prov(LEDGER_OK), crontab=boom, code_refs=boom)
        t = [re.sub(r"<[^>]+>", "", x) for x in c["live_dd_spacex"].thr]
        check("T11l không đọc được crontab ⇒ «không xác định được» kèm lỗi thật, KHÔNG khẳng định có/không",
              "không xác định được" in t[0] and "PermissionError" in t[0] and "dòng đang bật" not in t[0]
              and "chưa có tiến trình" not in t[0], t[0])
        check("T11m quét code lỗi ⇒ «không xác định được» kèm lỗi thật, không nói «chưa có code nào đọc»",
              "không xác định được" in t[1] and "PermissionError" in t[1] and "chưa có code nào đọc" not in t[1], t[1])
        check("T11n … ô vẫn dựng được, trang vẫn đạt bất biến", c["live_dd_spacex"].error is None and D.validate_html(page) == [])
        t = [re.sub(r"<[^>]+>", "", x) for x in D.cell_live_dd("SpaceX", os.path.join(r, "khong_co"), D.Citer(D.WC_ROOT), NOW,
                                                               dict(fake_providers(), unit_ledger=ledger_prov(LEDGER_OK))).thr]
        check("T11o không liệt kê được thư mục đầu vào ⇒ «không xác định được» kèm lỗi thật", "không xác định được" in t[0]
              and "FileNotFoundError" in t[0], t[0][-300:])
    real = D.default_providers(D.WC_ROOT)
    n, hits = real["code_refs"]("recovery_episode_state")
    check("T11p provider THẬT code_refs: quét được > 100 file, thấy risk_monitor.py nhắc file trạng thái episode",
          n > 100 and "mike/agents/Spyros/risk_monitor.py" in hits, (n, hits))
    n2, hits2 = real["code_refs"]("chuoi_khong_ton_tai_o_dau_ca_xyz_123")
    check("T11q provider THẬT code_refs: chuỗi không tồn tại ⇒ 0 file (không khớp bừa)", n2 == n and hits2 == [])


def t12_real_provider():
    print("\n[T12] C2 + C3 — provider THẬT unit_ledger trên fixture tạm (cổng NAV-jump THẬT)")
    real = D.default_providers(D.WC_ROOT)

    def cells_real(data, kb):
        prov = fake_providers(); prov["unit_ledger"] = real["unit_ledger"]; prov["is_session"] = real["is_session"]
        cells, ct = D.build_cells(NOW, data_dir=data, kb_dir=kb, providers=prov, citer=D.Citer(D.WC_ROOT))
        return by(cells), D.render_page(cells, NOW, ct.misses)

    SX = [1.01e9, 1.00e9, 1.02e9, 0.99e9, 1.00e9]                           # giá đơn vị 10100/10000/10200/9900/10000
    ZP = [505000000, 605000000, 599009901, 605000000, 602004950]             # nạp 100tr sáng 10-06 ⇒ 10100/10100/10000/10100/10050
    DEP = [{"date": "2026-10-06", "amount_vnd": 100000000, "kind": "deposit", "time_ict": "08:30", "evidence": "selfcheck"}]
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r)
        write_real(data, "SpaceX", SX, 1e9)
        write_real(data, "ZaloPay", ZP, 5e8, flows=DEP)
        a, b = real["unit_ledger"]("SpaceX", data), real["unit_ledger"]("ZaloPay", data)
        check("T12a hai tài khoản đọc HAI file NAV khác nhau (khẳng định trực tiếp, không qua cổng «giống hệt»)",
              a["ledger"][1]["nav"] == 1.01e9 and b["ledger"][1]["nav"] == 505000000, (a["ledger"][1], b["ledger"][1]))
        check("T12b … hai mốc khởi điểm khác nhau", a["ledger"][0]["nav"] == 1e9 and b["ledger"][0]["nav"] == 5e8)
        check("T12c … hai sổ dòng tiền khác nhau: SpaceX 0 bản ghi, ZaloPay 1", a["n_flows"] == 0 and b["n_flows"] == 1, (a["n_flows"], b["n_flows"]))
        check("T12d nạp CÓ khai ⇒ cổng NAV-jump không chặn (bước nhảy +19,8% đã có bản ghi)", a["jumps"] == [] and b["jumps"] == [], b["jumps"])
        check("T12e nạp có khai ⇒ giá đơn vị KHÔNG nhảy theo tiền nạp (10100 → 10100)",
              abs(b["ledger"][2]["unit_price"] - 10100) < 1e-6 and b["ledger"][2]["flow_bod_vnd"] == 1e8, b["ledger"][2])
        check("T12f ΔNAV thô của dòng mới nhất được trả kèm (chưa loại dòng tiền)", abs(a["raw_last"]["change_pct"] - (1.00 / 0.99 - 1) * 100) < 1e-9
              and str(a["raw_last"]["date"]) == "2026-10-09")
        c, page = cells_real(data, kb)
        ra, rb = _rows(c["live_dd_spacex"].body), _rows(c["live_dd_zalopay"].body)
        check("T12g SpaceX qua ô: max −2,94% · hiện tại −1,96% · từ khi live +0,00% · N=5",
              c["live_dd_spacex"].error is None and ra["Drawdown lớn nhất từ khi live"][0] == "−2,94%"
              and ra["Drawdown hiện tại từ đỉnh"][0] == "−1,96%" and ra["Tỉ suất từ khi live (gia quyền thời gian)"][0] == "+0,00%"
              and ra["Số phiên live (N)"][0] == "5", (c["live_dd_spacex"].error, ra))
        check("T12h ZaloPay qua ô (đã loại khoản nạp): max −0,99% · hiện tại −0,50% · từ khi live +0,50%",
              c["live_dd_zalopay"].error is None and rb["Drawdown lớn nhất từ khi live"][0] == "−0,99%"
              and rb["Drawdown hiện tại từ đỉnh"][0] == "−0,50%" and rb["Tỉ suất từ khi live (gia quyền thời gian)"][0] == "+0,50%",
              (c["live_dd_zalopay"].error, rb))
        check("T12i nguồn ô ZaloPay ghi «hiện 1 bản ghi», SpaceX «hiện 0 bản ghi»", "hiện <b>1 bản ghi</b>" in c["live_dd_zalopay"].source
              and "hiện <b>0 bản ghi</b>" in c["live_dd_spacex"].source)
        check("T12j trang đạt bất biến, không ô drawdown nào CŨ (NAV tới Thứ Sáu, now = Thứ Hai 09:00)",
              D.validate_html(page) == [] and c["live_dd_spacex"].stale is False and c["live_dd_zalopay"].stale is False)
        # nạp KHÔNG khai: cùng NAV, sổ dòng tiền rỗng
        write_real(data, "ZaloPay", ZP, 5e8, flows=[])
        c, page = cells_real(data, kb)
        z = c["live_dd_zalopay"]
        check("T12k nạp KHÔNG khai ⇒ cổng NAV-jump THẬT chặn, ô báo lỗi thật, KHÔNG in drawdown",
              "NAV-jump" in (z.error or "") and "+19.80%" in z.error and "Drawdown hiện tại" not in z.body, z.error)
        check("T12l … ô vẫn hiện ΔNAV thô + nêu cần khai dòng tiền / market_only; tài khoản kia không bị kéo theo",
              "ΔNAV <b>thô</b>" in z.body and "market_only" in z.body and c["live_dd_spacex"].error is None and z.touched == []
              and D.validate_html(page) == [], z.body)
        # thiếu sổ dòng tiền
        os.remove(os.path.join(data, "account_cash_flows.json"))
        c, page = cells_real(data, kb)
        check("T12m THIẾU sổ dòng tiền ⇒ cả hai ô từ chối kèm lỗi thật (không đoán «không có dòng tiền»)",
              all("KHÔNG có sổ dòng tiền" in (c[k].error or "") for k in ("live_dd_spacex", "live_dd_zalopay")), c["live_dd_spacex"].error)
        check("T12n … lỗi nêu đúng đường dẫn trong data_dir được truyền (provider không rơi về file thật)",
              os.path.join(data, "account_cash_flows.json") in c["live_dd_spacex"].error)
    # C2: phiên −5,5% và −4,99% đi qua CỔNG THẬT
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r)
        write_real(data, "SpaceX", [1.01e9, 1.00e9, 1.02e9, 1.00e9, 0.945e9], 1e9)             # phiên cuối −5,50%
        write_real(data, "ZaloPay", [5.05e8, 5.00e8, 5.10e8, 5.00e8, 4.7505e8], 5e8)           # phiên cuối −4,99%
        c, page = cells_real(data, kb)
        a, b = c["live_dd_spacex"], c["live_dd_zalopay"]
        check("T12o phiên −5,50% không khai: cổng chặn (ô KHÔNG CÓ DỮ LIỆU) NHƯNG vẫn CHẠM phanh lỗ trong ngày trên ΔNAV thô",
              "NAV-jump" in (a.error or "") and len(a.touched) == 1 and "ΔNAV thô" in a.touched[0] and "−5,50%" in a.touched[0], (a.error, a.touched))
        check("T12p … ô hiện rõ con số thô + ghi chú chưa loại dòng tiền + cổng đang chặn phần còn lại",
              "−5,50%" in a.body and "CHƯA loại dòng tiền" in a.body and "Cổng NAV-jump đang chặn phần còn lại" in a.body
              and "market_only" in a.body, a.body)
        check("T12q … lên khối «đáng chú ý» của trang; ngày dữ liệu của ô vẫn có", "ΔNAV thô" in page.split("<h2>")[0]
              and a.as_of == "2026-10-09" and D.validate_html(page) == [])
        check("T12r phiên −4,99%: cổng không chặn, KHÔNG chạm", b.error is None and b.touched == []
              and _rows(b.body)["Phiên gần nhất so với phiên trước"][0] == "−4,99%", (b.error, b.touched))
        # cùng phiên −5,50% nhưng ĐÃ khai market_only ⇒ cổng mở, chạm theo giá đơn vị
        write_real(data, "SpaceX", [1.01e9, 1.00e9, 1.02e9, 1.00e9, 0.945e9], 1e9,
                   flows=[{"date": "2026-10-09", "amount_vnd": 0, "kind": "market_only", "evidence": "selfcheck: thị trường"}])
        c, page = cells_real(data, kb)
        a = c["live_dd_spacex"]
        check("T12s −5,50% đã khai market_only ⇒ cổng mở, ô có số, chạm đúng 1 lần theo giá đơn vị",
              a.error is None and len(a.touched) == 1 and "giá đơn vị −5,50%" in a.touched[0]
              and _rows(a.body)["Drawdown hiện tại từ đỉnh"][0] == "−7,35%", (a.error, a.touched))
    # N1 + N6 qua provider thật: giờ chụp lệch + dòng ngày lễ + phiên thiếu
    with tempfile.TemporaryDirectory() as r:
        data, kb = write_fixture(r)
        # 08-27 (T5) … 09-04 (T6): 08-31, 09-01, 09-02 nghỉ lễ theo trading_bot.vn_market
        write_real(data, "SpaceX", [1.00e9, 1.01e9, 1.01e9, 0.98e9, 0.99e9], 1e9, start="2026-08-27", inception="2026-08-26",
                   ts={0: "2026-08-27T09:46:35", 3: "2026-09-04T19:15:15"})
        ex = os.path.join(data, "execution_logs", "nav_history_SpaceX.csv")
        lines = open(ex).read().splitlines()
        lines[3] = lines[3].replace("2026-08-31", "2026-08-31")                # dòng 08-31 = ngày nghỉ lễ, giữ
        lines[4] = lines[4].replace("2026-09-01", "2026-09-03")                # 09-03 = phiên thật, chụp sáng 09-04
        lines[5] = lines[5].replace("2026-09-02", "2026-09-07").replace("2026-09-07T19", "2026-09-07T19")
        open(ex, "w").write("\n".join(lines) + "\n")                           # ⇒ thiếu dòng phiên 09-04
        write_real(data, "ZaloPay", [5.05e8, 5.00e8, 5.10e8, 5.00e8, 5.02e8], 5e8)
        got = real["unit_ledger"]("SpaceX", data)
        off = {str(x["date"]): x["snap_off"] for x in got["ledger"][1:]}
        check("T12t (N1) balance_ts TRƯỚC đóng cửa cùng ngày, hoặc của NGÀY KHÁC ⇒ gắn «chụp lệch giờ»; chụp 19:10 cùng ngày ⇒ không",
              off["2026-08-27"] == "balance_ts 2026-08-27T09:46:35" and off["2026-09-03"] == "balance_ts 2026-09-04T19:15:15"
              and off["2026-08-28"] is None and off["2026-09-07"] is None, off)
        s = D.drawdown_stats(got["ledger"], real["is_session"])
        check("T12u (N6) N = số PHIÊN: 5 dòng file, 1 dòng rơi ngày lễ 08-31 ⇒ N = 4; phiên 09-04 thiếu được nêu, ngày lễ không bị coi là thiếu",
              s["n"] == 4 and [str(x["date"]) for x in s["non_session"]] == ["2026-08-31"]
              and [str(d) for d in s["missing"]] == ["2026-09-04"], (s["n"], s["non_session"], s["missing"]))
        now = datetime(2026, 9, 8, 9, 0, tzinfo=D.ICT)
        prov = fake_providers(); prov["unit_ledger"] = real["unit_ledger"]; prov["is_session"] = real["is_session"]
        x = D.cell_live_dd("SpaceX", data, D.Citer(D.WC_ROOT), now, prov)
        rw = _rows(x.body)
        check("T12v (N1) đáy drawdown rơi vào dòng chụp lệch giờ ⇒ nhãn ngay cạnh ngày + nêu cỡ sai số tính từ dữ liệu",
              x.error is None and "chụp lệch giờ: balance_ts 2026-09-04T19:15:15" in rw["Drawdown lớn nhất từ khi live"][1]
              and "sai số tới cỡ 3,0 điểm phần trăm" in rw["Drawdown lớn nhất từ khi live"][1], (x.error, rw))
        check("T12w (N1) cặp có đầu mút lệch giờ KHÔNG được gọi là giá chốt; ô liệt kê các phiên lệch giờ",
              "KHÔNG chụp sau đóng cửa cùng ngày" in rw["Phiên giảm mạnh nhất"][1] and "giá chốt → giá chốt" not in x.body.replace(
                  "không phải giá chốt → giá chốt", "") and "2/4 phiên có NAV <b>chụp lệch giờ</b>" in x.body, rw["Phiên giảm mạnh nhất"])
        check("T12x (N6) ô ghi N = 4 và nêu dòng ngày lễ + phiên thiếu", rw["Số phiên live (N)"][0] == "4"
              and "ngày KHÔNG có phiên" in x.body and "2026-08-31" in x.body and "PHIÊN có thật nhưng thiếu dòng NAV" in x.body, x.body[-700:])


def t13_stale_and_touch():
    print("\n[T13] C4b — CŨ theo mốc 19:10 ICT + lịch phiên; N7 — biên chạm ngưỡng")
    wd = lambda d: d.weekday() < 5
    real = D.default_providers(D.WC_ROOT)
    f = D.nav_expected_date
    mk = lambda y, m, d, hh, mm, tz=D.ICT: datetime(y, m, d, hh, mm, tzinfo=tz)
    check("T13a Thứ Hai 19:09 ICT ⇒ kỳ vọng NAV của Thứ Sáu trước", str(f(mk(2026, 10, 12, 19, 9), wd)) == "2026-10-09")
    check("T13b Thứ Hai 19:10 ICT ⇒ kỳ vọng NAV của CHÍNH hôm nay", str(f(mk(2026, 10, 12, 19, 10), wd)) == "2026-10-12")
    check("T13c Thứ Bảy/Chủ Nhật ⇒ Thứ Sáu", str(f(mk(2026, 10, 10, 23, 0), wd)) == "2026-10-09" and str(f(mk(2026, 10, 11, 23, 0), wd)) == "2026-10-09")
    check("T13d now cho bằng UTC (12:10Z = 19:10 ICT) ⇒ vẫn là hôm nay — neo ICT tường minh, không theo tz của now",
          str(f(mk(2026, 10, 12, 12, 10, timezone.utc), wd)) == "2026-10-12" and str(f(mk(2026, 10, 12, 12, 9, timezone.utc), wd)) == "2026-10-09")
    check("T13e now 17:30Z Chủ Nhật = 00:30 ICT Thứ Hai ⇒ Thứ Sáu (ngày ICT, không phải ngày UTC)",
          str(f(mk(2026, 10, 11, 17, 30, timezone.utc), wd)) == "2026-10-09")
    check("T13f lịch nghỉ lễ THẬT (trading_bot.vn_market): sáng 09-03 sau Quốc khánh ⇒ kỳ vọng 08-28; tối 09-02 (lễ) ⇒ 08-28",
          str(f(mk(2026, 9, 3, 9, 0), real["is_session"])) == "2026-08-28" and str(f(mk(2026, 9, 2, 20, 0), real["is_session"])) == "2026-08-28")
    for hh, mm, want in ((19, 0, False), (19, 30, True)):
        with tempfile.TemporaryDirectory() as r:
            now = mk(2026, 10, 12, hh, mm)
            c, page, _ = _cells(r, ledger_prov(LEDGER_OK), now=now)       # NAV tới Thứ Sáu 10-09
            x = c["live_dd_spacex"]
            check(f"T13g Thứ Hai {hh}:{mm:02d} ICT, NAV mới tới Thứ Sáu ⇒ ô drawdown {'CŨ' if want else 'KHÔNG cũ'}",
                  x.stale is want and (not want or ("2026-10-12" in x.stale_why and "19:10" in x.stale_why)), (x.stale, x.stale_why))
            if want:
                check("T13h … huy hiệu CŨ + lý do hiện trên trang và trong khối «đáng chú ý»",
                      'class="bdg stale"' in D.render_cell(x) and "Nguồn CŨ</b> — Drawdown thật — tài khoản SpaceX" in page)
    with tempfile.TemporaryDirectory() as r:        # thứ tự chạy thật: ZaloPay đã chụp hôm nay, SpaceX chưa
        now = mk(2026, 10, 12, 19, 11)
        zp_today = ledger_prov({"ZaloPay": [10000, 9800, 9700, 9900]}, end="2026-10-12")
        sx_yday = ledger_prov({"SpaceX": [10000, 10100, 9900, 10050]}, end="2026-10-09")
        c, page, _ = _cells(r, lambda acc, d=None: (zp_today if acc == "ZaloPay" else sx_yday)(acc, d), now=now)
        check("T13i lượt ZaloPay (chạy trước): ô ZaloPay tươi, ô SpaceX gắn CŨ — không còn số hôm qua trôi qua không nhãn",
              c["live_dd_zalopay"].stale is False and c["live_dd_spacex"].stale is True, (c["live_dd_zalopay"].stale_why, c["live_dd_spacex"].stale_why))
    with tempfile.TemporaryDirectory() as r:        # ô lỗi vì cổng chặn vẫn mang ngày dữ liệu + cờ CŨ
        j = [dict(date="2026-10-08", prev_date="2026-10-07", nav0=1e9, nav1=1.2e9, change_pct=20.0)]
        c, page, _ = _cells(r, ledger_prov(LEDGER_OK, jumps=j), now=mk(2026, 10, 12, 19, 30))
        check("T13j cổng chặn ⇒ ô lỗi nhưng VẪN có ngày dữ liệu và cờ CŨ", c["live_dd_spacex"].error and c["live_dd_spacex"].as_of == "2026-10-09"
              and c["live_dd_spacex"].stale is True)
    # ── N7
    with tempfile.TemporaryDirectory() as r:
        c, page, _ = _cells(r, ledger_prov({"SpaceX": [10000, 12000, 9000, 10800], "ZaloPay": [10000, 9000, 9500, 9400]}))
        ra = _rows(c["live_dd_spacex"].body)
        check("T13k (M11) từng dòng bảng hiện ĐÚNG đại lượng của nó: hiện tại −10,00% (từ ĐỈNH 12000, không từ mốc) · lớn nhất −25,00% · "
              "từ khi live +8,00% · phiên gần nhất +20,00% · phiên giảm mạnh nhất −25,00%",
              ra["Drawdown hiện tại từ đỉnh"][0] == "−10,00%" and ra["Drawdown lớn nhất từ khi live"][0] == "−25,00%"
              and ra["Tỉ suất từ khi live (gia quyền thời gian)"][0] == "+8,00%" and ra["Phiên gần nhất so với phiên trước"][0] == "+20,00%"
              and ra["Phiên giảm mạnh nhất"][0] == "−25,00%", ra)
        check("T13l (M18) drawdown LỚN NHẤT lịch sử −25% nhưng HIỆN TẠI −10% ⇒ KHÔNG chạm mức 25%",
              not any("25% của luật HALT" in t for t in c["live_dd_spacex"].touched), c["live_dd_spacex"].touched)
        check("T13m (M21) phiên xấu nhất LỊCH SỬ −25% / −10% nhưng phiên GẦN NHẤT không tới −5% ⇒ KHÔNG chạm phanh lỗ trong ngày",
              c["live_dd_spacex"].touched == [] and c["live_dd_zalopay"].touched == [], (c["live_dd_spacex"].touched, c["live_dd_zalopay"].touched))
    with tempfile.TemporaryDirectory() as r:
        c, page, _ = _cells(r, ledger_prov({"SpaceX": [10000, 20000, 18998], "ZaloPay": [10000, 20000, 19002]}))
        check("T13n (M19) biên −5%: phiên −5,01% ⇒ chạm; phiên −4,99% ⇒ không", len(c["live_dd_spacex"].touched) == 1
              and "−5,01%" in c["live_dd_spacex"].touched[0] and c["live_dd_zalopay"].touched == [],
              (c["live_dd_spacex"].touched, c["live_dd_zalopay"].touched))
    with tempfile.TemporaryDirectory() as r:        # ngưỡng ĐỌC từ file luật, không viết cứng: đổi luật thành −3% ⇒ phiên −4% chạm
        root = os.path.join(r, "root"); os.makedirs(os.path.join(root, "data"))
        for rel in ("CLAUDE.md", "mike/agents/Spyros/risk_monitor.py", "mike/kb/projects/fund-unit-performance-policy-20261010.md",
                    "data/trading_rules.json"):
            os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
            txt = open(os.path.join(D.WC_ROOT, rel), encoding="utf-8").read()
            if rel.endswith("trading_rules.json"):
                txt = txt.replace('"daily_loss_limit_pct": -0.05', '"daily_loss_limit_pct": -0.03')
            if rel.endswith("risk_monitor.py"):
                txt = txt.replace("DD_THRESHOLD = 0.25", "DD_THRESHOLD = 0.10")
            open(os.path.join(root, rel), "w", encoding="utf-8").write(txt)
        prov = dict(fake_providers(), unit_ledger=ledger_prov([10000, 12500, 12000, 11520]))
        x = D.cell_live_dd("SpaceX", os.path.join(root, "data"), D.Citer(root), NOW, prov)
        check("T13o (M19) ngưỡng đọc từ file luật lúc chạy: luật −3% ⇒ phiên −4,00% chạm; luật 10% ⇒ drawdown −7,84% không chạm",
              len(x.touched) == 1 and "−4,00%" in x.touched[0] and "−3,0%" in x.touched[0] and "10%" in x.thr[0], (x.touched, x.thr[0][:120]))
        prov = dict(fake_providers(), unit_ledger=ledger_prov([10000, 12500, 12400, 11240]))
        x = D.cell_live_dd("SpaceX", os.path.join(root, "data"), D.Citer(root), NOW, prov)
        check("T13p (M18) … drawdown hiện tại −10,08% với luật 10% ⇒ chạm (cùng lúc phiên −9,35% chạm luật −3%)",
              len(x.touched) == 2 and any("10% của luật HALT" in t for t in x.touched), x.touched)


def main():
    print(f"strategy_fit_dashboard selfcheck — TZ env = {os.environ.get('TZ')!r}, WC_ROOT = {D.WC_ROOT}")
    for t in (t1_full, t2_missing, t3_stale, t4_empty, t5_nan, t6_tz, t7_mutation, t8_anchors, t9_touch_logic, t10_tier3,
              t11_enforcement, t12_real_provider, t13_stale_and_touch):
        try:
            t()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAIL.append(f"{t.__name__} CRASH: {e!r}")
    print(f"\n==> {len(PASS)} PASS / {len(FAIL)} FAIL")
    for f in FAIL:
        print("   FAIL:", f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
