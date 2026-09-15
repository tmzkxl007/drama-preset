---
name: deliver-only-the-final-video
description: "사용자는 완성본 하나만 받길 원한다 — 중간 파일 목록을 늘어놓지 말 것"
metadata:
  type: feedback
---

숏폼을 다 만들었으면 **완성본 영상 하나만 건넨다.**

> 사용자: 「영상을 만들고 파일을 이렇게 다 주지마 그냥 완성본 하나만 주고」

**Why:** 중간산물(컷·나레·자막·자산팩)을 줄줄이 나열하면 정작 올릴 파일이 묻힌다.

**How to apply:** 완성본은 채널 폴더(`volcano_work/딸기우유/` · `volcano_work/일본팬튜브/`)로 모은다 — `presets/_engine/base.py` 의 `DELIVER_ROOT` 가 저장소 위치를 스스로 찾는다. 편 폴더에 남는 중간물은 언급하지 않는다.

[[ttalgiuyu-preset]] · [[jp-reaction-channel]]
