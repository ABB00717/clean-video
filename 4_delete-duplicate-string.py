import re


def remove_adjacent_repeating_prefix(input_str: str) -> str:
    """
    檢查一個字串，如果開頭的子字串（長度>2）與其相鄰部分重複，
    則刪除開頭的那個子字串，並持續此過程直到沒有重複為止。
    """
    current_str = input_str
    while True:
        was_modified = False
        # 前綴長度最大不可能超過字串的一半
        # 從最長的可能前綴長度開始檢查，遞減至 3
        # 使用 max(2, ...) 避免 len(current_str)//2 小於 3 的情況
        for prefix_len in range(
            len(current_str) // 2, max(2, len(current_str) // 2) % 2 + 2, -1
        ):
            prefix = current_str[:prefix_len]
            next_segment = current_str[prefix_len:prefix_len * 2]

            if prefix == next_segment:
                print(input_str)
                current_str = current_str[prefix_len:]
                was_modified = True
                # 找到並修改後，立即從頭開始檢查新的字串
                break

        if not was_modified:
            break

    return current_str


def is_timestamp(input_str: str) -> bool:
    """
    使用正規表示式檢查輸入字串是否符合 SRT 時間戳格式。
    格式範例: '00:01:23,456 --> 00:01:25,789'
    """
    # ^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$
    # 這個模式精確匹配 HH:MM:SS,ms --> HH:MM:SS,ms 的格式
    timestamp_pattern = re.compile(
        r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\s*$"
    )
    return bool(timestamp_pattern.match(input_str))


# --- 主程式邏輯 ---

# 定義檔案路徑
file_path = "L15_B_modified.srt"
processed_lines = []

try:
    # 步驟 1: 以 'utf-8' 編碼讀取所有行到一個列表中
    # 使用 utf-8 可以避免處理多數語言時的編碼錯誤
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 步驟 2: 迭代列表，處理內容並存到新列表中
    next_is_sentence = False
    for line in lines:
        # .strip() 用於移除結尾的換行符 '\n'，方便處理
        line_content = line.strip()

        if next_is_sentence:
            # 這是時間戳的下一行，也就是字幕內容，對其進行處理
            modified_content = remove_adjacent_repeating_prefix(line_content)
            processed_lines.append(modified_content + "\n")
            next_is_sentence = False
        else:
            # 將當前行先加入待辦清單
            processed_lines.append(line)
            # 檢查當前行是否為時間戳，如果是，則設定旗標，讓下一行被處理
            if is_timestamp(line_content):
                next_is_sentence = True

    # 步驟 3: 將處理過的所有內容一次性寫回原檔案
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(processed_lines)

    print(f"檔案 '{file_path}' 處理完成。")

except FileNotFoundError:
    print(f"錯誤：找不到檔案 '{file_path}'。請確認檔案名稱和路徑是否正確。")
except Exception as e:
    print(f"處理檔案時發生錯誤：{e}")
