from comfy_api.latest import io
from comfy_api.latest import io

from comfy_api.latest import io


class HumanReadableBytesNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="nynxz.Util.HumanReadableBytes",
            display_name="Human Readable Bytes",
            category="Nynxz",
            inputs=[
                io.Int.Input("bytes", display_name="bytes"),
            ],
            outputs=[io.String.Output("string", display_name="string")],
        )

    @classmethod
    def execute(cls, bytes, **kwargs):
        """ """
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0: "Bytes", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        size = bytes
        while size >= power and n < 4:
            size /= power
            n += 1
        hr_bytes = f"{size:.2f} {power_labels[n]}"
        return io.NodeOutput(str(hr_bytes))
