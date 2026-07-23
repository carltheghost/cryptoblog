@echo off
REM Double-click to play Wizard's Chess on localhost.
cd /d "%~dp0"
echo Starting Wizard's Chess...
python serve.py
pause
