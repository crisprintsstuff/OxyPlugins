# Agent instructions

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the
[OxyBrush agent guidance](https://github.com/crisprintsstuff/OxyBrush/blob/main/AGENTS.md)
where applicable. The Python Blender extension follows the same boundary as
OxyBrush's Blender add-on. Keep Blender API code within the GPL extension.
Keep any future Rust core free of Blender and GPU dependencies, written in
safe Rust and compatible with OxyBrush's licensing rules.

Work on feature branches and use signed-off commits. Open a PR for review
when the repository has a base branch. User-facing designs go through an RFC.
Keep solver work out of Blender's UI process. Preserve the input and make each
successful edit undoable. No telemetry or network access in the extension.
Report which Blender versions and platforms were actually exercised.
