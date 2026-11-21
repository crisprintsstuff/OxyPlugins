# Clean-room source log

- Exoside's [public product page](https://exoside.com/quadremesher/) identifies
  the feature category as automatic quad retopology. This informed the
  high-level workflow only.
- Blender's [object operator documentation](https://docs.blender.org/api/4.2/bpy.ops.object.html#bpy.ops.object.quadriflow_remesh)
  and Blender 4.3.2's public operator RNA describe QuadriFlow's controls.
  OxyRemesher invokes that API through the installed Blender executable.
- Blender's [extension documentation](https://docs.blender.org/manual/en/4.2/advanced/extensions/getting_started.html)
  describes manifest and ZIP packaging.

No proprietary binaries, code, assets, or decompiled material were used.
The implementation and UI were written for OxyRemesher. QuadriFlow is
provided by Blender and is called through its documented API.
