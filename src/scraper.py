import os
import yt_dlp as youtube_dl
from multiprocessing import Pool, cpu_count


def download_audio(video_info):
    video_url, video_title, output_folder = video_info
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_folder, f"{video_title}.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def download_audio_from_channel(channel_url, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        "format": "bestaudio/best",
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(channel_url, download=False)

            if "entries" in info_dict:
                video_infos = []
                for entry in info_dict["entries"]:
                    video_url = entry["url"]
                    video_title = entry.get("title", "Unknown Title")
                    video_infos.append((video_url, video_title, output_folder))
                    print(f"Preparing to download: {video_title}")

                with Pool(processes=cpu_count()) as pool:
                    pool.map(download_audio, video_infos)
        except Exception as e:
            print(e)
