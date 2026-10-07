@echo off
title LeetRecall AI Launcher

cd /d "%~dp0"

echo ==========================================
echo Starting LeetRecall AI (React + Express)
echo ==========================================
echo.

echo Starting frontend and backend together...
start "LeetRecall API" cmd /k "npm run server"
start "LeetRecall Frontend" cmd /k "npm run client"

echo.
echo Done.
echo Open: http://localhost:5173
echo API: http://localhost:5000/api/health
echo.
pause