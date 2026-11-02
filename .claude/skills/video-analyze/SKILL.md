---
name: video-analyze
description: Use when Mykyta sends a video link (YouTube, Vimeo, Instagram, TikTok, a direct file) and wants it watched, broken down, referenced or transcribed. Downloads the video, grabs evenly spaced frames and a contact sheet, and transcribes the audio with timestamps, so the video can be analysed for structure, shots, hooks, pacing and what is said.
argument-hint: "<video link> [--frames N] [--lang en|el]"
---

# Video Analyze SOP

## Run it
```
python3 .claude/skills/video-analyze/analyze.py "<link>" --frames 12
```
Options:
- `--frames N`: how many frames to grab, spread evenly. Default 12; use 20 to 30 for a breakdown of a whole film.
- `--lang el`: force Greek, `en` for English. Default is auto-detect.
- `--model small`: Whisper size. `base` is faster, `medium` is more accurate for Greek or noisy audio.
- `--no-transcript`: frames only.
- `--cookies cookies.txt`: for links that need a login, like most Instagram reels. Mykyta exports this from his browser; never ask for his password.
- `--out DIR`: where to save. Default `video_analysis/<video id>`. Keep outputs out of git; put them in the scratchpad when one exists.

It installs `yt-dlp` and `faster-whisper` itself if they are missing; `ffmpeg` must already be there.

## Then read the results
1. Open `contact_sheet.jpg` with the Read tool to see the whole video at a glance; open single frames from `frames/` for detail.
2. Read `transcript.txt` for what is said, with `[mm:ss]` stamps.
3. `info.json` has the title, uploader, duration and detected language.

## What to report
Tie it to what Mykyta needs, not a generic summary:
- **Reference for a pitch or shoot:** structure in beats with timestamps, the hook in the first 3 seconds, shot types, lighting, pacing, music, text on screen, how it ends.
- **A prospect's existing video:** whether a videographer or agency is credited, which is ICP test 3, and what the video does and doesn't show. Never criticise their content in outreach; frame film as the missing piece.
- **His own interview footage:** a timed transcript for a paper edit, like the Efthymia SRT.

Quote lines exactly from the transcript. Whisper can mishear names and Greek words, so flag anything uncertain instead of guessing.
