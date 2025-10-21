import argparse
import os.path
import subprocess
from faster_whisper import WhisperModel
from typing import Tuple, List

def delete_video_blank(input_file, gap=1):
    """Remove blank/silent segments from video using ffmpeg directly.
    
    Bypasses moviepy for much faster processing by building an
    ffmpeg filter_complex command and using hardware acceleration (nvenc).
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Couldn't find the target video: {input_file}")

    # Step 1: Transcribe video (same as yours)
    print("Transcribing video with faster-whisper...")
    model_size = "base"
    model = WhisperModel(model_size, device="cuda")
    segments, info = model.transcribe(
            audio=input_file, word_timestamps=True, language="zh")

    video_duration = info.duration
    print(f"Video duration: {video_duration:.2f}s")

    # --- 找出要 *刪除* 的安靜片段 (segments_to_be_deleted) ---
    segments_to_be_deleted: List[Tuple] = []
    previous_segment_end = 0.00
    
    # 處理開頭的安靜
    first_segment = next(segments, None)
    if not first_segment:
        print("No speech detected in the video.")
        return input_file # 沒偵測到任何語音，直接回傳原檔

    if first_segment.start - 0.0 > gap:
        segments_to_be_deleted.append((0.0, first_segment.start))
    previous_segment_end = first_segment.end
    
    # 處理中間的安靜
    for segment in segments:
        if segment.start - previous_segment_end > gap:
            segments_to_be_deleted.append(
                    (previous_segment_end, segment.start))
        previous_segment_end = segment.end

    # 處理結尾的安靜 (你原版 code 漏掉的)
    if video_duration - previous_segment_end > gap:
         segments_to_be_deleted.append(
                    (previous_segment_end, video_duration))
    
    if not segments_to_be_deleted:
        print("No gaps found longer than {gap}s. No changes made.")
        return input_file

    # --- 根據 "刪除" 片段，反推出要 *保留* 的片段 (keep_segments) ---
    keep_segments = []
    previous_gap_end = 0.00
    
    # 尊重你原本的 "half_gap" 邏輯，在安靜區間各縮一點
    half_gap = gap / 2 
    
    for (silence_start, silence_end) in segments_to_be_deleted:
        keep_start = previous_gap_end
        keep_end = silence_start + half_gap # 保留到 "安靜開始 + half_gap"
        
        if keep_end > keep_start:
            keep_segments.append((keep_start, keep_end))
            
        previous_gap_end = silence_end - half_gap # 下一段從 "安靜結束 - half_gap" 開始
        
    # 加入最後一段影片 (如果有的話)
    if previous_gap_end < video_duration:
        keep_segments.append((previous_gap_end, video_duration))

    if not keep_segments:
        print("Error: No segments to keep after trimming logic.")
        return input_file

    # Step 2: Build ffmpeg filter_complex string
    print("Building ffmpeg command...")
    filter_parts = []
    concat_inputs = []
    for i, (start, end) in enumerate(keep_segments):
        filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
        filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")
        concat_inputs.append(f"[v{i}][a{i}]")
        
    filter_complex = ";".join(filter_parts) + ";" + \
                     "".join(concat_inputs) + \
                     f"concat=n={len(keep_segments)}:v=1:a=1[outv][outa]"
                     
    output_file = input_file.rsplit(".", 1)[0] + "_trimmed_ffmpeg.mp4"

    # Step 3: Run ffmpeg command with h264_nvenc
    command = [
        'ffmpeg',
        '-i', input_file,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-map', '[outa]',
        '-c:v', 'h264_nvenc',  # 用你的 RTX 3050
        '-preset', 'fast',     # 快速編碼
        '-c:a', 'aac',         # 音訊轉成 aac
        '-y',                  # 強制覆蓋
        output_file
    ]
    
    print(f"Running ffmpeg... Output: {output_file}")
    # print(" ".join(command)) # uncomment for debugging
    
    try:
        # 用 capture_output=True 才不會把 ffmpeg 的 log 全印在 console
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("ffmpeg command failed:")
        print("STDERR:", e.stderr) # 印出 ffmpeg 錯誤
        raise
        
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Remove blank/silent segments from video")
    parser.add_argument("input_file", type=str, help="Path to the video file")
    parser.add_argument("gap", type=float, default=1.0, nargs='?',
                        help="Minimum silence duration to remove (seconds, default: 1.0)")

    args = parser.parse_args()
    
    try:
        # 改成呼叫新的 function
        output_file = delete_video_blank(args.input_file, args.gap)
        print(f"Generated trimmed video: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
