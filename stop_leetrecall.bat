@echo off
title Stop LeetRecall AI

echo ==========================================
echo      Stopping LeetRecall AI
echo ==========================================
echo.

taskkill /FI "WINDOWTITLE eq LeetRecall API*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LeetRecall Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LeetRecall AI*" /T /F >nul 2>&1

echo.
echo All LeetRecall AI processes stopped.
echo.

pause