# Contributing

Use feature branches, sign off every commit with `git commit -s`, and submit
changes for review. Document user-facing proposals under `docs/rfcs/` and
allow a week for discussion before acceptance. See the
[OxyBrush contribution guide](https://github.com/crisprintsstuff/OxyBrush/blob/main/CONTRIBUTING.md)
for the DCO and clean-room rules.

Use public documentation, published papers, and documented APIs. Record
sources in [the clean-room log](docs/CLEAN_ROOM.md). Use original code, UI,
and assets. The Blender extension uses GPL-3.0-or-later, matching the
licensing boundary of OxyBrush's Blender integration.

## Verification

From the repository root, build and test using an isolated Blender profile
so your own preferences and extensions are preserved.

```sh
stage=$(mktemp -d)
blender --command extension validate extensions/oxyremesher
blender --command extension build --source-dir extensions/oxyremesher --output-dir "$stage"
export BLENDER_USER_RESOURCES="$stage/blender"
blender --command extension install-file -r user_default -e "$stage/oxyremesher-0.1.0.zip"
blender -b --python-exit-code 1 --python tests/smoke_blender.py
git diff --check
```

For changes to the interactive operator, also run Blender with a viewport
and check the dialog, cancellation, and undo.
