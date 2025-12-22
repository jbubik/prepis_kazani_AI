import sys
import mlx_whisper
import os

def transcribe_audio(audio_file):
    print(f"Transcribing '{audio_file}' using MLX Whisper (Large V3)...")
    
    # "mlx-community/whisper-large-v3-mlx" is the Hugging Face repo for the MLX-optimized model
    # We can output directly to a file or handle the text here. 
    # mlx_whisper.transcribe returns a dictionary with 'text' and 'segments'.
    
    try:
        result = mlx_whisper.transcribe(
            audio_file,
            path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
            language="cs"
        )
        
        # Save the output to a .txt file with the same basename
        base_name = os.path.splitext(audio_file)[0]
        output_file = f"{base_name}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["text"].strip())
            
        print(f"Transcription saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_whispermlx.py <audio_file>")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        sys.exit(1)
        
    transcribe_audio(audio_path)
