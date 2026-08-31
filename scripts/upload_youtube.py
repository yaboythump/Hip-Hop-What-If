import argparse
import json
import os
from pathlib import Path


REQUIRED_SECRETS = [
    "YOUTUBE_CLIENT_ID",
    "YOUTUBE_CLIENT_SECRET",
    "YOUTUBE_REFRESH_TOKEN",
    "YOUTUBE_CHANNEL_ID",
]


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Direct YouTube uploader for Hip Hop What If.")
    parser.add_argument("--episode-dir", required=True, help="Example: output/what-if-tupac-signed-with-no-limit")
    parser.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    parser.add_argument("--dry-run", action="store_true", help="Validate upload package without uploading.")
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir)
    metadata_path = episode_dir / "episode-package.json"
    final_video = episode_dir / "final.mp4"
    thumbnail = episode_dir / "thumbnail.png"
    shorts_dir = episode_dir / "shorts"

    require_file(metadata_path, "episode metadata")

    with metadata_path.open("r", encoding="utf-8") as f:
        package = json.load(f)

    missing_secrets = [name for name in REQUIRED_SECRETS if not os.getenv(name)]

    print("Hip Hop What If YouTube Upload Check")
    print("-----------------------------------")
    print(f"Episode topic: {package.get('episode_topic')}")
    print(f"Privacy: {args.privacy}")
    print(f"Episode directory: {episode_dir}")
    print(f"Main title: {package.get('main_episode', {}).get('title')}")
    print(f"Main expected video: {final_video}")
    print(f"Thumbnail expected: {thumbnail}")
    print(f"Shorts expected folder: {shorts_dir}")

    for short in package.get("shorts", []):
        print(f"Short {short.get('part')}: {short.get('title')} -> {short.get('filename')}")

    if missing_secrets:
        print("")
        print("Missing YouTube secrets:")
        for name in missing_secrets:
            print(f"- {name}")

    if args.dry_run:
        print("")
        print("Dry run complete. No upload attempted.")
        return

    if missing_secrets:
        raise RuntimeError("Cannot upload until all YouTube secrets are configured.")

    require_file(final_video, "main episode video")
    require_file(thumbnail, "thumbnail")

    raise NotImplementedError(
        "Direct YouTube upload is not active yet. Next phase adds Google API upload logic."
    )


if __name__ == "__main__":
    main()
