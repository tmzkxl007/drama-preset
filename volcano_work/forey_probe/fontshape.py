# -*- coding: utf-8 -*-
"""후보 글꼴을 실제 자막과 '잉크높이 + 전체폭' 둘 다 맞춰(자간 조절) 그려 모양을 견준다."""
import sys, os, glob
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

TXT = "경성 제1의 정보통이거든요"
REF_H = 101.0    # 실측 잉크높이 (1080x1920 기준)
REF_W = 848.0    # 실측 폭
CANVAS_W = 1216  # 견줄 그림 폭 (=1080 을 2배 가깝게)
K = CANVAS_W / 1080.0


def ink(img):
    a = np.array(img)
    ys = np.where(a.max(axis=1) > 40)[0]
    xs = np.where(a.max(axis=0) > 40)[0]
    if not len(ys):
        return 0, 0
    return ys.max() - ys.min() + 1, xs.max() - xs.min() + 1


def draw(fp, size, track, W=4000, H=800):
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(fp, size)
    x = 60.0
    for chx in TXT:
        d.text((x, 150), chx, font=f, fill=255)
        x += d.textlength(chx, font=f) + track
    return im


cands = sorted(glob.glob("fonts/*.ttf")) + ["C:/Windows/Fonts/malgunbd.ttf",
                                            "C:/Windows/Fonts/NanumGothic.ttf"]
rows = []
for fp in cands:
    if not os.path.exists(fp):
        continue
    name = os.path.basename(fp).rsplit(".", 1)[0]
    lo, hi = 20, 400
    for _ in range(22):
        mid = (lo + hi) / 2
        h, _w = ink(draw(fp, int(round(mid)), 0))
        if h < REF_H * K:
            lo = mid
        else:
            hi = mid
    size = int(round((lo + hi) / 2))
    lo2, hi2 = -size * 0.5, size * 0.5
    for _ in range(22):
        mid = (lo2 + hi2) / 2
        _h, w = ink(draw(fp, size, mid))
        if w < REF_W * K:
            lo2 = mid
        else:
            hi2 = mid
    track = (lo2 + hi2) / 2
    rows.append((name, fp, size, round(track, 1), round(track / size * 100, 1)))

rows.sort(key=lambda r: abs(r[3]))
print(f"{'글꼴':16}{'크기':>6}{'자간':>8}{'자간%':>8}   (자간이 0 에 가까울수록 원본 비례와 맞다)")
for name, fp, size, tr, pc in rows:
    print(f"{name:16}{size:>6}{tr:>8}{pc:>7}%")

ref = Image.open("cap/_ref.png").convert("RGB")
ref = ref.resize((CANVAS_W, int(ref.height * CANVAS_W / ref.width)))
H = 150
out = Image.new("RGB", (CANVAS_W, ref.height + H * len(rows)), (12, 12, 12))
out.paste(ref, (0, 0))
d0 = ImageDraw.Draw(out)
y = ref.height
lbl = ImageFont.truetype("fonts/Jua.ttf", 24)
for name, fp, size, tr, pc in rows:
    f = ImageFont.truetype(fp, size)
    total = sum(d0.textlength(c, font=f) for c in TXT) + tr * (len(TXT) - 1)
    x = (CANVAS_W - total) / 2
    for chx in TXT:
        d0.text((x, y + 25), chx, font=f, fill=(255, 255, 255),
                stroke_width=max(2, int(size * 0.085)), stroke_fill=(0, 0, 0))
        x += d0.textlength(chx, font=f) + tr
    d0.text((8, y + 4), f"{name}  size{size} track{tr}", font=lbl, fill=(120, 200, 255))
    y += H
out.save("font_shape.png")
print("font_shape.png 저장", out.size)
