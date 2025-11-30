from comfy_api.latest import io
from comfy_api.latest import io

from comfy_api.latest import io


class IntToStringNode(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="nynxz.Util.IntToString",
            display_name="Int To String",
            category="Nynxz",
            inputs=[
                io.Int.Input("int", display_name="int"),
            ],
            outputs=[
                io.String.Output("string", display_name="string")
            ]
        )

    @classmethod
    def execute(cls, int, **kwargs):
        """
        zip_info: can be a ZipLoaderInfo instance or dict passed from the node input.
        """

        return io.NodeOutput(str(int))
