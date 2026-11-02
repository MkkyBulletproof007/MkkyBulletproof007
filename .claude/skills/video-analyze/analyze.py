#!/usr/bin/env python3
"""Download a video from a link, grab frames, and transcribe the audio.

Usage:
    python3 analyze.py URL [--out DIR] [--frames N] [--model small] [--lang en]
                           [--cookies cookies.txt] [--no-transcript]

Writes into DIR (default ./video_analysis/<id>):
    video.mp4         the downloaded video
    frames/           N frames spread evenly through the video, named by timestamp
    contact_sheet.jpg all frames on one image, for a quick look
    audio.wav         16 kHz mono audio
    transcript.srt    timed transcript
    transcript.txt    plain transcript with [mm:ss] stamps
    info.json         title, uploader, duration, link, language
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def ensure(module, package):
    try:
        __import__(module)
    except ImportError:
        print(f"Installing {package}...", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", package], check=True)


def stamp(seconds, srt=False):
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if srt:
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def download(url, out, cookies):
    ensure("yt_dlp", "yt-dlp")
    import yt_dlp

    opts = {
        "outtmpl": str(out / "video.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "quiet": True,
        "noprogress": True,
    }
    if cookies:
        opts["cookiefile"] = cookies
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    video = next(out.glob("video.*"))
    return video, info


def duration_of(video):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(video)])
    return float(r.stdout.strip())


def grab_frames(video, out, count, duration):
    frames = out / "frames"
    frames.mkdir(exist_ok=True)
    paths = []
    for i in range(count):
        t = duration * (i + 0.5) / count
        p = frames / f"frame_{i + 1:02d}_{stamp(t).replace(':', 'm')}s.jpg"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video),
             "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2", "-q:v", "3", str(p)])
        paths.append(p)
    cols = 4 if count > 6 else count
    rows = math.ceil(count / cols)
    sheet = out / "contact_sheet.jpg"
    # concat list instead of a glob pattern, which ffmpeg does not support on Windows
    listing = frames / "frames.txt"
    listing.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in paths), encoding="utf-8")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listing),
         "-vf", f"scale=480:-2,tile={cols}x{rows}:padding=6:color=black",
         "-frames:v", "1", "-q:v", "3", str(sheet)])
    return paths, sheet


def transcribe(video, out, model_size, lang):
    audio = out / "audio.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn",
         "-ac", "1", "-ar", "16000", str(audio)])
    ensure("faster_whisper", "faster-whisper")
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio), language=lang, vad_filter=True)
    srt, txt = [], []
    for n, seg in enumerate(segments, 1):
        text = seg.text.strip()
        srt.append(f"{n}\n{stamp(seg.start, True)} --> {stamp(seg.end, True)}\n{text}\n")
        txt.append(f"[{stamp(seg.start)}] {text}")
    (out / "transcript.srt").write_text("\n".join(srt), encoding="utf-8")
    (out / "transcript.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
    return info.language, len(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--out", help="output folder")
    ap.add_argument("--frames", type=int, default=12, help="number of frames to grab")
    ap.add_argument("--model", default="small", help="whisper model: tiny, base, small, medium")
    ap.add_argument("--lang", default=None, help="audio language code, e.g. en or el; default auto")
    ap.add_argument("--cookies", help="cookies.txt for links that need a login, like Instagram")
    ap.add_argument("--no-transcript", action="store_true")
    a = ap.parse_args()

    tmp = Path(a.out or "video_analysis/_download")
    tmp.mkdir(parents=True, exist_ok=True)
    video, info = download(a.url, tmp, a.cookies)
    out = tmp
    if not a.out:
        slug = re.sub(r"[^A-Za-z0-9_-]+", "_", str(info.get("id") or "video"))[:60]
        out = tmp.parent / slug
        if out.exists():
            shutil.rmtree(out)
        tmp.rename(out)
        video = out / video.name

    dur = duration_of(video)
    frames, sheet = grab_frames(video, out, max(1, a.frames), dur)
    lang, lines = (None, 0)
    if not a.no_transcript:
        lang, lines = transcribe(video, out, a.model, a.lang)

    meta = {
        "url": a.url,
        "title": info.get("title"),
        "uploader": info.get("uploader") or info.get("channel"),
        "duration_seconds": round(dur, 1),
        "transcript_language": lang,
        "transcript_lines": lines,
        "frames": [str(p) for p in frames],
        "contact_sheet": str(sheet),
    }
    (out / "info.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"folder": str(out), **meta}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
