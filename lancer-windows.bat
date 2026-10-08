@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python n'est pas detecte. Installe Python 3 avec le lanceur py depuis python.org.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import PyQt6" >nul 2>nul
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install PyQt6
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" "patradio\app.py"
if errorlevel 1 goto failed
exit /b 0
:failed
echo Echec de lancement de PatRadio.
pause
exit /b 1
