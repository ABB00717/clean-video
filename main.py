import os
import sys
import argparse
from multiprocessing import Pool

# Import the module functions
from delete_blank import delete_video_blank
from generate_srt import generate_srt
from srt_modifier import modify_srt
from delete_duplicate_string import delete_duplicate_string


def process_video(video_path, gap=1):
    """Process a single video file through all steps.

    Args:
        video_path: Path to the video file
        gap: Minimum silence duration (in seconds) to be removed in step 1
    """
    print(f"\n{'='*60}")
    print(f"Processing: {video_path}")
    print(f"{'='*60}\n")

    try:
        # Step 1: file.mp4 -> file_trimmed.mp4
        print(f"Step 1: Removing blank segments from video for {os.path.basename(video_path)}...")
        trimmed_video = delete_video_blank(video_path, gap)
        print(f"✓ Created: {os.path.basename(trimmed_video)} for {os.path.basename(video_path)}\n")

        # Step 2: file_trimmed.mp4 -> file_trimmed.srt
        print(f"Step 2: Generating SRT subtitle file for {os.path.basename(video_path)}...")
        srt_file = generate_srt(trimmed_video)
        print(f"✓ Created: {os.path.basename(srt_file)} for {os.path.basename(video_path)}\n")

        # Step 3: file_trimmed.srt -> file_trimmed_modified.srt
        print(f"Step 3: Modifying SRT with AI for {os.path.basename(video_path)}...")
        modified_srt = modify_srt(srt_file)
        print(f"✓ Created: {os.path.basename(modified_srt)} for {os.path.basename(video_path)}\n")

        # Step 4: Remove duplicate strings in modified SRT
        print(f"Step 4: Removing duplicate strings for {os.path.basename(video_path)}...")
        delete_duplicate_string(modified_srt)
        print(f"✓ Processed: {os.path.basename(modified_srt)} for {os.path.basename(video_path)}\n")

        # Clean up temporary files
        print(f"Cleaning up temporary files for {os.path.basename(video_path)}...")
        # Delete the unmodified SRT file
        if os.path.exists(srt_file):
            os.remove(srt_file)
            print(f"✓ Deleted: {os.path.basename(srt_file)}")

        # Rename original file to _orig.mp4
        orig_name = video_path.rsplit(".", 1)[0] + "_orig.mp4"
        if not os.path.exists(orig_name):
            os.rename(video_path, orig_name)
            print(f"✓ Renamed: {os.path.basename(video_path)} -> {os.path.basename(orig_name)}")

        # Rename _trimmed.mp4 to original name
        final_video = video_path
        os.rename(trimmed_video, final_video)
        print(f"✓ Renamed: {os.path.basename(trimmed_video)} -> {os.path.basename(final_video)}")

        # Rename _trimmed_modified.srt to .srt
        final_srt = video_path.rsplit(".", 1)[0] + ".srt"
        os.rename(modified_srt, final_srt)
        print(f"✓ Renamed: {os.path.basename(modified_srt)} -> {os.path.basename(final_srt)}")

        print(f"\n{'='*60}")
        print(f"✓ Successfully processed: {os.path.basename(video_path)}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n✗ Error processing {video_path}: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Process videos: remove blanks, generate and modify subtitles")
    parser.add_argument("target_dir", type=str, help="Directory containing video files")
    parser.add_argument("--gap", type=float, default=1, help="Minimum silence duration to remove (seconds)")

    args = parser.parse_args()

    # Check if target directory exists
    if not os.path.isdir(args.target_dir):
        print(f"Error: Directory '{args.target_dir}' not found")
        sys.exit(1)

    # Find all .mp4 files in the target directory, excluding _orig.mp4 files
    video_files = [os.path.join(args.target_dir, f) for f in os.listdir(args.target_dir) if
                   f.endswith('.mp4') and not f.endswith('_orig.mp4')]

    if not video_files:
        print(f"No .mp4 files to process in '{args.target_dir}'")
        sys.exit(0)

    print(f"Found {len(video_files)} video file(s) to process")

    # Create a pool of worker processes
    # The number of processes will be the number of CPU cores by default
    with Pool(processes=5) as pool:
        # Prepare arguments for each process
        process_args = [(video_path, args.gap) for video_path in video_files]
        # Process videos in parallel
        pool.starmap(process_video, process_args)

    print("\n" + "="*60)
    print("All videos processed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()