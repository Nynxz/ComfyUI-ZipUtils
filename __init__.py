from comfy_api.latest import ComfyExtension, io

from .nodes.load_zip import LoadZipNode

from .nodes.GetZipInfo import GetZipInfoNode
from .nodes.util.IntToString import IntToStringNode
from .nodes.util.HumanReadableBytes import HumanReadableBytesNode


class NynxzZipUtilsExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            GetZipInfoNode,
            LoadZipNode,
            IntToStringNode,
            HumanReadableBytesNode
        ]


async def comfy_entrypoint() -> ComfyExtension:
    return NynxzZipUtilsExtension()
