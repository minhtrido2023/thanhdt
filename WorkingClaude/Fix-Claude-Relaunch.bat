@echo off
REM ===================================================================
REM Fix Claude Desktop "file in use" / won't relaunch after update
REM Kills orphan Claude processes + removes stale lockfile
REM Double-click this file when Claude refuses to open
REM ===================================================================

title Fix Claude Relaunch
echo.
echo ====================================================
echo  Fixing Claude Desktop relaunch lock...
echo ====================================================
echo.

echo [1/4] Killing Claude processes...
taskkill /F /IM "Claude.exe" /T >nul 2>&1
taskkill /F /IM "claude.exe" /T >nul 2>&1

REM Kill any Electron helper / Squirrel updater stragglers
taskkill /F /IM "Update.exe" /T >nul 2>&1
taskkill /F /IM "Squirrel.exe" /T >nul 2>&1

echo     done.
echo.

echo [2/4] Waiting for file handles to release...
timeout /t 2 /nobreak >nul

echo [3/4] Removing stale lock files...
if exist "%APPDATA%\Claude\lockfile" (
    del /F /Q "%APPDATA%\Claude\lockfile" >nul 2>&1
    echo     removed lockfile
) else (
    echo     no lockfile present
)

if exist "%APPDATA%\Claude\SingletonLock" (
    del /F /Q "%APPDATA%\Claude\SingletonLock" >nul 2>&1
    echo     removed SingletonLock
)
if exist "%APPDATA%\Claude\SingletonCookie" del /F /Q "%APPDATA%\Claude\SingletonCookie" >nul 2>&1
if exist "%APPDATA%\Claude\SingletonSocket" del /F /Q "%APPDATA%\Claude\SingletonSocket" >nul 2>&1

echo.

echo [4/4] Launching Claude...
REM Common install locations - try in order
set "CLAUDE_EXE="
if exist "%LOCALAPPDATA%\AnthropicClaude\Claude.exe" set "CLAUDE_EXE=%LOCALAPPDATA%\AnthropicClaude\Claude.exe"
if exist "%LOCALAPPDATA%\Programs\Claude\Claude.exe" set "CLAUDE_EXE=%LOCALAPPDATA%\Programs\Claude\Claude.exe"
if exist "%LOCALAPPDATA%\claude\Claude.exe" set "CLAUDE_EXE=%LOCALAPPDATA%\claude\Claude.exe"

if defined CLAUDE_EXE (
    start "" "%CLAUDE_EXE%"
    echo     launched: %CLAUDE_EXE%
) else (
    echo     Claude.exe not found in standard locations.
    echo     Please launch Claude manually from Start Menu.
)

echo.
echo ====================================================
echo  Done. This window will close in 3 seconds.
echo ====================================================
timeout /t 3 /nobreak >nul
exit /b 0
