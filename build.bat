@echo off
echo 正在建置前端（首次使用前請先執行一次）...
cd /d "%~dp0jp-front"
call npm run build
echo.
echo 建置完成！可以執行 start.bat 啟動應用程式。
pause
