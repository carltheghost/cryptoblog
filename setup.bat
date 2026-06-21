@echo off
REM One-step setup for kalshibot (Windows). Double-click this file, or run: setup.bat
cd /d "%~dp0"

echo == kalshibot setup ==
echo.

echo [1/3] Installing Python dependencies ...
python -m pip install -r requirements.txt

echo.
echo [2/3] Checking for a local LLM (optional) ...
where ollama >nul 2>nul
if %errorlevel%==0 (
  echo   Ollama is installed. Models you have:
  ollama list
  ollama list | findstr /I hermes >nul && (echo   Hermes detected - the assistant will use it automatically.) || (echo   No Hermes model found. To use Hermes:  ollama pull hermes3)
) else (
  echo   Ollama not installed ^(optional^). Get it at https://ollama.com to enable chat.
  echo   The assistant works fine without it ^(rule-based mode^).
)

echo.
echo [3/3] Running the assistant's self-check ...
python -c "from kalshibot.assistant import Assistant; a=Assistant(); print(a.handle('doctor')[0])"

echo.
echo == Done. Start it with: ==
echo   python -m kalshibot.launch         (EVERYTHING: swarm dashboard + data recording)
echo   python -m kalshibot.assistant      (talk to it; type: doctor)
echo   python -m kalshibot.webui          (just the dashboards /  and  /swarm)
pause
