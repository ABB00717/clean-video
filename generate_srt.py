import argparse
import os.path
import sys

from faster_whisper import WhisperModel


def format_srt_timestamp(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, remainder = divmod(remainder, 1)
    milliseconds = remainder * 1000

    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)

    args = parser.parse_args()

    # Open Video
    if not os.path.exists(args.input_file):
        print("Error: Couldn't find the target video.")
        return

    # Configure Whisper model
    model_size = "medium"
    model = WhisperModel(model_size, device="cuda")
    segments, info = model.transcribe(
        audio=args.input_file,
        word_timestamps=True,
        language="zh",
    )

    # Create SRT file
    output_srt = args.input_file.rsplit(".", 1)[0] + ".srt"
    if os.path.exists(output_srt):
        print("Error: file already exists")
        sys.exit(1)

    # Generate SRT
    try:
        with open(output_srt, "w", encoding="UTF-8") as file:
            i = 1
            for segment in segments:
                file.write(str(i) + "\n")
                start = format_srt_timestamp(segment.start)
                end = format_srt_timestamp(segment.end)
                file.write(f"{start} --> {end}\n")
                file.write(segment.text + "\n")
                file.write("\n")
                i += 1
    except IOError as e:
        print(f"IOError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
