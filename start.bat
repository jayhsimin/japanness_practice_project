@echo off
echo 啟動日文學習應用...

REM 檢查是否已在執行
netstat -ano | findstr ":8000 " > nul 2>&1
if %errorlevel%==0 (
    echo 伺服器已在執行，開啟瀏覽器...
    start http://127.0.0.1:8000
    exit /b
)

REM 用 PowerShell 啟動伺服器視窗
powershell -Command "Start-Process cmd -ArgumentList '/k', 'cd /d ""%~dp0backend"" && uvicorn main:app --host 127.0.0.1 --port 8000' -WindowStyle Normal"

REM 等待 port 8000 就緒（最多 20 秒）
echo 等待伺服器啟動中...
set /a count=0
:wait_loop
ping 127.0.0.1 -n 2 > nul
set /a count+=1
netstat -ano | findstr ":8000 " > nul 2>&1
if %errorlevel%==0 goto server_ready
if %count% geq 20 goto timeout_error
echo 等待中... (%count%/20)
goto wait_loop

:server_ready
echo 伺服器已啟動！
start http://127.0.0.1:8000
exit /b

:timeout_error
echo.
echo 錯誤：伺服器啟動失敗（請查看開啟的視窗中的錯誤訊息）
pause
