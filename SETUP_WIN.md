# Setup Guide for Windows

This guide will help you set up the environment and run the transcription workflow on Windows.

## 1. Prerequisites

### Python 3.11
This project requires **Python 3.11**. 
- Download and install it from [python.org](https://www.python.org/downloads/windows/).
- **Important:** During installation, check the box **"Add Python to PATH"**.

### FFmpeg
FFmpeg is required for processing audio files.
1. Download a "gyan.dev" build (e.g., `ffmpeg-git-full.7z`) from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows).
2. Extract the archive (e.g., to `C:\ffmpeg`).
3. Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system **Path** environment variable.

## 2. API Key Configuration

If you plan to use the LLM features (`llm_processor.py`), you need an OpenAI API key.
1. Create a file named `api.key` in the project root directory.
2. Paste your OpenAI API key into this file.

## 3. Running the Workflow

The `full_workflow.cmd` script automates the process, including setting up a virtual environment and installing python dependencies.

1.  **Place your audio files** (`.wav`) in the project directory.
2.  **Run the script**:
    - Double-click `full_workflow.cmd` or run it from Command Prompt/PowerShell:
    ```cmd
    .\full_workflow.cmd
    ```

### Selecting Transcription Method
By default, the script uses `whisper` (Faster-Whisper). You can change this by setting an environment variable before running:
```cmd
set TRANSCRIBE_METHOD=seamless
.\full_workflow.cmd
```
Supported methods: `whisper`, `seamless`. (Note: `whispermlx` is for macOS only).

## Troubleshooting

- **"python is not recognized"**: Ensure Python is installed and the "Add to PATH" option was selected.
- **"ffmpeg is not recognized"**: Ensure the FFmpeg `bin` folder is correctly added to your system Environment Variables.
