# -*- coding: utf-8 -*-
"""포레이로 한 편 완전 해부. 608x1080 실측 -> 1080x1920 환산(S=16/9)."""
import sys, io, os, json, re, subprocess
import numpy as np, cv2
S = 1920/1080.0


def vtt(p):
    if not os.path.exists(p):
        return []
    cues = []
    cur = None
    for ln in io.open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = re.match(r"(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)", ln)
        if m:
            def f(t):
                h, mi, se = t.split(":")
                return int(h) * 3600 + int(mi) * 60 + float(se)
            cur = [f(m.group(1)), f(m.group(2)), []]
            cues.append(cur)
            continue
        if cur is not None and ln.strip() and not ln.startswith(("WEBVTT", "Kind:", "Language:")):
            t = re.sub(r"<[^>]+>", "", ln).strip()
            t = t.replace("&gt;&gt;", "\u00bb").replace("&gt;", ">").replace("&amp;", "&")
            if t:
                cur[2].append(t)
    segs = []
    for a, b, ls in cues:
        t = re.sub(r"\s+", " ", " ".join(ls)).strip()
        if not t:
            continue
        if segs and segs[-1][2] == t:
            segs[-1][1] = b
            continue
        if segs and t.startswith(segs[-1][2]):
            segs[-1] = [segs[-1][0], b, t]
            continue
        segs.append([a, b, t])
    full = []
    prev = ""
    for a, b, t in segs:
        add = t[len(prev):].strip() if (prev and t.startswith(prev)) else t
        if add:
            full.append([round(a, 2), round(b, 2), add])
        prev = t
    return full


def audio(mp4):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    sr = 16000
    win = int(sr * 0.05)
    n = max(1, len(x) // win)
    rms = np.array([np.sqrt((x[i * win:(i + 1) * win] ** 2).mean() + 1e-12) for i in range(n)])
    db = 20 * np.log10(rms + 1e-9)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4,
                        "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    tail = r.split("Summary")[-1]
    def grab(pat):
        m = re.search(pat, tail)
        return float(m.group(1)) if m else None
    w = 10
    floor = np.array([db[i:i + w].min() for i in range(0, max(1, n - w), w)])
    return {"lufs": grab(r"I:\s*(-?[\d.]+) LUFS"),
            "lra": grab(r"LRA:\s*(-?[\d.]+) LU"),
            "peak": grab(r"Peak:\s*(-?[\d.]+) dBFS"),
            "med_db": round(float(np.median(db)), 1),
            "p10": round(float(np.percentile(db, 10)), 1),
            "p90": round(float(np.percentile(db, 90)), 1),
            "sil_45": round(float((db < -45).mean() * 100), 2),
            "sil_35": round(float((db < -35).mean() * 100), 2),
            "floor_med": round(float(np.median(floor)), 1),
            "floor_min": round(float(floor.min()), 1)}


def run(mp4):
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
    n = len(fs)
    dur = n / fps
    R = {"id": vid, "w": w, "h": h, "fps": round(fps, 3), "n": n, "dur": round(dur, 2)}

    gs = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fs]
    fill = np.max(np.stack([(g > 30).sum(axis=1) / w for g in gs[::3]]), axis=0)
    pic = np.where(fill > 0.9)[0]
    ptop, pbot = int(pic.min()), int(pic.max())
    R["pic"] = {"top": ptop, "bot": pbot, "h": pbot - ptop + 1,
                "top1920": round(ptop * S), "bot1920": round(pbot * S),
                "h1920": round((pbot - ptop + 1) * S),
                "ar": round(w / (pbot - ptop + 1), 4)}
    R["bands"] = {"top1920": round(ptop * S), "bot1920": round((h - 1 - pbot) * S)}

    # 제목: 색으로 두 행을 가른다 (1행 살구 R>>B, 2행 순백)
    band = np.median(np.stack(fs[::7])[:, :ptop], axis=0).astype(np.uint8)
    bg = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    rows = []
    for y in range(ptop):
        m = bg[y] > 150
        if m.sum() < 5:
            rows.append(None)
            continue
        px = band[y][m]
        b, g_, r_ = np.median(px, axis=0)
        rows.append(("white" if (r_ - b) < 18 else "warm", int(m.sum()), (b, g_, r_)))
    runs = []
    cur = None
    for y, v in enumerate(rows):
        if v is None:
            continue
        k = v[0]
        if cur and cur["kind"] == k and y - cur["y1"] <= 3:
            cur["y1"] = y
            cur["px"].append(v[2])
        else:
            if cur:
                runs.append(cur)
            cur = {"kind": k, "y0": y, "y1": y, "px": [v[2]]}
    if cur:
        runs.append(cur)
    runs = [q for q in runs if q["y1"] - q["y0"] >= 15]
    title = []
    for q in runs:
        col = np.median(np.array(q["px"]), axis=0)
        sub = band[q["y0"]:q["y1"] + 1]
        m = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY) > 150
        cx = np.where(m.any(axis=0))[0]
        title.append({"kind": q["kind"], "y": [q["y0"], q["y1"]], "h": q["y1"] - q["y0"] + 1,
                      "y1920": [round(q["y0"] * S), round(q["y1"] * S)],
                      "h1920": round((q["y1"] - q["y0"] + 1) * S),
                      "x1920": [round(int(cx.min()) * S), round(int(cx.max()) * S)],
                      "w1920": round((int(cx.max()) - int(cx.min()) + 1) * S),
                      "cx1920": round((int(cx.min()) + int(cx.max())) / 2 * S),
                      "hex": "#%02X%02X%02X" % (int(col[2]), int(col[1]), int(col[0]))})
    R["title"] = title

    # 자막: 흰 글자(>=240) 중 가로 +-7px 안에 아주 어두운 픽셀(<=50) = 검은 테두리
    K = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    onoff = np.zeros(n, dtype=bool)
    rowhit = np.zeros(h)
    boxes = []
    for i, g in enumerate(gs):
        roi = g[ptop:pbot + 1]
        white = (roi >= 240).astype(np.uint8)
        dark = (roi <= 50).astype(np.uint8)
        near = cv2.dilate(dark, K)
        capm = white & near
        cnt = capm.sum(axis=1)
        hot = np.where(cnt >= 8)[0]
        if len(hot) >= 14 and capm.sum() >= 350:
            onoff[i] = True
            rowhit[ptop + hot] += 1
            xs = np.where(capm.sum(axis=0) >= 2)[0]
            boxes.append((i / fps, int(ptop + hot.min()), int(ptop + hot.max()),
                          int(xs.min()), int(xs.max())))
    R["cap"] = {"on": round(float(onoff.mean()), 3)}
    if boxes:
        b = np.array([[x[1], x[2], x[3], x[4]] for x in boxes])
        R["cap"].update({
            "y1920": [round(float(np.percentile(b[:, 0], 5)) * S),
                      round(float(np.percentile(b[:, 1], 95)) * S)],
            "texth1920": round(float(np.median(b[:, 1] - b[:, 0])) * S),
            "x1920": [round(float(np.percentile(b[:, 2], 5)) * S),
                      round(float(np.percentile(b[:, 3], 95)) * S)],
            "w1920_med": round(float(np.median(b[:, 3] - b[:, 2])) * S)})
        zone = np.where(rowhit > len(boxes) * 0.15)[0]
        if len(zone):
            R["cap"]["band1920"] = [round(int(zone.min()) * S), round(int(zone.max()) * S)]
    ch = []
    i = 0
    while i < n:
        if onoff[i]:
            j = i
            while j < n and onoff[j]:
                j += 1
            if (j - i) / fps >= 0.25:
                ch.append([round(i / fps, 2), round(j / fps, 2)])
            i = j
        else:
            i += 1
    R["cap"]["chunks"] = len(ch)
    R["cap"]["chunk_secs"] = [round(y - x, 2) for x, y in ch]
    R["cap"]["gaps"] = [round(ch[k][0] - ch[k - 1][1], 2) for k in range(1, len(ch))]

    # 컷
    sm = [cv2.cvtColor(cv2.resize(f[ptop:pbot + 1], (152, 142)), cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fs]
    d = np.array([np.abs(sm[i] - sm[i - 1]).mean() for i in range(1, n)])
    thr = max(12.0, d.mean() + 3 * d.std())
    idx = np.where(d > thr)[0] + 1
    keep = []
    for i in idx:
        if not keep or (i - keep[-1]) / fps > 0.25:
            keep.append(int(i))
    ts = [round(i / fps, 2) for i in keep]
    if ts:
        lens = [ts[0]] + [round(ts[k] - ts[k - 1], 2) for k in range(1, len(ts))] + [round(dur - ts[-1], 2)]
    else:
        lens = [round(dur, 2)]
    acc = []
    s = 0.0
    for L in lens:
        s += L
        acc.append(round(s, 2))
    R["cuts"] = {"n": len(ts), "per_min": round(len(ts) / dur * 60, 1),
                 "avg": round(dur / max(1, len(ts) + 1), 2),
                 "times": ts, "lens": lens,
                 "n_first5s": len([t for t in ts if t <= 5.0]),
                 "lens_first5": [L for L, A in zip(lens, acc) if A <= 5.5],
                 "min": min(lens), "max": max(lens),
                 "pct_under1s": round(float(np.mean([L < 1.0 for L in lens])), 3)}

    # 화면 움직임 (줌/팬을 넣었는가)
    scales = []
    bounds = [0] + keep + [n - 1]
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < 12:
            continue
        i0, i1 = a + 2, min(b - 2, a + 12)
        if i1 <= i0:
            continue
        f0 = cv2.cvtColor(fs[i0][ptop:pbot + 1], cv2.COLOR_BGR2GRAY)
        f1 = cv2.cvtColor(fs[i1][ptop:pbot + 1], cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(f0, 200, 0.01, 8)
        if p0 is None or len(p0) < 20:
            continue
        p1, st, _ = cv2.calcOpticalFlowPyrLK(f0, f1, p0, None)
        if p1 is None:
            continue
        ok = st.ravel() == 1
        if ok.sum() < 20:
            continue
        M, _ = cv2.estimateAffinePartial2D(p0[ok], p1[ok])
        if M is None:
            continue
        sc = float(np.sqrt(M[0, 0] ** 2 + M[0, 1] ** 2))
        scales.append((sc - 1.0) / (i1 - i0) * fps)
    R["motion"] = {"n": len(scales),
                   "scale_per_s_med": round(float(np.median(scales)), 4) if scales else None,
                   "scale_per_s_p90": round(float(np.percentile(scales, 90)), 4) if scales else None,
                   "zooming_cuts": int(sum(1 for s in scales if abs(s) > 0.01))}

    # 나레이션 / 원본대사 분리
    segs = vtt(os.path.splitext(mp4)[0] + ".ko.vtt")
    narr = []
    dlg = []
    for a, b, t in segs:
        parts = re.split(r"\s*\u00bb\s*", t)
        lead = 1 if t.strip().startswith("\u00bb") else 0
        for k, p in enumerate(parts):
            p = p.strip()
            if not p:
                continue
            if (k + lead) % 2 == 1 or (lead and k == 1) or (lead == 0 and k >= 1):
                dlg.append([a, b, p])
            else:
                narr.append([a, b, p])

    def cl(L):
        return len(re.sub(r"[\s\[\]]|음악|박수|웃음|비명", "", "".join(x[2] for x in L)))
    R["narr"] = {"segs": len(segs), "narr_segs": len(narr), "dlg_segs": len(dlg),
                 "narr_chars": cl(narr), "dlg_chars": cl(dlg),
                 "narr_share": round(cl(narr) / max(1, cl(narr) + cl(dlg)), 3),
                 "cps_narr": round(cl(narr) / dur, 2),
                 "start": segs[0][0] if segs else None,
                 "end": segs[-1][1] if segs else None,
                 "timeline": segs}
    R["audio"] = audio(mp4)
    return R


if __name__ == "__main__":
    out = []
    for p in sys.argv[1:]:
        print("...", os.path.basename(p), flush=True)
        out.append(run(p))
    io.open("analysis2.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("wrote analysis2.json")
