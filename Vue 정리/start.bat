@echo off
setlocal
cd /d "%~dp0"
if exist "%ProgramFiles%\nodejs\node.exe" set "PATH=%ProgramFiles%\nodejs;%PATH%"
set "NODE=node"
set "NPM=npm.cmd"
if exist "%ProgramFiles%\nodejs\node.exe" set "NODE=%ProgramFiles%\nodejs\node.exe"
if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM=%ProgramFiles%\nodejs\npm.cmd"
if not exist "node_modules" (
  echo Installing project dependencies...
  call "%NPM%" install
  if errorlevel 1 goto error
)
"%NODE%" scripts\prepare-data.mjs
if errorlevel 1 goto error
echo Starting safe_nav at http://localhost:5173
start "" http://localhost:5173
call "%NPM%" run dev
exit /b 0
:error
echo safe_nav could not start.
pause
exit /b 1
