# YouTube Direct Upload Setup

## Goal

Replace Upload-Post with direct YouTube uploads.

Higgsfield still creates the episode. GitHub Actions uploads the finished MP4 and Shorts directly to YouTube.

## Required GitHub Secrets

These values must be stored in GitHub Secrets, never inside code.

- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN
- YOUTUBE_CHANNEL_ID

## Required GitHub Variables

- DEFAULT_UPLOAD_PRIVACY

Recommended starting value:

private

## Upload safety rule

All first tests must upload as private.

Do not use public until the direct upload has been tested successfully.

## Files the uploader should expect

Main episode:

output/<episode-slug>/final.mp4

Shorts:

output/<episode-slug>/shorts/short-1.mp4
output/<episode-slug>/shorts/short-2.mp4
output/<episode-slug>/shorts/short-3.mp4

Thumbnail:

output/<episode-slug>/thumbnail.png

Metadata:

output/<episode-slug>/episode-package.json

## Naming rule

The uploader must use the titles from episode-package.json.

It should not invent new names.

Main episode and Shorts must share the same base episode topic.
