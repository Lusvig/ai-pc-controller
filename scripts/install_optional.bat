@echo off
TITLE AI PC Controller - Install Optional Packages
COLOR 0E

echo.
echo ============================================================
echo     OPTIONAL PACKAGES INSTALLER
echo ============================================================
echo.
echo These packages provide extra features but require either:
echo  - Microsoft Visual C++ Build Tools, OR
echo  - Pre-compiled wheel files
echo.
echo ============================================================
echo.

cd /d "%~dp0.."
call venv\Scripts\activate.bat

echo [1/3] Attempting to install PyAudio...
echo.

:: Try normal install first
pip install pyaudio 2>nul
if %errorlevel% equ 0 (
    echo    [OK] PyAudio installed successfully!
    goto :pyaudio_done
)

:: Try pipwin
echo    Regular install failed, trying pipwin method...
pip install pipwin 2>nul
pipwin install pyaudio 2>nul
if %errorlevel% equ 0 (
    echo    [OK] PyAudio installed via pipwin!
    goto :pyaudio_done
)

echo    [!] PyAudio could not be installed automatically.
echo    [!] Voice input will still work via SpeechRecognition.
echo.
echo    To install manually:
echo    1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo    2. Download the wheel for your Python version
echo    3. Run: pip install [downloaded_file].whl
echo.

:pyaudio_done
echo.

echo [2/3] Checking for other optional packages...
echo.

:: These are less critical
echo    Skipping webrtcvad (not critical for voice functionality)
echo    Skipping netifaces (replaced with pure Python solution)
echo.

echo [3/3] Installation complete!
echo.

echo ============================================================
echo     DONE!
echo ============================================================
echo.
pause