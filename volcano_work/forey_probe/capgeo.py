# -*- coding: utf-8 -*-
"""자막 박스만 골라 실측한다. 글자높이가 사람 글자 범위(1920 환산 70~210)인 것만 신뢰한다."""
import sys, io, os, json
import numpy as np, cv2
S = 1920 / 1080.0
K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
out = []
for mp4 in sys.argv[1:]:
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
    one, two = [], []
    for i, g in enumerate(gs):
        roi = g[ptop:pbot + 1]
        white = (roi >= 240).astype(np.uint8)
        dark = (roi <= 50).astype(np.uint8)
        capm = white & cv2.dilate(dark, K)
        cnt = capm.sum(axis=1)
        hot = cnt >= 8
        if hot.sum() < 12:
            continue
        # 연속 행 묶음 = 글줄
        ys = np.where(hot)[0]
        groups = []
        s = ys[0]
        p = ys[0]
        for y in ys[1:]:
            if y - p > 6:
                groups.append((s, p))
                s = y
            p = y
        groups.append((s, p))
        groups = [(a, b) for a, b in groups if (b - a + 1) * S >= 60 and (b - a + 1) * S <= 210]
        if not groups or len(groups) > 2:
            continue
        xs = np.where(capm.sum(axis=0) >= 2)[0]
        rec = {"t": round(i / fps, 2), "lines": len(groups),
               "top": ptop + groups[0][0], "bot": ptop + groups[-1][1],
               "lineh": [round((b - a + 1) * S) for a, b in groups],
               "x0": int(xs.min()), "x1": int(xs.max())}
        (one if len(groups) == 1 else two).append(rec)

    def stat(L, name):
        if not L:
            return {name: 0}
        bot = np.array([r["bot"] for r in L]) * S
        top = np.array([r["top"] for r in L]) * S
        lh = np.array([r["lineh"][0] for r in L])
        cx = np.array([(r["x0"] + r["x1"]) / 2 for r in L]) * S
        wd = np.array([(r["x1"] - r["x0"] + 1) for r in L]) * S
        return {name: len(L),
                name + "_bot": round(float(np.median(bot))),
                name + "_top": round(float(np.median(top))),
                name + "_lineh": round(float(np.median(lh))),
                name + "_cx": round(float(np.median(cx))),
                name + "_w_med": round(float(np.median(wd))),
                name + "_w_p95": round(float(np.percentile(wd, 95)))}
    r = {"id": vid, "frames": len(fs)}
    r.update(stat(one, "one"))
    r.update(stat(two, "two"))
    out.append(r)
io.open("capgeo.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
hdr = f"{'id':13}{'1행프레임':>8}{'글자높이':>7}{'아래끝':>7}{'중심x':>6}{'폭중앙':>7}{'폭95%':>7}   |{'2행프레임':>8}{'행높이':>7}{'위':>6}{'아래':>6}"
print(hdr)
for r in out:
    print(f"{r['id']:13}{r.get('one',0):>8}{r.get('one_lineh','-'):>7}{r.get('one_bot','-'):>7}"
          f"{r.get('one_cx','-'):>6}{r.get('one_w_med','-'):>7}{r.get('one_w_p95','-'):>7}   |"
          f"{r.get('two',0):>8}{r.get('two_lineh','-'):>7}{r.get('two_top','-'):>6}{r.get('two_bot','-'):>6}")
