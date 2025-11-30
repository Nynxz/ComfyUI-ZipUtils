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

from custom_nodes.nynxz_zip_utils.utils.zip import (
    ZipLoaderInfoType,
    handle_7z,
    handle_dir,
    handle_zip,
)


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
                io.Image.Output(id="images", display_name="Image Batch"),
                io.String.Output(
                    id="filenames", display_name="Filenames (one per line)"
                ),
                io.Int.Output(id="count", display_name="Image Count"),
                ZipLoaderInfoType.Output(id="zip_info", display_name="zip_info"),
            ],
        )

    @classmethod
    def execute(
        cls,
        path,
        sorting_method="name",
        reverse_order=True,
        max_images=10,
        width=512,
        height=512,
    ):
        tensors = []
        names = []
        info = None
        target_size = (width, height)
        path = Path(path.strip())
        if path.suffix.lower() == ".zip" or path.suffix.lower() == ".7z":
            if path.suffix.lower() == ".7z":
                (tensors, names, info) = handle_7z(
                    path, max_images, sorting_method, reverse_order
                )
            else:
                (tensors, names, info) = handle_zip(
                    path, max_images, sorting_method, reverse_order
                )
        else:
            (tensors, names, info) = handle_dir(
                path, max_images, sorting_method, reverse_order
            )

        images = []
        for img in tensors:
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            bg = Image.new("RGBA", target_size, (0, 0, 0, 0))
            offset = (
                (target_size[0] - img.width) // 2,
                (target_size[1] - img.height) // 2,
            )
            bg.paste(img, offset)

            arr = np.array(bg).astype(np.float32) / 255.0  # normalize
            tensor = torch.from_numpy(arr)
            images.append(tensor)

        return io.NodeOutput(images, "\n".join(names), len(names), info)
