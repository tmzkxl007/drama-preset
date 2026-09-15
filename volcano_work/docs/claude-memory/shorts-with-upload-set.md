---
name: shorts-with-upload-set
description: 쇼츠를 건넬 때 제목·설명글·해시태그를 영상과 한 벌로 같이 준다 — 영상만 주지 마라
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3e4cb580-c057-4c4c-a652-bb87af32e768
  modified: 2026-09-13T12:47:29.235Z
---

2026-09-13 사용자: **"쇼츠 만들때 제목설명글해시태그도같이세트로줘"**

**Why:** 사용자는 받은 영상을 바로 유튜브에 올린다. 메타데이터가 긴 답변 속에 흩어져 있거나
빠지면 따로 찾아 옮겨야 한다.

**How to apply:**
- 모든 숏폼 편에서 완성본과 함께 **제목 · 설명글 · 해시태그**를 복사해 붙일 수 있는 한 덩어리로 낸다.
  답변에도 그 세트를 코드블록으로 보여 주고, 파일도 영상 옆에 둔다.
- 일뽕: `presets/일뽕/meta.py` 가 `build.py` 끝에서 돌아 `volcano_work/일뽕/<편>_업로드.txt` 를 쓴다.
  episode.py 에 `TITLE · DESC · HASHTAGS(딱 5개) · THUMB · RAKUTEN · SOURCE_URL · CREDIT` (+`*_KO`).
- 다른 프리셋(국뽕·일뽕롱폼·일본사이다숏폼 등)은 이미 `meta.py` 가 있다 — 빠뜨리지 말고 같이 건넨다.
- [[deliver-only-the-final-video]] 의 "완성본만"은 중간 파일 얘기다 — 업로드 세트는 완성본의 일부다.

관련: [[jp-reaction-channel]] · [[deliver-only-the-final-video]]
