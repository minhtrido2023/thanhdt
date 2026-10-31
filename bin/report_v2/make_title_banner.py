#!/usr/bin/env python3
"""make_title_banner.py — banner tiêu đề báo cáo DD (PNG) bằng font Be Vietnam Pro (OFL, thiết kế cho tiếng Việt)
+ logo doanh nghiệp. Dùng cho: đầu thân email (thay header HTML) và đầu trang 1 PDF.

  python3 make_title_banner.py --title "DRI — ...: ..., nhưng ..." --ticker DRI \
      --kicker "BÁO CÁO DUE DILIGENCE · UPCoM: DRI" --sub "Nhóm nghiên cứu · 29/10/2026" \
      --logo /path/logo.png --out banner.png [--accent "#e0674f"]

Không có --logo (hoặc file lỗi) ⇒ huy hiệu chữ (monogram) bằng mã cổ phiếu — KHÔNG bịa logo.
Chữ luôn NFC-normalize (tránh dấu rời). Cần PIL (có sẵn).
"""
import argparse, os, unicodedata
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")  # report_v2: font đi kèm repo (bản gốc: skill dd-investor-report)
W = 1600  # px; hiển thị ~760-800px trong email (retina 2x)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, f"BeVietnamPro-{name}.ttf"), size)


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def logo_chip(logo_path, ticker, h):
    """Trả ảnh RGBA chip trắng bo góc chứa logo (hoặc monogram), cao h."""
    pad = 22
    if logo_path and os.path.exists(logo_path):
        try:
            lg = Image.open(logo_path).convert("RGBA")
            s = (h - 2 * pad) / lg.height
            lg = lg.resize((max(1, int(lg.width * s)), h - 2 * pad), Image.LANCZOS)
            chip = Image.new("RGBA", (lg.width + 2 * pad, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(chip); d.rounded_rectangle((0, 0, chip.width - 1, h - 1), 18, fill="white")
            chip.alpha_composite(lg, (pad, pad))
            return chip
        except Exception:
            pass
    f = font("Bold", int(h * 0.42))
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(tmp.textlength(ticker, font=f))
    chip = Image.new("RGBA", (tw + 2 * 34, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip); d.rounded_rectangle((0, 0, chip.width - 1, h - 1), 18, fill="white")
    d.text((34, h // 2), ticker, font=f, fill="#0d1b2a", anchor="lm")
    return chip


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True); ap.add_argument("--ticker", required=True)
    ap.add_argument("--kicker", default=None); ap.add_argument("--sub", default="")
    ap.add_argument("--logo"); ap.add_argument("--out", required=True)
    ap.add_argument("--accent", default="#e0674f"); ap.add_argument("--bg", default="#0d1b2a")
    a = ap.parse_args()
    nfc = lambda s: unicodedata.normalize("NFC", s)
    title, kicker, sub = nfc(a.title), nfc(a.kicker or f"BÁO CÁO DUE DILIGENCE · {a.ticker}").upper(), nfc(a.sub)
    m = 64
    chip = logo_chip(a.logo, a.ticker, 120)
    tf, kf, sf = font("Bold", 50), font("Medium", 22), font("Regular", 24)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines = wrap(probe, title, tf, W - 2 * m)
    lh = 68
    H = (m - 10 + chip.height + 34) + len(lines) * lh + (56 if sub else 10) + 44
    img = Image.new("RGB", (W, H), a.bg)
    d = ImageDraw.Draw(img)
    # hàng đầu: chip logo bên trái + kicker cạnh logo
    img.paste(chip, (m, m - 10), chip)
    x_k = m + chip.width + 28
    d.text((x_k, m - 10 + chip.height // 2), "   ".join(kicker), font=kf, fill="#9fb0c3", anchor="lm") if False else None
    # kicker giãn chữ nhẹ
    x = x_k
    for ch in kicker:
        d.text((x, m - 10 + chip.height // 2), ch, font=kf, fill="#9fb0c3", anchor="lm")
        x += d.textlength(ch, font=kf) + 2.2
    y = m - 10 + chip.height + 34
    d.rectangle((m, y - 12, m + 90, y - 8), fill=a.accent)
    for ln in lines:
        d.text((m, y), ln, font=tf, fill="white"); y += lh
    if sub:
        d.text((m, y + 10), sub, font=sf, fill="#9fb0c3")
    img.save(a.out, dpi=(200, 200)); print(f"✅ {a.out} {img.size}")


if __name__ == "__main__":
    main()
