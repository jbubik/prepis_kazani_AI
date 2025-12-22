@echo off
setlocal

echo Workflow started at: %DATE% %TIME%

set "TEMP_BASE=%TEMP%"
rem Remove trailing backslash if present
if "%TEMP_BASE:~-1%"=="\" set "TEMP_BASE=%TEMP_BASE:~0,-1%"
set "VENV_DIR=%TEMP_BASE%\venv_prepis_kazani_AI"
set "TEMP_BASE=%TEMP_BASE%\temp_prepis_kazani_AI"
if not exist "%TEMP_BASE%" (
    mkdir "%TEMP_BASE%"
)

rem Transcription method configuration
rem Possible values: "seamless", "whispermlx", "whisper"
rem Default: "whisper"
if "%TRANSCRIBE_METHOD%" == "" (
    set "TRANSCRIBE_METHOD=whisper"
)

rem Validate TRANSCRIBE_METHOD
if not "%TRANSCRIBE_METHOD%" == "whispermlx" (
    if not "%TRANSCRIBE_METHOD%" == "seamless" (
        if not "%TRANSCRIBE_METHOD%" == "whisper" (
            echo Error: Invalid TRANSCRIBE_METHOD '%TRANSCRIBE_METHOD%'. Must be 'whispermlx', 'seamless', or 'whisper'.
            goto :eof
        )
    )
)

echo Transcription method: %TRANSCRIBE_METHOD%
echo Using temporary directory: "%TEMP_BASE%"

rem --- PYTHON VERSION CHECK ---
python -c "import sys; exit(0 if sys.version_info[:2] == (3, 11) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3.11 is required.
    python --version
    goto :eof
)

rem --- VENV SETUP ---
if "%VIRTUAL_ENV%"=="" (
    if not exist "%VENV_DIR%" (
        echo Creating virtual environment in "%VENV_DIR%"...
        python -m venv "%VENV_DIR%"
        if errorlevel 1 (
            echo Error: Failed to create virtual environment.
            echo Please ensure Python is installed and in your PATH.
            goto :eof
        )
    )
    set "PYTHON_EXEC=%VENV_DIR%\Scripts\python.exe"
    set "PIP_EXEC=%VENV_DIR%\Scripts\pip.exe"
) else (
    echo Using active virtual environment: %VIRTUAL_ENV%
    set "PYTHON_EXEC=python"
    set "PIP_EXEC=pip"
)

rem --- INSTALL DEPENDENCIES ---

rem Transcription specific dependencies
if "%TRANSCRIBE_METHOD%" == "seamless" (
    rem Check for transformers (used by transcribe_seamless.py)
    "%PYTHON_EXEC%" -c "import transformers" >NUL 2>&1
    if errorlevel 1 (
        echo Installing transformers and related dependencies...
        "%PIP_EXEC%" install transformers torch sentencepiece accelerate protobuf
        if errorlevel 1 (
             echo Error: Failed to install dependencies.
             goto :eof
        )
    )
) else if "%TRANSCRIBE_METHOD%" == "whispermlx" (
    rem Check for mlx_whisper (used by transcribe_whispermlx.py)
    "%PYTHON_EXEC%" -c "import mlx_whisper" >NUL 2>&1
    if errorlevel 1 (
        echo Installing mlx_whisper...
        "%PIP_EXEC%" install mlx_whisper
        if errorlevel 1 (
             echo Error: Failed to install mlx_whisper.
             goto :eof
        )
    )
) else if "%TRANSCRIBE_METHOD%" == "whisper" (
    rem Check for faster-whisper (used by transcribe_whisper.py)
    "%PYTHON_EXEC%" -c "import faster_whisper" >NUL 2>&1
    if errorlevel 1 (
        echo Installing faster-whisper...
        "%PIP_EXEC%" install faster-whisper
        if errorlevel 1 (
             echo Error: Failed to install faster-whisper.
             goto :eof
        )
    )
)

rem Check for openai (used by llm_processor.py)
"%PYTHON_EXEC%" -c "import openai" >NUL 2>&1
if errorlevel 1 (
    echo Installing openai...
    "%PIP_EXEC%" install openai
    if errorlevel 1 (
         echo Error: Failed to install openai.
         goto :eof
    )
)

rem Determine transcription script
if "%TRANSCRIBE_METHOD%" == "seamless" (
    set "TRANSCRIBE_SCRIPT=transcribe_seamless.py"
) else if "%TRANSCRIBE_METHOD%" == "whispermlx" (
    set "TRANSCRIBE_SCRIPT=transcribe_whispermlx.py"
) else if "%TRANSCRIBE_METHOD%" == "whisper" (
    set "TRANSCRIBE_SCRIPT=transcribe_whisper.py"
)

rem Step 1: Download YouTube HTML
echo Downloading YouTube page...
rem The -L flag is added to follow redirects
curl.exe -s -L "https://www.youtube.com/acvyskov/live" -o "%TEMP_BASE%\youtube.html"

if %errorlevel% neq 0 (
    echo Error: Failed to download YouTube HTML.
    goto :eof
)

rem Step 2: Extract video information
echo Extracting video information...
"%PYTHON_EXEC%" extract_yt_data.py

if %errorlevel% neq 0 (
    echo Error: Failed to extract video data.
    goto :eof
)

rem Check if video_info.json was created
if not exist "%TEMP_BASE%\video_info.json" (
    echo Error: video_info.json was not created.
    goto :eof
)

rem Step 3 & 4: Transcribe audio and convert to RTF for all .wav files
for %%f in (*.wav) do (
    echo Processing "%%f"...
    
    rem Transcribe if txt does not exist
    if not exist "%%~nf.txt" (
        echo Transcribing "%%f"...
        "%PYTHON_EXEC%" "%TRANSCRIBE_SCRIPT%" "%%f"
        if errorlevel 1 (
            echo Error: Audio transcription failed for "%%f".
        )
    ) else (
        echo "%%~nf.txt" already exists. Skipping transcription.
    )

    rem Convert to RTF
    if exist "%%~nf.txt" (
        echo Converting "%%~nf.txt" to RTF...
        "%PYTHON_EXEC%" convert_to_rtf.py "%%~nf.txt" "%%~nf.rtf"
        if errorlevel 1 (
            echo Error: RTF conversion failed for "%%~nf.txt".
        )
    )
)

echo Workflow completed successfully.

rem Clean up temporary files
echo Cleaning up temporary files...
rmdir /S /Q "%TEMP_BASE%" 2>NUL

echo Workflow finished at: %DATE% %TIME%

endlocal
