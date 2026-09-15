# -*- coding: utf-8 -*-
"""자막 한 줄을 실측(잉크 높이·폭)하고, 후보 글꼴을 같은 잉크높이로 렌더해 폭을 견준다."""
import sys, io, os, glob, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = 1920 / 1080.0
K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))

mp4, t, text = sys.argv[1], float(sys.argv[2]), sys.argv[3]
cap = cv2.VideoCapture(mp4)
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
ok, f = cap.read()
cap.release()
h, w = f.shape[:2]
g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
white = (g >= 240).astype(np.uint8)
dark = (g <= 50).astype(np.uint8)
capm = white & cv2.dilate(dark, K)
capm[:400] = 0                      # 제목 띠 제외
ys = np.where(capm.sum(axis=1) >= 8)[0]
xs = np.where(capm.sum(axis=0) >= 2)[0]
y0, y1, x0, x1 = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
ink_h = (y1 - y0 + 1) * S
ink_w = (x1 - x0 + 1) * S
print(f"실측  잉크높이 {ink_h:.0f}  폭 {ink_w:.0f}  글자수 {len(text.replace(' ',''))}  "
      f"y {round(y0*S)}~{round(y1*S)}  x {round(x0*S)}~{round(x1*S)}  중심x {round((x0+x1)/2*S)}")

cv2.imwrite("cap/_ref.png", cv2.resize(f[max(0,y0-20):y1+20, :], (w*2, (y1-y0+40)*2),
                                       interpolation=cv2.INTER_LANCZOS4))

rows = []
for p in sorted(glob.glob("fonts/*.ttf")):
    name = os.path.basename(p)[:-4]
    # 잉크높이가 실측과 같아지는 글자크기를 이분탐색
    lo, hi = 20, 400
    for _ in range(24):
        mid = (lo + hi) / 2
        fnt = ImageFont.truetype(p, int(round(mid)))
        im = Image.new("L", (4000, 700), 0)
        ImageDraw.Draw(im).text((50, 100), text, font=fnt, fill=255)
        a = np.array(im)
        yy = np.where(a.max(axis=1) > 40)[0]
        ih = (yy.max() - yy.min() + 1) if len(yy) else 0
        if ih < ink_h:
            lo = mid
        else:
            hi = mid
    size = int(round((lo + hi) / 2))
    fnt = ImageFont.truetype(p, size)
    im = Image.new("L", (4000, 700), 0)
    ImageDraw.Draw(im).text((50, 100), text, font=fnt, fill=255)
    a = np.array(im)
    yy = np.where(a.max(axis=1) > 40)[0]
    xx = np.where(a.max(axis=0) > 40)[0]
    wdt = xx.max() - xx.min() + 1
    rows.append((abs(wdt - ink_w), name, size, wdt))
rows.sort()
print(f"\n{'글꼴':16}{'맞춘크기':>8}{'렌더폭':>8}{'실측폭차':>9}")
for d, name, size, wdt in rows:
    print(f"{name:16}{size:>8}{wdt:>8}{d:>9.0f}")

# 상위 4개를 실제 자막 위에 겹쳐 그린 비교표
best = [r for r in rows[:4]]
H = 150
out = Image.new("RGB", (1216, H * (len(best) + 1)), (16, 16, 16))
ref = Image.open("cap/_ref.png").convert("RGB")
ref = ref.resize((1216, int(ref.height * 1216 / ref.width)))
out.paste(ref, (0, 0))
d0 = ImageDraw.Draw(out)
y = H
for _, name, size, _w in best:
    fnt = ImageFont.truetype(f"fonts/{name}.ttf", int(size * 1216 / 1920))
    tw = d0.textlength(text, font=fnt)
    d0.text(((1216 - tw) / 2, y + 30), text, font=fnt, fill=(255, 255, 255),
            stroke_width=max(2, int(size * 0.075 * 1216 / 1920)), stroke_fill=(0, 0, 0))
    d0.text((10, y + 5), name, fill=(120, 200, 255))
    y += H
out.save("font_match.png")
print("\nfont_match.png 저장")
