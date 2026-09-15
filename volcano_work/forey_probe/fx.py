# -*- coding: utf-8 -*-
"""분홍(자홍) 효과자막 계층을 찾아 실측한다. 흰 대사자막과 다른 계층이다."""
import sys, io, os, json, glob
import numpy as np, cv2
S = 1920 / 1080.0
out = []
os.makedirs("fx", exist_ok=True)
for mp4 in sorted(glob.glob("dl/*.mp4")):
    vid = os.path.splitext(os.path.basename(mp4))[0]
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
    gs = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fs]
    fill = np.max(np.stack([(g > 30).sum(axis=1) / w for g in gs[::3]]), axis=0)
    pic = np.where(fill > 0.9)[0]
    ptop, pbot = int(pic.min()), int(pic.max())

    hits = []
    for i, f in enumerate(fs):
        roi = f[ptop:pbot + 1].astype(np.int16)
        B, G, R = roi[:, :, 0], roi[:, :, 1], roi[:, :, 2]
        # 자홍: R 높고 G 낮고 B 는 중간 이상, 채도 확실
        m = ((R > 150) & (R - G > 60) & (B - G > 20) & (R - B > 20)).astype(np.uint8)
        if m.sum() < 250:
            continue
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3)))
        ys = np.where(m.sum(axis=1) >= 6)[0]
        xs = np.where(m.sum(axis=0) >= 2)[0]
        if len(ys) < 10 or len(xs) < 20:
            continue
        px = roi[m.astype(bool)]
        col = np.median(px, axis=0)
        hits.append({"i": i, "t": round(i / fps, 2),
                     "y": [int(ptop + ys.min()), int(ptop + ys.max())],
                     "x": [int(xs.min()), int(xs.max())],
                     "h1920": round((ys.max() - ys.min() + 1) * S),
                     "w1920": round((xs.max() - xs.min() + 1) * S),
                     "cx1920": round((xs.min() + xs.max()) / 2 * S),
                     "cy1920": round((ptop + (ys.min() + ys.max()) / 2) * S),
                     "hex": "#%02X%02X%02X" % (int(col[2]), int(col[1]), int(col[0])),
                     "area": int(m.sum())})
    # 덩이로 묶기
    ch = []
    for hh in hits:
        if ch and hh["i"] - ch[-1][-1]["i"] <= 4:
            ch[-1].append(hh)
        else:
            ch.append([hh])
    ch = [c for c in ch if len(c) >= 5]
    r = {"id": vid, "dur": round(len(fs) / fps, 2), "n_fx": len(ch),
         "on_ratio": round(sum(len(c) for c in ch) / len(fs), 3), "items": []}
    for c in ch:
        best = max(c, key=lambda x: x["area"])
        r["items"].append({"t0": c[0]["t"], "t1": c[-1]["t"], "sec": round(c[-1]["t"] - c[0]["t"], 2),
                           "h1920": best["h1920"], "w1920": best["w1920"],
                           "cx1920": best["cx1920"], "cy1920": best["cy1920"], "hex": best["hex"]})
        y0 = max(ptop, best["y"][0] - 30)
        y1 = min(h, best["y"][1] + 30)
        crop = fs[best["i"]][y0:y1]
        cv2.imwrite(f"fx/{vid}_{best['i']}.png",
                    cv2.resize(crop, (w * 2, crop.shape[0] * 2), interpolation=cv2.INTER_LANCZOS4))
    out.append(r)
io.open("fx.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{'id':13}{'효과자막수':>8}{'떠있음':>8}   각 등장(초) / 글자높이 / 중심xy / 색")
for r in out:
    print(f"{r['id']:13}{r['n_fx']:>8}{r['on_ratio']*100:>7.1f}%")
    for it in r["items"]:
        print(f"    {it['t0']:6.2f}~{it['t1']:6.2f} ({it['sec']:4.1f}s)  h{it['h1920']:>4} w{it['w1920']:>4} "
              f"중심({it['cx1920']},{it['cy1920']})  {it['hex']}")
