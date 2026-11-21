# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise the installed extension in background Blender."""

import bpy


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, location=(2, -3, 4))
source = bpy.context.active_object
original_mesh = source.data
original_faces = len(original_mesh.polygons)
subdivision = source.modifiers.new("Sculpt detail", "SUBSURF")
subdivision.levels = 1

assert bpy.ops.object.oxyremesher_create(target_faces=400) == {"FINISHED"}
output = bpy.data.objects.get(f"{source.name} Quads")
assert output and output.data != original_mesh
assert output.matrix_world == source.matrix_world
assert 200 <= len(output.data.polygons) <= 800
assert all(len(face.vertices) == 4 for face in output.data.polygons)
assert source.data == original_mesh and len(source.data.polygons) == original_faces
assert source.modifiers.get("Sculpt detail") == subdivision
assert bpy.context.active_object == source

assert bpy.ops.object.oxyremesher_create(target_faces=400, mirror_x=True) == {"FINISHED"}
symmetric = bpy.data.objects.get(f"{source.name} Quads.001")
assert symmetric and len(symmetric.data.polygons) > 0
assert all(len(face.vertices) == 4 for face in symmetric.data.polygons)
positions = {tuple(round(axis, 4) for axis in vertex.co) for vertex in symmetric.data.vertices}
assert all((-x, y, z) in positions for x, y, z in positions)

# A failed solve must leave the scene untouched.
empty_mesh = bpy.data.meshes.new("Empty geometry")
empty = bpy.data.objects.new("Empty geometry", empty_mesh)
bpy.context.scene.collection.objects.link(empty)
bpy.context.view_layer.objects.active = empty
count = len(bpy.context.scene.objects)
try:
    result = bpy.ops.object.oxyremesher_create()
except RuntimeError as error:
    assert "Select a mesh with faces" in str(error)
else:
    assert result == {"CANCELLED"}
assert len(bpy.context.scene.objects) == count

print(f"OxyRemesher smoke test passed with {len(output.data.polygons)} quads")
