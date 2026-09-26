# English Express を「チェック → ビルド → GitHub へアップロード」まで一度に行うスクリプト
# 使い方：publish.bat をダブルクリック（または PowerShell で .\publish.bat）
#   .\publish.bat -Message "宇宙のショートを追加"   … 記録のメモを付ける
#   .\publish.bat -Force                            … GitHub 側の中身を手元の内容で上書きする（初回だけ必要なことがある）
param(
    [string]$Message = "",
    [string]$RepoUrl = "https://github.com/closeAI-astra/English_short_learning.git",
    [switch]$Force
)

Set-Location -LiteralPath $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

function Step($text) { Write-Host ""; Write-Host "== $text" -ForegroundColor Cyan }
function Fail($text) { Write-Host ""; Write-Host "!! $text" -ForegroundColor Red; exit 1 }

# ---------- 1. 必要な道具 ----------
Step "1/5 必要な道具の確認"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail "git が見つかりません。https://git-scm.com/ から入れてください。" }
$py = $null
if (Test-Path ".venv\Scripts\python.exe") { $py = @(".venv\Scripts\python.exe") }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $py = @("py", "-3") }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = @("python") }
elseif (Get-Command uv -ErrorAction SilentlyContinue) { $py = @("uv", "run", "python") }
else { Fail "Python が見つかりません。" }
Write-Host "git と Python を確認しました（Python: $($py -join ' ')）"

# ---------- 2. 教材チェック＋ビルド ----------
Step "2/5 教材チェックとビルド"
$pyExe = $py[0]; $pyArgs = @($py | Select-Object -Skip 1) + @("build_site.py")
& $pyExe @pyArgs
if ($LASTEXITCODE -ne 0) { Fail "ビルドが止まりました。上に出ている問題を直してから、もう一度実行してください。" }

if (Get-Command node -ErrorAction SilentlyContinue) {
    foreach ($t in @("test_video.cjs", "test_study.cjs", "test_fluency.cjs")) {
        if (Test-Path $t) {
            node $t
            if ($LASTEXITCODE -ne 0) { Fail "テスト $t が失敗しました。アップロードを中止します。" }
        }
    }
} else {
    Write-Host "（Node.js が無いので自動テストは省略します）"
}

# ---------- 3. git の準備 ----------
Step "3/5 git の準備"
if (-not (Test-Path ".git")) {
    git init | Out-Null
    Write-Host "このフォルダーを git で管理し始めました"
}
git branch -M main 2>$null
if (-not (git config user.name)) {
    $n = Read-Host "GitHub に表示する名前を入力してください"
    git config --global user.name $n
}
if (-not (git config user.email)) {
    Write-Host "メールアドレスは公開されます。GitHub の Settings → Emails にある noreply アドレスがおすすめです。"
    $m = Read-Host "メールアドレスを入力してください"
    git config --global user.email $m
}
$origin = git remote get-url origin 2>$null
if (-not $origin) { git remote add origin $RepoUrl; Write-Host "アップロード先を登録しました: $RepoUrl" }
elseif ($origin -ne $RepoUrl) { git remote set-url origin $RepoUrl; Write-Host "アップロード先を変更しました: $RepoUrl" }

# ---------- 4. 記録（commit） ----------
Step "4/5 変更の記録"
git add -A
$staged = @(git diff --cached --name-only)
$danger = $staged | Where-Object { $_ -match '(^|/)\.venv/|(^|/)results\.csv$|(^|/)\.env|\.(wav|mp3|m4a|webm|ogg)$' }
if ($danger) {
    git reset -q
    Fail ("アップロードしてはいけないファイルが含まれています。.gitignore を確認してください:`n  " + ($danger -join "`n  "))
}
if ($staged.Count -eq 0) {
    Write-Host "前回から変更はありません"
} else {
    if (-not $Message) { $Message = "Update " + (Get-Date -Format "yyyy-MM-dd HH:mm") }
    git commit -q -m $Message
    if ($LASTEXITCODE -ne 0) { Fail "記録（commit）に失敗しました。" }
    Write-Host "$($staged.Count) 個のファイルの変更を記録しました"
}

# ---------- 5. GitHub へ送る ----------
Step "5/5 GitHub へアップロード"
if ($Force) { git push -u origin main --force } else { git push -u origin main }
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "GitHub 側に、手元に無い変更があるため送れませんでした。" -ForegroundColor Yellow
    Write-Host "GitHub 上でファイルを直接編集していなければ、手元の内容で上書きして問題ありません。"
    $ans = Read-Host "GitHub 側を手元の内容で上書きしますか？ (y/N)"
    if ($ans -eq "y") {
        git push -u origin main --force
        if ($LASTEXITCODE -ne 0) { Fail "アップロードに失敗しました。ログインやURLを確認してください。" }
    } else { Fail "アップロードを中止しました。" }
}

$parts = ($RepoUrl -replace '\.git$', '') -split '/'
$site = "https://" + $parts[-2].ToLower() + ".github.io/" + $parts[-1] + "/"
Step "完了"
Write-Host "公開ページ: $($site)（反映まで1〜2分）"
Write-Host "初回だけ：リポジトリの Settings → Pages で Branch を main、フォルダーを /docs にしてください。"
