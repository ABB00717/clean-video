import argparse
import os.path

from moviepy import VideoFileClip, concatenate_videoclips
from faster_whisper import WhisperModel
from typing import Tuple, List


def delete_video_blank(input_file, gap=1):
    """Remove blank/silent segments from video file.
    
    This function analyzes the video using Whisper to detect speech segments,
    identifies gaps longer than the specified duration, and removes them.
    
    Args:
        input_file: Path to the video file
        gap: Minimum silence duration (in seconds) to be removed. Default is 1 second.
        
    Returns:
        Path to the trimmed video file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Couldn't find the target video: {input_file}")

    # Step 1: Transcribe video to detect speech segments
    # Use base model for faster processing since we only need timestamps
    model_size = "base"
    model = WhisperModel(model_size, device="cuda")
    segments, info = model.transcribe(
            audio=input_file, word_timestamps=True, language="zh")

    # Identify gaps/silence segments to be removed
    segments_to_be_deleted: List[Tuple] = []
    previous_segment_end = 0.00
    for segment in segments:
        if segment.start - previous_segment_end > gap:
            # print(f"Found silence gap: {previous_segment_end:.2f} - {segment.start:.2f}")
            segments_to_be_deleted.append(
                    (previous_segment_end, segment.start))

        # print(segment.start, segment.end, segment.text)
        previous_segment_end = segment.end

    # Step 2: Extract video clips excluding the silence gaps
    # Keep a small buffer (half_gap) on each side of the silence
    videoclips = []
    previous_segment_end = 0.00
    video_file_clip = VideoFileClip(input_file)
    
    for segment in segments_to_be_deleted:
        half_gap = gap / 2
        new_start = segment[0] + half_gap
        new_end = segment[1] - half_gap

        # Add the clip before this silence gap
        if new_start < new_end:
            clip = video_file_clip.subclipped(previous_segment_end, new_start)
            videoclips.append(clip)

        previous_segment_end = new_end

    # Append the remaining clip after the last gap
    clip = video_file_clip.subclipped(
            previous_segment_end, video_file_clip.duration)
    videoclips.append(clip)

    # Step 3: Combine all clips and save
    combined = concatenate_videoclips(videoclips)
    output_file = input_file.rsplit(".", 1)[0] + "_trimmed.mp4"
    combined.write_videofile(output_file)
    
    return output_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Remove blank/silent segments from video")
    parser.add_argument("input_file", type=str, help="Path to the video file")
    parser.add_argument("gap", type=float, default=1.0, nargs='?',
                        help="Minimum silence duration to remove (seconds, default: 1.0)")

    args = parser.parse_args()
    
    try:
        output_file = delete_video_blank(args.input_file, args.gap)
        print(f"Generated trimmed video: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()