import re


def remove_adjacent_repeating_prefix(input_str: str) -> str:
    """Check if a string has a repeating prefix and remove it.
    
    Checks if the beginning substring (length > 2) repeats with its adjacent part,
    and removes the prefix repeatedly until no repetition exists.
    
    Args:
        input_str: The string to check and modify
        
    Returns:
        String with adjacent repeating prefixes removed
    """
    current_str = input_str
    while True:
        was_modified = False
        # Maximum prefix length cannot exceed half of the string
        # Check from longest possible prefix length, decrementing to 3
        for prefix_len in range(
            len(current_str) // 2, max(2, len(current_str) // 2) % 2 + 2, -1
        ):
            prefix = current_str[:prefix_len]
            next_segment = current_str[prefix_len:prefix_len * 2]

            if prefix == next_segment:
                # print(input_str)
                current_str = current_str[prefix_len:]
                was_modified = True
                # After finding and modifying, immediately re-check the new string
                break

        if not was_modified:
            break

    return current_str


def is_timestamp(input_str: str) -> bool:
    """Check if input string matches SRT timestamp format.
    
    Format example: '00:01:23,456 --> 00:01:25,789'
    
    Args:
        input_str: String to check
        
    Returns:
        True if string matches SRT timestamp format, False otherwise
    """
    # Pattern matches HH:MM:SS,ms --> HH:MM:SS,ms format
    timestamp_pattern = re.compile(
        r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*$"
    )
    return bool(timestamp_pattern.match(input_str))


def delete_duplicate_string(file_path):
    """Remove duplicate adjacent repeating prefixes from SRT subtitle content.
    
    Processes an SRT file line by line, identifying subtitle text lines
    (those that follow timestamp lines) and removing any adjacent repeating
    prefixes to clean up transcription errors.
    
    Args:
        file_path: Path to the SRT file to process
        
    Returns:
        Path to the processed file (same as input, modified in-place)
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    processed_lines = []

    try:
        # Step 1: Read all lines with UTF-8 encoding
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Step 2: Iterate through lines and process content
        next_is_sentence = False
        for line in lines:
            line_content = line.strip()

            if next_is_sentence:
                # This is the subtitle text line after a timestamp
                modified_content = remove_adjacent_repeating_prefix(line_content)
                processed_lines.append(modified_content + "\n")
                next_is_sentence = False
            else:
                # Add current line to processed list
                processed_lines.append(line)
                # Check if current line is a timestamp
                if is_timestamp(line_content):
                    next_is_sentence = True

        # Step 3: Write all processed content back to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(processed_lines)

        print(f"File '{file_path}' processed successfully.")
        return file_path

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: '{file_path}'. Please check the filename and path.")


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Remove duplicate strings from SRT subtitles")
    parser.add_argument("input_file", type=str, help="Path to the SRT file to process")
    args = parser.parse_args()
    
    try:
        delete_duplicate_string(args.input_file)
    except Exception as e:
        print(f"Error processing file: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
