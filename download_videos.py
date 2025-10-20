import yt_dlp
import os


def download_videos_from_file(filename):
    """Read a file with a list of URLs and download the videos.
    
    Downloads videos from URLs listed in a text file (one URL per line).
    Uses yt-dlp to download the best quality available.
    
    Args:
        filename: Path to the text file containing video URLs
    """
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    with open(filename, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print(f"No URLs found in '{filename}'.")
        return

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
    }

    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Downloading: {url}")
                ydl.download([url])
                print(f"Finished downloading: {url}")
        except yt_dlp.utils.DownloadError as e:
            print(f"Error downloading {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for {url}: {e}")


if __name__ == '__main__':
    download_videos_from_file('urls.txt')
