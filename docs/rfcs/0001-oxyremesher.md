# RFC 0001 — OxyRemesher

Status — proposal with a working preview.

## Problem

Artists need an automatic starting mesh for retopology after sculpting.
The original sculpt should stay available for cleanup and attribute transfer.

## Preview design

In Blender Object Mode, open the OxyRemesher sidebar and select
**Create Quad Mesh**. Set an approximate face target and choose whether to
keep sharp features, keep open boundaries, or solve with local-X symmetry.
The result is a separate geometry-only object at the source's world
transform. The operation leaves the original mesh and its modifiers intact.

The extension sends evaluated positions and polygon indices through a
temporary directory to a fresh, background Blender process. The worker calls
the documented QuadriFlow operator and returns an all-quad mesh or an error.
Esc cancels the worker. Blender's native undo removes the finished result.

## Follow-up design work

Test open and hard-surface meshes alongside organic sculpts. Measure solve
time, surface deviation, and actual face count on shareable fixtures. Use
these results to assess attribute transfer, local density controls,
and whether more control over edge flow requires a separate solver.
