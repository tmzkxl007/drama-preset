# 포레이로 프리셋

드라마·영화 장면을 **나레이션으로 끌고 가는** 세로 숏폼 제작 프리셋.
유튜브 @포레이로 · 토메이로 실측 규격과, 2026-09-05 ~ 09-15 사이 제작하며 박은 규칙이 전부 들어 있다.

> 비공개 저장소. **API 키 · 소재 영상 · 완성본은 들어 있지 않다.**

## 다른 PC 에서 쓰기

```powershell
git clone https://github.com/jihyunok/forey-preset.git
cd forey-preset
.\설치.bat
```

`설치.bat` 이 Python 3.12 · ffmpeg · 전용 venv · 글꼴(그리운 코코초이툰)을 깔고,
`volcano_work` 를 `%USERPROFILE%\volcano_work` 에 놓은 뒤 API 키(typecast · speechmatics · gemini)를 묻고 점검표를 찍는다.
그다음 Claude Code 를 `%USERPROFILE%\volcano_work` 에서 열고 **「포레이로프리셋 불러와」**.

자세한 설치 안내와 들어 있는 것 목록은 [`START-HERE.md`](START-HERE.md).

## 구성

| 위치 | 무엇 |
|---|---|
| `volcano_work/CLAUDE.md` | Claude 가 제일 먼저 읽는 안내 (읽는 순서 · 절차 · 최상위 규칙) |
| `volcano_work/docs/포레이로-지침서.md` | 사용자가 못 박은 것 전부 |
| `volcano_work/docs/포레이로-지침서-부록.md` | 지침서 뒤(09-09~09-15)에 박힌 것 — 숫자가 다르면 이쪽이 이긴다 |
| `volcano_work/docs/PLAYBOOK-포레이로.md` | 실측값·함정 전량 (§8 · §10 · §16 · §17) |
| `volcano_work/docs/SESSION-LOG-포레이로.md` | 작업 이력 |
| `volcano_work/docs/claude-memory/` | 대화에서 박은 작업 방식 |
| `volcano_work/presets/포레이로/` | 엔진 (prep · tts · align · reframe · build · 검사기) |
| `volcano_work/examples/` | 지난 편 설계도 `episode.py` · 업로드 세트 |
| `install.ps1` · `설치.bat` · `requirements.txt` | 설치 |

## 고치고 올리기

규칙이나 코드를 고쳤으면 원본 작업 폴더(`volcano_work`)에서 이식팩을 다시 만들고 이 저장소에 반영해 커밋한다.

```
python volcano_work/scripts/forey_pack/build_pack.py
```
