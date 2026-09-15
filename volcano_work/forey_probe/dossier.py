# -*- coding: utf-8 -*-
"""편별 해부 카드 — 제목/설명문/나레이션 타임라인/컷/자막을 한 장에."""
import json, io, re

A = {r["id"]: r for r in json.load(io.open("analysis2.json", encoding="utf-8"))}
F = {r["id"]: r for r in json.load(io.open("finish.json", encoding="utf-8"))}
G = {r["id"]: r for r in json.load(io.open("capgeo.json", encoding="utf-8"))}
order = sorted(A, key=lambda k: -(F[k]["views"] or 0))

o = []
for k in order:
    a, f, g = A[k], F[k], G[k]
    o.append("=" * 78)
    o.append(f"[{k}]  조회 {f['views']:,} · {f['date']} · {a['dur']}초")
    o.append(f"제목: {f['title']}")
    o.append(f"태그: {' '.join(f['tags'])}")
    o.append("설명문:")
    for ln in (f["desc"] or "").split("\n"):
        if ln.strip() and not ln.strip().startswith("#"):
            o.append("    " + ln.strip())
    tl = a["title"]
    if len(tl) >= 2:
        o.append(f"화면 제목: 1행 {tl[0]['hex']} h{tl[0]['h1920']} 폭{tl[0]['w1920']} / "
                 f"2행 {tl[1]['hex']} h{tl[1]['h1920']} 폭{tl[1]['w1920']}  (행간 {tl[1]['y1920'][0]-tl[0]['y1920'][1]})")
    c = a["cuts"]
    o.append(f"컷: {c['n']}개 · 분당 {c['per_min']} · 평균 {c['avg']}s · 최단 {c['min']} 최장 {c['max']} · "
             f"1초미만 {c['pct_under1s']*100:.0f}% · 첫5초 {c['n_first5s']}컷")
    o.append(f"    컷 길이: " + " ".join(f"{x:.1f}" for x in c["lens"]))
    o.append(f"자막: 1행 글자높이 {g.get('one_lineh','-')} 아래끝 {g.get('one_bot','-')} 중심x {g.get('one_cx','-')} "
             f"폭중앙 {g.get('one_w_med','-')} / 2행 아래끝 {g.get('two_bot','-')} · 테두리 {f['outline_px1080']}px")
    n = a["narr"]
    o.append(f"나레: {n['narr_chars']}자 (비중 {n['narr_share']*100:.0f}%) · 대사 {n['dlg_chars']}자 · "
             f"나레 초당 {n['cps_narr']}자 · 말 {n['start']}s~{n['end']}s")
    au = a["audio"]
    o.append(f"소리: {au['lufs']} LUFS · LRA {au['lra']} · 피크 {au['peak']} · 무음(-45dB) {au['sil_45']}%")
    o.append("나레이션/대사 타임라인:")
    for s, e, t in n["timeline"]:
        mark = "대사" if t.strip().startswith("»") else "나레"
        o.append(f"    {s:6.2f}  [{mark}] {t.replace(chr(187),'').strip()}")
io.open("dossier.txt", "w", encoding="utf-8").write("\n".join(o))
print("ok", len(o))
