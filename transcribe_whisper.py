import sys
import os
import time
from faster_whisper import WhisperModel

def transcribe_audio(audio_file):
    print(f"Transcribing '{audio_file}' using faster-whisper (Large V3)...")

    model_size = "large-v3"
    device = "cpu"
    compute_type = "float32"
    
    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        segments, info = model.transcribe(audio_file, language="cs", beam_size=5)

        base_name = os.path.basename(audio_file)
        file_root = os.path.splitext(base_name)[0]
        output_file = f"{file_root}.txt"
        
        print(f"Detected language '{info.language}' with probability {info.language_probability}")
        if info.duration:
             print(f"Audio duration: {info.duration:.2f}s")

        last_update_time = time.time()
        
        with open(output_file, "w", encoding="utf-8") as f:
            for segment in segments:
                start = int(segment.start)
                hours = start // 3600
                minutes = (start % 3600) // 60
                seconds = start % 60
                if hours > 0:
                    timestamp = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
                else:
                    timestamp = f"[{minutes:02d}:{seconds:02d}]"
                
                text = segment.text.strip()
                f.write(f"{timestamp} {text}\n")
                
                # Report progress every 60 seconds
                if time.time() - last_update_time >= 60:
                    progress_pct = ""
                    if info.duration:
                        pct = (segment.end / info.duration) * 100
                        progress_pct = f" ({pct:.1f}%)"
                    
                    print(f"Progress{progress_pct}: {timestamp} {text}")
                    last_update_time = time.time()
                
        if os.path.exists(output_file):
            print(f"Transcription saved to '{output_file}'")

    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_whisper.py <audio_file>")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        sys.exit(1)
        
    transcribe_audio(audio_path)