# 環境要求
```python
pip install faster-whisper moviepy python-dotenv google-genai
```
# 使用方法
依照四個檔案依序處理

1_delete-blank.py：刪除影片空白處（沒有人講話的片段）
```python
python 1_delete-blank.py {影片檔案} {空白時長}
```
會額外生成一個 `output.mp4`。

2_generate-srt.py：生成字幕
```python
python 2_generate-srt.py {影片檔案}
```
生成字幕檔案，檔名為影片檔名後綴改為 `.srt`。

3_srt-modifier.py：請 LLM 幫忙修改字幕稿
```python
python 3_srt-modifier.py {字幕稿}
```
請 LLM 幫忙去除贅字，詳細規則請看原檔案。

4_delete-duplicate-string.py：刪除重複字串
```python
python 4_delete-duplicate-string.py {字幕稿}
```
LLM 生成後的字幕，有時字串合併會失敗，導致兩串相同的字串重複出現。使用此檔案即可刪除。
