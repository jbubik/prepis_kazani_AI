# Setup Guide for macOS (OSX)

This project was originally designed for Windows. To run it on macOS, follow these steps to set up your environment.

## 1. Install Prerequisites

You will need **Homebrew**, a package manager for macOS, to install necessary tools. If you don't have it, install it from [brew.sh](https://brew.sh).

Open your Terminal and run the following commands:

### System Tools
Install Python and FFmpeg (required for audio processing).

```bash
brew install python ffmpeg curl
```

### Python Dependencies
Install the required Python libraries.

```bash
pip3 install whisper-ctranslate2 openai
```

*(Note: If you are using a virtual environment, activate it before running pip install.)*

## 2. API Key Configuration

Ensure you have your OpenAI API key saved in a file named `api.key` in the project root directory.

```bash
echo "your-api-key-here" > api.key
```

## 3. Running the Workflow

I have created a shell script `full_workflow.sh` which is the equivalent of the Windows `full_workflow.cmd`.

1.  **Make the script executable** (you only need to do this once):
    ```bash
    chmod +x full_workflow.sh
    ```

2.  **Run the script**:
    ```bash
    ./full_workflow.sh
    ```

## Troubleshooting

*   **"command not found: whisper-ctranslate2"**: Ensure your Python bin directory is in your system PATH. You can often fix this by adding `export PATH="$HOME/Library/Python/3.9/bin:$PATH"` (adjust version number) to your `~/.zshrc` or `~/.bash_profile`.
*   **Permission denied**: Make sure you ran `chmod +x full_workflow.sh`.
