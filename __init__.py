from comfy_api.latest import ComfyExtension, io

from .nodes.load_zip import LoadZipNode


class NynxzZipUtilsExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            LoadZipNode
        ]


async def comfy_entrypoint() -> ComfyExtension:
    return NynxzZipUtilsExtension()
