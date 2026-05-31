@echo off
chcp 65001 > nul
cd /d "%~dp0"
set PATH=C:\Program Files\Git\cmd;%PATH%


echo ============================
echo  YouTube Insight 실행 중...
echo ============================

python main.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 실행 실패. 확인 후 다시 시도해주세요.
    pause
    exit /b 1
)

echo.
echo [완료] 결과 GitHub에 업로드 중...
git add output/ data/
git diff --cached --quiet && (
    echo 새 영상 없음 - 업로드 생략
) || (
    git commit -m "update: %date% %time%"
    git push
    echo 업로드 완료!
)

echo.
pause
