# -*- coding: utf-8 -*-
"""남은 실측: 자막 테두리 두께 · 0초 프레임 · 설명문 · 나레이션 원문."""
import sys, io, os, json, re, glob
import numpy as np, cv2
S = 1920 / 1080.0
K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))

meta = {}
for ln in io.open("meta.jsonl", encoding="utf-8"):
    if ln.strip():
        j = json.loads(ln)
        meta[j["id"]] = j

out = []
os.makedirs("hook", exist_ok=True)
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

    # 자막 테두리 두께: 글자 흰 획을 가로로 훑어 흰->검->그림 전이의 검은 구간 길이
    thick = []
    for i, g in enumerate(gs):
        roi = g[ptop:pbot + 1]
        white = (roi >= 240).astype(np.uint8)
        dark = (roi <= 50).astype(np.uint8)
        capm = white & cv2.dilate(dark, K)
        ys = np.where(capm.sum(axis=1) >= 8)[0]
        if len(ys) < 12:
            continue
        y = int(np.median(ys))
        row_w = white[y]
        row_d = dark[y]
        runs = []
        x = 0
        while x < len(row_w):
            if row_w[x]:
                while x < len(row_w) and row_w[x]:
                    x += 1
                d0 = 0
                while x < len(row_w) and row_d[x]:
                    d0 += 1
                    x += 1
                if 0 < d0 < 40:
                    runs.append(d0)
            else:
                x += 1
        if runs:
            thick.append(np.median(runs))
        if len(thick) > 200:
            break
    # 0초 프레임 저장
    cv2.imwrite(f"hook/{vid}_t0.jpg", fs[0], [cv2.IMWRITE_JPEG_QUALITY, 88])

    m = meta.get(vid, {})
    r = {"id": vid, "views": m.get("view_count"), "date": m.get("upload_date"),
         "title": m.get("title"), "desc": m.get("description"),
         "tags": re.findall(r"#\S+", m.get("description") or ""),
         "dur": round(len(fs) / fps, 2),
         "outline_px1080": round(float(np.median(thick)) * S, 1) if thick else None,
         "outline_samples": len(thick)}
    # 나레이션 원문
    v = os.path.splitext(mp4)[0] + ".ko.vtt"
    r["vtt_exists"] = os.path.exists(v)
    out.append(r)

io.open("finish.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{'id':13}{'테두리px':>9}{'표본':>6}  태그")
for r in out:
    print(f"{r['id']:13}{str(r['outline_px1080']):>9}{r['outline_samples']:>6}  {' '.join(r['tags'])}")
