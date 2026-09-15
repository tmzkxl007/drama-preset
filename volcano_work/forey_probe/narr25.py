# -*- coding: utf-8 -*-
import re, io, os, sys, glob, json, statistics as st
sys.stdout.reconfigure(encoding="utf-8")
exec(open("cadence25.py", encoding="utf-8").read().split("views=json")[0].split("# -*-")[1].replace("coding: utf-8 -*-","",1))

views = json.load(io.open("views25.json", encoding="utf-8"))
clean = lambda s: re.sub(r"[\s\[\]]|음악", "", s)

rows = []
for p in sorted(glob.glob("dl25/*.ko.vtt")):
    vid = os.path.basename(p).split(".")[0]
    f = parse(p)
    if not f: continue
    end = f[-1][1]
    # 한 자막 덩이 안에서도 » 뒤는 원본 대사다. 시간은 글자수 비례로 나눈다.
    n_ch = d_ch = 0.0; n_t = d_t = 0.0
    for a, b, t in f:
        dur = max(b - a, 1e-6)
        parts = re.split(r"(»)", t)
        mode = "n"; buf = {"n": 0, "d": 0}
        for q in parts:
            if q == "»": mode = "d"; continue
            buf[mode] += len(clean(q))
        tot = buf["n"] + buf["d"]
        if tot == 0: continue
        n_ch += buf["n"]; d_ch += buf["d"]
        n_t += dur * buf["n"] / tot; d_t += dur * buf["d"] / tot
    if n_t <= 0: continue
    rows.append(dict(id=vid, view=views.get(vid, 0), end=end,
                     n_ch=n_ch, n_t=n_t, ncps=n_ch / n_t,
                     share=100 * n_t / end, dlg=" ".join(t for _, _, t in f).count("»")))

print("id            조회      길이  나레자  나레초  나레초당자  나레비중  대사인용")
for r in sorted(rows, key=lambda r: -r["view"]):
    print("%-11s %9s %6.1f %6d %7.1f %9.1f %8.0f%% %7d" % (
        r["id"], format(r["view"], ","), r["end"], r["n_ch"], r["n_t"], r["ncps"], r["share"], r["dlg"]))

top = [r for r in rows if r["view"] >= 200000]
bot = [r for r in rows if r["view"] < 200000]
print()
for name, g in (("터진편 20만+", top), ("안터진편", bot), ("전체", rows)):
    print("%-12s %2d편 | 나레 초당 %5.2f자 | 나레비중 %3.0f%% | 대사인용 중앙 %2d회 | 길이 중앙 %.0f초" % (
        name, len(g), st.mean([r["ncps"] for r in g]), st.mean([r["share"] for r in g]),
        int(st.median([r["dlg"] for r in g])), st.median([r["end"] for r in g])))
