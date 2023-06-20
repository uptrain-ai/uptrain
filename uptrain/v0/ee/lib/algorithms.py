import numpy as np
from uptrain.v0.core.lib.helper_funcs import fn_dependency_required

try:
    import faster_whisper
except:
    faster_whisper = None

try:
    import rouge
except:
    rouge = None

@fn_dependency_required(faster_whisper, "faster-whisper")
def faster_whisper_speech_to_text(audio_files):
    model_size = "large-v2"
    model = faster_whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
    prescribed_texts = []
    for audio_file in audio_files:
        segments, _ = model.transcribe(audio_file, beam_size=5)
        prescribed_text = ''
        for segment in segments:
            prescribed_text += segment.text
        prescribed_texts.append(prescribed_text)
    return prescribed_texts

@fn_dependency_required(rouge, "rouge")
def rogue_l_similarity(text1_list, text2_list):
    r = rouge.Rouge()
    res = r.get_scores([x.lower() for x in text1_list],[x.lower() for x in text2_list])
    return np.array([x['rouge-l']['f'] for x in res])
