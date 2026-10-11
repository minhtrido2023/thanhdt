"""Mô phỏng quỹ 'đúng' (đơn vị phát hành ở NAV liên tục) rồi so giá đơn vị của nhánh với sự thật.
Dòng tiền CHỈ ngoài phiên (giữa 14:45 và 09:00 phiên kế) ⇒ luật D1 phải cho ĐÚNG CHÍNH XÁC."""
import sys, random, datetime as dt, collections
sys.path.insert(0, "/tmp/ar2/fix/WC/mike/bin")
import account_cash_flows as acf, nav_unit_ledger as nul
OPEN, CLOSE = dt.time(9,0), dt.time(14,45)
def sim(seed, p_missing=0.0, p_weekend_row=0.0, p_preclose=0.0, p_nextmorning=0.0, p_holiday=0.0, nflows=2, in_session=False):
    rnd = random.Random(seed)
    d0 = dt.date(2026,6,1)                       # Thứ Hai; mốc khởi điểm = Chủ nhật 05-31
    days = [d0 + dt.timedelta(days=i) for i in range(21)]
    trading = [d for d in days if d.weekday() < 5 and rnd.random() >= p_holiday]
    ret = {d: rnd.uniform(-0.06, 0.06) for d in trading}
    def V(t):                                    # giá trị 1 đơn vị tại thời điểm t
        v = 1.0
        for d in trading:
            o, c = dt.datetime.combine(d, OPEN), dt.datetime.combine(d, CLOSE)
            if t >= c: v *= 1 + ret[d]
            elif t > o: v *= 1 + ret[d] * ((t - o) / (c - o))
        return v
    # dòng tiền
    flows = []
    for _ in range(nflows):
        while True:
            t = dt.datetime.combine(rnd.choice(days[1:-2]), dt.time(rnd.randrange(24), rnd.randrange(60), rnd.randrange(60)))
            ins = t.date() in ret and OPEN <= t.time() < CLOSE
            if ins == in_session: break
        amt = rnd.choice([1,-1]) * rnd.uniform(0.05, 0.3) * 1e9
        flows.append((t, amt))
    flows.sort()
    def U(t):
        u = 1e9 / 1.0
        for tf, a in flows:
            if tf <= t: u += a / V(tf)
        return u
    rows, truth, tags = [], {}, set()
    for d in days:
        is_tr = d in ret
        if is_tr and rnd.random() < p_missing: tags.add("missing"); continue
        if not is_tr and rnd.random() >= p_weekend_row: continue
        if not is_tr: tags.add("nontrading_row")
        x = rnd.random()
        if x < p_preclose:
            snap = dt.datetime.combine(d, dt.time(rnd.randrange(0, 14), rnd.randrange(60), 7)); tags.add("preclose")
        elif x < p_preclose + p_nextmorning:
            snap = dt.datetime.combine(d + dt.timedelta(days=1), dt.time(rnd.randrange(0, 12), rnd.randrange(60), 7)); tags.add("nextmorning")
        else:
            snap = dt.datetime.combine(d, dt.time(19, rnd.randrange(5, 20), 7))
        closed = snap >= dt.datetime.combine(d, CLOSE)
        # NAV chụp: vị thế định giá ở giá chốt ngày của dòng (nếu đã qua đóng cửa), tiền/đơn vị tại lúc chụp
        vref = V(dt.datetime.combine(d, dt.time(23,59))) if closed else V(snap)
        nav = U(snap) * vref
        rows.append(acf.NavRow(d, nav, balance_ts=snap.isoformat()))
        truth[d] = vref
    fl = [{"date": t.date(), "time_ict": t.strftime("%H:%M:%S"), "amount_vnd": a, "kind": "deposit" if a > 0 else "withdraw",
           "evidence": "x", "timing": None} for t, a in flows]
    try:
        led, info = nul.build_ledger(rows, fl, dt.date(2026,5,31), 1e9)
    except Exception as e:
        return "error", tags, str(e)[:150], None
    worst = 0.0; where = None
    assigned = {f["date"]: (r["date"], f["timing"]) for r in led for f in r["flows"]}
    for r in led[1:]:
        dev = r["unit_price"] / 10000.0 / truth[r["date"]] - 1
        if abs(dev) > abs(worst): worst, where = dev, r["date"]
    if abs(worst) > 1e-9:
        return "SILENT_WRONG", tags, f"lệch {worst*100:+.3f}% tại {where}; flows={[(t.isoformat(), round(a/1e6)) for t,a in flows]} assigned={assigned} rows={[(r[0].isoformat()[5:], r.balance_ts[5:16]) for r in rows]} trading={[d.isoformat()[5:] for d in trading]}", worst
    return ("ok_pending" if info["pending"] else "ok"), tags, None, None
def campaign(name, n=3000, **kw):
    c = collections.Counter(); ex = None; mx = 0
    for s in range(n):
        st, tags, msg, w = sim(s, **kw)
        c[st] += 1
        if st == "SILENT_WRONG":
            if abs(w) > mx: mx, ex = abs(w), msg
    print(f"{name:55s} {dict(c)}  max|lệch|={mx*100:.3f}%")
    if ex: print("    ví dụ tệ nhất:", ex[:900])
if __name__ == "__main__":
    campaign("A. sạch: mọi phiên có dòng, chụp ~19:1x")
    campaign("B. + ngày nghỉ lễ giữa tuần", p_holiday=0.2)
    campaign("C. + dòng NAV cả cuối tuần/ngày nghỉ", p_holiday=0.2, p_weekend_row=0.5)
    campaign("D. + chụp sáng hôm sau", p_nextmorning=0.2)
    campaign("E. + chụp TRƯỚC đóng cửa", p_preclose=0.2)
    campaign("F. + THIẾU dòng của một phiên giao dịch", p_missing=0.15)
    campaign("G. tất cả", p_holiday=0.15, p_weekend_row=0.3, p_nextmorning=0.1, p_preclose=0.1, p_missing=0.1)
    campaign("H. sạch, 5 dòng tiền", nflows=5)
