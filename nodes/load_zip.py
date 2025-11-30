from comfy_api.latest import ComfyExtension, io
import os
from pathlib import Path
import tempfile
from comfy_api.latest import io
from comfy_extras.nodes_dataset import load_and_process_images
import torch
import numpy as np
from PIL import Image, ImageSequence, ImageOps
import zipfile

from custom_nodes.nynxz_zip_utils.utils.zip import handle_7z, handle_dir, handle_zip


class LoadZipNode(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="nynxz.Loader.Zip",
            display_name="Zip Loader",
            category="Nynxz",
            inputs=[
                io.String.Input("path"),
                io.Combo.Input(
                    "sorting_method",
                    options=["name", "date"],
                    default="name",
                ),
                io.Boolean.Input("reverse_order", default=True),
                io.Int.Input("width", default=512, min=0, max=2048),
                io.Int.Input("height", default=512, min=0, max=2048),
                io.Int.Input("max_images", default=10, min=0, max=1000),
            ],
            outputs=[
                io.Image.Output(
                    id="images", display_name="Image Batch"),
                io.String.Output(
                    id="filenames", display_name="Filenames (one per line)"),
                io.Int.Output(id="count", display_name="Image Count"),
            ]
        )

    @classmethod
    def handle_zip(cls, zip_path: Path, max_images: int):
        output_images = []
        successful_names = []
        w, h = None, None
        with zipfile.ZipFile(zip_path, 'r') as z:
            image_filenames = [
                name for name in z.namelist()
                if name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff', '.avif'))
            ]
            if max_images > 0:
                image_filenames = image_filenames[:max_images]

            for name in image_filenames:
                try:
                    with z.open(name) as file:
                        img = Image.open(file).convert("RGB")
                except Exception as e:
                    print(
                        f"[GalleryLoader] Failed to load {name} from zip: {e}")
                    continue

                for frame in ImageSequence.Iterator(img):
                    frame = ImageOps.exif_transpose(frame)
                    frame = frame.convert("RGB")
                    if w is None and h is None:
                        w, h = frame.size
                    if frame.size != (w, h):
                        continue

                    np_frame = np.array(frame).astype(np.float32) / 255.0
                    torch_frame = torch.from_numpy(np_frame)  # (H, W, C)
                    output_images.append(torch_frame)
                    successful_names.append(Path(name).name)

        return output_images, successful_names

    @classmethod
    def execute(cls, path, sorting_method="name", reverse_order=True, max_images=10, width=512, height=512):
        tensors = []
        names = []
        target_size = (width, height)
        path = Path(path.strip())
        if path.suffix.lower() == ".zip" or path.suffix.lower() == '.7z':
            if path.suffix.lower() == ".7z":
                (tensors, names) = handle_7z(
                    path, max_images, sorting_method, reverse_order)
            else:
                (tensors, names) = handle_zip(
                    path, max_images, sorting_method, reverse_order)
        else:
            (tensors, names) = handle_dir(
                path, max_images, sorting_method, reverse_order)

        images = []
        for img in tensors:
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            bg = Image.new("RGBA", target_size, (0, 0, 0, 0))
            offset = ((target_size[0] - img.width) // 2,
                      (target_size[1] - img.height) // 2)
            bg.paste(img, offset)

            arr = np.array(bg).astype(np.float32) / 255.0          # normalize
            tensor = torch.from_numpy(arr)
            images.append(tensor)

        return io.NodeOutput(
            images,
            "\n".join(names),
            len(names),
        )
