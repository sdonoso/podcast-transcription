import json

import whisperx
from tqdm import tqdm


def process_files(gpu, audio_files, shared_list, compute_type="float16"):
    model = whisperx.load_model(
        "large-v2", "cuda", device_index=gpu, compute_type=compute_type
    )
    transcriptions = []
    for audio_file in tqdm(audio_files):
        file_name = audio_file.split("/")[-1].split(".mp3")[0]
        audio = whisperx.load_audio(audio_file)
        result = model.transcribe(audio, language="es")
        text = "\n".join([segment["text"] for segment in result["segments"]])
        transcriptions.append([file_name, text])

    shared_list.extend(transcriptions)


def chunk_list(lst, n):
    return [lst[i::n] for i in range(n)]


def save_json(dct, name):
    with open(name, "w") as json_file:
        json.dump(dct, json_file)
