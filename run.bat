@echo off
REM Double-click this file to run EVERYTHING (dashboard + data recording).
REM %~dp0 = the folder this .bat lives in, so it always finds the project.
cd /d "%~dp0"
echo Starting kalshibot from %cd%
echo.
git pull
python -m kalshibot.launch
pause
