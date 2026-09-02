import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import magic  # pip install python-magic

from common import is_video, get_logger, add_file_handler, iter_files

logger = get_logger(__name__)


@dataclass
class Project:
    name: str = ""
    videos: int = 0
    nonvideos: int = 0
    errors: int = 0

    def total_files(self) -> int:
        return self.videos + self.nonvideos


def _check_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        try:
            result = subprocess.run([tool, "-version"], capture_output=True)
        except FileNotFoundError:
            raise RuntimeError(f"{tool} not found — install ffmpeg before running this tool")
        if result.returncode != 0:
            raise RuntimeError(f"{tool} not found — install ffmpeg before running this tool")


def _is_video(file_path: Path) -> bool:
    mime = magic.Magic(mime=True)
    if mime.from_file(str(file_path)).startswith("video"):
        return True
    # libmagic misidentifies some formats (AVCHD .mts/.m2ts, MPEG-TS, VOB, etc.)
    # as application/octet-stream — fall back to the shared ffprobe-based check
    return is_video(file_path)


def _is_hevc(file_path: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "csv=p=0",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == "hevc"


def _compress_video(src: Path, dst: Path, crf: int) -> Path:
    # H.265 output always in .mp4 container
    dst = dst.with_suffix(".mp4")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if _is_hevc(src):
        # already H.265 — remux instead of a wasteful re-encode
        args = ["ffmpeg", "-i", str(src), "-c", "copy", "-y", str(dst)]
    else:
        args = ["ffmpeg", "-i", str(src), "-vcodec", "libx265", "-crf", str(crf), "-y", str(dst)]
    result = subprocess.run(args, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())
    return dst


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _dir_stats(path: Path) -> tuple[int, int]:
    files = [f for f in path.rglob("*") if f.is_file()]
    return len(files), sum(f.stat().st_size for f in files)


def archive_project(source: Path, destination: Path, crf: int = 28, dry_run: bool = False) -> Project:
    project = Project(name=source.name)

    for root, file in iter_files(source):
        root_path = Path(root)
        rel = root_path.relative_to(source)
        src_file = root_path / file
        dst_file = destination / rel / file

        try:
            if _is_video(src_file):
                out = dst_file.with_suffix(".mp4")
                logger.info('[VIDEO] %s -> %s', src_file, out)
                if not dry_run:
                    out = _compress_video(src_file, dst_file, crf)
                    logger.info('done %s', out)
                project.videos += 1
            else:
                logger.info('[COPY] %s -> %s', src_file, dst_file)
                if not dry_run:
                    _copy_file(src_file, dst_file)
                    logger.info('done %s', dst_file)
                project.nonvideos += 1
        except Exception as exc:
            project.errors += 1
            logger.error('[ERROR] %s: %s', src_file, exc)

    return project


def statistics(source: Path, destination: Path) -> None:
    src_count, src_size = _dir_stats(source)
    dst_count, dst_size = _dir_stats(destination)
    reduction = (1 - dst_size / src_size) * 100 if src_size else 0

    logger.info('--- Statistics ---')
    logger.info('Source:      %d files  %s', src_count, _human_size(src_size))
    logger.info('Destination: %d files  %s', dst_count, _human_size(dst_size))
    if reduction > 0:
        logger.info('Size saved:  %.1f%%', reduction)


def main(source_directory: str, destination_directory: str, crf: int = 28, dry_run: bool = False, log_file=None) -> None:
    source = Path(source_directory).expanduser().resolve()
    destination = Path(destination_directory).expanduser().resolve() / source.name

    if not source.exists():
        logger.error("source '%s' does not exist", source)
        return

    if log_file:
        log_path = Path(destination, 'archiver.log') if log_file is True else Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        add_file_handler(logger, log_path)

    try:
        _check_ffmpeg()
    except RuntimeError as e:
        logger.error(str(e))
        return

    logger.info('Source:      %s', source)
    logger.info('Destination: %s', destination)
    logger.info('Video CRF:   %d (H.265)', crf)
    if dry_run:
        logger.info('Mode:        DRY RUN — no files will be written')

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    project = archive_project(source, destination, crf, dry_run)

    verb = "would compress" if dry_run else "compressed"
    prefix = "(dry-run) " if dry_run else ""
    logger.info(
        '%s%d videos %s, %d files %s, %d errors',
        prefix, project.videos, verb, project.nonvideos,
        'would copy' if dry_run else 'copied', project.errors
    )

    if not dry_run:
        statistics(source, destination)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a project: copy non-video files as-is, compress videos with H.265"
    )
    parser.add_argument("-s", "--source_directory", required=True, help="Source project directory")
    parser.add_argument("-d", "--destination_directory", required=True, help="Destination archive directory")
    parser.add_argument("-c", "--crf", type=int, default=28, help="H.265 CRF quality (lower = better, default 28)")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Show what would be done without writing any files")
    parser.add_argument("-l", "--log-file", nargs="?", const=True,
                         help="also write log output to a file (default: <destination>/archiver.log)")
    args = parser.parse_args()

    main(args.source_directory, args.destination_directory, args.crf, args.dry_run, args.log_file)
