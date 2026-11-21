# OxyPlugins

## OxyRemesher

OxyRemesher is a Blender extension that creates a new quad mesh from an
existing sculpt or mesh. It uses Blender's documented QuadriFlow operator
and runs the solve in a separate, local Blender process.

### Install and use

1. Build the extension with Blender 4.2 or newer from the repository root.

   ```sh
   blender --command extension build --source-dir extensions/oxyremesher
   ```

2. In Blender, open **Edit > Preferences > Get Extensions > Install from
   Disk…** and choose the resulting ZIP.
3. Select a mesh in Object Mode. In the 3D Viewport sidebar, open
   **OxyRemesher > Create Quad Mesh**.
4. Set the target quad count and choose whether to keep sharp features, keep
   open boundaries, or enforce symmetry across the source's local X plane.
   Click **OK**. Press **Esc** to cancel a running solve.
5. The new object appears as **〈source name〉 Quads**. The original object
   remains selected and retains its mesh and modifiers.

The count is approximate. OxyRemesher uses the evaluated surface, including
enabled viewport modifiers. The new object contains geometry and retains the
source's world transform. Transfer UVs, materials, colors, weights, and other
attributes separately if needed. Surfaces with non-manifold or inconsistent
geometry can fail to remesh. This preview uses one global density.

See the [design RFC](docs/rfcs/0001-oxyremesher.md) and
[clean-room source log](docs/CLEAN_ROOM.md). The extension is licensed under
[GPL-3.0-or-later](extensions/oxyremesher/LICENSE).
