# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-destructive quad retopology for Blender."""

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, IntProperty


_active_jobs = []


class OXYREMESHER_OT_create(bpy.types.Operator):
    """Create a separate quad mesh from the active mesh's evaluated surface"""

    bl_idname = "object.oxyremesher_create"
    bl_label = "Create Quad Mesh"
    bl_options = {"UNDO"}

    target_faces: IntProperty(name="Target quads", default=2000, min=100, max=100_000)
    preserve_sharp: BoolProperty(name="Keep sharp features", default=True)
    preserve_boundary: BoolProperty(name="Keep open boundaries", default=True)
    mirror_x: BoolProperty(name="Symmetry across local X", default=False)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and obj.mode == "OBJECT"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_faces")
        layout.separator()
        layout.prop(self, "preserve_sharp")
        layout.prop(self, "preserve_boundary")
        layout.prop(self, "mirror_x")

    def execute(self, context):
        if _active_jobs:
            self.report({"WARNING"}, "OxyRemesher is already running")
            return {"CANCELLED"}
        self.timer = None
        self.process = None
        self.temporary = None
        self.manager = context.window_manager
        self.scene = context.scene
        source = context.active_object
        self.result_name = f"{source.name} Quads"
        evaluated = source.evaluated_get(context.evaluated_depsgraph_get())
        self.transform = evaluated.matrix_world.copy()
        geometry = evaluated.to_mesh()
        try:
            if not geometry.polygons:
                self.report({"ERROR"}, "Select a mesh with faces")
                return {"CANCELLED"}
            request = {
                "vertices": [list(vertex.co) for vertex in geometry.vertices],
                "faces": [list(face.vertices) for face in geometry.polygons],
                "options": {
                    "target_faces": self.target_faces,
                    "use_preserve_sharp": self.preserve_sharp,
                    "use_preserve_boundary": self.preserve_boundary,
                    "use_mesh_symmetry": self.mirror_x,
                },
            }
        finally:
            evaluated.to_mesh_clear()

        try:
            self.temporary = TemporaryDirectory(prefix="oxyremesher-")
            self.folder = Path(self.temporary.name)
            (self.folder / "input.json").write_text(json.dumps(request), encoding="utf-8")
            with (self.folder / "worker.log").open("w", encoding="utf-8") as log:
                self.process = subprocess.Popen(
                    [bpy.app.binary_path, "--background", "--factory-startup",
                     "--disable-autoexec", "--python-exit-code", "1",
                     "--python", str(Path(__file__).with_name("worker.py")),
                     "--", str(self.folder)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
            if bpy.app.background:
                self.process.wait()
                return self.finish(context)
            self.timer = self.manager.event_timer_add(0.2, window=context.window)
            self.manager.modal_handler_add(self)
            _active_jobs.append(self)
            self.report({"INFO"}, "Building quad mesh. Press Esc to cancel.")
            return {"RUNNING_MODAL"}
        except (OSError, RuntimeError) as error:
            self.cleanup()
            self.report({"ERROR"}, f"Could not start remeshing: {error}")
            return {"CANCELLED"}

    def modal(self, context, event):
        if self.process is None:
            return {"CANCELLED"}
        if event.type == "ESC":
            self.cancel(context)
            self.report({"INFO"}, "Remeshing cancelled")
            return {"CANCELLED"}
        if event.type == "TIMER" and event.timer == self.timer:
            if self.process.poll() is not None:
                return self.finish(context)
        return {"PASS_THROUGH"}

    def finish(self, context):
        try:
            if self.process.returncode:
                raise RuntimeError("The background Blender process exited unexpectedly")
            result = json.loads((self.folder / "output.json").read_text(encoding="utf-8"))
            if "error" in result:
                raise ValueError(result["error"])
            if context.scene != self.scene:
                raise RuntimeError("The active scene changed during remeshing")

            mesh = bpy.data.meshes.new(self.result_name)
            obj = None
            try:
                mesh.from_pydata(result["vertices"], [], result["faces"])
                mesh.update()
                obj = bpy.data.objects.new(self.result_name, mesh)
                obj.matrix_world = self.transform
                self.scene.collection.objects.link(obj)
            except Exception:
                if obj is not None:
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.meshes.remove(mesh)
                raise
            self.report({"INFO"}, f"Created {obj.name} with {len(mesh.polygons):,} quads")
            return {"FINISHED"}
        except (OSError, ValueError, RuntimeError, ReferenceError) as error:
            self.report({"ERROR"}, f"Remeshing failed: {error}")
            return {"CANCELLED"}
        finally:
            self.cleanup()

    def cancel(self, context):
        self.cleanup()

    def cleanup(self):
        if self.timer is not None:
            self.manager.event_timer_remove(self.timer)
            self.timer = None
        if self in _active_jobs:
            _active_jobs.remove(self)
        if self.process is not None:
            if self.process.poll() is None:
                self.process.kill()
                self.process.wait()
            self.process = None
        if self.temporary is not None:
            self.temporary.cleanup()
            self.temporary = None


class OXYREMESHER_PT_tools(bpy.types.Panel):
    bl_label = "OxyRemesher"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OxyRemesher"

    def draw(self, context):
        self.layout.operator(OXYREMESHER_OT_create.bl_idname, icon="MOD_REMESH")
        if _active_jobs:
            self.layout.label(text="Building quad mesh… Esc cancels")


_classes = (OXYREMESHER_OT_create, OXYREMESHER_PT_tools)


@persistent
def _cancel_before_load(_):
    for job in _active_jobs[:]:
        job.cleanup()


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_pre.append(_cancel_before_load)


def unregister():
    bpy.app.handlers.load_pre.remove(_cancel_before_load)
    _cancel_before_load(None)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
