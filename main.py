import argparse
import os.path

from moviepy import VideoFileClip, concatenate_videoclips
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment

def main():
    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("gap", type=float)

    args = parser.parse_args()

    # Open Files
    if not os.path.exists(args.input_file):
        print(f"Error: Couldn't find the target video.")
        return

    """
    In this step, we only need the timestamp, it doesn't matter if the transcription is 
    accurate or not. So we should 
    1. Use the most minimalist model.
    2. Store the timestamp only.
    """
    # Step 1: Generate clean SRT file
    model_size = "turbo"

    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, info = model.transcribe(audio=args.input_file, language="en", word_timestamps=True, beam_size=2)

    segments_to_be_deleted: List[Tuple] = []
    previous_segment_end = 0.00
    for segment in segments:
        if segment.start - previous_segment_end > args.gap:
            # This is so wrong wtf
            # We should cut the silence part instead of the clip after the silence ...
            segments_to_be_deleted.append((previous_segment_end, segment.start))
            print(segment.start, segment.end, segment.text)

        previous_segment_end = segment.end

    """
    For example, the timestamp from Step 1 should look like
    ..., (2341.12, 2348.10), (2351.03, 2359.83), ...
    
    In step 2, we first examine if the gap exceeds 1.2 seconds.
    If it does, we trim the gap between 2348.10+0.5 and 2351.03-0.5.
    But we can't actually trim it, instead, we record the parts we want then merge them.
    """
    # Step 2: Cut silence over $gap seconds long
    videoclips = []
    previous_segment_end = 0.00
    video_file_clip = VideoFileClip(args.input_file)
    for segment in segments_to_be_deleted:
        half_gap = args.gap/2
        new_start = segment[0] + half_gap
        new_end = segment[1] - half_gap

        # Cut the gap in both SRT and Video
        if new_start < new_end:
            clip = video_file_clip.subclipped(previous_segment_end, new_start) 
            videoclips.append(clip)

        previous_segment_end = new_end
        
    # Append the remain clip
    if previous_segment_end != 0.00:
        clip = video_file_clip.subclipped(previous_segment_end, video_file_clip.duration)
        videoclips.append(clip)

    # Combine the clips we want
    combined = concatenate_videoclips(videoclips)
    combined.write_videofile("output.mp4")

    """
    Regenerate the SRT file for the processed video.
    """
    # Step 3: Regenerate the SRT file

    """
    This step is kinda optional, cause I think the Professor won't be that picky.
    
    Using LLM processes the SRT file, making it more readable for humans.
    We should divide the SRT file into
    """
    # Step 4: Combine incomplete sentences in SRT file
        # Combine incomplete sentences
        # Make the combined sentence look tidy

if __name__ == "__main__":
    main()
