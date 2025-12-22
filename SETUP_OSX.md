# Setup Guide for macOS (OSX)

To run this project on macOS, follow these steps to set up your environment.

## 1. Install Prerequisites

You will need **Homebrew**, a package manager for macOS. If you don't have it, install it from [brew.sh](https://brew.sh).

Open your Terminal and run the following command to install Python 3.12 (required), FFmpeg (required for audio), and curl:

```bash
brew install python@3.12 ffmpeg curl
```

Ensure `python3.12` is in your PATH.

## 2. API Key Configuration

If you plan to use the LLM features (`llm_processor.py`), ensure you have your OpenAI API key saved in a file named `api.key` in the project root directory.

```bash
echo "your-api-key-here" > api.key
```

## 3. Running the Workflow

The `full_workflow.sh` script automates the process, including setting up a virtual environment and installing python dependencies.

1.  **Make the script executable** (only needed once):
    ```bash
    chmod +x full_workflow.sh
    ```

2.  **Run the script**:
    ```bash
    ./full_workflow.sh
    ```

    By default, it uses `whispermlx` (optimized for Apple Silicon). To use other methods:
    ```bash
    TRANSCRIBE_METHOD=whisper ./full_workflow.sh
    # or
    TRANSCRIBE_METHOD=seamless ./full_workflow.sh
    ```

