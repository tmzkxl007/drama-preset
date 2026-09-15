# 포레이로 프리셋 이식팩 — 다른 PC 에서 쓰는 법

## 1. 설치 (한 번만)

1. 이 zip 을 아무 데나 푼다.
2. **`설치.bat` 을 더블클릭**한다. 하는 일:
   - Python 3.12 · ffmpeg 이 없으면 winget 으로 설치
   - 전용 파이썬 `%USERPROFILE%\.volcano\venv` 를 만들고 패키지 설치
   - `volcano_work` 폴더를 `%USERPROFILE%\volcano_work` 에 놓는다
     (이미 있으면 기존 `presets\포레이로` 는 `.bak-날짜` 로 옮겨 두고, 기존 `CLAUDE.md` 는 건드리지 않고 `CLAUDE-포레이로.md` 로 둔다)
   - 글꼴 **그리운 코코초이툰**을 사용자 글꼴로 설치
   - API 키를 물어본다 → `%USERPROFILE%\.volcano\keys\` 에 저장 (비우고 엔터 = 건너뜀)
   - 마지막에 점검표를 찍는다 (`[!!]` 가 없으면 끝)
   - 다른 위치에 놓으려면: `powershell -ExecutionPolicy Bypass -File install.ps1 -Target D:\volcano_work`
3. ffmpeg 을 새로 깔았다면 **창을 닫고 새로 연 다음** `설치.bat` 을 한 번 더 돌린다 (PATH 반영).

## 2. API 키 — ★이 팩에는 들어 있지 않다

지금 PC 의 `C:\Users\<이름>\.volcano\keys\` 에 있는 파일 내용을 옮겨 적는다.

| 파일 | 쓰는 곳 | |
|---|---|---|
| `typecast` | 나레 목소리 (SeHee 1.2배) | 필수 |
| `speechmatics` | 대사 전사 (단어 시각) | 필수 |
| `gemini` | 시대극 두 번째 귀 (종결어미·호칭 확인) | 선택 |

## 3. 쓰기

1. Claude Code 를 **`volcano_work` 폴더에서** 연다.
2. **"포레이로프리셋 불러와"** 라고 한다. Claude 가 `CLAUDE.md` → 지침서 → 부록 → README → PLAYBOOK → 규칙 메모 순으로 읽는다.
3. 소재(공식 클립 URL 또는 내 파일 + 구간)를 준다.

## 4. 들어 있는 것

| 위치 | 무엇 |
|---|---|
| `volcano_work/CLAUDE.md` | Claude 가 제일 먼저 읽는 안내 (읽는 순서 · 절차 · 최상위 규칙) |
| `volcano_work/docs/포레이로-지침서.md` | 사용자가 못 박은 것 전부 (원본 그대로) |
| `volcano_work/docs/포레이로-지침서-부록.md` | 지침서 뒤(09-09~09-15)에 새로 박힌 것 — 숫자가 다르면 이쪽이 이긴다 |
| `volcano_work/docs/PLAYBOOK-포레이로.md` | 실측값·함정 전량 (§8 · §10 · §16 · §17) |
| `volcano_work/docs/SESSION-LOG-포레이로.md` | 포레이로 작업 이력 전부 |
| `volcano_work/docs/claude-memory/` | 대화에서 박은 작업 방식 (묻지 말고 계속 · 완성본+업로드 세트 · 한 프리셋만 · 커밋 …) |
| `volcano_work/presets/포레이로/` | 엔진 전체 (prep · tts · align · reframe · build · 검사기들) |
| `volcano_work/presets/_engine/base.py` | spec.py 가 물려받는 바탕값 |
| `volcano_work/scripts/_asr_sm.py` · `_asr_sm_fetch.py` | 전사 |
| `volcano_work/models/yunet.onnx` | 얼굴 검출 (reframe) |
| `volcano_work/LLJtlSPtAMU/sfx/whoosh.wav` | 장면전환음 |
| `volcano_work/fonts/Griun_Cocochoitoon-Rg.ttf` | 제목·대사·효과자막 글꼴 |
| `volcano_work/examples/` | 지난 포레이로 편의 `episode.py` 설계도 · 업로드 세트 예시 |
| `volcano_work/forey_probe/` | 벤치 채널 실측 스크립트·결과 (텍스트만) |
| `volcano_work/bootstrap_포레이로.py` | 환경 점검 |

## 5. 들어 있지 않은 것

- API 키 (보안)
- 소재 영상 · 완성본 영상 · 편 폴더의 미디어 (용량 — 필요하면 따로 옮긴다)
- 다른 채널 프리셋 (포레이로만 담았다)
