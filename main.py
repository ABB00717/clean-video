import os
import sys
import argparse
from pathlib import Path

# Import the module functions
from delete_blank import delete_video_blank
from generate_srt import generate_srt  # Import from 2_generate-srt.py
from srt_modifier import modify_srt  # Import from 3_srt-modifier.py
from delete_duplicate_string import delete_duplicate_string  # Import from 4_delete-duplicate-string.py


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
        print("Step 1: Removing blank segments from video...")
        trimmed_video = delete_video_blank(video_path, gap)
        print(f"✓ Created: {trimmed_video}\n")
        
        # Step 2: file_trimmed.mp4 -> file_trimmed.srt
        print("Step 2: Generating SRT subtitle file...")
        srt_file = generate_srt(trimmed_video)
        print(f"✓ Created: {srt_file}\n")
        
        # Step 3: file_trimmed.srt -> file_trimmed_modified.srt
        print("Step 3: Modifying SRT with AI...")
        modified_srt = modify_srt(srt_file)
        print(f"✓ Created: {modified_srt}\n")
        
        # Step 4: Remove duplicate strings in modified SRT
        print("Step 4: Removing duplicate strings...")
        delete_duplicate_string(modified_srt)
        print(f"✓ Processed: {modified_srt}\n")
        
        # Clean up temporary files
        print("Cleaning up temporary files...")
        # Delete the unmodified SRT file
        if os.path.exists(srt_file):
            os.remove(srt_file)
            print(f"✓ Deleted: {srt_file}")
        
        # Rename original file to _orig.mp4
        orig_name = video_path.rsplit(".", 1)[0] + "_orig.mp4"
        if not os.path.exists(orig_name):
            os.rename(video_path, orig_name)
            print(f"✓ Renamed: {video_path} -> {orig_name}")
        
        # Rename _trimmed.mp4 to original name
        final_video = video_path
        os.rename(trimmed_video, final_video)
        print(f"✓ Renamed: {trimmed_video} -> {final_video}")
        
        # Rename _trimmed_modified.srt to .srt
        final_srt = video_path.rsplit(".", 1)[0] + ".srt"
        os.rename(modified_srt, final_srt)
        print(f"✓ Renamed: {modified_srt} -> {final_srt}")
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully processed: {video_path}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Error processing {video_path}: {e}\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Process videos: remove blanks, generate and modify subtitles")
    parser.add_argument("target_dir", type=str, help="Directory containing video files")
    parser.add_argument("--gap", type=float, default=1, help="Minimum silence duration to remove (seconds)")
    
    args = parser.parse_args()
    
    # Check if target directory exists
    if not os.path.isdir(args.target_dir):
        print(f"Error: Directory '{args.target_dir}' not found")
        sys.exit(1)
    
    # Find all .mp4 files in the target directory
    video_files = [f for f in os.listdir(args.target_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print(f"No .mp4 files found in '{args.target_dir}'")
        sys.exit(0)
    
    print(f"Found {len(video_files)} video file(s) to process")
    
    # Process each video file
    for video in video_files:
        video_path = os.path.join(args.target_dir, video)
        process_video(video_path, args.gap)
    
    print("\n" + "="*60)
    print("All videos processed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()