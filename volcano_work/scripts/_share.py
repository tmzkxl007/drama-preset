# -*- coding: utf-8 -*-
"""편별 나레/대사 비중 재기 — narr_align.json(마지막 덩이 끝) + episode.py D 블록 길이 + ffprobe."""
import io, json, re, glob, os, subprocess, statistics
rows = []
for d in sorted(glob.glob('mk[0-9][0-9]_*') + glob.glob('mk13[bc]_*')):
    e = os.path.basename(d)
    n = int(re.match(r'mk(\d+)', e).group(1))
    if n < 12:
        continue
    ep = os.path.join(e, 'episode.py'); na = os.path.join(e, 'narr_align.json')
    mp = [f for f in glob.glob(e + '/*.mp4') if 'src' not in f]
    if not (os.path.exists(ep) and os.path.exists(na) and mp):
        continue
    src = io.open(ep, encoding='utf-8').read()
    ns = re.findall(r'\("N",\s*"([^"]+)"', src); nch = sum(len(x.replace(' ', '')) for x in ns)
    D = re.findall(r'\("D",\s*([\d.]+),\s*([\d.]+)', src); dsec = sum(float(b) - float(a) for a, b in D)
    dtxt = re.findall(r'\("D",.*?\[(.*?)\]\)', src, re.S)
    dch = sum(len(''.join(re.findall(r'\("([^"]+)"', t)).replace(' ', '')) for t in dtxt)
    al = json.load(io.open(na, encoding='utf-8'))
    nsec = sum(v[-1][2] for v in al.values() if v)
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp[0]],
                         capture_output=True).stdout.decode('utf-8', 'replace').strip()
    try:
        tot = float(out)
    except ValueError:
        tot = 0
    if tot <= 0:
        continue   # 굽는 중인 편
    rows.append((e, tot, nsec, dsec, len(ns), nch, len(D), dch))
print(f"{'편':24} 길이  나레초 대사초 나레% 대사%  나레마디/글자 대사블록/글자")
for e, tot, ns, ds, nn, nch, nd, dch in rows:
    print(f"{e:24} {tot:5.1f} {ns:6.1f} {ds:6.1f} {ns/tot*100:5.0f} {ds/tot*100:5.0f}    {nn}/{nch:3}      {nd}/{dch:3}")
print('평균 나레%', round(statistics.mean(r[2] / r[1] * 100 for r in rows)),
      '대사%', round(statistics.mean(r[3] / r[1] * 100 for r in rows)))
