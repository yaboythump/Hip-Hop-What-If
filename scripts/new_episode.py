import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "episode"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Hip Hop What If test episode package.")
    parser.add_argument("--episode-topic", required=True)
    parser.add_argument("--upload-privacy", required=True, choices=["private", "unlisted", "public"])
    args = parser.parse_args()

    topic = args.episode_topic.strip()
    slug = slugify(topic)
    now = datetime.now(timezone.utc).isoformat()

    episode_title = topic
    short_titles = [
        f"{topic} | Short #1",
        f"{topic} | Short #2",
        f"{topic} | Short #3",
    ]

    package = {
        "channel": "Hip Hop What If",
        "created_at": now,
        "episode_topic": topic,
        "episode_slug": slug,
        "upload_privacy": args.upload_privacy,
        "protected_rule": "Do not change the episode look, format, naming style, or production feel unless explicitly requested.",
        "main_episode": {
            "title": episode_title,
            "filename": f"{slug}-full-episode.mp4",
            "youtube_description": f"{topic}\\n\\nA cinematic Hip Hop What If alternate-history episode.",
            "tags": ["hip hop", "what if", "music history", "rap", "alternate history"],
        },
        "shorts": [
            {
                "part": 1,
                "title": short_titles[0],
                "filename": f"{slug}-short-1.mp4",
            },
            {
                "part": 2,
                "title": short_titles[1],
                "filename": f"{slug}-short-2.mp4",
            },
            {
                "part": 3,
                "title": short_titles[2],
                "filename": f"{slug}-short-3.mp4",
            },
        ],
        "next_steps": [
            "Connect real Higgsfield production output.",
            "Preserve existing episode visual style.",
            "Add direct YouTube upload after final MP4 and Shorts exist.",
        ],
    }

    output_dir = Path("output") / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "episode-package.json").open("w", encoding="utf-8") as f:
        json.dump(package, f, indent=2)

    with (output_dir / "README.txt").open("w", encoding="utf-8") as f:
        f.write(f"Hip Hop What If test package\\n")
        f.write(f"Episode topic: {topic}\\n")
        f.write(f"Upload privacy: {args.upload_privacy}\\n")
        f.write(f"Main title: {episode_title}\\n")
        f.write("\\nShort titles:\\n")
        for title in short_titles:
            f.write(f"- {title}\\n")

    print(f"Built test episode package for: {topic}")
    print(f"Output folder: {output_dir}")


if __name__ == "__main__":
    main()
