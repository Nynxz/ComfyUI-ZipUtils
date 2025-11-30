from dataclasses import dataclass, fields
from pathlib import Path
import tempfile
import py7zr
from PIL import Image

import zipfile

from comfy_api.latest._io import ComfyTypeIO, WidgetInput, comfytype


TARGET_SIZE = (512, 512)  # (width, height)


class SortingMethod:
    NAME = "name"
    DATE = "date"


@dataclass
class ZipLoaderInfo:
    files: int = 0
    directories: int = 0
    images: int = 0
    videos: int = 0
    total_size: int = 0  # in bytes
    file_name: str = ""
    path: str = ""


VIDEOS_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGES_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".avif"}


@comfytype(io_type="NYNXZ_ZIP_LOADER_INFO")
class ZipLoaderInfoType(ComfyTypeIO):
    Type = ZipLoaderInfo

    class Input(WidgetInput):
        def __init__(
            self,
            id: str,
            display_name: str = None,
            optional=False,
            tooltip: str = None,
            lazy: bool = None,
            socketless: bool = None,
            force_input: bool = None,
        ):
            zip_loader_defaults = {f.name: f.default for f in fields(ZipLoaderInfo)}
            super().__init__(
                id=id,
                display_name=display_name,
                optional=optional,
                tooltip=tooltip,
                lazy=lazy,
                default=zip_loader_defaults.get(id),
                socketless=socketless,
                force_input=force_input,
            )

            # store extra attributes for dynamic properties
            for key, value in zip_loader_defaults.items():
                setattr(self, key, value)


def handle_7z(
    path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True
):
    info = ZipLoaderInfo()
    tensors = []
    names = []
    with tempfile.TemporaryDirectory() as tmp:
        info.file_name = path.name
        info.total_size = path.stat().st_size

        with py7zr.SevenZipFile(path) as z:
            z.extractall(tmp)
        # reuse folder code on tmp
        image_count = sum(
            1 for f in Path(tmp).rglob("*") if f.suffix.lower() in IMAGES_EXTENSIONS
        )
        video_count = sum(
            1 for f in Path(tmp).rglob("*") if f.suffix.lower() in VIDEOS_EXTENSIONS
        )
        file_count = sum(1 for f in Path(tmp).rglob("*") if f.is_file())
        dir_count = sum(1 for f in Path(tmp).rglob("*") if f.is_dir())
        info.images = image_count
        info.videos = video_count
        info.files = file_count
        info.directories = dir_count
        info.path = str(path)

        paths = sorted(
            Path(tmp).rglob("*"),
            key=lambda x: x.stat().st_mtime
            if sorting_method == SortingMethod.DATE
            else x.name.lower(),
            reverse=reverse_order,
        )
        for img_path in paths:
            if img_path.is_file() and img_path.suffix.lower() in {
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".bmp",
                ".tiff",
                ".avif",
            }:
                if max_images and len(tensors) >= max_images:
                    break
                img = Image.open(img_path).convert("RGB")
                tensors.append(img)
                names.append(img_path.name)
    return tensors, names, info


def handle_zip(
    path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True
):
    tensors = []
    names = []
    info = ZipLoaderInfo()
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(tmp)
        # reuse folder code on tmp
        image_count = sum(
            1 for f in Path(tmp).rglob("*") if f.suffix.lower() in IMAGES_EXTENSIONS
        )
        video_count = sum(
            1 for f in Path(tmp).rglob("*") if f.suffix.lower() in VIDEOS_EXTENSIONS
        )
        file_count = sum(1 for f in Path(tmp).rglob("*") if f.is_file())
        dir_count = sum(1 for f in Path(tmp).rglob("*") if f.is_dir())
        info.images = image_count
        info.videos = video_count
        info.files = file_count
        info.directories = dir_count
        info.file_name = path.name
        info.total_size = path.stat().st_size
        info.path = str(path)
        paths = sorted(
            Path(tmp).rglob("*"),
            key=lambda x: x.stat().st_mtime
            if sorting_method == SortingMethod.DATE
            else x.name.lower(),
            reverse=reverse_order,
        )
        for img_path in paths:
            if img_path.is_file() and img_path.suffix.lower() in {
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".bmp",
                ".tiff",
                ".avif",
            }:
                if max_images and len(tensors) >= max_images:
                    break
                img = Image.open(img_path).convert("RGB")
                tensors.append(img)
                names.append(img_path.name)
    return tensors, names, info


def handle_dir(
    path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True
):
    tensors = []
    names = []
    info = ZipLoaderInfo()

    paths = sorted(
        path.rglob("*"),
        key=lambda x: x.stat().st_mtime
        if sorting_method == SortingMethod.DATE
        else x.name.lower(),
        reverse=reverse_order,
    )
    image_count = sum(
        1 for f in path.rglob("*") if f.suffix.lower() in IMAGES_EXTENSIONS
    )
    video_count = sum(
        1 for f in path.rglob("*") if f.suffix.lower() in VIDEOS_EXTENSIONS
    )
    file_count = sum(1 for f in path.rglob("*") if f.is_file())
    dir_count = sum(1 for f in path.rglob("*") if f.is_dir())
    info.images = image_count
    info.videos = video_count
    info.files = file_count
    info.directories = dir_count
    info.path = str(path)
    info.total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

    for img_path in paths:
        if not img_path.is_file():
            continue
        if img_path.suffix.lower() not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".tiff",
            ".avif",
        }:
            continue
        if max_images and len(tensors) >= max_images:
            break

        try:
            img = Image.open(img_path).convert("RGB")
            tensors.append(img)
            names.append(img_path.name)
        except Exception as e:
            print(f"[GalleryLoader] Failed {img_path.name}: {e}")
            continue

    return tensors, names, info
