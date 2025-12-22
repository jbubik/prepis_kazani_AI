# Directory Overview

This directory is a workspace for a speech-to-text transcription task. The primary goal is to transcribe audio files and produce formatted RTF documents as the final output, including metadata from a YouTube video.

# Key Files

*   `*.wav`: The source audio files to be transcribed. These contain speech that can be processed for transcription.
*   `*.txt`: The raw text transcription of the audio files. This is the direct output from the speech-to-text tool.
*   `*.rtf`: The final, formatted Rich Text Format document. This is generated from the `.txt` file and includes YouTube video metadata.
*   `convert_to_rtf.py`: A Python script that reads the raw transcription from the text file and converts it into the formatted RTF document. It reads video metadata from `video_info.json` to prepend formatted information. It handles file locking issues by writing to a temporary file before moving it to the final destination.
*   `extract_yt_data.py`: A Python script that fetches the YouTube channel page, extracts the latest video's title, preacher, place, and date, and saves this information to `video_info.json`.
*   `video_info.json`: (Temporary file) Stores the extracted video metadata from YouTube.
*   `youtube.html`: (Temporary file) Stores the downloaded HTML content from the YouTube channel page.
*   `full_workflow.cmd` / `full_workflow.sh`: Batch/Bash scripts that orchestrate the entire process, from fetching YouTube data to generating the final RTF for all `.wav` files.
*   `transcribe_whisper.py`: A Python script that uses the `faster-whisper` library to transcribe audio files (default method).
*   `transcribe_whispermlx.py`: A Python script that uses the `mlx-whisper` library (optimized for Apple Silicon).
*   `transcribe_seamless.py`: A Python script that uses Facebook's Seamless M4T model for transcription.
*   `llm_processor.py`: A Python script for processing text using an LLM (requires OpenAI API key).
*   `README.md`: Main project overview and entry point.
*   `SETUP_OSX.md`: Setup instructions for macOS users.
*   `SETUP_WIN.md`: Setup instructions for Windows users.

# Usage

The workflow for this directory involves a multi-step process, fully automated by `full_workflow.cmd`:

1.  **Run the full workflow script:**
    ```sh
    .\full_workflow.cmd
    ```

This script will perform the following actions:

*   Download the YouTube channel page to a temporary directory.
*   Extract the latest video's title, preacher, event place, and date from the HTML and save it to `video_info.json`.
*   Iterate through all `*.wav` files in the directory.
*   Transcribe each `*.wav` file into a `.txt` file using the selected transcription script (default is `transcribe_whisper.py`).
    *   Example command (when using whisper): `python transcribe_whisper.py <filename>.wav`
*   Convert each `.txt` file to an `.rtf` file, prepending the extracted video metadata (sermon title as Header1, preacher as Header2, date and place as Normal text).
*   Clean up temporary files.