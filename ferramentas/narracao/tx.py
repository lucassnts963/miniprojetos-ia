import json, sys
import torch  # noqa: F401  (carrega DLLs do CUDA no Windows, como no transcribe.py)
from faster_whisper import WhisperModel
try:
    m = WhisperModel("medium", device="cuda", compute_type="float16"); dev = "cuda"
except Exception:
    m = WhisperModel("medium", device="cpu", compute_type="int8"); dev = "cpu"
print("device", dev, flush=True)
out = {}
for name in ["parte01", "parte02"]:
    segs, info = m.transcribe(f"C:/dev/snake/demo/{name}.mp3", language="pt", word_timestamps=True, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words:
            words.append([round(w.start, 2), round(w.end, 2), w.word])
    out[name] = dict(duration=info.duration, words=words)
    print(name, round(info.duration, 1), len(words), flush=True)
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
