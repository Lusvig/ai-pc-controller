@echo off
TITLE AI PC Controller - Installer
COLOR 0A
setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo     AI PC CONTROLLER - AUTOMATIC INSTALLER v2.0
echo ============================================================
echo.

:: Create log file
set "LOGFILE=%TEMP%\ai_pc_controller_install.log"
echo Installation started at %DATE% %TIME% > "%LOGFILE%"

:: ============================================
:: STEP 1: Check Administrator Privileges
:: ============================================
echo [Step 1/6] Checking permissions...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo    [!] Warning: Not running as Administrator
    echo    [!] Some features may not install correctly
    echo.
) else (
    echo    [OK] Running with Administrator privileges
)
echo.

:: ============================================
:: STEP 2: Check Python Installation
:: ============================================
echo [Step 2/6] Checking Python installation...

where python >nul 2>&1
if %errorLevel% neq 0 (
    echo    [X] Python is not installed!
    echo.
    echo    Please download and install Python from: https://python.org
    echo    Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
    echo    [OK] Python !PYVER! is installed
)
echo.

:: ============================================
:: STEP 3: Create Virtual Environment
:: ============================================
echo [Step 3/6] Setting up Python virtual environment...

if not exist "venv\Scripts\activate.bat" (
    python -m venv venv 2>>"%LOGFILE%"
    if %errorLevel% neq 0 (
        echo    [X] Failed to create virtual environment
        echo    Error logged to: %LOGFILE%
        pause
        exit /b 1
    )
    echo    [OK] Virtual environment created
) else (
    echo    [OK] Virtual environment exists
)

:: Activate virtual environment
call venv\Scripts\activate.bat
echo    [OK] Virtual environment activated
echo.

:: ============================================
:: STEP 4: Install Python Dependencies
:: ============================================
echo [Step 4/6] Installing Python packages...
echo    This may take several minutes, please wait...
echo.

:: Upgrade pip first
python -m pip install --upgrade pip --quiet 2>>"%LOGFILE%"

:: Install from requirements.txt
pip install -r requirements.txt 2>>"%LOGFILE%"

if %errorLevel% neq 0 (
    echo    [!] Some packages may have failed to install
    echo    Check the log file: %LOGFILE%
) else (
    echo    [OK] Python packages installed
)
echo.

:: ============================================
:: STEP 5: Install Ollama
:: ============================================
echo [Step 5/6] Setting up Ollama ^(Local AI^)...
echo.

where ollama >nul 2>&1
if %errorLevel% neq 0 (
    echo    Ollama is not installed.
    echo.
    echo    Downloading Ollama installer...
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'}" 2>>"%LOGFILE%"
    
    if exist "%TEMP%\OllamaSetup.exe" (
        echo    Installing Ollama...
        echo    ^(A setup window may appear - please complete the installation^)
        start /wait "" "%TEMP%\OllamaSetup.exe"
        del "%TEMP%\OllamaSetup.exe"
        
        :: Wait for installation to complete
        timeout /t 5 /nobreak >nul
        
        :: Refresh PATH
        set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
        
        echo    [OK] Ollama installed
    ) else (
        echo    [X] Failed to download Ollama
        echo    Please install manually from: https://ollama.com/download
    )
) else (
    echo    [OK] Ollama is already installed
)
echo.

:: ============================================
:: STEP 6: Download AI Model
:: ============================================
echo [Step 6/6] Setting up AI model...
echo.

:: Start Ollama service if not running
echo    Starting Ollama service...
start /B ollama serve >nul 2>&1
timeout /t 5 /nobreak >nul

:: Check if model exists
ollama list 2>nul | findstr /i "llama3.2" >nul
if %errorLevel% neq 0 (
    echo    Downloading AI model ^(llama3.2:1b^)...
    echo    This is approximately 1.3GB and may take several minutes.
    echo.
    
    ollama pull llama3.2:1b
    
    if !errorLevel! equ 0 (
        echo.
        echo    [OK] AI model downloaded successfully
    ) else (
        echo.
        echo    [!] Model download may have failed
        echo    [!] You can try manually: ollama pull llama3.2:1b
    )
) else (
    echo    [OK] AI model already available
)
echo.

:: ============================================
:: INSTALLATION COMPLETE
:: ============================================
echo.
echo ============================================================
echo     INSTALLATION COMPLETE!
echo ============================================================
echo.
echo   NEXT STEPS:
echo   -----------
echo   1. Run the application with: python -m src.main
echo   2. Or use the run.bat script
echo.
echo   TROUBLESHOOTING:
echo   ----------------
echo   If you get AI errors, run these commands:
echo     ollama serve        ^(start the AI service^)
echo     ollama pull llama3.2:1b   ^(download the AI model^)
echo.
echo   Log file: %LOGFILE%
echo.
echo ============================================================
echo.
pause

endlocal
