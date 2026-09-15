# -*- coding: utf-8 -*-
import json, io
A = json.load(io.open("analysis2.json", encoding="utf-8"))
meta = {}
for ln in io.open("meta.jsonl", encoding="utf-8"):
    if ln.strip():
        j = json.loads(ln)
        meta[j["id"]] = j
A.sort(key=lambda r: -(meta.get(r["id"], {}).get("view_count") or 0))
o = []

o.append("### 1. 캔버스·배치  (1080x1920 환산)")
o.append(f"{'id':13}{'조회':>10}{'올린날':>9}{'길이':>6}{'윗띠':>6}{'그림top':>8}{'그림bot':>8}{'그림h':>7}{'가로/세로':>9}{'아랫띠':>7}")
for r in A:
    m = meta.get(r["id"], {})
    p = r["pic"]
    o.append(f"{r['id']:13}{(m.get('view_count') or 0):>10,}{str(m.get('upload_date')):>9}{r['dur']:>6.1f}"
             f"{r['bands']['top1920']:>6}{p['top1920']:>8}{p['bot1920']:>8}{p['h1920']:>7}{p['ar']:>9.3f}{r['bands']['bot1920']:>7}")

o.append("")
o.append("### 2. 제목 두 행")
for r in A:
    m = meta.get(r["id"], {})
    o.append(f"{r['id']}  {m.get('title','')[:52]}")
    for t in r["title"]:
        o.append(f"    {t['kind']:5} y{t['y1920'][0]:>4}~{t['y1920'][1]:<4} 글자높이{t['h1920']:>4}  x{t['x1920'][0]:>4}~{t['x1920'][1]:<4} 폭{t['w1920']:>4} 중심{t['cx1920']:>4}  {t['hex']}")

o.append("")
o.append("### 3. 자막 (그림 안쪽)")
o.append(f"{'id':13}{'떠있음':>7}{'덩이':>5}{'띠y(환산)':>14}{'글자높이':>7}{'x범위':>12}{'중앙폭':>7}")
for r in A:
    c = r["cap"]
    if "band1920" not in c:
        o.append(f"{r['id']:13}  검출실패")
        continue
    o.append(f"{r['id']:13}{c['on']*100:>6.0f}%{c['chunks']:>5}"
             f"{str(c['band1920'][0])+'~'+str(c['band1920'][1]):>14}{c['texth1920']:>7}"
             f"{str(c['x1920'][0])+'~'+str(c['x1920'][1]):>12}{c['w1920_med']:>7}")
o.append("  덩이 길이(초):")
for r in A:
    o.append(f"    {r['id']}: " + " ".join(f"{s:.1f}" for s in r["cap"]["chunk_secs"]))
o.append("  덩이 사이 빈틈(초):")
for r in A:
    o.append(f"    {r['id']}: " + " ".join(f"{s:.2f}" for s in r["cap"]["gaps"]))

o.append("")
o.append("### 4. 컷")
o.append(f"{'id':13}{'길이':>6}{'컷':>4}{'분당':>6}{'평균':>6}{'최단':>6}{'최장':>6}{'1초미만':>8}{'5초내컷':>7}  앞부분 컷 길이")
for r in A:
    c = r["cuts"]
    o.append(f"{r['id']:13}{r['dur']:>6.1f}{c['n']:>4}{c['per_min']:>6.1f}{c['avg']:>6.2f}{c['min']:>6.1f}{c['max']:>6.1f}"
             f"{c['pct_under1s']*100:>7.0f}%{c['n_first5s']:>7}  " + " ".join(f"{x:.1f}" for x in c["lens_first5"]))

o.append("")
o.append("### 5. 화면 움직임 (직접 넣은 줌/팬)")
o.append(f"{'id':13}{'잰컷수':>7}{'초당배율중앙':>13}{'p90':>9}{'움직인컷':>9}")
for r in A:
    m = r["motion"]
    o.append(f"{r['id']:13}{m['n']:>7}{str(m['scale_per_s_med']):>13}{str(m['scale_per_s_p90']):>9}{m['zooming_cuts']:>9}")

o.append("")
o.append("### 6. ★나레이션 vs 원본대사")
o.append(f"{'id':13}{'조회':>10}{'길이':>6}{'나레자':>7}{'대사자':>7}{'나레비중':>9}{'나레초당':>9}{'말시작':>7}{'말끝':>7}")
for r in A:
    nr = r["narr"]
    m = meta.get(r["id"], {})
    o.append(f"{r['id']:13}{(m.get('view_count') or 0):>10,}{r['dur']:>6.1f}{nr['narr_chars']:>7}{nr['dlg_chars']:>7}"
             f"{nr['narr_share']*100:>8.0f}%{nr['cps_narr']:>9.2f}{(nr['start'] or 0):>7.1f}{(nr['end'] or 0):>7.1f}")

o.append("")
o.append("### 7. 소리")
o.append(f"{'id':13}{'LUFS':>7}{'LRA':>6}{'피크':>7}{'중앙dB':>7}{'p10':>7}{'p90':>7}{'-45무음%':>9}{'-35무음%':>9}{'바닥중앙':>8}")
for r in A:
    a = r["audio"]
    o.append(f"{r['id']:13}{str(a['lufs']):>7}{str(a['lra']):>6}{str(a['peak']):>7}{a['med_db']:>7.1f}"
             f"{a['p10']:>7.1f}{a['p90']:>7.1f}{a['sil_45']:>9.2f}{a['sil_35']:>9.2f}{a['floor_med']:>8.1f}")

io.open("sum2.txt", "w", encoding="utf-8").write("\n".join(o))
print("ok")
