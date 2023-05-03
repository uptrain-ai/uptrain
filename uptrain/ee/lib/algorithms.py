import numpy as np

def faster_whisper_speech_to_text(audio_files):
    from faster_whisper import WhisperModel
    model_size = "large-v2"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    prescribed_texts = []
    for audio_file in audio_files:
        segments, _ = model.transcribe(audio_file, beam_size=5)
        prescribed_text = ''
        for segment in segments:
            prescribed_text += segment.text
        prescribed_texts.append(prescribed_text)
    return prescribed_texts


def rogue_l_similarity(text1_list, text2_list): 
    from rouge import Rouge 
    r = Rouge()
    res = r.get_scores([x.lower() for x in text1_list],[x.lower() for x in text2_list])
    return np.array([x['rouge-l']['f'] for x in res])
