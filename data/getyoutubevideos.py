import os
import subprocess

classes = [
    "skateboarding",
    "guitar playing",
    "cooking",
    "playing piano",
    "soccer juggling",
    "basketball dunk",
    "yoga",
    "weightlifting",
    "running",
    "biking",
    "swimming",
    "surfing",
    "boxing",
    "dancing",
    "karate",
    "walking a dog",
    "fishing",
    "skiing",
    "snowboarding",
    "playing drums",
    "parkour",
    "typing on a keyboard",
    "playing violin",
    "jump rope",
    "tennis serve"
]

os.makedirs("data/youtube_clips", exist_ok=True)

def download_clips(query, label, max_videos=25):
    save_dir = os.path.join("data/youtube_clips", label)
    os.makedirs(save_dir, exist_ok=True)

    search_query = f"ytsearch25:{query} short highlights"
    command = [
        "yt-dlp",
        search_query,
        "--format", "mp4",
        "--max-filesize", "50M",
        "--match-filter", "duration < 60",
        "--download-archive", f"{save_dir}/downloaded.txt",
        "--output", f"{save_dir}/%(title).40s.%(ext)s",
        "--quiet",
        "--no-warnings"
    ]
    print(f"🔍 Downloading: {query}")
    subprocess.run(command)

# Run for each class
for cls in classes:
    download_clips(cls, cls.replace(" ", "_"), max_videos=15)
