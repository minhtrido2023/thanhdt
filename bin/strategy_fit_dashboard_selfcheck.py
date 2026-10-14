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
                                 deposit_rate_source="cctg_12m", asof=vr_asof),
        killswitch=lambda: ks or dict(armed=False, rate=0.074, threshold=0.075, stale=False,
                                      last_update="2026-10-03", age_days=8, rate_source="cctg_12m(2026-10-05)",
                                      reason="cctg_12m(2026-10-05) 7.40% <= 7.5% -> CLEAR"),
        big4_rate=lambda: big4,
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
        check("T1a đủ 9 ô, không ô nào lỗi", list(c) == D.CELL_KEYS and all(x.error is None for x in cells),
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
        check("T1k2 ô Value Radar ghi đúng tenor CCTG 12T (nhãn cctg_12m, rebase 05/10)",
              "CCTG 12T" in c["env_value"].body and "CCTG 6T" not in c["env_value"].body)
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
        check("T2a không crash, đủ 9 ô", list(c) == D.CELL_KEYS)
        check("T2b 8 ô dữ liệu đều báo lỗi", all(x.error is not None for x in data_cells),
              [x.key for x in data_cells if x.error is None])
        check("T2c lỗi THẬT được in ra (tên file / thông điệp exception)",
              "edge_health_matrix.csv" in (c["edge_ic"].error or "")
              and "BQ không kết nối được" in (c["env_dt5g"].error or ""),
              (c["edge_ic"].error, c["env_dt5g"].error))
        check("T2d trang vẫn đạt bất biến (as_of + ngưỡng vẫn hiện)", D.validate_html(page) == [], D.validate_html(page))
        check("T2e có đủ 8 thông báo KHÔNG CÓ DỮ LIỆU", page.count("nodata-msg") >= 8, page.count("nodata-msg"))
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
        for k in ("edge_ic", "edge_lag", "env_dt5g", "env_breadth", "env_value", "env_rates", "env_structural"):
            check(f"T3 {k} gắn CŨ", c[k].stale is True and 'class="bdg stale"' in D.render_cell(c[k]), c[k].stale_why)
        check("T3 edge_capit KHÔNG gắn CŨ (nguồn không có nhịp)", c["edge_capit"].stale is None)
        page = D.render_page(cells, NOW)
        check("T3 khối đầu trang liệt kê nguồn CŨ", page.count("<b>Nguồn CŨ</b>") == 7, page.count("<b>Nguồn CŨ</b>"))
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
        check("T9g ô mô tả không bao giờ chạm", t["env_breadth"] == [] and t["env_value"] == [] and t["book_map"] == [])
        check("T9h Không còn câu «Không ô nào chạm ngưỡng»", "Không ô nào chạm ngưỡng." not in page)
    check("T9i tercile: thấp nhất 252 phiên ⇒ LOW (pct=0 không bị ném mất)",
          D.breadth_tercile([0.5] * 252 + [0.1]) == (0.0, "LOW"))
    check("T9j tercile: cao nhất ⇒ HIGH", D.breadth_tercile([0.5] * 252 + [0.9])[1] == "HIGH")
    check("T9k tercile: thiếu 252 phiên trước ⇒ không xếp", D.breadth_tercile([0.5] * 100) == (None, None))


def main():
    print(f"strategy_fit_dashboard selfcheck — TZ env = {os.environ.get('TZ')!r}, WC_ROOT = {D.WC_ROOT}")
    for t in (t1_full, t2_missing, t3_stale, t4_empty, t5_nan, t6_tz, t7_mutation, t8_anchors, t9_touch_logic):
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
