import sys
import os
import torch
import numpy as np
import librosa
import warnings
import math
import soundfile as sf
from omegaconf import OmegaConf

# Suppress warnings before importing NeMo
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

try:
    import nemo.collections.asr.models as asr_models
    from nemo.utils import logging
    logging.setLevel(logging.ERROR)
except ImportError:
    print("Error: NeMo toolkit not found. Please install it using: pip install nemo_toolkit['asr'] Cython")
    sys.exit(1)

def format_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"

def transcribe_audio(audio_file):
    print(f"Transcribing '{audio_file}' using NVIDIA Canary-1B-v2 with granular timestamps...")
    
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon (MPS) acceleration.")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using NVIDIA GPU (CUDA) acceleration.")
    else:
        device = torch.device("cpu")
        print("Using CPU for transcription.")

    try:
        # Load Canary-1B-v2 model
        model = asr_models.EncDecMultiTaskModel.from_pretrained("nvidia/canary-1b-v2")
        model.to(device=device, dtype=torch.float32)
        model.eval()

        print("Loading audio...")
        audio, sr = librosa.load(audio_file, sr=16000)
        total_duration_sec = len(audio) / sr
        
        # 10-minute chunks for processing safety
        chunk_size_sec = 600 
        overlap_sec = 15 # 15 seconds overlap on both ends to provide full context
        num_chunks = math.ceil(total_duration_sec / chunk_size_sec)
        
        all_segments = []
        last_processed_time = 0.0
        
        for i in range(num_chunks):
            # The core window we want to cover in this iteration
            window_start = i * chunk_size_sec
            window_end = min((i + 1) * chunk_size_sec, total_duration_sec)
            
            # The actual audio segment we load (with overlap for context)
            load_start = max(0, window_start - overlap_sec)
            load_end = min(window_end + overlap_sec, total_duration_sec)
            
            chunk_audio = audio[int(load_start * sr) : int(load_end * sr)]
            temp_chunk_path = f"temp_chunk_{i}.wav"
            sf.write(temp_chunk_path, chunk_audio, sr)
            
            # Show starting progress for this chunk
            progress = (i / num_chunks) * 100
            print(f"[{progress:3.0f}%] Processing {format_time(window_start)} - {format_time(window_end)} (with context)...")
            
            with torch.no_grad():
                hypotheses = model.transcribe(
                    [temp_chunk_path],
                    batch_size=1,
                    task="asr",
                    source_lang="cs",
                    target_lang="cs",
                    pnc="pnc",
                    timestamps=True,
                    return_hypotheses=True
                )
            
            if os.path.exists(temp_chunk_path):
                os.remove(temp_chunk_path)
            
            if hypotheses and len(hypotheses) > 0:
                hyp = hypotheses[0]
                if isinstance(hyp, list): hyp = hyp[0]
                
                found_timestamps = False
                for attr in ['timestep', 'timestamp']:
                    ts_data = getattr(hyp, attr, None)
                    if ts_data is not None and 'segment' in ts_data:
                        segments = ts_data['segment']
                        for seg in segments:
                            # IMPORTANT: Timestamps are relative to load_start
                            seg_start = seg['start'] + load_start
                            seg_end = seg['end'] + load_start
                            
                            # LOGIC:
                            # 1. Skip if the segment already ended before our window
                            # 2. Skip if we already processed this time (overlap with previous chunk)
                            # 3. Include if the segment STARTS within our current window
                            if seg_start < window_start - 0.5:
                                continue
                            if seg_start < last_processed_time - 0.1:
                                continue
                            if seg_start >= window_end:
                                continue
                                
                            seg_text = ""
                            if 'segment' in seg:
                                seg_text = seg['segment']
                            elif 'text' in seg:
                                seg_text = seg['text']
                            else:
                                seg_text = str(seg)
                                
                            all_segments.append({
                                'start': seg_start,
                                'end': seg_end,
                                'text': seg_text.strip()
                            })
                            print(f"   [{format_time(seg_start)}] {seg_text.strip()[:80]}...")
                            last_processed_time = seg_end
                        
                        found_timestamps = True
                        break
                
                if not found_timestamps:
                    text = hyp.text if hasattr(hyp, 'text') else str(hyp)
                    all_segments.append({
                        'start': window_start,
                        'end': window_end,
                        'text': text.strip()
                    })
                    last_processed_time = window_end
                    print("   (Warning: Segment timestamps not found in this chunk)")

        print("[100%] All chunks processed.")
        base_name = os.path.splitext(audio_file)[0]
        output_file = f"{base_name}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            for seg in all_segments:
                time_label = f"[{format_time(seg['start'])}]"
                f.write(f"{time_label} {seg['text']}\n")
            
        print(f"\nTranscription completed and saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        for i in range(100):
            p = f"temp_chunk_{i}.wav"
            if os.path.exists(p): os.remove(p)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe_canary.py <audio_file>")
        sys.exit(1)
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        sys.exit(1)
    transcribe_audio(audio_path)
