import sys
import os
import torch
from transformers import pipeline

def transcribe_audio(audio_file):
    print(f"Transcribing '{audio_file}' using facebook/seamless-m4t-v2-large...")
    
    # Device detection
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda:0"
    elif torch.backends.mps.is_available():
        device = "mps"
    
    print(f"Using device: {device}")

    try:
        # Initialize pipeline
        translator = pipeline(
            task="automatic-speech-recognition",
            model="facebook/seamless-m4t-v2-large",
            device=device,
            trust_remote_code=True
        )
        
        # Cast to fp16 if on MPS (as seen in app.py)
        if device == "mps":
             translator.model = translator.model.to(torch.float16)
             print("Model cast to FP16 on MPS")

        # Transcribe
        # Using chunk_length_s to handle long audio files
        # tgt_lang="ces" sets the target language to Czech
        print("Starting transcription... this may take a while.")
        result = translator(audio_file, tgt_lang="ces", chunk_length_s=30)
        
        text = result["text"].strip()
        
        # Cleanup (as seen in app.py)
        text = text.replace("#err", "")
        
        # Save to file
        base_name = os.path.splitext(audio_file)[0]
        output_file = f"{base_name}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Transcription saved to '{output_file}'")

    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_seamless.py <audio_file>")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        sys.exit(1)
        
    transcribe_audio(audio_path)
