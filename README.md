# Přepis kázání AI (Sermon Transcription AI)

An automated workflow for transcribing audio files (sermons) into formatted RTF documents, enriched with metadata extracted from YouTube channel.

## Overview

This project automates the transition from raw audio to a polished transcription document. It handles:
1.  **Metadata Extraction:** Automatically fetches the latest sermon details (title, preacher, date, location) from the church's YouTube channel.
2.  **AI Transcription:** Converts `.wav` files to text using state-of-the-art AI models (Faster-Whisper, Seamless M4T, or MLX-Whisper).
3.  **RTF Formatting:** Produces a Rich Text Format (`.rtf`) document with standardized headers and formatting, ready for distribution or archiving.

## Key Features

- **Multiple Transcription Engines:**
  - `whisper` (Faster-Whisper): High-performance, general-purpose transcription (Default).
  - `whispermlx`: Optimized specifically for Apple Silicon (Mac M1/M2/M3).
  - `seamless`: Uses Facebook's Seamless M4T for robust multilingual support.
- **Automated Metadata:** No manual entry for sermon titles or dates.
- **Cross-Platform:** Full support for Windows (`.cmd`) and macOS/Linux (`.sh`).
- **Batch Processing:** Processes all `.wav` files in the directory in one go (but YouTube metadata apply to all of them).

## Quick Start

### 1. Setup
Detailed setup instructions are available for your operating system:
- **Windows:** See [SETUP_WIN.md](SETUP_WIN.md)
- **macOS:** See [SETUP_OSX.md](SETUP_OSX.md)

### 2. Usage
1.  Place your `.wav` file in the root directory of this project.
2.  Run the workflow:
    - **Windows:** Double-click `full_workflow.cmd`
    - **macOS/Linux:** Run `./full_workflow.sh`

### 3. Configuration
You can switch transcription methods by setting the `TRANSCRIBE_METHOD` environment variable:
- `whisper` (Default on Windows)
- `whispermlx` (Default on macOS)
- `seamless`

## File Structure

- `full_workflow.cmd/sh`: Orchestration scripts.
- `transcribe_whisper.py`: Core transcription logic using `faster-whisper`.
- `extract_yt_data.py`: Scrapes metadata from YouTube.
- `convert_to_rtf.py`: Handles document generation and formatting.
- `llm_processor.py`: (Optional) Post-processing using OpenAI's GPT models.

## Requirements

- Python 3.11 (Windows) or 3.12 (macOS)
- FFmpeg (for audio processing)
- Active internet connection (for YouTube metadata and model downloading)
