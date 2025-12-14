@echo off
setlocal

rem The GEMINI_TEMP_DIR environment variable is provided by the agent's environment.
rem We don't need to set it here.
if "%GEMINI_TEMP_DIR%" == "" (
    set "GEMINI_TEMP_DIR=%~dp0\TEMP"
)
if not exist "%GEMINI_TEMP_DIR%" (
    mkdir "%GEMINI_TEMP_DIR%"
)

rem Step 1: Download YouTube HTML
echo Downloading YouTube page...
rem The -L flag is added to follow redirects
curl.exe -s -L "https://www.youtube.com/acvyskov/live" -o "%GEMINI_TEMP_DIR%\youtube.html"

if %errorlevel% neq 0 (
    echo Error: Failed to download YouTube HTML.
    goto :eof
)

rem Step 2: Extract video information
echo Extracting video information...
python extract_yt_data.py

if %errorlevel% neq 0 (
    echo Error: Failed to extract video data.
    goto :eof
)

rem Check if video_info.json was created
if not exist "%GEMINI_TEMP_DIR%\video_info.json" (
    echo Error: video_info.json was not created.
    goto :eof
)

rem Step 3 & 4: Transcribe audio and convert to RTF for all .m4a files
for %%f in (*.wav) do (
    echo Processing "%%f"...
    
    rem Transcribe if txt does not exist
    if not exist "%%~nf.txt" (
        echo Transcribing "%%f"...
        python transcribe_seamless.py "%%f"
        if errorlevel 1 (
            echo Error: Audio transcription failed for "%%f".
        )
    ) else (
        echo "%%~nf.txt" already exists. Skipping transcription.
    )

    rem Convert to RTF
    if exist "%%~nf.txt" (
        echo Converting "%%~nf.txt" to RTF...
        python convert_to_rtf.py "%%~nf.txt" "%%~nf.rtf"
        if errorlevel 1 (
            echo Error: RTF conversion failed for "%%~nf.txt".
        )
    )
)

echo Workflow completed successfully.

rem Clean up temporary files
echo Cleaning up temporary files...
rmdir /S /Q "%GEMINI_TEMP_DIR%" 2>NUL

endlocal