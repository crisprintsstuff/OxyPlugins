# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the documented Blender remesher in an isolated background process."""

import json
from pathlib import Path
import sys

import bpy


def solve(vertices, faces, options):
    mesh = bpy.data.meshes.new("Remesh geometry")
    mesh.from_pydata(vertices, [], faces)
    if mesh.validate():
        raise ValueError("The evaluated mesh contains invalid geometry")
    mesh.update()

    obj = bpy.data.objects.new("Remesh input", mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mesh.use_mirror_x = options["use_mesh_symmetry"]

    result = bpy.ops.object.quadriflow_remesh(mode="FACES", **options)
    if result != {"FINISHED"}:
        raise ValueError("QuadriFlow could not remesh this surface")
    output = obj.data
    if not output.polygons or any(len(face.vertices) != 4 for face in output.polygons):
        raise ValueError("QuadriFlow did not produce an all-quad surface")
    geometry = {
        "vertices": [list(vertex.co) for vertex in output.vertices],
        "faces": [list(face.vertices) for face in output.polygons],
    }
    if geometry["vertices"] == vertices and geometry["faces"] == faces:
        raise ValueError("QuadriFlow returned the input mesh unchanged")
    return geometry


if __name__ == "__main__":
    folder = Path(sys.argv[sys.argv.index("--") + 1])
    try:
        request = json.loads((folder / "input.json").read_text(encoding="utf-8"))
        response = solve(**request)
    except Exception as error:
        response = {"error": str(error)}
    (folder / "output.json").write_text(json.dumps(response), encoding="utf-8")
