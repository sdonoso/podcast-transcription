import shutil
import argparse
import yaml
from glob import glob
from multiprocessing import Process, set_start_method, Manager
import subprocess

from src.scraper import download_audio_from_channel
from src.whisper import process_files, chunk_list, save_json


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Download audio from a YouTube channel."
    )
    parser.add_argument("config_file", type=str, help="The YAML configuration file.")
    return parser.parse_args()


def load_config(config_file):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


def validate_config(config):
    required_keys = ["channel_url", "output_folder", "output_json"]
    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        raise ValueError(
            f"Error: The YAML file must contain {', '.join(missing_keys)}."
        )

    return config["channel_url"], config["output_folder"], config["output_json"]


def get_available_gpus(max_gpus=4):
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        gpu_info = result.stdout.strip().split("\n")
        available_gpus = []

        for line in gpu_info:
            index, memory_used, memory_total = map(int, line.split(","))
            if memory_used < 10:
                available_gpus.append(index)
            if len(available_gpus) >= max_gpus:
                break

        return available_gpus

    except Exception as e:
        print(f"Error detecting GPUs: {e}")
        return []


def download_and_transcribe(channel_url, output_folder, output_json):
    download_audio_from_channel(channel_url, output_folder)

    manager = Manager()
    shared_list = manager.list()

    try:
        set_start_method("spawn", force=True)
    except RuntimeError as e:
        print(f"Error setting start method: {e}")

    audio_list = glob(f"{output_folder}/*.mp3")
    gpus = get_available_gpus()
    audio_chunks = chunk_list(audio_list, len(gpus))

    processes = []

    for gpu, audio_chunk in zip(gpus, audio_chunks):
        p = Process(target=process_files, args=(gpu, audio_chunk, shared_list))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    dict_list = [
        {"name": transcript[0], "transcription": transcript[1]}
        for transcript in shared_list
    ]
    save_json({"transcripts": dict_list}, output_json)
    shutil.rmtree(output_folder)


def main():
    args = parse_arguments()
    config = load_config(args.config_file)

    try:
        channel_url, output_folder, output_json = validate_config(config)
    except ValueError as e:
        print(e)
        return

    for url, folder_path, json_path in zip(channel_url, output_folder, output_json):
        download_and_transcribe(url, folder_path, json_path)


if __name__ == "__main__":
    main()
