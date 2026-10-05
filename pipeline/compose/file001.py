"""Reproducible picture-lock compositor for FILE #001.

The module intentionally does not generate media or contact external services.
It joins the owner-approved local source clips and renders the fictional
full-screen anomaly interface with vendored OFL fonts.  Narration, music and
final loudness processing are deliberately separate stages.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


WIDTH = 1080
HEIGHT = 1920
FRAME_RATE = 30


@dataclass(frozen=True)
class Scene:
    scene_id: str
    seconds: float
    source: str | None
    kind: str


SCENES = (
    Scene("scene-01", 3.8, "clips/scene-01-global-message-v3.mp4", "source"),
    Scene("scene-02", 2.2, None, "message-one"),
    Scene("scene-03", 3.5, "clips/scene-03-reaction-v3.mp4", "source"),
    Scene("scene-04", 2.0, "clips/scene-04-normal-moon.mp4", "moon-viewfinder"),
    Scene("scene-05", 3.0, "clips/scene-05-stream-grid.mp4", "source"),
    Scene("scene-06", 5.0, "clips/scene-06-moon-reveal.mp4", "source"),
    Scene("scene-07", 5.0, "clips/scene-07-consequence-v2.mp4", "source"),
    Scene("scene-08", 5.0, None, "message-two"),
    Scene("scene-09", 3.5, None, "archive"),
)


def compose_file_001_picture_lock(repository_root: Path, ffmpeg: str | None = None) -> Path:
    """Render the silent visual master for FILE #001 and return its path.

    Raises ``FileNotFoundError`` before rendering if any required generated
    clip or licensed typeface is unavailable.  All on-screen strings are
    written to UTF-8 text files and fed to FFmpeg through the text-file
    option, rather than an inline string option.
    """
    root = repository_root.resolve()
    binary = _resolve_ffmpeg(ffmpeg)
    output = root / "output" / "file-001"
    clips = output / "clips"
    work = output / "compose"
    work.mkdir(parents=True, exist_ok=True)
    fonts = root / "assets" / "fonts"
    mono_regular = fonts / "IBMPlexMono-Regular.ttf"
    mono_bold = fonts / "IBMPlexMono-Bold.ttf"
    inter = fonts / "Inter-Variable.ttf"
    for path in (mono_regular, mono_bold, inter):
        _require(path)

    text = _write_text_assets(work)
    rendered: list[Path] = []
    for scene in SCENES:
        destination = work / f"{scene.scene_id}.mp4"
        if scene.kind == "source" or scene.kind == "moon-viewfinder":
            assert scene.source is not None
            source = output / scene.source
            _require(source)
            _render_source_scene(binary, source, destination, scene, mono_regular, text)
        elif scene.kind == "message-one":
            _render_message_scene(binary, destination, scene, mono_regular, mono_bold, text, blinking=True)
        elif scene.kind == "message-two":
            _render_message_scene(binary, destination, scene, mono_regular, mono_bold, text, blinking=False)
        elif scene.kind == "archive":
            _render_archive_scene(binary, destination, scene, inter, text)
        else:
            raise ValueError(f"unsupported composition scene kind: {scene.kind}")
        rendered.append(destination)

    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{path.name}'\n" for path in rendered), encoding="utf-8")
    final = output / "final" / "file-001-picture-lock.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            binary, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
            "-i", str(concat), "-an", "-c", "copy", "-movflags", "+faststart", str(final),
        ],
        root,
    )
    return final


def _write_text_assets(work: Path) -> dict[str, Path]:
    values = {
        "time": "03:17:00 UTC\n",
        "message_one": "DON'T LOOK\nAT THE MOON.\n",
        "message_two": "WE SAW\nYOU TOO.\n",
        "archive": "FILE #001 — ARCHIVED\n",
        "message_one_line_one": "DON'T LOOK\n",
        "message_one_line_two": "AT THE MOON.\n",
        "message_two_line_one": "WE SAW\n",
        "message_two_line_two": "YOU TOO.\n",
    }
    files: dict[str, Path] = {}
    for key, value in values.items():
        path = work / f"{key}.txt"
        path.write_text(value, encoding="utf-8")
        files[key] = path
    ass_documents = {
        "scene_one_overlay": _ass_document(
            "Inter", "Meta", 36, "99F4F4F4", 7, 80, 90, "03:17:00 UTC"
        ),
        "message_one_overlay": _ass_document(
            "IBM Plex Mono", "Message", 118, "00F4F4F4", 7, 130, 730,
            "DON'T LOOK\\NAT THE MOON.",
            secondary_style=("Meta", "IBM Plex Mono", 36, "99F4F4F4", 7, 130, 130, "03:17:00 UTC"),
        ),
        "message_two_overlay": _ass_document(
            "IBM Plex Mono", "Message", 118, "00F4F4F4", 7, 130, 730,
            "WE SAW\\NYOU TOO.",
            secondary_style=("Meta", "IBM Plex Mono", 36, "99F4F4F4", 7, 130, 130, "03:17:00 UTC"),
        ),
        "archive_overlay": _ass_document(
            "Inter", "Archive", 54, "00F4F4F4", 8, 0, 900, "FILE #001 — ARCHIVED"
        ),
    }
    for key, document in ass_documents.items():
        path = work / f"{key}.ass"
        path.write_text(document, encoding="utf-8")
        files[key] = path
    return files


def _ass_document(
    font_name: str,
    style_name: str,
    size: int,
    color: str,
    alignment: int,
    margin_l: int,
    margin_v: int,
    message: str,
    *,
    secondary_style: tuple[str, str, int, str, int, int, int, str] | None = None,
) -> str:
    header = "[Script Info]\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\n"
    primary = (
        f"Style: {style_name},{font_name},{size},&H{color},&H{color},&H00000000,&H00000000,"
        f"0,0,0,0,100,100,0,0,1,0,0,{alignment},{margin_l},0,{margin_v},1\n"
    )
    secondary = ""
    event_secondary = ""
    if secondary_style:
        name, second_font, second_size, second_color, second_alignment, second_left, second_vertical, second_message = secondary_style
        secondary = (
            f"Style: {name},{second_font},{second_size},&H{second_color},&H{second_color},&H00000000,&H00000000,"
            f"0,0,0,0,100,100,0,0,1,0,0,{second_alignment},{second_left},0,{second_vertical},1\n"
        )
        event_secondary = f"Dialogue: 0,0:00:00.00,0:00:10.00,{name},,0,0,0,,{second_message}\n"
    events = "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    return header + primary + secondary + "\n" + events + event_secondary + f"Dialogue: 0,0:00:00.00,0:00:10.00,{style_name},,0,0,0,,{message}\n"


def _render_source_scene(
    ffmpeg: str,
    source: Path,
    destination: Path,
    scene: Scene,
    mono_regular: Path,
    text: dict[str, Path],
) -> None:
    filters = ["scale=1080:1920:flags=lanczos", "setsar=1"]
    if scene.scene_id == "scene-01":
        filters.append(_subtitles_filter(text["scene_one_overlay"], mono_regular.parent))
    if scene.kind == "moon-viewfinder":
        # Minimal original framing brackets; this is not a real camera UI.
        filters.extend((
            "drawbox=x=132:y=470:w=150:h=8:color=0xF4F4F4@0.60:t=fill",
            "drawbox=x=132:y=470:w=8:h=150:color=0xF4F4F4@0.60:t=fill",
            "drawbox=x=798:y=470:w=150:h=8:color=0xF4F4F4@0.60:t=fill",
            "drawbox=x=940:y=470:w=8:h=150:color=0xF4F4F4@0.60:t=fill",
        ))
    _run(
        [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(source), "-t", str(scene.seconds),
            "-vf", ",".join(filters), "-an", "-r", str(FRAME_RATE), "-c:v", "libx264", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-movflags", "+faststart", str(destination),
        ],
        source.parent.parents[2],
    )


def _render_message_scene(
    ffmpeg: str,
    destination: Path,
    scene: Scene,
    mono_regular: Path,
    mono_bold: Path,
    text: dict[str, Path],
    *,
    blinking: bool,
) -> None:
    cursor_enable = ":enable='lt(mod(t\\,1)\\,0.5)'" if blinking else ""
    cursor_x = "992" if blinking else "700"
    filters = [
        _subtitles_filter(text["message_one_overlay"] if blinking else text["message_two_overlay"], mono_regular.parent),
        # Monospaced text is fixed-width; these positions derive from the text
        # metric (0.6 × font size × characters on the final line), not a phone UI.
        f"drawbox=x={cursor_x}:y=880:w=52:h=112:color=0xE0161E@1:t=fill{cursor_enable}",
    ]
    _run(
        [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
            f"color=c=0x0B0B0B:s={WIDTH}x{HEIGHT}:r={FRAME_RATE}:d={scene.seconds}", "-vf", ",".join(filters),
            "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FRAME_RATE),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart",
            str(destination),
        ],
        destination.parent.parents[2],
    )


def _render_archive_scene(ffmpeg: str, destination: Path, scene: Scene, inter: Path, text: dict[str, Path]) -> None:
    filters = [
        "drawbox=x=170:y=840:w=740:h=2:color=0xF4F4F4@0.70:t=fill",
        _subtitles_filter(text["archive_overlay"], inter.parent),
        "drawbox=x=170:y=1020:w=740:h=2:color=0xF4F4F4@0.70:t=fill",
    ]
    _run(
        [
            ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
            f"color=c=black:s={WIDTH}x{HEIGHT}:r={FRAME_RATE}:d={scene.seconds}", "-vf", ",".join(filters),
            "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FRAME_RATE),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart",
            str(destination),
        ],
        destination.parent.parents[2],
    )


def _drawtext(font: Path, textfile: Path, color: str, size: int, x: str, y: str, *, line_spacing: int = 0) -> str:
    return (
        f"drawtext=fontfile='{_filter_path(font)}':textfile='{_filter_path(textfile)}':fontcolor={color}:"
        f"fontsize={size}:line_spacing={line_spacing}:x={x}:y={y}"
    )


def _subtitles_filter(document: Path, fonts_dir: Path) -> str:
    return f"subtitles=filename='{_filter_path(document)}':fontsdir='{_filter_path(fonts_dir)}'"


def _filter_path(path: Path) -> str:
    return path.resolve().as_posix().replace(":", r"\:")


def _resolve_ffmpeg(explicit: str | None) -> str:
    if explicit:
        return explicit
    if located := shutil.which("ffmpeg"):
        return located
    winget = Path.home() / "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
    if winget.is_file():
        return str(winget)
    raise FileNotFoundError("FFmpeg not found; set FFMPEG_BIN or install FFmpeg 9.0.2")


def _require(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"required composition asset is missing: {path}")


def _run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)
