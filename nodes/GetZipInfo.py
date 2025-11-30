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
    ZipLoaderInfo,
    ZipLoaderInfoType,
    handle_7z,
    handle_dir,
    handle_zip,
)

from comfy_api.latest import io
from dataclasses import fields


def _outputs_from_type(dataclass_type, id_prefix=""):
    """
    Generate ComfyUI outputs dynamically from a dataclass type.
    `id_prefix` can be used to namespace outputs if needed.
    """
    outputs = []
    for f in fields(dataclass_type):
        attr_name = f.name
        default_value = f.default

        # determine ComfyUI output type based on Python type
        if isinstance(default_value, str):
            outputs.append(
                io.String.Output(id=f"{id_prefix}{attr_name}", display_name=attr_name)
            )
        elif isinstance(default_value, int):
            outputs.append(
                io.Int.Output(id=f"{id_prefix}{attr_name}", display_name=attr_name)
            )
        elif isinstance(default_value, float):
            outputs.append(
                io.Float.Output(id=f"{id_prefix}{attr_name}", display_name=attr_name)
            )
        else:
            # fallback to a generic type if needed
            outputs.append(
                io.String.Output(id=f"{id_prefix}{attr_name}", display_name=attr_name)
            )
    return outputs


class GetZipInfoNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="nynxz.Info.Zip",
            display_name="Get Zip Info",
            category="Nynxz",
            inputs=[
                ZipLoaderInfoType.Input("zip_info", display_name="zip_info"),
            ],
            outputs=_outputs_from_type(ZipLoaderInfoType.Type, id_prefix="zip_info."),
        )

    @classmethod
    def execute(cls, zip_info, **kwargs):
        """
        zip_info: can be a ZipLoaderInfo instance or dict passed from the node input.
        """
        if isinstance(zip_info, dict):
            zip_info = ZipLoaderInfo(**zip_info)  # convert dict to dataclass

        # Build NodeOutput dynamically
        output_dict = {f.name: getattr(zip_info, f.name) for f in fields(ZipLoaderInfo)}
        return io.NodeOutput(*output_dict.values())
