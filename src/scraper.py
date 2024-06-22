import os
import youtube_dl


def download_audio_from_channel(channel_url, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)

        if "entries" in info_dict:
            for entry in info_dict["entries"]:
                video_title = entry.get("title", "Unknown Title")
                print(f"Downloading: {video_title}")

                ydl.download([entry["url"]])
