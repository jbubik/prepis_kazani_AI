#!/bin/bash

# Start timer
start_time=$(date +%s)
echo "Workflow started at: $(date)"

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR" || exit
TEMP_BASE="${TMPDIR:-${TMP:-/tmp}}"
TEMP_BASE="${TEMP_BASE%/}"
VENV_DIR="$TEMP_BASE/venv_prepis_kazani_AI"
TEMP_BASE="$TEMP_BASE/temp_prepis_kazani_AI"

export TEMP_BASE="$TEMP_BASE"
echo "Using temporary directory: $TEMP_BASE"

PYTHON_CMD="python3.12"

# Transcription method configuration
# Possible values: "seamless", "whispermlx", "whisper"
# Default: "whispermlx"
TRANSCRIBE_METHOD="${TRANSCRIBE_METHOD:-whispermlx}"

# Validate TRANSCRIBE_METHOD
if [[ "$TRANSCRIBE_METHOD" != "whispermlx" && "$TRANSCRIBE_METHOD" != "seamless" && "$TRANSCRIBE_METHOD" != "whisper" ]]; then
    echo "Error: Invalid TRANSCRIBE_METHOD '$TRANSCRIBE_METHOD'. Must be 'whispermlx', 'seamless', or 'whisper'."
    exit 1
fi

echo "Transcription method: $TRANSCRIBE_METHOD"

# --- VENV SETUP ---

# Check if we are already in a venv (optional, but good practice)
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in $VENV_DIR..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
    
    # Use the venv python and pip
    PYTHON_EXEC="$VENV_DIR/bin/python3"
    PIP_EXEC="$VENV_DIR/bin/pip"
else
    echo "Using active virtual environment: $VIRTUAL_ENV"
    PYTHON_EXEC="python3"
    PIP_EXEC="pip"
fi

# Install dependencies if needed

# Transcription specific dependencies
if [ "$TRANSCRIBE_METHOD" = "seamless" ]; then
    # Check for transformers (used by transcribe_seamless.py)
    if ! "$PYTHON_EXEC" -c "import transformers" 2>/dev/null;
 then
        echo "Installing transformers and related dependencies..."
        "$PIP_EXEC" install transformers torch sentencepiece accelerate protobuf
    fi
elif [ "$TRANSCRIBE_METHOD" = "whispermlx" ]; then
    # Check for mlx_whisper (used by transcribe_whispermlx.py)
    if ! "$PYTHON_EXEC" -c "import mlx_whisper" 2>/dev/null;
 then
        echo "Installing mlx_whisper..."
        "$PIP_EXEC" install mlx_whisper
    fi
elif [ "$TRANSCRIBE_METHOD" = "whisper" ]; then
    # Check for faster-whisper (used by transcribe_whisper.py)
    if ! "$PYTHON_EXEC" -c "import faster_whisper" 2>/dev/null;
 then
        echo "Installing faster-whisper..."
        "$PIP_EXEC" install faster-whisper
    fi
fi

# Check for openai (used by llm_processor.py)
if ! "$PYTHON_EXEC" -c "import openai" 2>/dev/null;
 then
    echo "Installing openai..."
    "$PIP_EXEC" install openai
fi
# ------------------

# Determine transcription script
if [ "$TRANSCRIBE_METHOD" = "seamless" ]; then
    TRANSCRIBE_SCRIPT="transcribe_seamless.py"
elif [ "$TRANSCRIBE_METHOD" = "whispermlx" ]; then
    TRANSCRIBE_SCRIPT="transcribe_whispermlx.py"
elif [ "$TRANSCRIBE_METHOD" = "whisper" ]; then
    TRANSCRIBE_SCRIPT="transcribe_whisper.py"
fi

# Step 1: Download YouTube HTML
echo "Downloading YouTube page..."
# -s: Silent mode, -L: Follow redirects
if ! curl -s -L "https://www.youtube.com/acvyskov/live" -o "$TEMP_BASE/youtube.html"; then
    echo "Error: Failed to download YouTube HTML."
    exit 1
fi

# Step 2: Extract video information
echo "Extracting video information..."
if ! "$PYTHON_EXEC" extract_yt_data.py; then
    echo "Error: Failed to extract video data."
    exit 1
fi

# Check if video_info.json was created
if [ ! -f "$TEMP_BASE/video_info.json" ]; then
    echo "Error: video_info.json was not created."
    exit 1
fi

# Step 3 & 4: Transcribe audio and convert to RTF for all .wav files
# Check if any .wav files exist to avoid error in loop
# Using nullglob to handle case with no matches gracefully
shopt -s nullglob
files=(*.wav)

if [ ${#files[@]} -eq 0 ]; then
    echo "No .wav files found in the current directory."
else
    for f in "${files[@]}"; do
        filename=$(basename -- "$f")
        filename_no_ext="${filename%.*}"

        echo "Processing \"$f\"..."

        # Transcribe if txt does not exist
        if [ ! -f "${filename_no_ext}.txt" ]; then
            echo "Transcribing \"$f\"..."
            if ! "$PYTHON_EXEC" "$TRANSCRIBE_SCRIPT" "$f"; then
                echo "Error: Audio transcription failed for \"$f\"."
            fi
        else
            echo "\"${filename_no_ext}.txt\" already exists. Skipping transcription."
        fi

        # Convert to RTF
        if [ -f "${filename_no_ext}.txt" ]; then
            echo "Converting \"${filename_no_ext}.txt\" to RTF..."
            if ! "$PYTHON_EXEC" convert_to_rtf.py "${filename_no_ext}.txt" "${filename_no_ext}.rtf"; then
                echo "Error: RTF conversion failed for \"${filename_no_ext}.txt\"."
            fi
        fi
    done
fi

echo "Workflow completed successfully."

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf "$TEMP_BASE"

# End timer and print duration
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
hours=$(( elapsed / 3600 ))
minutes=$(( (elapsed % 3600) / 60 ))
seconds=$(( elapsed % 60 ))
echo "Workflow finished at: $(date)"
printf "Total elapsed time: %02d:%02d:%02d\n" $hours $minutes $seconds