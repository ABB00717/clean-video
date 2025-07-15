import argparse
import os.path

from faster_whisper import WhisperModel

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

    # Step 1: Generate clean SRT file

    # Step 2: Cut silence over $gap seconds long
        # Cut the gap in both SRT and Video

    # Step 3: Combine incomplete sentences in SRT file
        # Combine incomplete sentences
        # Make the combined sentence look tidy

if __name__ == "__main__":
    main()