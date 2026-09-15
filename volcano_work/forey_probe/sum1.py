# -*- coding: utf-8 -*-
import json,io
A=json.load(io.open("analysis.json",encoding="utf-8"))
M=json.load(io.open("meta.jsonl",encoding="utf-8")) if False else {}
meta={}
for ln in io.open("meta.jsonl",encoding="utf-8"):
    if ln.strip():
        j=json.loads(ln); meta[j["id"]]=j
A.sort(key=lambda r:-(meta.get(r["id"],{}).get("view_count") or 0))
o=[]
o.append("### 배치 (608x1080 실측 → 1080x1920 환산)")
o.append(f"{'id':13} {'조회':>9} {'길이':>6} {'제목띠h':>7} {'그림top':>7} {'그림bot':>7} {'그림h':>6} {'가로세로비':>8} {'아래띠h':>7}")
for r in A:
    v=meta.get(r['id'],{}).get('view_count') or 0
    p=r["pic"]
    o.append(f"{r['id']:13} {v:>9,} {r['dur']:>6.1f} {r['title_band']['h_1920']:>7} {p['top_1920']:>7} {p['bot_1920']:>7} {p['h_1920']:>6} {p['aspect']:>8.3f} {r['bottom_band']['h_1920']:>7}")
o.append("")
o.append("### 제목 (환산 · 색은 글자 중앙값)")
for r in A:
    o.append(f"{r['id']}  {meta.get(r['id'],{}).get('title','')[:40]}")
    for i,l in enumerate(r["title_lines"],1):
        o.append(f"    {i}행 y{round(l['y'][0]*1920/1080)}~{round(l['y'][1]*1920/1080)} 글자높이 {l['h_1920']:>3} 폭 {l['w_1920']:>4} 중심x {round(l['cx']*1920/1080)} 색 {l['hex']}")
o.append("")
o.append("### 자막")
o.append(f"{'id':13} {'떠있는비율':>9} {'덩이':>4} {'y범위(환산)':>14} {'중심y':>6} {'덩이길이(초)'}")
for r in A:
    c=r["caption"]
    y=c.get("y_1920",["?","?"])
    o.append(f"{r['id']:13} {c['on_ratio']*100:>8.0f}% {c['chunks']:>4} {str(y[0])+'~'+str(y[1]):>14} {c.get('center_1920','?'):>6} "+" ".join(f"{s:.1f}" for s in c['chunk_secs'][:14]))
o.append("")
o.append("### 컷")
o.append(f"{'id':13} {'길이':>5} {'컷수':>4} {'분당':>5} {'평균':>5} {'3.5초내':>6} {'디졸브':>5}  앞 6컷 길이")
for r in A:
    c=r["cuts"]
    o.append(f"{r['id']:13} {r['dur']:>5.1f} {c['n']:>4} {c['per_min']:>5.1f} {c['avg']:>5.2f} {c['open3s']:>6} {c['soft']:>5}  "+" ".join(f"{x:.1f}" for x in c['open_lens']))
o.append("")
o.append("### 나레이션")
o.append(f"{'id':13} {'길이':>5} {'글자':>4} {'초당':>5} {'덩이':>4} {'»':>3} {'시작':>5} {'끝':>5} 마지막 말")
for r in A:
    nr=r["narr"]
    o.append(f"{r['id']:13} {r['dur']:>5.1f} {nr['chars']:>4} {nr['cps']:>5.2f} {nr['segs']:>4} {nr['dlg_marks']:>3} {nr['start_t']:>5.1f} {nr['end_t']:>5.1f} {nr['last'][:38]}")
io.open("sum1.txt","w",encoding="utf-8").write("\n".join(o))
print("ok")
