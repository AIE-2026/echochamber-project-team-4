# scripts/collect_youtube.py
"""
Colectare simplă de comentarii YouTube.
Rulează din root-ul proiectului:
python scripts/collect_youtube.py --handle digi24hd56 --max-videos 2 --max-comments 50 --output data/raw/student_01_youtube_raw.jsonl
"""
# 1. Biblioteci
import os
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
# 2. Setări API
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"
if API_KEY is None:
    print("Lipsește YOUTUBE_API_KEY. Creează fișierul .env în root-ul proiectului.")
    exit()
# 3. Argumente din terminal
parser = argparse.ArgumentParser()
parser.add_argument("--handle", required=True)
parser.add_argument("--max-videos", type=int, default=2)
parser.add_argument("--max-comments", type=int, default=50)
parser.add_argument("--output", required=True)
args = parser.parse_args()
# 4. Găsim canalul după handle
channel_response = requests.get(
    f"{BASE_URL}/channels",
    params={
        "part": "id",
        "forHandle": args.handle,
        "key": API_KEY
    }
)
channel_data = channel_response.json()
if "items" not in channel_data or len(channel_data["items"]) == 0:
    print("Nu am găsit canalul. Verifică handle-ul sau cheia API.")
    print(channel_data)
    exit()
channel_id = channel_data["items"][0]["id"]
# 5. Luăm cele mai recente videoclipuri
videos_response = requests.get(
    f"{BASE_URL}/search",
    params={
        "part": "snippet",
        "channelId": channel_id,
        "type": "video",
        "order": "date",
        "maxResults": args.max_videos,
        "key": API_KEY
    }
)
videos_data = videos_response.json()
# 6. Colectăm comentariile
comments = []
for video_item in videos_data["items"]:
    video_id = video_item["id"]["videoId"]
    video_title = video_item["snippet"]["title"]
    video_date = video_item["snippet"]["publishedAt"][:10]
    print("Colectez:", video_title[:70])
    comments_response = requests.get(
        f"{BASE_URL}/commentThreads",
        params={
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(args.max_comments, 100),
            "textFormat": "plainText",
            "order": "relevance",
            "key": API_KEY
        }
    )
    comments_data = comments_response.json()
    for comment_item in comments_data.get("items", []):
        snippet = comment_item["snippet"]["topLevelComment"]["snippet"]
        record = {
            "id": f"yt_{video_id}_{comment_item['id']}",
            "source_platform": "youtube",
            "source_channel": args.handle,
            "text_raw": snippet["textDisplay"],
            "video_id": video_id,
            "video_title": video_title,
            "video_date": video_date,
            "comment_date": snippet["publishedAt"][:10],
            "likes": snippet["likeCount"],
            "collected_at": datetime.utcnow().strftime("%Y-%m-%d")
        }
        comments.append(record)
# 7. Salvăm fișierul JSONL
output_path = Path(args.output)
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8") as file:
    for comment in comments:
        file.write(json.dumps(comment, ensure_ascii=False) + "\n")
# 8. Mesaj final
print("Comentarii salvate:", len(comments))
print("Fișier:", args.output)