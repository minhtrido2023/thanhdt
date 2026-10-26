#!/usr/bin/env python3
"""Khối HIỂN THỊ "nowcast KQKD theo hàng hoá" cho mã producer (job Taylor_20261026_095926, user duyệt 26/10).

DISPLAY-ONLY: không gate, không tilt, không đổi sizing/lệnh. Nguồn nghiên cứu:
agents/Taylor/research/commodity_cycle_te_20261026/ (REPORT.md §B2/§B4/§5).

- Giá: BQ tav2_bq.commodity_prices với source + cadence='daily' TƯỜNG MINH: mặc định 'trading_economics';
  ngoại lệ duy nhất SOURCE_OVERRIDE (P4 'yellow_phosphorus' -> 'sunsirs', từ 2018; job Taylor_20261026_163838).
  KHÔNG dùng commodity_latest / unified — view đó trộn nguồn. Mốc thời gian = observation_date.
- c_yoy = log(giá TB quý / giá TB cùng quý năm trước) × dấu vai trò (producer +1 / consumer −1), TB theo QUÝ LỊCH,
  quý chỉ tính khi có ≥ MIN_OBS quan sát (đúng b2_nowcast.py).
- Phân vị TB63 = tỉ lệ giá trị TB63 phiên (toàn lịch sử đến nay) ≤ giá trị mới nhất; R/MA252 = giá cuối / TB 252 quan sát.
- Nhãn là MÔ TẢ theo ngưỡng cố định (NEUTRAL_BAND), không phải tín hiệu.
- Độ tươi: data/commodity_freshness_state.json; STALE/FROZEN/thiếu => 'KHÔNG ĐỦ TƯƠI', không in số.
  Series sunsirs P4 CHƯA nằm trong monitor => tự kiểm theo tuổi quan sát cuối (<= P4_MAX_AGE_D ngày), nói rõ trong dòng.
- FAIL-OPEN: mọi lỗi => log WARN ra stderr + trả chuỗi rỗng, không bao giờ ném lỗi ra caller.

Dùng: commodity_nowcast_block.py --plan-file <plan.json> | --tickers DPM,DRI,GAS
"""
import argparse, csv, io, json, math, os, subprocess, sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # .../mike
WC_ROOT = os.environ.get("WC_ROOT", os.path.dirname(ROOT))                  # .../WorkingClaude
MAP_CSV = os.environ.get("COMMODITY_MAP_CSV", os.path.join(
    ROOT, "agents/Taylor/research/commodity_cycle_te_20261026/commodity_map_te.csv"))
FRESH_JSON = os.environ.get("COMMODITY_FRESH_JSON", os.path.join(WC_ROOT, "data/commodity_freshness_state.json"))

NEUTRAL_BAND = 0.05      # |c_yoy| < 0.05 => trung tính (mô tả, không phải tín hiệu)
MIN_OBS = 40             # quý lịch cần >= 40 quan sát (b2_nowcast.py)
FRESH_MAX_AGE_H = 72     # file trạng thái tươi cũ hơn mức này => coi như thiếu
BQ_TIMEOUT_S = 15
ICT = timezone(timedelta(hours=7))

SOURCE_OVERRIDE = {"yellow_phosphorus": "sunsirs"}     # key -> source khác TE
SOURCE_FROM = {"yellow_phosphorus": "2018-01-01"}      # trước mốc này chuỗi thưa (khe tới 191 ngày) => cắt
P4_MAX_AGE_D = 7                                       # P4 sunsirs chưa có trong monitor: tuổi quan sát cuối tối đa
P4_KEY = "yellow_phosphorus"

# Override hiển thị (KHÔNG sửa commodity_map_te.csv — md5 bị khoá bởi tracker/PREREG-4): bỏ dòng TE phosphorus (nay là quặng)
# của DGC/PAT + lưu huỳnh của DGC/PAT (chỉ đạo user: không in lưu huỳnh), thêm P4 sunsirs tier D (chỉ mô tả).
MAP_DROP = {("DGC", "phosphorus"), ("PAT", "phosphorus"), ("DGC", "sulfur"), ("PAT", "sulfur")}
MAP_ADD = [("DGC", "p4_yellow"), ("PAT", "p4_yellow")]
P4_NOTE = "P4 sunsirs (CNY/t, từ 2018) thay dòng TE phosphorus (nay là quặng); quan hệ gãy từ 2024"

QUERY = ("SELECT metric_key, observation_date, value FROM tav2_bq.commodity_prices "
         "WHERE cadence='daily' AND ((source='trading_economics' AND metric_key IN ({te_keys})) "
         "OR (source='sunsirs' AND metric_key IN ({ss_keys}) AND observation_date >= '{ss_from}' "
         "AND EXTRACT(DAYOFWEEK FROM observation_date) BETWEEN 2 AND 6)) "
         "ORDER BY metric_key, observation_date")

FOOTER = ("_Thị trường đã định giá phần này trước ngày công bố (nowcast IC 0,44 với KQKD, ~0 với giá CP sau công bố); "
          "chỉ dùng để đọc KQKD, không phải tín hiệu mua/bán._")
OIL_WARN = "⚠️ dầu thô: IC với LN ~0 (hợp đồng trễ)"
P4_WARN = ("⚠️ P4: quan hệ giá P4 với LN DGC đã GÃY từ 2024 (IC 0,46-0,50 toàn mẫu 30 quý, nhưng 0,23 khi bỏ 2021Q3-2022Q4 "
           "và -0,21 từ 2024) — chỉ mô tả, KHÔNG phải tín hiệu giao dịch, không sizing")
DGC_LEGAL_WARN = ("⚠️ DGC pháp lý/quản trị (chỉ cảnh báo): theo hồ sơ nội bộ — kiểm toán ngoại trừ (hàng tồn kho + vụ án hình sự), "
                  "lãnh đạo bị truy tố, diện kiểm soát; giá hàng hoá KHÔNG xoá rủi ro này")
STALE_TXT = "KHÔNG ĐỦ TƯƠI"


def warn(msg):
    print(f"[commodity_nowcast] WARN {msg}", file=sys.stderr)


def load_map(path=None):
    """{ticker: [row,...]} chỉ tier A/B/D, bỏ dòng ticker '-'. Mỗi row: family,key,sign,tier,note."""
    out = {}
    with open(path or MAP_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ticker"] == "-" or r["tier"] not in ("A", "B", "D"):
                continue
            out.setdefault(r["ticker"], []).append(dict(
                family=r["family"], key=r["te_metric_key"], sign=int(r["sign"]), tier=r["tier"], note=r["note"]))
    for (t, fam) in MAP_ADD:
        rows = out.setdefault(t, [])
        rows[:] = [r for r in rows if (t, r["key"]) not in MAP_DROP]
        if not any(r["key"] == P4_KEY for r in rows):
            rows.append(dict(family=fam, key=P4_KEY, sign=1, tier="D", note=P4_NOTE))
    for t, rows in out.items():
        rows[:] = [r for r in rows if (t, r["key"]) not in MAP_DROP]
        rows.sort(key=lambda r: r["tier"])        # A trước B trước D
    return out


def fetch_te(keys, runner=None):
    """-> {metric_key: [(date, value), ...]} sắp theo ngày. Ném lỗi nếu BQ chết (caller bắt)."""
    q = lambda ks: ",".join("'%s'" % k for k in sorted(ks)) or "''"
    ss = {k for k in keys if SOURCE_OVERRIDE.get(k) == "sunsirs"}
    sql = QUERY.format(te_keys=q(set(keys) - ss), ss_keys=q(ss), ss_from=SOURCE_FROM.get(P4_KEY, "2018-01-01"))
    if runner is None:
        env = f"source {WC_ROOT}/wc_env.sh >/dev/null 2>&1; "
        cmd = env + "bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000 \"$SQL\""
        p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=BQ_TIMEOUT_S,
                           env={**os.environ, "SQL": sql})
        if p.returncode != 0:
            raise RuntimeError(f"bq rc={p.returncode}: {p.stderr.strip()[-200:]}")
        text = p.stdout
    else:
        text = runner(sql)
    series = {}
    for r in csv.DictReader(io.StringIO(text)):
        try:
            d = r["observation_date"][:10]
            if r["metric_key"] in SOURCE_OVERRIDE and datetime.fromisoformat(d).weekday() >= 5:
                continue                                  # sunsirs lặp giá T6 vào T7/CN => lệch TB; SQL đã lọc, đây là lớp 2
            series.setdefault(r["metric_key"], []).append((d, float(r["value"])))
        except (ValueError, KeyError):
            continue
    for v in series.values():
        v.sort()
    return series


def load_fresh(path=None, now=None):
    """-> (dict series_state, err). err != '' khi file thiếu/hỏng/cũ => mọi series coi như KHÔNG ĐỦ TƯƠI."""
    try:
        d = json.load(open(path or FRESH_JSON, encoding="utf-8"))
        gen = datetime.fromisoformat(d["generated_at"])
        age_h = ((now or datetime.now(ICT)) - gen).total_seconds() / 3600
        if age_h > FRESH_MAX_AGE_H:
            return {}, f"freshness_state cũ {age_h:.0f}h"
        return d["series"], ""
    except Exception as e:
        return {}, f"freshness_state không đọc được: {e}"


def is_fresh(key, fresh, series=None, now=None):
    src = SOURCE_OVERRIDE.get(key, "trading_economics")
    st = fresh.get(f"{key}|{src}|daily")
    if st:
        return st.get("status") == "OK"
    if key in SOURCE_OVERRIDE and series and series.get(key):       # chưa có trong monitor: tự kiểm tuổi quan sát cuối
        last = datetime.fromisoformat(series[key][-1][0]).date()
        return ((now or datetime.now(ICT)).date() - last).days <= P4_MAX_AGE_D
    return False


def _qkey(date_s):
    y, m = int(date_s[:4]), int(date_s[5:7])
    return y, (m - 1) // 3 + 1


def metrics(obs):
    """obs: [(date,value)] sắp xếp. -> dict số liệu hoặc None nếu thiếu dữ liệu."""
    if len(obs) < 252:
        return None
    dates = [d for d, _ in obs]; vals = [v for _, v in obs]
    last_d, last_v = dates[-1], vals[-1]
    qs = {}
    for d, v in obs:
        qs.setdefault(_qkey(d), []).append(v)
    mean = lambda q: (sum(qs[q]) / len(qs[q])) if q in qs and len(qs[q]) >= MIN_OBS else None
    cy, cq = _qkey(last_d)
    # quý hoàn tất gần nhất: quý hiện tại nếu đã đủ (last_d là ngày cuối quý ±), ngược lại quý trước
    prev = (cy, cq - 1) if cq > 1 else (cy - 1, 4)
    end_month = {1: 3, 2: 6, 3: 9, 4: 12}[cq]
    cur_done = int(last_d[5:7]) == end_month and int(last_d[8:10]) >= 28
    rq = (cy, cq) if cur_done else prev
    def yoy(q):
        a, b = mean(q), mean((q[0] - 1, q[1]))
        return math.log(a / b) if a and b and a > 0 and b > 0 else None
    # quý-đến-nay: TB từ đầu quý đến last_d so với CÙNG CỬA SỔ NGÀY (MM-DD) của năm trước
    qtd = None
    if not cur_done:
        win = [v for d, v in obs if _qkey(d) == (cy, cq)]
        md = last_d[5:]
        first_md = {1: "01-01", 2: "04-01", 3: "07-01", 4: "10-01"}[cq]
        py = [v for d, v in obs if d[:4] == str(cy - 1) and first_md <= d[5:] <= md]
        if len(win) >= 5 and len(py) >= 5 and min(win) > 0 and min(py) > 0:
            qtd = math.log((sum(win) / len(win)) / (sum(py) / len(py)))
    # TB63 expanding percentile
    roll = []
    s = 0.0
    for i, v in enumerate(vals):
        s += v
        if i >= 63:
            s -= vals[i - 63]
        if i >= 62:
            roll.append(s / 63)
    pct = sum(1 for x in roll if x <= roll[-1]) / len(roll) if roll else None
    r_ma = last_v / (sum(vals[-252:]) / 252)
    return dict(last_date=last_d, rq=rq, c_yoy_raw=yoy(rq), qtd_raw=qtd, pct=pct, r_ma=r_ma)


def label(c):
    if c is None:
        return "không đủ dữ liệu"
    if abs(c) < NEUTRAL_BAND:
        return "trung tính"
    return "thuận" if c > 0 else "bất lợi"


def _fmt(c):
    return f"{(c if round(c, 2) != 0 else 0.0):+.2f}".replace(".", ",")


def _fmtp(p):
    return f"{p:.2f}".replace(".", ",")


def build_block(tickers, series, fresh, fresh_err, cmap, now=None):
    """Thuần hàm (không I/O). tickers đã dedupe. Trả '' nếu không mã nào có trong map."""
    lines = []
    cache = {}
    for t in tickers:
        rows = cmap.get(t)
        if not rows:
            continue
        lines.append(f"• **{t}**")
        if t == "DGC":
            lines.append("    " + DGC_LEGAL_WARN)
        for r in rows:
            sign = r["sign"]
            role = "producer" if sign > 0 else "consumer (chi phí, dấu ngược)"
            head = f"  - {r['family']} [{r['key']}, {role}, nhóm {r['tier']}]: "
            if fresh_err or not is_fresh(r["key"], fresh, series, now):
                src = "sunsirs" if r["key"] in SOURCE_OVERRIDE else "TE"
                lines.append(head + f"{STALE_TXT} (nguồn {src} '{r['key']}' không OK/thiếu/quá cũ; không in số)")
                if r["key"] == P4_KEY:
                    lines.append("    " + P4_WARN)
                continue
            m = cache.get(r["key"]) or cache.setdefault(r["key"], metrics(series.get(r["key"], [])))
            if not m:
                lines.append(head + "thiếu dữ liệu giá (không in số)")
                continue
            c = m["c_yoy_raw"] * sign if m["c_yoy_raw"] is not None else None
            q = m["qtd_raw"] * sign if m["qtd_raw"] is not None else None
            qtxt = f"Q{m['rq'][1]}/{m['rq'][0]}"
            txt = (f"{qtxt} YoY {_fmt(c) if c is not None else 'n/a'}"
                   f" | quý-đến-nay YoY {_fmt(q) if q is not None else 'n/a'}"
                   f" | phân vị TB63 {_fmtp(m['pct'])} | R/MA252 {_fmtp(m['r_ma'])} | giá tới {m['last_date']}")
            if r["tier"] == "D":
                txt += " → nhóm D: chỉ mô tả, không nhãn; " + r["note"][:90]
            else:
                txt += f" → hàng hoá nói: LN quý này **{label(c)}**"
            lines.append(head + txt)
            if r["family"] == "crude":
                lines.append("    " + OIL_WARN)
            if r["key"] == P4_KEY:
                lines.append("    " + P4_WARN)
    if not lines:
        return ""
    hdr = "🛢️ **Nowcast KQKD theo hàng hoá (nội bộ, display-only)** — c_yoy = log giá TB quý TE/sunsirs / cùng quý năm trước × dấu vai trò; nhãn = mô tả theo ngưỡng ±0,05, không phải tín hiệu"
    if fresh_err:
        hdr += f"\n  ({STALE_TXT}: {fresh_err})"
    return "\n".join([hdr] + lines + [FOOTER])


def tickers_from_plan(path):
    p = json.load(open(path, encoding="utf-8"))
    out = []
    for k in ("orders", "deferred_orders"):
        for o in p.get(k) or []:
            t = o.get("ticker") if isinstance(o, dict) else None
            if t and t not in out:
                out.append(t)
    return out


def run(tickers, runner=None, now=None):
    """Điểm vào fail-open: trả str (có thể rỗng), không bao giờ ném."""
    try:
        cmap = load_map()
        tickers = [t for t in dict.fromkeys(tickers) if t in cmap]
        if not tickers:
            return ""
        fresh, ferr = load_fresh(now=now)
        keys = {r["key"] for t in tickers for r in cmap[t]}
        series = fetch_te(keys, runner=runner)
        return build_block(tickers, series, fresh, ferr, cmap, now=now)
    except Exception as e:                                   # noqa: BLE001 — fail-open có chủ đích
        warn(f"{type(e).__name__}: {e}")
        return ""


def main():
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("--plan-file"); ap.add_argument("--tickers")
        a = ap.parse_args()
        tk = []
        if a.plan_file:
            tk += tickers_from_plan(a.plan_file)
        if a.tickers:
            tk += [x.strip().upper() for x in a.tickers.split(",") if x.strip()]
        out = run(tk)
        if out:
            print(out)
    except BaseException as e:                               # noqa: BLE001 — kể cả SystemExit của argparse
        warn(f"main {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
