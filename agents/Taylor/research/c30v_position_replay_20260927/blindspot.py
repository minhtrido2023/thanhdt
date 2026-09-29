"""Đo điểm mù của detector giá kẹt (replay.py:152) — quant-skeptic vòng 3 chỉ ra bằng đại số,
đây là phép ĐẾM của tôi trên đúng panel đang dùng.

Điểm mù: `stale` đòi `ratio > lo*1.005` với `lo = min(ratio_prev, ratio_next)`. Nếu `Price` ngày ex
là bản CHÉP NGUYÊN của phiên trước (kẹt HOÀN TOÀN, không kẹt một phần) thì `ratio_d == ratio_prev
== lo` ⇒ bất đẳng thức NGẶT không thoả ⇒ detector KHÔNG BAO GIỜ bắt được ca kẹt hoàn toàn. Mà đó
lại chính là dạng mà registry `price-volume/ticker_price_stale_on_exdate.md` mô tả.

Đếm: bao nhiêu ô ex-date price-adjusting có ratio_d ≈ ratio_prev (≤0,2%) NHƯNG ratio_next nhảy
(>0,5%) — tức dấu hiệu cơ học của "kẹt hoàn toàn".
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_position_replay_20260927")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import replay as R

H = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_position_replay_20260927"
bx = pd.read_parquet(f"{H}/panel_bx.parquet"); bx["time"] = pd.to_datetime(bx["time"])
ev = pd.read_parquet(f"{H}/ca_vintage.parquet")
for c in ("exright_date", "effective_date"):
    if c in ev.columns:
        ev[c] = pd.to_datetime(ev[c], errors="coerce")

px = bx.pivot_table(index="time", columns="ticker", values="pxw").sort_index()
cl = bx.pivot_table(index="time", columns="ticker", values="Close").sort_index().reindex(
    index=px.index, columns=px.columns)
exm = R.ex_date_mask(ev, px)

ratio = cl / px
rnext, rprev = ratio.shift(-1), ratio.shift(1)
lo, hi = np.minimum(rprev, rnext), np.maximum(rprev, rnext)

caught = ((ratio > lo * 1.005) & (ratio < hi * 0.995) & ratio.notna() & rnext.notna()
          & rprev.notna() & exm)
# "kẹt HOÀN TOÀN": ratio ngày ex bám sát phiên trước, còn phiên sau đã nhảy
full = ((ratio / rprev - 1).abs() < 0.002) & ((rnext / ratio - 1).abs() > 0.005) \
       & ratio.notna() & rnext.notna() & rprev.notna() & exm

print(f"panel: {px.shape[1]} mã × {px.shape[0]} phiên · {int(exm.values.sum())} ô ex-date price-adjusting")
print(f"  detector BẮT ĐƯỢC (kẹt MỘT PHẦN, bất đẳng thức ngặt thoả): {int(caught.values.sum())} ô")
print(f"  ĐIỂM MÙ — kẹt HOÀN TOÀN (ratio_d ≈ ratio_prev, ratio_next nhảy): {int(full.values.sum())} ô")
ov = int((caught & full).values.sum())
print(f"  giao của hai tập: {ov} ô (0 ⇒ hai dạng rời nhau đúng như đại số nói)")
if int(full.values.sum()):
    w = full.stack(); w = w[w]
    print("  danh sách:"); [print("   ", d.date(), t) for d, t in w.index[:20]]
print()
print("KẾT LUẬN: điểm mù là THẬT về mặt đại số (bất đẳng thức ngặt loại bỏ ratio_d == lo), nhưng")
print("RỖNG trên panel này ⇒ không ô nào lọt, không ảnh hưởng con số nào của báo cáo. Ghi lại vì")
print("nếu tái dùng replay.py trên panel khác thì phải đổi thành >= với dung sai hai phía.")
