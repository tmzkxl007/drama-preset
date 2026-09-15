# -*- coding: utf-8 -*-
"""자막이 켜진 순간을 찾아 그 프레임의 자막 박스를 실측하고 잘라 저장한다."""
import sys, io, os, json
import numpy as np, cv2
S = 1920 / 1080.0
K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
os.makedirs("cap", exist_ok=True)
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
    hits = []
    for i, g in enumerate(gs):
        roi = g[ptop:pbot + 1]
        white = (roi >= 240).astype(np.uint8)
        dark = (roi <= 50).astype(np.uint8)
        capm = white & cv2.dilate(dark, K)
        cnt = capm.sum(axis=1)
        hot = np.where(cnt >= 8)[0]
        if len(hot) >= 14 and capm.sum() >= 350:
            xs = np.where(capm.sum(axis=0) >= 2)[0]
            hits.append((i, int(ptop + hot.min()), int(ptop + hot.max()),
                         int(xs.min()), int(xs.max()), int(capm.sum())))
    if not hits:
        out.append({"id": vid, "hits": 0})
        continue
    # 잉크가 가장 많은 3프레임 = 자막이 확실히 떠 있는 순간
    hits.sort(key=lambda x: -x[5])
    picked = hits[:3]
    rows = []
    for k, (i, y0, y1, x0, x1, ink) in enumerate(picked):
        crop = fs[i][max(0, y0 - 25):min(h, y1 + 25)]
        cv2.imwrite(f"cap/{vid}_pick{k}.png", cv2.resize(crop, (w * 2, crop.shape[0] * 2),
                                                         interpolation=cv2.INTER_LANCZOS4))
        rows.append({"t": round(i / fps, 2),
                     "y1920": [round(y0 * S), round(y1 * S)],
                     "texth1920": round((y1 - y0 + 1) * S),
                     "x1920": [round(x0 * S), round(x1 * S)],
                     "w1920": round((x1 - x0 + 1) * S),
                     "cx1920": round((x0 + x1) / 2 * S)})
    # 전체 히트의 통계 (오검출 줄이려 잉크 상위 40%만)
    hh = sorted(hits, key=lambda x: -x[5])[:max(3, len(hits) * 4 // 10)]
    a = np.array([[x[1], x[2], x[3], x[4]] for x in hh])
    out.append({"id": vid, "hits": len(hits), "picked": rows,
                "bot_med1920": round(float(np.median(a[:, 1])) * S),
                "top_med1920": round(float(np.median(a[:, 0])) * S),
                "texth_med1920": round(float(np.median(a[:, 1] - a[:, 0])) * S),
                "cx_med1920": round(float(np.median((a[:, 2] + a[:, 3]) / 2)) * S),
                "w_med1920": round(float(np.median(a[:, 3] - a[:, 2])) * S),
                "w_max1920": round(float(np.percentile(a[:, 3] - a[:, 2], 95)) * S)})
io.open("capshot.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
for r in out:
    if r.get("hits"):
        print(r["id"], "글자높이", r["texth_med1920"], "아래끝", r["bot_med1920"],
              "중심x", r["cx_med1920"], "폭중앙", r["w_med1920"], "폭최대", r["w_max1920"])
