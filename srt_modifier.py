from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

import sys
import srt
import os
import textwrap
import argparse


class Modified_Sentence(BaseModel):
    output: str


# System instruction defines the persona, rules, and output format.
SYSTEM_INSTRUCTION = textwrap.dedent(
    """
    我是一個專業的字幕編輯，擅長將口語化的逐字稿，精煉成更具可讀性、更通順的書面風格字幕。我會遵循以下規則來完成任務。

    ## Rules:
    1.  **刪除贅字**: 刪除所有不影響語意的口語贅字，例如「嗯」、「啊」、「那個」、「然後」、「就是說」、「對」等。
    舉例：這其實就是一個什麼 -> 這其實就是什麼
    2.  **修正錯字**: 根據上下文，修正明顯的打字錯誤或同音異字錯誤。
    舉例：這其實就是一個什麼 -> 這其實就是什麼
    3.  **維持原意**: 所有修改都必須在不改變原說話者意圖的前提下進行。
    4.  **格式遵循**: 嚴格按照指定的 JSON 格式輸出，不要有任何多餘的文字或解釋。
    5. **文字格式**: 若文字內有英文或是數字，則之間一定要加上空格。
    舉例：那你看這個1和2是不是就符合Counting Sort的要求 -> 那你看這個 1 和 2 是不是就符合 Counting Sort 的要求
    6. **簡體轉繁體**: 若當前文字是簡體中文，請把它轉換成繁體。

    ## Output Format:
    {
      "output": "{修改後的目標句文字}",
    }
    """
)

"""
    3.  **判斷合併**:
        - 如果「目標句」在語意上是「前一句」的直接延續，且兩句合併後成為一個更完整、通順的短句，則將 merge 設為 `true`。
            - 若 merge 為 true，我的外部工具會自動將這一句與前一句合併，所以你不必再重述上一個句子，但你一定要確保他們合併後是通順的。
        - 如果「目標句」本身就是一個完整的句子，或者與前一句的關聯性不強，則設為 `false`。
    舉例：
    前一個句子: 那到底哪些東西是
    當前句子: 我有多算跟少算的部份
    -> 那到底哪些東西是我有多算跟少算的部份
"""


def modify_srt(input_file):
    """Modify SRT subtitle file using Gemini AI to improve readability.
    
    This function processes each subtitle entry through Gemini AI to:
    - Remove filler words and verbal tics
    - Fix typos and homophones
    - Merge incomplete sentences for better readability (deleted)
    - Maintain the original speaker's intent
    
    Args:
        input_file: Path to the input SRT file
        
    Returns:
        Path to the modified SRT file (with '_modified' suffix)
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If the SRT file is empty
    """
    load_dotenv()
    client = genai.Client(api_key=str(os.getenv("GEMINI_API_KEY")))
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))
    except FileNotFoundError:
        raise FileNotFoundError(f"Can't find {input_file}")

    if len(subtitles) < 1:
        raise ValueError("The SRT file is empty")

    final_subtitles = []
    for i, current_sub in enumerate(subtitles):
        # Get surrounding context for better AI processing
        pre_4_sentence = (
            final_subtitles[-4].content if len(final_subtitles) > 3 else ""
        )
        pre_3_sentence = (
            final_subtitles[-3].content if len(final_subtitles) > 2 else ""
        )
        pre_2_sentence = (
            final_subtitles[-2].content if len(final_subtitles) > 1 else ""
        )
        pre_1_sentence = (
            final_subtitles[-1].content if len(final_subtitles) > 0 else ""
        )
        cur_sentence = current_sub.content
        next_1_sentence = subtitles[i + 1].content if i < len(subtitles) - 1 else ""
        next_2_sentence = subtitles[i + 2].content if i < len(subtitles) - 2 else ""
        next_3_sentence = subtitles[i + 3].content if i < len(subtitles) - 3 else ""
        next_4_sentence = subtitles[i + 4].content if i < len(subtitles) - 4 else ""

        # Build prompt with context
        user_prompt = f"""
        ## Input:
        - 前四句: {pre_4_sentence}
        - 前三句: {pre_3_sentence}
        - 前二句: {pre_2_sentence}
        - 前一句: {pre_1_sentence}
        - 目標句: {cur_sentence}
        - 後一句: {next_1_sentence}
        - 後二句: {next_2_sentence}
        - 後三句: {next_3_sentence}
        - 後四句: {next_4_sentence}
        """

        print(f"{i+1}/{len(subtitles)}: {cur_sentence}")

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    # thinking_config=types.ThinkingConfig(
                    #     thinking_budget=0
                    # ),  # Disables thinking mode for faster response
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=Modified_Sentence,
                ),
            )

            modified_data = Modified_Sentence.model_validate_json(response.text)

            new_sub = srt.Subtitle(
                index=len(final_subtitles) + 1,
                start=current_sub.start,
                end=current_sub.end,
                content=modified_data.output,
            )
            final_subtitles.append(new_sub)

            print(response.text)
        except Exception as e:
            print(f"Error: {e}")
            # Keep the original sentence on error
            current_sub.index = len(final_subtitles) + 1
            final_subtitles.append(current_sub)

        # Save progress after each subtitle (overwrites each time)
        final_srt_content = srt.compose(final_subtitles)
        output_filename = os.path.splitext(input_file)[0] + "_modified.srt"

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_srt_content)

    print("Done!")
    print(f"Saved the modified result at {output_filename}")
    return output_filename


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Modify SRT subtitles using AI to improve readability")
    parser.add_argument("input_file", type=str, help="Path to the input SRT file")

    args = parser.parse_args()
    try:
        modify_srt(args.input_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
