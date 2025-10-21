import argparse
import os.path
import sys

from faster_whisper import WhisperModel


def format_srt_timestamp(total_seconds):
    """Convert seconds to SRT timestamp format.
    
    Args:
        total_seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS,mmm)
    """
    hours, remainder = divmod(total_seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, remainder = divmod(remainder, 1)
    milliseconds = remainder * 1000

    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


def generate_srt(input_file):
    """Generate SRT subtitle file from video file using Whisper model.
    
    Uses Whisper medium model to transcribe audio and generate subtitles
    in SRT format with accurate timestamps.
    
    Args:
        input_file: Path to the video file
        
    Returns:
        Path to the generated SRT file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        FileExistsError: If output SRT file already exists
        IOError: If there's an error writing the SRT file
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Couldn't find the target video: {input_file}")

    # Configure Whisper model (medium for better accuracy)
    model_size = "medium"
    model = WhisperModel(model_size, device="cuda")
    segments, info = model.transcribe(
        audio=input_file,
        word_timestamps=True,
        language="zh",
        initial_prompt="這是一個繁體中文的句子",
    )

    # Prepare output file path
    output_srt = input_file.rsplit(".", 1)[0] + ".srt"
    if os.path.exists(output_srt):
        raise FileExistsError(f"File already exists: {output_srt}")

    # Write SRT file
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
        raise IOError(f"Error writing SRT file: {e}")
    
    return output_srt


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate SRT subtitles from video file")
    parser.add_argument("input_file", type=str, help="Path to the video file")

    args = parser.parse_args()

    try:
        output_srt = generate_srt(args.input_file)
        print(f"Generated SRT file: {output_srt}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
