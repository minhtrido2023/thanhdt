#!/usr/bin/env python3
"""LAYER 1 — DETECT-ONLY: vendor back-adjustment factor vs self-computed factor.

**Cổng này KHÔNG công bố, KHÔNG sửa, KHÔNG ghi số nào vào bất kỳ consumer nào.** Nó chỉ so
`tav2_bq.ticker` (`Price`/`Close`) với hệ số tự suy từ `tav2_bq.corporate_action` và in ra dòng
MÁY ĐỌC cho `bin/adjfactor_drift_alert.sh`. Không đụng `report_return_gate.py` /
`dividend_adjusted_return.py` — đó là cổng §21 hiện có, chạy SONG SONG và độc lập.

Sự cố gốc (job Taylor_20260927_034929, R&D `agents/Taylor/research/self_computed_adjfactor_20260927/`):
FPT ex-date 2026-09-21 thưởng 10% — `Close` chỉ được điều chỉnh lùi đúng **4 phiên cum** cuối
(09-15..09-18), còn 419/428 phiên trước đó nằm nguyên trong frame CŨ ⇒ lệch phẳng −9,0909%
(= 1 − 1/1,1) suốt 20 tháng. Không phải ca riêng FPT: **15 BROKEN / 0 OK** trên toàn cohort
ex-date 2026-09-19..09-25, trong đó **VPB −20,66% đang nắm LIVE ở CẢ HAI tài khoản**. Cohort
tuần trước đó (09-01..09-18) khớp 46/57 → đây là gián đoạn trong DỮ LIỆU, không phải trong công cụ.

CÔNG THỨC (đã validate trên 46 mã control, sai số ≤0,08% ở hệ số 1,01 → 4,16):

    r_obs(t)  = Price(t) / Close(t)                    # vendor-implied, tích luỹ
    r_pred(t) = PROD{ f_E : ex-date E > t }            # tự suy
    f_E       = (1 + q_total) * P_cum / (P_cum - D_total)

`q_total` = Σ tỉ lệ cổ phiếu (thưởng + cổ tức CP), `D_total` = Σ cổ tức tiền/cp, `P_cum` = giá
THÔ (`Price`) phiên cum cuối. **Mọi sự kiện CÙNG một ex-date phải vào CHUNG công thức giá tham
chiếu của sàn, KHÔNG nhân riêng lẻ** — hai bug thật mà bản naive đã tạo ra CÁO BUỘC SAI:
  · GEX 2026-05-05 (thưởng 20% + cổ tức CP 25%): sàn dùng 1+0,45 = 1,450, khớp vendor 1,450191;
    tích 1,20×1,25 = 1,500 lệch −3,32%.
  · DGC 2026-09-14 (tiền 3.000 + 5.000 trên giá thô 46.750): 46750/38750 = 1,206452 khớp vendor
    tới 6 chữ số; tích hai hệ số đơn cho 1,196544, lệch +0,83%.
Taxonomy sự kiện TÁI DÙNG `corp_action_lib.is_price_adjusting` (ESOP / phát hành riêng lẻ KHÔNG
làm rơi giá) — không tự định nghĩa lại.

NGƯỠNG (cả hai đều đo được, đừng hạ):
  · `--dev-tol 0.003` (0,3%): sàn chính xác của phương pháp ≈0,3%, KHÔNG phải 0,1% — DXG mang dư
    −0,17% trên đợt thưởng 14% suốt 95 phiên mà vendor vẫn đúng quy ước. Dưới 0,3% phương pháp
    này không phân biệt được lỗi với quy ước làm tròn.
  · `--min-run 3` (3 phiên LIÊN TIẾP): đây là bộ lọc đã loại được **ffill `Price` TOÀN THỊ TRƯỜNG
    ngày 2026-01-30** (662/1.252 mã) và 40 đỉnh tỉ số 1 phiên khác. Bỏ persistence sẽ phóng đại
    điểm mù ~4×. **KHÔNG hạ ngưỡng này.**

UNCOMPUTABLE = fail-closed, KHÔNG BAO GIỜ suy đoán f=1,0:
  · Quyền mua CP cho cổ đông hiện hữu cần giá phát hành — KHÔNG phải cột của `corporate_action`;
    cột `ref_price` lẽ ra giải được thì NULL trên toàn bộ 2.418 dòng từ 2025-01-01 (đã kiểm).
  · Một ex-date không tính được làm r_pred SAI cho mọi t < ex-date đó ⇒ chỉ đánh giá các phiên
    d >= max(ex-date uncomputable), phần còn lại báo UNCOMPUTABLE. Đây là lý do audit_week.py
    (prototype) bỏ CẢ mã khi có unknown; ở đây ta giữ phần CÒN HỢP LỆ thay vì bỏ hết, nhưng
    KHÔNG BAO GIỜ đánh giá phần đã bị nhiễm.

DÒNG MÁY ĐỌC trên stdout (giá trị đã chuẩn hoá — §28, shell KHÔNG grep văn xuôi). Dựng ở MỘT chỗ
duy nhất, các hàm `marker_*` — xem ghi chú ở đó về vì sao:
  ADJFACTOR_DRIFT|<tk>|<ex>|<r_obs>|<r_pred>|<dev>|<run>|<d0>|<d1>|<dir>|<held>
  ADJFACTOR_UNCOMPUTABLE|<tk>|<ex>|<reason_code>|<held>
  ADJFACTOR_NODATA|<tk>|<held>
  ADJFACTOR_FEED|<status>|<max_ingested_ict>|<max_public>|<rows>|<age_days>|<reason>
  ADJFACTOR_SCAN|<asof>|<n_scanned>|<n_drift>|<n_uncomputable>|<n_agree>|<n_nodata>
`<ex>` của dòng DRIFT = ex-date SỚM NHẤT nằm SAU cụm lệch, tức ex-date mà hệ số của nó đang thiếu —
KHÔNG phải ex-date sớm nhất trong cửa sổ (nó vừa nêu sai tên sự kiện vừa làm khoá de-dup của
alert.sh không theo dõi đúng định danh của lỗi).
`<dir>` là GỢI Ý ĐIỀU HƯỚNG, không phải bằng chứng: r_obs < r_pred ⇒ `vendor_missing` (vendor
thiếu hệ số — việc của Winston/data-ops); r_obs > r_pred ⇒ `our_table_missing` (bảng
corporate_action của ta thiếu một mắt xích — việc của ta). Chỉ dấu duy nhất phân biệt được hai
lớp này là DẤU của lệch; detector KHÔNG tự kết luận bên nào sai.

EXIT CODE (phân biệt rõ 3 trạng thái KHÁC nhau — §29, không gộp "không có gì" với "không chạy được"):
  0  = feed nguồn TƯƠI, mọi mã tính được và khớp, 0 uncomputable, 0 nodata. Đây là trạng thái
       DUY NHẤT có nghĩa "không có gì".
  10 = có ≥1 DRIFT (lệch thật, persistent) → alert Discord.
  11 = ĐIỂM MÙ, KHÔNG phải "sạch": ≥1 UNCOMPUTABLE, hoặc ≥1 NODATA, hoặc feed `corporate_action`
       KHÔNG tươi (STALE/DEAD/UNREADABLE), hoặc universe rỗng (bất khả về cấu trúc ở VN — đo thật
       95 mã cho cửa sổ 18 ngày). Dòng máy đọc phân biệt rõ ba loại; chỉ mã đang NẮM LIVE và ca
       feed-không-tươi mới lên Discord (uncomputable là trạng thái BÌNH THƯỜNG của quyền mua —
       26/83 mã cohort control — bắn Discord mỗi ngày cho nó là dạy người ta bỏ qua đúng topic).
  1  = lỗi HẠ TẦNG (BQ không tra được) — KHÔNG phải "sạch".
  2  = sai đối số.
"""
import argparse
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WC)
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
import corp_action_lib as cal  # noqa: E402

BQ = cal.BQ_PROJECT
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

DEV_TOL = 0.003          # sàn chính xác của phương pháp, xem docstring
MIN_RUN = 3              # persistence, xem docstring — KHÔNG hạ
LOOKBACK_DAYS = 120      # cửa sổ giá đánh giá
EX_DAYS = 30             # cohort: ex-date trong bao nhiêu ngày gần nhất
CUM_PAD_DAYS = 25        # đệm để tìm được phiên cum cuối của ex-date ở rìa trái cửa sổ

RIGHTS_METHOD = "Quyền mua CP cho Cổ đông hiện hữu"

# Ngưỡng "feed đã CHẾT" — cùng giá trị `FEED_DEAD_DAYS` của `bin/corp_action_daily.py:181`, nguồn
# chuẩn tắc cho việc phân loại độ tươi của `corporate_action`.
FEED_DEAD_DAYS = 5


# ---------------------------------------------------------------- data access

def bq_max_session():
    rows = cal.bq(f'SELECT CAST(MAX(t.time) AS STRING) AS d FROM `{BQ}.tav2_bq.ticker` AS t')
    if not rows or not rows[0].get("d"):
        raise RuntimeError("tav2_bq.ticker: MAX(time) rong — khong xac dinh duoc phien moi nhat")
    return rows[0]["d"]


def feed_gate(asof):
    """(status, detail) với status ∈ FRESH / STALE / DEAD / UNREADABLE — độ tươi của feed nguồn.

    Bắt buộc, không phải tuỳ chọn: `tav2_bq.corporate_action` là bảng **TRAP** có writer NGOÀI repo
    (`kb/data_registry/price-volume/corporate_action_bq.md`, Bẫy 2 — "ai đọc bảng này ngoài cron đó
    thì vẫn phải tự gọi `feed_freshness()`"). Nếu feed đứng im, mọi mã sẽ "khớp" và detector trả rc=0
    ⇒ **một feed chết không phân biệt được với một tuần sạch** — đúng lớp lỗi §14/§29 mà runner của
    chính nó tuyên bố ngăn cho ca BQ-down. arch-review 2026-09-27 đo được: feed trả 0 ex-date + bảng
    giá khoẻ ⇒ `ADJFACTOR_SCAN|...|0|0|0|0|0`, rc=0, không một dòng cảnh báo nào.

    Mốc FRESH neo vào `asof` = `MAX(time)` của `tav2_bq.ticker` = **phiên giao dịch cuối đã có dữ
    liệu**, nên "nạp vào hoặc sau `asof`" chính là điều kiện tươi — KHÔNG cần lịch nghỉ lễ, và vì vậy
    KHÔNG chạm vào bẫy `tdays`/`np.busday_count` của §16 RULE 2.

    CỐ Ý KHÔNG import `corp_action_daily.gate_freshness` dù logic giống: module đó có side effect ở
    TOP LEVEL (`os.environ.pop("BQ_LOCAL_CACHE")` dòng 138 và một cổng phiên bản có thể `raise
    SystemExit` dòng 154) — không chấp nhận được với một script chỉ-phát-hiện. Hằng số thì tái dùng.
    """
    try:
        f = cal.feed_freshness()
    except Exception as e:                                   # noqa: BLE001
        # Ở đây KHÔNG được fail-open: không tra được độ tươi nghĩa là không biết feed còn sống hay
        # không ⇒ trả UNREADABLE kèm LỖI THẬT, để caller coi là điểm mù chứ không phải "sạch".
        return "UNREADABLE", {"reason": f"feed_freshness() lỗi: {type(e).__name__}: {e}"}
    raw = (f.get("max_ingested") or "")[:19]
    try:
        ing_ict = (datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)).astimezone(ICT)
    except ValueError as e:
        return "UNREADABLE", {**f, "reason": f"max_ingested={f.get('max_ingested')!r} không đọc "
                                            f"được: {e}"}
    age = (date.fromisoformat(asof) - ing_ict.date()).days
    detail = {"max_ingested_ict": ing_ict.isoformat(timespec="seconds"),
              "max_public": f.get("max_public"), "rows": f.get("n"), "age_days": age}
    if age > FEED_DEAD_DAYS:
        return "DEAD", {**detail, "reason": f"lần nạp gần nhất cũ {age} ngày (> {FEED_DEAD_DAYS}) "
                                           f"so với phiên {asof} — bảng không còn refresh"}
    if age > 0:
        return "STALE", {**detail, "reason": f"chưa có lần nạp nào kể từ phiên {asof} "
                                            f"(nạp gần nhất cách {age} ngày)"}
    return "FRESH", detail


def price_rows(tickers, start, end):
    """Chuỗi giá thô + đã điều chỉnh. `Price` = thô (cafef GiaDongCua), `Close` = điều chỉnh lùi.

    `High`/`Low` đi kèm vì `ticker.Price` có thể là ffill im lặng của T-1 trên dòng ex-date
    (`kb/data_registry/price-volume/ticker_price_stale_on_exdate.md`, VHM 2026-08-06) — hệ số
    tính trên một `Price` đã ffill sai bằng đúng cả hệ số.
    """
    tk = ",".join(f'"{t}"' for t in sorted(set(tickers)))
    return cal.bq(f"""
        SELECT t.ticker AS tk, CAST(t.time AS STRING) AS d,
               t.Close AS close, t.Price AS price, t.High AS hi, t.Low AS lo
        FROM `{BQ}.tav2_bq.ticker` AS t
        WHERE t.ticker IN ({tk}) AND t.time BETWEEN DATE "{start}" AND DATE "{end}"
          AND t.Close > 0 AND t.Price > 0
        ORDER BY t.ticker, t.time
    """)


def series_by_ticker(rows):
    out = defaultdict(list)
    for r in rows:
        out[r["tk"]].append({
            "d": r["d"], "close": float(r["close"]), "price": float(r["price"]),
            "hi": float(r["hi"] or 0), "lo": float(r["lo"] or 0),
        })
    return out


def cohort_tickers(ex0, ex1):
    """Mã có ex-date ĐIỀU CHỈNH GIÁ trong [ex0, ex1]. Lọc thô ở SQL, taxonomy chốt ở Python.

    SQL chỉ khoanh vùng cho rẻ; quyết định "có điều chỉnh giá hay không" vẫn do
    `cal.is_price_adjusting` trong `build_factor_curve` — một chỗ duy nhất giữ taxonomy.
    """
    methods = ",".join(f'"{m}"' for m in sorted(cal.PRICE_ADJUSTING_ISS))
    rows = cal.bq(f"""
        SELECT DISTINCT c.ticker AS tk
        FROM `{BQ}.tav2_bq.corporate_action` AS c
        WHERE c.exright_date BETWEEN DATE "{ex0}" AND DATE "{ex1}"
          AND c.event_status = "executed"
          AND (c.event_code = "DIV"
               OR (c.event_code = "ISS" AND c.issue_method_name_vi IN ({methods})))
    """)
    return sorted(r["tk"] for r in rows)


def held_map():
    """{mã: "SpaceX,ZaloPay"} cho vị thế LIVE, hoặc None nếu không tra được.

    CHỈ để phân loại mức độ cấp bách (VPB là ca quan trọng vì đang nắm thật, FPT thì không) —
    KHÔNG ảnh hưởng tới việc phát hiện. Fail-open có chủ ý: tra không được thì `held=unknown` và
    VẪN cảnh báo; một cảnh báo thiếu nhãn còn hơn không có cảnh báo.
    `dividend_adjusted_return` chỉ được ĐỌC (import), không sửa — Layer 1 là lớp song song.
    """
    try:
        import dividend_adjusted_return as dar
        out = defaultdict(set)
        for label, acct in dar.ACCOUNTS.items():
            qmap = dar.broker_qty(acct)
            if not qmap:
                continue
            last = max(d for _tk, d in qmap)
            for (tk, d), qty in qmap.items():
                if d == last and float(qty or 0) > 0:
                    out[tk].add(label)
        return {tk: ",".join(sorted(v)) for tk, v in out.items()}
    except Exception as e:                                   # noqa: BLE001
        print(f"[warn] khong tra duoc vi the LIVE -> held=unknown cho moi ma. "
              f"Loi that: {type(e).__name__}: {e}", file=sys.stderr)
        return None


# ------------------------------------------------------------ factor building

def price_stale_suspect(series, idx):
    """True khi `Price` không thể là giao dịch thật của phiên đó (chữ ký ffill lớp VHM).

    `High`/`Low` nằm trong frame ĐÃ ĐIỀU CHỈNH (như `Close`), `Price` thì không — so trực tiếp
    sẽ báo MỌI phiên trước sự kiện là hỏng (đo thật: FPT 2025-06-11 Price=117.900 vs band đã
    điều chỉnh [97.750, 99.520], một dòng hoàn toàn khoẻ; trước khi sửa, 44/51 mã control
    fail-closed oan). Phải nâng band về frame thô trước, và tỉ số nâng phải lấy từ dòng LÁNG
    GIỀNG, KHÔNG BAO GIỜ từ chính dòng nghi vấn — trên một dòng ffill thì `Price/Close` chính là
    đại lượng đã hỏng. Phiên trước là láng giềng đúng vì dòng ta kiểm luôn là phiên CUM, nên nó
    và phiên trước cùng một chế độ điều chỉnh (dòng ex-date thì không).
    """
    bar = series[idx]
    if bar["hi"] <= 0 or bar["lo"] <= 0 or idx == 0:
        return False
    prev = series[idx - 1]
    if prev["close"] <= 0:
        return False
    r_ref = prev["price"] / prev["close"]
    lo, hi = bar["lo"] * r_ref, bar["hi"] * r_ref
    return not (lo * (1 - 1e-6) <= bar["price"] <= hi * (1 + 1e-6))


def group_price_factor(ex, evs, series):
    """(factor, reason_code, note) cho TẤT CẢ sự kiện điều chỉnh giá cùng một ex-date.

    factor None ⇒ không tính được; `reason_code` khi đó là mã lý do MÁY ĐỌC suy ra TỪ ĐÚNG thứ
    vừa đọc được (§29: không khẳng định nguyên nhân chưa đọc bằng chứng), `note` là văn xuôi kèm
    số thật để người đọc log truy lại.

    Chân cổ tức tiền cần giá THÔ của phiên cum cuối nên chịu guard ffill; sự kiện cổ phiếu thuần
    không cần giá nào và vẫn tính được kể cả khi dòng giá không dùng được.
    """
    q_total, d_total, kinds = 0.0, 0.0, []
    for ev in evs:
        code = ev["event_code"]
        method = (ev.get("issue_method_name_vi") or "").strip()
        if code == "ISS":
            if method == RIGHTS_METHOD:
                return None, "rights_issue_no_subscription_price", (
                    f"{ex} ISS {method}: gia phat hanh KHONG phai cot cua corporate_action va "
                    f"ref_price NULL tren moi dong tu 2025-01-01 -> he so khong the biet duoc")
            try:
                ratio = float(ev.get("exercise_ratio") or 0.0)
            except (TypeError, ValueError):
                return None, "iss_ratio_unparsable", (
                    f"{ex} ISS {method}: exercise_ratio={ev.get('exercise_ratio')!r} khong parse duoc")
            if ratio <= 0:
                return None, "iss_ratio_nonpositive", (
                    f"{ex} ISS {method}: exercise_ratio={ratio!r} <= 0")
            q_total += ratio
            kinds.append(f"ISS {method} {ratio:g}")
        elif code == "DIV":
            try:
                dps = float(ev.get("value_per_share") or 0.0)
            except (TypeError, ValueError):
                return None, "div_dps_unparsable", (
                    f"{ex} DIV: value_per_share={ev.get('value_per_share')!r} khong parse duoc")
            if dps <= 0:
                return None, "div_dps_nonpositive", f"{ex} DIV: value_per_share={dps!r} <= 0"
            d_total += dps
            kinds.append(f"DIV {dps:g}d")
        else:
            return None, "unsupported_event_code", f"{ex} event_code={code!r} khong ho tro"

    desc = " + ".join(kinds)
    # Registry Bẫy (3): `corporate_action` chứa CẢ tranche thật (phải CỘNG) LẪN bản đính chính của
    # cùng tranche (không được cộng), và `corp_action_lib.events()` nói rõ trường phân biệt là
    # `event_title_vi`. Dedupe theo số hạng kinh tế (xem `build_factor_curve`) bắt được bản đính
    # chính TRÙNG SỐ, nhưng KHÔNG bắt được bản đính chính ĐỔI SỐ — arch-review 2026-09-27 đo thật:
    # DIV 500 + "Điều chỉnh … 800" cộng thành f=1,028603 trong khi đúng là 1,017410 (+1,1%, VƯỢT
    # dung sai) ⇒ một cáo buộc `vendor_missing` SAI được quy cho Winston. Chưa phân biệt được bằng
    # code (đọc hiểu tiêu đề tiếng Việt), nên ít nhất phải ĐƯA TIÊU ĐỀ vào chứng từ để người xử lý
    # thấy ngay — KHÔNG im lặng cộng rồi khẳng định vendor sai (§29).
    same_code = len({e["event_code"] for e in evs}) < len(evs)
    if same_code:
        titles = " | ".join((e.get("event_title_vi") or "?").strip() for e in evs)
        desc += f"  [>1 dòng cùng event_code — KIỂM tiêu đề xem có bản ĐÍNH CHÍNH: {titles}]"
    if d_total <= 0:
        f = 1.0 + q_total
        return f, "", f"{ex} {desc} -> f={f:.6f} (khong co chan tien)"

    idxs = [i for i, b in enumerate(series) if b["d"] < ex]
    if not idxs:
        return None, "no_cum_session_in_window", (
            f"{ex} {desc}: khong co phien cum nao trong cua so gia")
    idx = idxs[-1]
    bar = series[idx]
    if price_stale_suspect(series, idx):
        return None, "price_ffill_suspect", (
            f"{ex} {desc}: phien cum cuoi {bar['d']} Price={bar['price']:.0f} nam ngoai band "
            f"[{bar['lo']:.0f},{bar['hi']:.0f}] da nang ve frame tho -> nghi ffill, tu choi")
    p_cum = bar["price"]
    if p_cum - d_total <= 0:
        return None, "cash_exceeds_price", (
            f"{ex} {desc}: tien {d_total:.0f} >= gia tho {p_cum:.0f}")
    f = (1.0 + q_total) * p_cum / (p_cum - d_total)
    return f, "", f"{ex} {desc} tren gia tho {p_cum:.0f} ({bar['d']}) -> f={f:.6f}"


def build_factor_curve(series, events):
    """(curve, used, notes, unknown) — r_pred cho mọi phiên trong `series`.

    r_pred(t) = tích các hệ số của những EX-DATE nằm HẲN sau t. Gộp theo ex-date TRƯỚC không phải
    vì gọn — xem `group_price_factor`.

    `unknown` = [(ex, reason_code, note)] các ex-date không tính được.

    Dòng trùng trên cùng (ex-date, code) được dedupe theo SỐ HẠNG KINH TẾ. `corporate_action` giữ
    hợp lệ nhiều tranche trong một ngày (registry Bẫy 3) và các tranche đó phải CỘNG, nhưng một
    bản đính chính của cùng tranche thì không được đếm hai lần. Hai dòng (code, ratio, dps) y hệt
    nhau không phân biệt được với nhau, nên coi là MỘT số hạng là cách đọc bảo thủ — và cũng là
    cách khớp vendor trên mọi sự kiện có dòng trùng trong cohort control.
    """
    notes, unknown, used = [], [], []
    by_ex = defaultdict(list)
    for ev in events:
        if not cal.is_price_adjusting(ev):
            notes.append(f"{ev['exright_date']} {ev['event_code']} "
                         f"{(ev.get('issue_method_name_vi') or '').strip()!r}: KHONG dieu chinh gia")
            continue
        by_ex[ev["exright_date"]].append(ev)

    for ex in sorted(by_ex):
        seen, uniq = set(), []
        for ev in by_ex[ex]:
            key = (ev["event_code"], str(ev.get("exercise_ratio")), str(ev.get("value_per_share")))
            if key in seen:
                notes.append(f"{ex} {ev['event_code']}: so hang kinh te trung lap, bo")
                continue
            seen.add(key)
            uniq.append(ev)
        f, code, note = group_price_factor(ex, uniq, series)
        notes.append(note)
        if f is None:
            unknown.append((ex, code, note))
        else:
            used.append((ex, f))

    curve, acc = {}, 1.0
    ex_after = sorted(used, key=lambda x: x[0], reverse=True)
    i = 0
    for bar in sorted(series, key=lambda b: b["d"], reverse=True):
        while i < len(ex_after) and ex_after[i][0] > bar["d"]:
            acc *= ex_after[i][1]
            i += 1
        curve[bar["d"]] = acc
    return curve, used, notes, unknown


# ------------------------------------------------------------------- scanning

def longest_bad_run(evaluated, dev_tol):
    """(run dài nhất các phiên LIÊN TIẾP lệch, danh sách phiên của run đó).

    `evaluated` = [(d, dev)] theo thứ tự thời gian tăng. "Liên tiếp" tính theo phiên KỀ NHAU
    trong chuỗi, không theo ngày lịch — một dòng `Price` ffill lẻ (lớp VHM) dài 1-2 phiên, còn
    một cửa sổ điều chỉnh lùi thiếu dài hàng chục tới hàng trăm phiên. Gộp hai lớp lại thì che
    mất đúng lớp ta đang tìm.
    """
    best, cur = [], []
    for d, dev in evaluated:
        if abs(dev) > dev_tol:
            cur.append((d, dev))
            if len(cur) > len(best):
                best = list(cur)
        else:
            cur = []
    return len(best), best


def scan_ticker(series, events, dev_tol, min_run, eval_from):
    """(verdict, payload) cho một mã. verdict ∈ AGREE / DRIFT / UNCOMPUTABLE / NODATA.

    `eval_from` = ngày sớm nhất được đánh giá (rìa cửa sổ đánh giá; các phiên trước đó chỉ nạp
    để tìm phiên cum cuối, không phải để chấm điểm).
    """
    curve, used, notes, unknown = build_factor_curve(series, events)
    if not series:
        return "NODATA", {"reason": "khong co dong gia nao", "notes": notes}

    # Một ex-date không tính được làm r_pred SAI cho MỌI phiên trước nó ⇒ chỉ đánh giá phần từ
    # ex-date uncomputable MUỘN NHẤT trở đi. Đây là fail-closed: không bao giờ chấm điểm phần
    # đã bị nhiễm, và cũng không lặng lẽ coi hệ số thiếu bằng 1,0.
    valid_from = max((ex for ex, _c, _n in unknown), default=None)
    floor = max(x for x in (eval_from, valid_from) if x) if (eval_from or valid_from) else None
    evaluated = [(b["d"], (b["price"] / b["close"]) / curve[b["d"]] - 1.0)
                 for b in series if (floor is None or b["d"] >= floor)]

    run, bad = longest_bad_run(evaluated, dev_tol)
    if run >= min_run:
        d0, d1 = bad[0][0], bad[-1][0]
        worst = max(bad, key=lambda x: abs(x[1]))
        bar = next(b for b in series if b["d"] == worst[0])
        r_obs = bar["price"] / bar["close"]
        r_pred = curve[worst[0]]
        # Ex-date được NÊU TÊN phải là ex-date mà hệ số của nó đang THIẾU trên cửa sổ lệch — tức
        # ex-date SỚM NHẤT nằm SAU phiên cuối của cụm lệch. `min(used)` (bản trước) là ex-date sớm
        # nhất trong cả cửa sổ 120 phiên, và arch-review 2026-09-27 đo được hai hệ quả thật: (1) câu
        # Discord nêu một ex-date KHÔNG phải cái bị hỏng; (2) khoá de-dup `<mã>|<ex>` không theo dõi
        # ĐỊNH DANH của lỗi ⇒ một lỗi MỚI −16,67% ở ex 09-05 tái dùng khoá của ex 07-05 và bị chặn
        # tới 7 ngày, còn khi ex cũ trôi khỏi cửa sổ thì lỗi CŨ y nguyên lại báo lại.
        ex_broken = min((ex for ex, _f in used if ex > d1), default="")
        if not ex_broken:
            ex_broken = min((ex for ex, _f in used), default="")
        out = {
            "ex": ex_broken,
            "r_obs": r_obs, "r_pred": r_pred, "dev": worst[1], "run": run,
            "d0": d0, "d1": d1,
            "dir": "vendor_missing" if worst[1] < 0 else "our_table_missing",
            "n_eval": len(evaluated), "notes": notes,
            "unknown": unknown, "partial": bool(unknown),
        }
        return "DRIFT", out
    if unknown:
        return "UNCOMPUTABLE", {"unknown": unknown, "notes": notes,
                                "n_eval_clean": len(evaluated)}
    return "AGREE", {"n_eval": len(evaluated), "notes": notes, "n_ex": len(used)}


# ── DÒNG MÁY ĐỌC: dựng ở MỘT chỗ duy nhất ───────────────────────────────────────────────────
# Trước bản này mỗi dòng được f-string tại chỗ in, nên selfcheck chỉ grep được VĂN BẢN NGUỒN;
# arch-review 2026-09-27 chứng minh hợp đồng KHÔNG được test: hoán đổi `dir` với `held` trong dòng
# DRIFT vẫn 142/142 PASS và sinh ra nhãn SAI "ĐANG NẮM LIVE: vendor_missing" trên Discord. Tách ra
# hàm để selfcheck bơm dòng THẬT qua alert.sh và so TỪNG TRƯỜNG.

def marker_drift(tk, p, held):
    return ("ADJFACTOR_DRIFT|{tk}|{ex}|{r_obs:.6f}|{r_pred:.6f}|{dev:.6f}|{run}|{d0}|{d1}"
            "|{dir}|{held}").format(tk=tk, held=held, **p)


def marker_uncomputable(tk, ex, code, held):
    return f"ADJFACTOR_UNCOMPUTABLE|{tk}|{ex}|{code}|{held}"


def marker_nodata(tk, held):
    return f"ADJFACTOR_NODATA|{tk}|{held}"


def marker_feed(status, detail):
    return (f"ADJFACTOR_FEED|{status}|{detail.get('max_ingested_ict', '?')}"
            f"|{detail.get('max_public', '?')}|{detail.get('rows', '?')}"
            f"|{detail.get('age_days', '?')}|{detail.get('reason', '')}")


def marker_scan(asof, n_scanned, n_drift, n_uncomp, n_agree, n_nodata):
    return (f"ADJFACTOR_SCAN|{asof}|{n_scanned}|{n_drift}|{n_uncomp}|{n_agree}|{n_nodata}")


def run_scan(args):
    asof = args.asof or bq_max_session()
    ex1 = args.ex1 or asof
    ex0 = args.ex0 or (date.fromisoformat(ex1) - timedelta(days=args.ex_days)).isoformat()
    win0 = (date.fromisoformat(asof) - timedelta(days=args.lookback_days)).isoformat()
    load0 = (date.fromisoformat(win0) - timedelta(days=CUM_PAD_DAYS)).isoformat()

    held = None if args.no_holdings else held_map()

    if args.tickers:
        tks = sorted({t.strip().upper() for t in args.tickers.split(",") if t.strip()})
        src = "--tickers"
    else:
        tks = cohort_tickers(ex0, ex1)
        src = f"cohort ex-date {ex0}..{ex1}"
        if held:
            extra = sorted(set(held) - set(tks))
            if extra:
                # Vị thế LIVE được quét kể cả khi ex-date của nó đã ra khỏi cohort: một điều
                # chỉnh CŨ có thể hỏng MUỘN khi vendor ghi lại lịch sử, và đó đúng là lớp mã
                # duy nhất mà lỗi lại thành tiền thật.
                tks = sorted(set(tks) | set(extra))
                src += f" + {len(extra)} ma dang nam LIVE"

    print(f"# adjfactor Layer 1 DETECT-ONLY | asof={asof} | universe={src} -> {len(tks)} ma")
    print(f"# cua so danh gia {win0}..{asof} (nap tu {load0} de tim phien cum cuoi) "
          f"| dev_tol={args.dev_tol:.3%} min_run={args.min_run}")
    print(f"# vi the LIVE: {'khong tra duoc (held=unknown)' if held is None else str(len(held)) + ' ma'}")

    feed_status, feed_detail = feed_gate(asof)
    print(marker_feed(feed_status, feed_detail))
    print(f"# feed corporate_action: {feed_status} {feed_detail}")

    if not tks:
        print(marker_scan(asof, 0, 0, 0, 0, 0))
        # Cohort 30 ngày RỖNG là bất khả về mặt cấu trúc ở VN (đo thật: 95 mã cho cửa sổ 18 ngày)
        # ⇒ đây là điểm mù, KHÔNG phải "không có gì để kiểm". rc=11, không bao giờ 0.
        print("# universe RONG -> DIEM MU, khong phai 'khong co lech'. rc=11.")
        return 11

    # GIÁ nạp từ `load0` (sớm hơn), SỰ KIỆN chỉ từ `win0`. Ngược lại là một bug thật: một ex-date
    # rơi đúng rìa trái của khoảng NẠP không còn phiên cum nào trước nó ⇒ `no_cum_session_in_window`
    # ⇒ UNCOMPUTABLE OAN (đo thật: TIP ex 2026-05-04 trên cohort control 09-01..09-18). Và sự kiện
    # có ex-date <= win0 vốn KHÔNG ảnh hưởng r_pred(t) với mọi t >= win0 (tích chỉ lấy ex > t), nên
    # nạp chúng không mua được gì mà chỉ tạo ra fail-closed giả.
    series = series_by_ticker(price_rows(tks, load0, asof))
    ev_by_tk = defaultdict(list)
    for e in cal.events(tks, since=win0, until=asof):
        ev_by_tk[e["ticker"]].append(e)

    drift, uncomp, agree, nodata = [], [], [], []
    for tk in tks:
        s = series.get(tk, [])
        verdict, payload = scan_ticker(s, ev_by_tk.get(tk, []),
                                       args.dev_tol, args.min_run, win0)
        h = "unknown" if held is None else held.get(tk, "none")
        if verdict == "DRIFT":
            drift.append((tk, payload, h))
        elif verdict == "UNCOMPUTABLE":
            uncomp.append((tk, payload, h))
        elif verdict == "AGREE":
            agree.append(tk)
        else:
            nodata.append((tk, h))

    for tk, p, h in sorted(drift, key=lambda x: -abs(x[1]["dev"])):
        print(marker_drift(tk, p, h))
    for tk, p, h in sorted(uncomp):
        for ex, code, _note in p["unknown"]:
            print(marker_uncomputable(tk, ex, code, h))
    # NODATA có dòng máy đọc RIÊNG: trước bản này nó chỉ là một con số trong SCAN ⇒ một mã đang NẮM
    # mà không có dòng giá nào không sinh ra bất cứ thứ gì người đọc thấy (arch-review 2026-09-27;
    # đo thật 12/95 mã NODATA trên cohort control).
    for tk, h in sorted(nodata):
        print(marker_nodata(tk, h))
    print(marker_scan(asof, len(tks), len(drift), len(uncomp), len(agree), len(nodata)))

    print(f"\n-- ket qua: DRIFT {len(drift)} | UNCOMPUTABLE {len(uncomp)} | "
          f"AGREE {len(agree)} | NODATA {len(nodata)} --")
    if drift:
        print(f"\n{'tk':<7}{'held':<16}{'r_obs':>10}{'r_pred':>10}{'dev':>10}{'run':>5}"
              f"  {'window':<24}dir")
        for tk, p, h in sorted(drift, key=lambda x: -abs(x[1]["dev"])):
            print(f"{tk:<7}{h:<16}{p['r_obs']:>10.6f}{p['r_pred']:>10.6f}{p['dev']:>+10.4%}"
                  f"{p['run']:>5}  {p['d0']}..{p['d1']:<12} {p['dir']}"
                  + ("  [PARTIAL: co ex-date uncomputable]" if p["partial"] else ""))
        print("\n-- chung tu he so cua cac ma DRIFT (doc de truy lai, khong phai ket luan) --")
        for tk, p, _h in sorted(drift, key=lambda x: -abs(x[1]["dev"])):
            for n in p["notes"]:
                print(f"   {tk}: {n}")
    if uncomp:
        print("\n-- UNCOMPUTABLE (fail-closed: KHONG suy doan f=1.0, KHONG tinh la khop) --")
        for tk, p, h in sorted(uncomp):
            for ex, code, note in p["unknown"]:
                print(f"   {tk} [{h}] {code}: {note}")
    if nodata:
        print(f"\nNODATA (khong co dong gia trong cua so): "
              f"{[f'{tk} [{h}]' for tk, h in sorted(nodata)]}")
    if agree:
        print(f"\nAGREE: {sorted(agree)}")

    if drift:
        return 10
    # rc=11 = ĐIỂM MÙ, không phải "sạch": uncomputable, NODATA, hoặc feed nguồn không tươi. Gộp cả
    # ba vào một mã vì hệ quả giống nhau (không kết luận được), nhưng dòng máy đọc phân biệt rõ.
    if uncomp or nodata or feed_status != "FRESH":
        return 11
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--asof", help="phien cuoi cua cua so (default: MAX(time) cua tav2_bq.ticker)")
    ap.add_argument("--ex0", help="dau cohort ex-date (default: ex1 - --ex-days)")
    ap.add_argument("--ex1", help="cuoi cohort ex-date (default: asof)")
    ap.add_argument("--ex-days", type=int, default=EX_DAYS)
    ap.add_argument("--lookback-days", type=int, default=LOOKBACK_DAYS)
    ap.add_argument("--dev-tol", type=float, default=DEV_TOL)
    ap.add_argument("--min-run", type=int, default=MIN_RUN)
    ap.add_argument("--tickers", help="quet dung danh sach nay thay vi cohort (test/dieu tra)")
    ap.add_argument("--no-holdings", action="store_true",
                    help="bo qua tra vi the LIVE (held=unknown)")
    args = ap.parse_args(argv)
    if args.min_run < MIN_RUN:
        ap.error(f"--min-run < {MIN_RUN} bi TU CHOI: nguong persistence nay la thu da loc duoc "
                 f"ffill `Price` toan thi truong 2026-01-30 (662/1252 ma). Xem docstring.")
    if not 0 < args.dev_tol < 0.5:
        # Trần 50%: một dung sai lớn hơn thế thì detector không bao giờ nổ trên bất kỳ sự kiện thật
        # nào (hệ số lớn nhất đo được trên cohort control là 4,16 ⇒ lệch tối đa ~76%), tức là một
        # cách TẮT cảnh báo mà trông như đang chạy.
        ap.error("--dev-tol phai nam trong (0, 0.5) — ngoai khoang nay detector thanh no-op")
    try:
        return run_scan(args)
    except Exception as e:                                   # noqa: BLE001
        # Lỗi hạ tầng KHÔNG được trả về "sạch": rc=1 riêng, và in LỖI THẬT (§29) chứ không đoán.
        print(f"[FATAL] adjfactor_drift_detect khong hoan tat duoc -> KHONG ket luan gi. "
              f"Loi that: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
