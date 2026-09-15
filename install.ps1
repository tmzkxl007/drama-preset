param([string]$Target = "$HOME\volcano_work")
# 포레이로 프리셋 이식팩 설치 — Windows PowerShell 5.1
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = Join-Path $Here "volcano_work"

function Say($m) { Write-Host "== $m" -ForegroundColor Cyan }
function Has($n) { [bool](Get-Command $n -ErrorAction SilentlyContinue) }
function RefreshPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}

Say "설치 위치: $Target"

# ── 1. 도구 ────────────────────────────────────────────
Say "ffmpeg"
if (-not (Has ffmpeg)) {
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    RefreshPath
    if (-not (Has ffmpeg)) { Write-Host "  ffmpeg 을 깔았지만 이 창에서는 아직 안 보인다. 창을 새로 열고 설치.bat 을 한 번 더 돌려라." -ForegroundColor Yellow }
} else { Write-Host "  있다" }

Say "전용 파이썬 (~/.volcano/venv)"
$Venv = Join-Path $HOME ".volcano\venv"
$Py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $Py)) {
    $base = $null
    foreach ($c in @("$env:LOCALAPPDATA\Programs\Python\Python312\python.exe", "C:\Program Files\Python312\python.exe")) {
        if (Test-Path $c) { $base = $c; break }
    }
    if (-not $base) {
        winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
        $base = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    }
    if (-not (Test-Path $base)) { throw "Python 3.12 를 찾지 못했다: $base" }
    & $base -m venv $Venv
}
& $Py -m pip install --upgrade pip --quiet
& $Py -m pip install -r (Join-Path $Here "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "pip 설치 실패" }

# ── 2. 파일 놓기 ───────────────────────────────────────
Say "파일 복사"
New-Item -ItemType Directory -Force $Target | Out-Null
$Preset = Join-Path $Target "presets\포레이로"
if (Test-Path $Preset) {
    $bak = $Preset + ".bak-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Move-Item $Preset $bak
    Write-Host "  기존 presets\포레이로 → $bak"
}
$keep = @("CLAUDE.md", "presets\_engine\base.py")
Get-ChildItem $Src -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($Src.Length + 1)
    $dst = Join-Path $Target $rel
    if ((Test-Path $dst) -and ($keep -contains $rel)) {
        if ($rel -eq "CLAUDE.md") {
            $dst = Join-Path $Target "CLAUDE-포레이로.md"
            Write-Host "  CLAUDE.md 가 이미 있어 CLAUDE-포레이로.md 로 둔다 (기존 CLAUDE.md 에서 이 파일을 가리키게 해라)"
        } else { return }
    }
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    Copy-Item $_.FullName $dst -Force
}

# ── 3. 글꼴 ────────────────────────────────────────────
Say "글꼴 (그리운 코코초이툰)"
$fontName = "Griun_Cocochoitoon-Rg.ttf"
$userFonts = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force $userFonts | Out-Null
$fontDst = Join-Path $userFonts $fontName
if (-not (Test-Path $fontDst)) {
    Copy-Item (Join-Path $Src "fonts\$fontName") $fontDst
    New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts" `
        -Name "Griun Cocochoitoon Regular (TrueType)" -Value $fontDst -PropertyType String -Force | Out-Null
    Write-Host "  설치했다"
} else { Write-Host "  이미 있다" }

# ── 4. API 키 ──────────────────────────────────────────
Say "API 키 (~/.volcano/keys) — 비우고 엔터면 건너뛴다"
$Keys = Join-Path $HOME ".volcano\keys"
New-Item -ItemType Directory -Force $Keys | Out-Null
foreach ($k in @(@("typecast", "나레 목소리 · 필수"), @("speechmatics", "대사 전사 · 필수"), @("gemini", "시대극 두 번째 귀 · 선택"))) {
    $p = Join-Path $Keys $k[0]
    if (Test-Path $p) { Write-Host "  $($k[0]) 이미 있다"; continue }
    $v = Read-Host "  $($k[0]) 키 ($($k[1]))"
    if ($v -and $v.Trim()) {
        [IO.File]::WriteAllText($p, $v.Trim())     # 값만, BOM·줄바꿈 없이
        Write-Host "  저장했다"
    }
}

# ── 5. 점검 ────────────────────────────────────────────
Say "점검"
& $Py (Join-Path $Target "bootstrap_포레이로.py")
Write-Host ""
Write-Host "끝. Claude Code 를 $Target 에서 열고 「포레이로프리셋 불러와」 라고 하면 된다." -ForegroundColor Green
