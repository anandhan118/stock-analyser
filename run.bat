@echo off
echo.
echo  ================================================
echo   EDGE SCANNER - NSE Swing Trading System
echo  ================================================
echo.
echo  Starting app... browser will open automatically.
echo  Press Ctrl+C to stop the app.
echo.

:: %~dp0 = the folder this .bat file lives in (always, on any machine)
cd /d "%~dp0"

:: Try 'streamlit' from PATH first (works if installed globally or venv is activated)
where streamlit >nul 2>&1
if %errorlevel% == 0 (
    streamlit run edge_scanner.py
    goto end
)

:: Fallback: search common venv locations inside this folder
for %%V in (
    ".venv\Scripts\streamlit.exe"
    "venv\Scripts\streamlit.exe"
    "env\Scripts\streamlit.exe"
) do (
    if exist "%~dp0%%V" (
        "%~dp0%%V" run edge_scanner.py
        goto end
    )
)

:: Nothing found — give a helpful message
echo.
echo  ERROR: streamlit not found.
echo  Fix options:
echo    1. Run:  pip install streamlit
echo    2. Or activate your venv first, then run this bat file.
echo.
pause
:end
pause
