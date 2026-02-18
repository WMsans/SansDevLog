# Video Builder Module Design

## Overview

Provide a minimal video assembly utility that writes frame images to disk and
invokes ffmpeg to combine frames with an audio track into an MP4 video.

## Goals

- Save sequentially numbered PNG frames to a target directory.
- Assemble a video from `frame_%06d.png` and an audio file.
- Keep configuration minimal (fps, resolution) to match CLI pipeline needs.

## Non-Goals

- Variable frame naming or non-sequential frame lists.
- Advanced encoding controls beyond a sensible default preset.

## API

- `save_frames(frames: list[Image.Image], output_dir: str, prefix: str = "frame") -> None`
- `assemble_video(frames_dir: str, audio_path: str, output_path: str, config: dict) -> str`

## Data Flow

1) CLI pipeline generates PIL frames and typing audio.
2) `save_frames` writes `prefix_%06d.png` into `frames_dir`.
3) `assemble_video` runs ffmpeg over `frames_dir/frame_%06d.png` and `audio_path`.
4) Returns `output_path` for downstream use.

## Error Handling

- Let ffmpeg errors surface via `subprocess.run(..., check=True)`.
- Expect callers to handle ffmpeg availability and user-facing messaging.

## Testing

- Unit tests verify `save_frames` writes expected count and handles empty input.
- Video assembly is not unit-tested here to avoid ffmpeg dependency in tests.
