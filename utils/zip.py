
from pathlib import Path
import tempfile
import py7zr
from PIL import Image

import zipfile


TARGET_SIZE = (512, 512)  # (width, height)


class SortingMethod:
    NAME = 'name'
    DATE = 'date'


def handle_7z(path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True):
    tensors = []
    names = []
    with tempfile.TemporaryDirectory() as tmp:
        with py7zr.SevenZipFile(path) as z:
            z.extractall(tmp)
        # reuse folder code on tmp
        paths = sorted(
            Path(tmp).rglob("*"),
            key=lambda x: x.stat().st_mtime if sorting_method == SortingMethod.DATE else x.name.lower(),
            reverse=reverse_order
        )
        for img_path in paths:
            if img_path.is_file() and img_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.avif'}:
                if max_images and len(tensors) >= max_images:
                    break
                img = Image.open(img_path).convert("RGB")
                tensors.append(img)
                names.append(img_path.name)
    return tensors, names


def handle_zip(path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True):
    tensors = []
    names = []
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(path, 'r') as z:
            z.extractall(tmp)
        # reuse folder code on tmp
        paths = sorted(
            Path(tmp).rglob("*"),
            key=lambda x: x.stat().st_mtime if sorting_method == SortingMethod.DATE else x.name.lower(),
            reverse=reverse_order
        )
        for img_path in paths:
            if img_path.is_file() and img_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.avif'}:
                if max_images and len(tensors) >= max_images:
                    break
                img = Image.open(img_path).convert("RGB")
                tensors.append(img)
                names.append(img_path.name)
    return tensors, names


def handle_dir(path: Path, max_images: int, sorting_method=SortingMethod.NAME, reverse_order=True):
    tensors = []
    names = []

    paths = sorted(
        path.rglob("*"),
        key=lambda x: x.stat().st_mtime if sorting_method == SortingMethod.DATE else x.name.lower(),
        reverse=reverse_order
    )

    for img_path in paths:
        print(img_path.name)
        print(img_path)
        if not img_path.is_file():
            continue
        if img_path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.avif'}:
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

    return tensors, names
