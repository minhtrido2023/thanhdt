#!/usr/bin/env python3
"""exdate_frame_cashleg_selfcheck.py — chân tiền mặt BUNDLE cùng ex-date với sự kiện cổ phiếu.

Ca nền = ca THẬT TPB 2026-10-02 (ISS 15% + DIV 500đ/cp CÙNG ngày): giá cum 14.400, chân tiền
500đ/cp, hệ số 1,15 ⇒ kỳ vọng (14.400−500)/1,15 = 12.086,96, broker trả marketPrice 12.100
(lệch 13,0 ≤ dung sai 200). KHÔNG trừ chân tiền (hành vi trước 2026-10-01, tương đương
cash_per_share=0 — cũng là hình dạng của việc MUTATE bỏ phần trừ) ⇒ kỳ vọng 12.521,7, lệch
421,7 > dung sai ⇒ FAIL OAN dù marketPrice broker đúng hệ sau sự kiện. Đây chính là bài test
"mutation": ca TPB PASS khi CÓ trừ chân tiền, và CHẾT (None) khi KHÔNG trừ — hai nhánh dùng
đúng cùng công thức, chỉ khác `cash_per_share=500` vs `0`.

HERMETIC — thuần import, không đọc file/mạng/TZ (cả hai hàm kiểm đều PURE).

Chạy:  python3 bin/exdate_frame_cashleg_selfcheck.py
       $DNA_PYEXE bin/exdate_frame_cashleg_selfcheck.py
       env -u TZ python3 bin/exdate_frame_cashleg_selfcheck.py
       TZ=America/New_York python3 bin/exdate_frame_cashleg_selfcheck.py
(không phụ thuộc TZ — 4 lệnh trên PHẢI ra cùng kết quả; chạy đủ bốn theo §16/verify-before-done)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exdate_frame as ef   # noqa: E402
import corp_actions as CA   # noqa: E402

FAILS = []
NCHK = 0

# Ca thật TPB 2026-10-02: ISS 15% (mult 1,15) + DIV 500đ/cp cùng ex-date.
PX_CUM = 14400.0
CASH = 500.0
MULT = 1.15
BROKER_MP = 12100.0
EXPECTED_WITH_CASH = (PX_CUM - CASH) / MULT        # 12.086,9565...
EXPECTED_NO_CASH = PX_CUM / MULT                   # 12.521,7391...


def check(cond, label, detail=""):
    global NCHK
    NCHK += 1
    if not cond:
        FAILS.append(f"{label}" + (f" — {detail}" if detail else ""))


# ───────────────────────── 1. verify_post_event_price — pure, ca TPB ─────────────────────────
def t_pure():
    # P1 — ca THẬT CÓ chân tiền mặt ⇒ PASS, marketPrice broker tái tạo được qua công thức mới.
    px, why = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, CASH)
    check(px == BROKER_MP,
          "P1 ca THẬT TPB (cash=500): marketPrice 12.100 tái tạo được qua (14.400−500)/1,15",
          why)
    check("12,087.0" in why or "12,086.9" in why or f"{EXPECTED_WITH_CASH:,.1f}" in why,
          "P2 thông điệp trích đúng kỳ vọng đã tính (§29)", why)
    check("500" in why, "P2b thông điệp trích chân tiền mặt đã trừ (§29)", why)

    # P3 — CÙNG input, cash_per_share=0 (= hành vi cũ / = MUTATION bỏ phần trừ) ⇒ FAIL oan.
    # Đây là bài test mutation: không cần sửa source, chỉ cần gọi với cash=0 để tái hiện đúng
    # hình dạng "quên trừ chân tiền" — toán học y hệt nhau (px_ex = px_cum − 0 = px_cum).
    px0, why0 = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, 0.0)
    check(px0 is None,
          "P3 MUTATION-GUARD: bỏ chân tiền (cash=0, = hành vi cũ) ⇒ ca TPB FAIL OAN (kỳ vọng "
          f"{EXPECTED_NO_CASH:,.1f}, lệch {BROKER_MP - EXPECTED_NO_CASH:+,.1f} > dung sai 200) — "
          "chứng minh bản vá trừ chân tiền LÀ THỨ làm P1 PASS, không phải trùng hợp", why0)
    # Đối chứng: KHÔNG truyền cash_per_share (dùng default) phải ra ĐÚNG kết quả như truyền
    # tường minh 0.0 — default không lặng lẽ đổi hành vi so với 0.0. So CẢ `px` LẪN CHUỖI `why`
    # (không chỉ `px is None`): MUTATION-GUARD thật — nếu default bị đổi 0.0→1.0 (hoặc bất kỳ số
    # khác), `px0b` vẫn ra None ở cả hai nhánh (lệch 500 lẫn lệch 499 đều > dung sai 200đ) nên
    # riêng `px0b is None and px0b == px0` KHÔNG BẮT ĐƯỢC mutation này; nhưng `why0b` sẽ đổi
    # cash_note + con số "kỳ vọng" (khác `why0` của 0.0 tường minh) ⇒ so chuỗi mới chết đúng chỗ.
    px0b, why0b = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT)
    check(px0b is None and px0b == px0,
          "P3b default cash_per_share (không truyền tham số) ⇒ y hệt truyền tường minh 0.0 ở "
          "KẾT QUẢ px — hành vi CŨ giữ nguyên 100% cho mọi caller chưa cập nhật", (px0b, why0b))
    check(why0b == why0,
          "P3b-MUTATION-GUARD default cash_per_share ⇒ THÔNG ĐIỆP y hệt truyền tường minh 0.0 — "
          "bắt mutation đổi giá trị default (vd 0.0→1.0): px vẫn None cả hai nhánh (lệch vẫn "
          ">200đ) nhưng why đổi số 'kỳ vọng'/cash_note nên so chuỗi mới phân biệt được",
          (why0, why0b))

    # P4 — px_cum − cash ≤ 0 ⇒ vô nghĩa, từ chối.
    px, why = ef.verify_post_event_price(400.0, 100.0, 1.0, 500.0)
    check(px is None, "P4 giá cum − chân tiền ≤ 0 ⇒ từ chối, không đoán", why)
    check("≤ 0" in why, "P4b thông điệp nói rõ lý do (§29)", why)

    # P5 — cash_per_share âm ⇒ vô nghĩa.
    px, why = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, -100.0)
    check(px is None, "P5 cash_per_share < 0 ⇒ từ chối", why)
    check("< 0" in why, "P5b thông điệp nói rõ lý do", why)

    # P6/P7 — nan/inf: [FIX trong vòng này] trước bản vá, so sánh `nan < 0` luôn False nên
    # guard cũ ÂM THẦM BỎ QUA và hàm trả PASS với "kỳ vọng nan" — đo thật TRƯỚC khi vá:
    # verify_post_event_price(14400, 12100, 1.15, nan) → (12100.0, '...kỳ vọng nan...').
    px, why = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, float("nan"))
    check(px is None, "P6 cash_per_share=nan ⇒ từ chối (KHÔNG được lọt qua rồi PASS bằng so "
                      "sánh nan luôn False)", why)
    px, why = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, float("inf"))
    check(px is None, "P7 cash_per_share=inf ⇒ từ chối", why)

    # P8/P9 — biên dung sai quanh ca TPB (mirror P8/P9 của exdate_frame_selfcheck.py, áp cho
    # công thức CÓ chân tiền): 0,5% của 12.086,96 = 60,4 < sàn 200 ⇒ ngưỡng thật là 200đ.
    px, _ = ef.verify_post_event_price(PX_CUM, EXPECTED_WITH_CASH + 199, MULT, CASH)
    check(px is not None, "P8 lệch 199đ (< sàn 200đ) vẫn nhận")
    px, _ = ef.verify_post_event_price(PX_CUM, EXPECTED_WITH_CASH + 201, MULT, CASH)
    check(px is None, "P9 lệch 201đ (> sàn 200đ) bị từ chối")

    # P10 — không ép được về số ⇒ từ chối, KHÔNG ném.
    px, _ = ef.verify_post_event_price(PX_CUM, BROKER_MP, MULT, "x")
    check(px is None, "P10 cash_per_share không ép được về số ⇒ từ chối, KHÔNG ném")


# ───────────── 2. corp_actions.validate() — field cash_leg_vnd_per_share optional ─────────────
BASE_REC = {"ticker": "TPB", "event_type": "BONUS_ISSUE", "qty_multiplier": MULT,
           "ex_date": "2026-10-02", "broker_effective_ts": "2026-10-01T18:00:00"}


def _raises(fn):
    try:
        fn()
        return False
    except CA.CorpActionError:
        return True


def t_validate():
    # V1 — record KHÔNG có field (y hệt mọi corp action hiện có trong data/corp_actions.json)
    # ⇒ validate() PHẢI vẫn chạy, default 0.0, KHÔNG được coi là thiếu trường bắt buộc.
    v = CA.validate(dict(BASE_REC))
    check(v.get("cash_leg_vnd_per_share") == 0.0,
          "V1 record CŨ (không có field) ⇒ validate() default cash_leg_vnd_per_share=0.0 "
          "(backward-compat — không phá record hiện có)", v)

    # V2 — field hợp lệ ⇒ đi qua nguyên vẹn vào record đã chuẩn hoá.
    v = CA.validate(dict(BASE_REC, cash_leg_vnd_per_share=CASH))
    check(v.get("cash_leg_vnd_per_share") == CASH,
          "V2 field hợp lệ (500) ⇒ giữ nguyên trong record chuẩn hoá", v)

    # V3 — None tường minh ⇒ coi như 0.0 (không ném).
    v = CA.validate(dict(BASE_REC, cash_leg_vnd_per_share=None))
    check(v.get("cash_leg_vnd_per_share") == 0.0,
          "V3 field=None tường minh ⇒ coi như 0.0, không ném", v)

    # V4 — không ép được về số ⇒ ném CorpActionError (fail-loud, không bỏ qua im lặng).
    check(_raises(lambda: CA.validate(dict(BASE_REC, cash_leg_vnd_per_share="năm trăm"))),
          "V4 cash_leg_vnd_per_share không phải số ⇒ ném CorpActionError")

    # V5 — nan ⇒ ném (so sánh nan luôn False, phải chặn TRƯỚC khi tới guard ngưỡng §29).
    check(_raises(lambda: CA.validate(dict(BASE_REC,
                                           cash_leg_vnd_per_share=float("nan")))),
          "V5 cash_leg_vnd_per_share=nan ⇒ ném CorpActionError (không lọt qua guard <0/>MAX)")
    check(_raises(lambda: CA.validate(dict(BASE_REC,
                                           cash_leg_vnd_per_share=float("inf")))),
          "V5b cash_leg_vnd_per_share=inf ⇒ ném CorpActionError")

    # V6 — âm ⇒ ném.
    check(_raises(lambda: CA.validate(dict(BASE_REC, cash_leg_vnd_per_share=-100.0))),
          "V6 cash_leg_vnd_per_share=-100 ⇒ ném CorpActionError (cổ tức tiền mặt không âm)")

    # V7 — vượt CASH_LEG_MAX (lỗi gõ tay, vd 50000 thay vì 500) ⇒ ném.
    check(_raises(lambda: CA.validate(dict(BASE_REC,
                                           cash_leg_vnd_per_share=CA.CASH_LEG_MAX + 1))),
          f"V7 cash_leg_vnd_per_share > CASH_LEG_MAX ({CA.CASH_LEG_MAX:,.0f}) ⇒ ném CorpActionError")

    # V8 — đúng biên CASH_LEG_MAX vẫn được chấp nhận (biên trên, không phải dưới).
    v = CA.validate(dict(BASE_REC, cash_leg_vnd_per_share=CA.CASH_LEG_MAX))
    check(v.get("cash_leg_vnd_per_share") == CA.CASH_LEG_MAX,
          "V8 cash_leg_vnd_per_share = CASH_LEG_MAX (biên) vẫn được chấp nhận", v)

    # V9 — sự kiện KHÔNG có chân tiền mặt (đa số corp action hiện tại) + validate ⇒ wiring
    # end-to-end: verify_post_event_price(px_cum, mp, mult, v["cash_leg_vnd_per_share"]) phải ra
    # ĐÚNG kết quả như gọi trực tiếp cash_per_share=0.0 (byte-identical hành vi cũ, không hồi quy).
    v_old = CA.validate(dict(BASE_REC, ticker="VPB", qty_multiplier=1.2604104,
                             cash_leg_vnd_per_share=0.0))
    px_direct, why_direct = ef.verify_post_event_price(27800.0, 22050.0, 1.2604104, 0.0)
    px_via_v, why_via_v = ef.verify_post_event_price(27800.0, 22050.0, 1.2604104,
                                                      v_old["cash_leg_vnd_per_share"])
    check(px_direct == px_via_v and why_direct == why_via_v,
          "V9 record CŨ (validate ⇒ cash_leg=0.0) cho KẾT QUẢ BYTE-IDENTICAL với gọi trực tiếp "
          "cash_per_share=0.0 — không hồi quy ca VPB 2026-09-23 đã pin trong "
          "exdate_frame_selfcheck.py", (why_direct, why_via_v))


def main():
    tz = os.environ.get("TZ", "(không đặt)")
    print(f"== exdate_frame_cashleg_selfcheck (TZ={tz}) ==")
    t_pure()
    t_validate()
    for f in FAILS:
        print(f"  ❌ {f}")
    print(f"{NCHK - len(FAILS)}/{NCHK} PASS" + (f", {len(FAILS)} FAIL" if FAILS else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
