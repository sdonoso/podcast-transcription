import argparse
import yaml
from src.scraper import download_audio_from_channel


def main():
    parser = argparse.ArgumentParser(
        description="Download audio from a YouTube channel."
    )
    parser.add_argument("config_file", type=str, help="The YAML configuration file.")
    args = parser.parse_args()

    with open(args.config_file, "r") as file:
        config = yaml.safe_load(file)

    channel_url = config.get("channel_url")
    output_folder = config.get("output_folder")

    if not channel_url or not output_folder:
        print("Error: The YAML file must contain 'channel_url' and 'output_folder'.")
        return

    download_audio_from_channel(channel_url, output_folder)


if __name__ == "__main__":
    main()
