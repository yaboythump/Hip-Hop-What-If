import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


REQUIRED_SECRETS = [
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
    "YOUTUBE_REFRESH_TOKEN",
]

OPTIONAL_SECRETS = [
    "YOUTUBE_CHANNEL_ID",
]

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment secret: {name}")
    return value


def load_package(episode_dir: Path) -> Dict[str, Any]:
    metadata_path = episode_dir / "episode-package.json"
    require_file(metadata_path, "episode metadata")

    with metadata_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_youtube_client():
    client_id = require_env("YOUTUBE_CLIENT_ID")
    client_secret = require_env("YOUTUBE_CLIENT_SECRET")
    refresh_token = require_env("YOUTUBE_REFRESH_TOKEN")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    return build("youtube", "v3", credentials=credentials)


def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str,
    category_id: str = "10",
) -> str:
    require_file(video_path, "video file")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True,
        mimetype="video/mp4",
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading video: {title}")
    response: Optional[Dict[str, Any]] = None

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded video ID: {video_id}")
    return video_id


def upload_thumbnail(youtube, video_id: str, thumbnail_path: Path) -> None:
    if not thumbnail_path.exists():
        print(f"No thumbnail found at {thumbnail_path}. Skipping thumbnail upload.")
        return

    media = MediaFileUpload(str(thumbnail_path), mimetype="image/png")

    youtube.thumbnails().set(
        videoId=video_id,
        media_body=media,
    ).execute()

    print(f"Uploaded thumbnail for video ID: {video_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Direct YouTube uploader for Hip Hop What If.")
    parser.add_argument(
        "--episode-dir",
        required=True,
        help="Example: output/what-if-tupac-signed-with-no-limit",
    )
    parser.add_argument(
        "--privacy",
        default="private",
        choices=["private", "unlisted", "public"],
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate upload package without uploading.",
    )
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir)
    package = load_package(episode_dir)

    final_video = episode_dir / "final.mp4"
    thumbnail = episode_dir / "thumbnail.png"
    shorts_dir = episode_dir / "shorts"

    main_episode = package.get("main_episode", {})
    shorts = package.get("shorts", [])

    print("Hip Hop What If YouTube Upload Check")
    print("-----------------------------------")
    print(f"Episode topic: {package.get('episode_topic')}")
    print(f"Privacy: {args.privacy}")
    print(f"Episode directory: {episode_dir}")
    print(f"Main title: {main_episode.get('title')}")
    print(f"Main expected video: {final_video}")
    print(f"Thumbnail expected: {thumbnail}")
    print(f"Shorts expected folder: {shorts_dir}")

    for short in shorts:
        print(f"Short {short.get('part')}: {short.get('title')} -> {short.get('filename')}")

    missing_secrets = [name for name in REQUIRED_SECRETS if not os.getenv(name)]
    missing_optional = [name for name in OPTIONAL_SECRETS if not os.getenv(name)]

    if missing_secrets:
        print("")
        print("Missing required YouTube secrets:")
        for name in missing_secrets:
            print(f"- {name}")

    if missing_optional:
        print("")
        print("Missing optional YouTube secrets:")
        for name in missing_optional:
            print(f"- {name}")
        print("Continuing is okay. Upload will use the channel tied to the OAuth token.")

    if args.dry_run:
        print("")
        print("Dry run complete. No upload attempted.")
        return

    if missing_secrets:
        raise RuntimeError("Cannot upload until all required YouTube secrets are configured.")

    youtube = get_youtube_client()

    main_title = main_episode.get("title") or package.get("episode_topic") or "Hip Hop What If Episode"
    main_description = main_episode.get("youtube_description") or main_title
    main_tags = main_episode.get("tags") or ["hip hop", "what if", "music history"]

    main_video_id = upload_video(
        youtube=youtube,
        video_path=final_video,
        title=main_title,
        description=main_description,
        tags=main_tags,
        privacy=args.privacy,
    )

    upload_thumbnail(youtube, main_video_id, thumbnail)

    uploaded = {
        "main_episode": {
            "title": main_title,
            "video_id": main_video_id,
            "privacy": args.privacy,
        },
        "shorts": [],
    }

    for short in shorts:
        filename = short.get("filename")
        if not filename:
            print(f"Skipping short with missing filename: {short}")
            continue

        short_path = shorts_dir / filename

        if not short_path.exists():
            print(f"Short file missing, skipping: {short_path}")
            continue

        short_title = short.get("title") or f"{main_title} | Short #{short.get('part')}"
        short_description = f"{short_title}\n\n#Shorts #HipHop #MusicHistory"
        short_tags = ["shorts", "hip hop", "what if", "music history", "rap"]

        short_video_id = upload_video(
            youtube=youtube,
            video_path=short_path,
            title=short_title,
            description=short_description,
            tags=short_tags,
            privacy=args.privacy,
        )

        uploaded["shorts"].append(
            {
                "part": short.get("part"),
                "title": short_title,
                "video_id": short_video_id,
                "privacy": args.privacy,
            }
        )

    upload_result_path = episode_dir / "youtube-upload.json"
    with upload_result_path.open("w", encoding="utf-8") as f:
        json.dump(uploaded, f, indent=2)

    print("")
    print(f"YouTube upload result saved to: {upload_result_path}")


if __name__ == "__main__":
    main()
