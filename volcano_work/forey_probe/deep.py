# -*- coding: utf-8 -*-
"""WbUliW8Or7E 한 편을 프레임 단위로 뜯는다.
자막이 언제 뜨고 어디에 어떤 크기로 앉는지, 뜨는 동안 움직이는지(애니메이션)까지.
"""
import io, json, sys
import numpy as np, cv2

S = 1920 / 1080.0
K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
mp4 = sys.argv[1] if len(sys.argv) > 1 else "dl/WbUliW8Or7E.mp4"

cap = cv2.VideoCapture(mp4)
fps = cap.get(cv2.CAP_PROP_FPS)
fs = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    fs.append(f)
cap.release()
h, w = fs[0].shape[:2]
n = len(fs)

gs = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fs]
fill = np.max(np.stack([(g > 30).sum(axis=1) / w for g in gs[::3]]), axis=0)
pic = np.where(fill > 0.85)[0]
ptop, pbot = int(pic.min()), int(pic.max())

rec = []
for i, f in enumerate(fs):
    g = gs[i]
    roi = g[ptop:pbot + 1]
    bgr = f[ptop:pbot + 1].astype(np.int16)
    B, G, R = bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2]
    dark = (roi <= 50).astype(np.uint8)
    near = cv2.dilate(dark, K)
    # 흰 글자
    wm = ((roi >= 238).astype(np.uint8)) & near
    # 분홍 글자
    pm = (((R > 150) & (R - G > 60) & (B - G > 25)).astype(np.uint8)) & near
    out = {"t": round(i / fps, 3)}
    for name, m in (("w", wm), ("p", pm)):
        ys = np.where(m.sum(axis=1) >= 8)[0]
        xs = np.where(m.sum(axis=0) >= 2)[0]
        if len(ys) >= 12 and m.sum() >= 300:
            # 글줄 나누기
            grp = []
            s = ys[0]
            prev = ys[0]
            for y in ys[1:]:
                if y - prev > 6:
                    grp.append((s, prev))
                    s = y
                prev = y
            grp.append((s, prev))
            grp = [t for t in grp if 55 <= (t[1] - t[0] + 1) * S <= 230]
            if grp:
                out[name] = {
                    "lines": len(grp),
                    "top": round((ptop + grp[0][0]) * S),
                    "bot": round((ptop + grp[-1][1]) * S),
                    "cy": round((ptop + (grp[0][0] + grp[-1][1]) / 2) * S),
                    "lh": round((grp[0][1] - grp[0][0] + 1) * S),
                    "x0": round(int(xs.min()) * S), "x1": round(int(xs.max()) * S),
                    "cx": round((int(xs.min()) + int(xs.max())) / 2 * S),
                    "w": round((int(xs.max()) - int(xs.min()) + 1) * S),
                    "ink": int(m.sum()),
                }
    rec.append(out)

# 덩이로 묶기
def group(key):
    out = []
    cur = None
    for r in rec:
        if key in r:
            if cur is None:
                cur = {"t0": r["t"], "t1": r["t"], "f": [r[key]]}
            else:
                cur["t1"] = r["t"]
                cur["f"].append(r[key])
        else:
            if cur and cur["t1"] - cur["t0"] >= 0.2:
                out.append(cur)
            cur = None
    if cur and cur["t1"] - cur["t0"] >= 0.2:
        out.append(cur)
    return out

o = []
o.append(f"{mp4}  {w}x{h} {fps:.2f}fps {n/fps:.2f}초   그림 y {round(ptop*S)}~{round(pbot*S)}")
for name, label in (("w", "흰 자막"), ("p", "분홍 효과자막")):
    ch = group(name)
    o.append("")
    o.append(f"=== {label} {len(ch)}덩이 ===")
    o.append(f"{'시작':>6}{'끝':>7}{'길이':>6}{'행':>3}{'중앙y':>7}{'글자h':>6}{'중심x':>6}{'폭':>6}"
             f"{'  y변화':>8}{'  폭변화':>9}{'  잉크변화'}")
    for c in ch:
        F = c["f"]
        cy = [x["cy"] for x in F]
        wd = [x["w"] for x in F]
        ik = [x["ink"] for x in F]
        lh = [x["lh"] for x in F]
        o.append(f"{c['t0']:>6.2f}{c['t1']:>7.2f}{c['t1']-c['t0']:>6.2f}"
                 f"{int(np.median([x['lines'] for x in F])):>3}"
                 f"{int(np.median(cy)):>7}{int(np.median(lh)):>6}"
                 f"{int(np.median([x['cx'] for x in F])):>6}{int(np.median(wd)):>6}"
                 f"{max(cy)-min(cy):>8}{max(wd)-min(wd):>9}"
                 f"   {min(ik)}~{max(ik)}")
io.open("deep.txt", "w", encoding="utf-8").write("\n".join(o))
json.dump(rec, io.open("deep.json", "w", encoding="utf-8"), ensure_ascii=False)
print("ok")
