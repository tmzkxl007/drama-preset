---
name: always-commit-session-record
description: 숏폼 작업 세션이 끝나면 대화 내용과 배운 것을 빠짐없이 로컬 git 에 커밋해 다음 세션이 재현할 수 있게 할 것
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a88e029c-8275-497b-ad54-33d044394a28
  modified: 2026-09-03T07:30:38.769Z
---

숏폼 제작 작업을 하면 **대화 내용과 그 과정에서 알아낸 것을 하나도 빠뜨리지 말고**
`~\volcano_work` 저장소의 `docs/SESSION-LOG.md` 와 `docs/PLAYBOOK.md` 에
갱신해 커밋한다. (2026-09-03 사용자 지시 — 본인이 "최상위 강제 규칙"이라고 못 박았다.)

**Why:** 같은 함정을 매 세션 다시 밟았다. 자막 시각 어긋남·나레 배속·박힌 자막처럼
한 번 푼 문제를 기록하지 않으면 다음 편에서 결과가 달라진다. 사용자는 **다음번에도
똑같이 나오는 것**을 원한다.

**How to apply:** 작업이 한 덩이 끝날 때마다 (편 하나를 뽑았거나, 새 함정을 풀었거나)
PLAYBOOK 에 규칙을, SESSION-LOG 에 요청·처리 이력을 더하고 커밋한다.
출입증(`.volcano_runner_key.json`)과 API 키, 미디어 파일은 절대 커밋하지 않는다.
git 은 `C:\Program Files\Git\cmd\git.exe` (PATH 에 없을 수 있다).

관련: [[volcano-linbox-playbook]]
