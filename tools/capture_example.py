"""Run one Newton example headless and save PNG screenshots.

Drives the example the same way ``newton.examples.run()`` does, but with a
headless ViewerGL, and calls ``viewer.get_frame()`` at chosen frames instead of
opening a window. Nothing about the example itself is modified.

Usage:
    il.bat -p tools\\capture_example.py cloth_hanging --out out\\shots
    il.bat -p tools\\capture_example.py cloth_hanging --out out\\shots --frames 200 --shots 3
    il.bat -p tools\\capture_example.py cloth_hanging --out out\\shots -- --solver style3d

Anything after a bare ``--`` is forwarded to the example's own parser.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import time
import traceback


def parse_own_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Split our args from the ones meant for the example."""
    if "--" in argv:
        cut = argv.index("--")
        ours, theirs = argv[:cut], argv[cut + 1 :]
    else:
        ours, theirs = argv, []

    p = argparse.ArgumentParser(description="Capture PNG screenshots from a Newton example.")
    p.add_argument("example", help="Example name as printed by 'python -m newton.examples --list'.")
    p.add_argument("--out", default="out/shots", help="Output directory for PNG files.")
    p.add_argument("--frames", type=int, default=150, help="Total frames to simulate.")
    p.add_argument("--shots", type=int, default=3, help="How many screenshots, evenly spaced, last frame included.")
    p.add_argument("--width", type=int, default=1280, help="Render width.")
    p.add_argument("--height", type=int, default=720, help="Render height.")
    return p.parse_args(ours), theirs


def load_example_module(name: str):
    """Import the module that defines *name* without executing its main block."""
    import newton.examples

    table = newton.examples.get_examples()
    if name not in table:
        raise SystemExit(f"unknown example '{name}'. Run: python -m newton.examples --list")

    # get_examples() maps the short name to a module path such as
    # "newton.examples.cloth.example_cloth_hanging". Importing it is safe: the
    # example's main block is guarded by __name__ == "__main__".
    modname = table[name]
    module = importlib.import_module(modname)
    return module, modname


def shot_frames(total: int, count: int) -> set[int]:
    """Evenly spaced 1-based frame numbers, always including the last one."""
    count = max(1, min(count, total))
    if count == 1:
        return {total}
    step = total / count
    return {int(round(step * (i + 1))) for i in range(count)}


def main() -> int:
    args, passthrough = parse_own_args(sys.argv[1:])

    import newton.examples

    module, path = load_example_module(args.example)
    example_cls = getattr(module, "Example", None)
    if example_cls is None:
        raise SystemExit(f"{path} has no 'Example' class; cannot drive it generically")

    # Build the example's own parser, then feed it a forced headless argv.
    if hasattr(example_cls, "create_parser"):
        parser = example_cls.create_parser()
    else:
        parser = newton.examples.create_parser()

    forced = [
        "--viewer", "gl",
        "--headless",
        "--num-frames", str(args.frames),
        "--quiet",
    ]
    sys.argv = [f"capture_{args.example}", *forced, *passthrough]

    viewer, parsed = newton.examples.init(parser)

    # The renderer size is fixed at construction, so nudge it if the viewer
    # exposes a renderer we can resize before the first frame.
    renderer = getattr(viewer, "renderer", None)
    if renderer is not None and hasattr(renderer, "_screen_width"):
        try:
            renderer._screen_width = args.width
            renderer._screen_height = args.height
        except Exception:
            pass

    example = example_cls(viewer, parsed)

    wanted = shot_frames(args.frames, args.shots)
    os.makedirs(args.out, exist_ok=True)

    import imageio.v3 as iio

    saved: list[str] = []
    frame = 0
    t0 = time.time()

    while viewer.is_running():
        if viewer.should_step():
            example.step()
        example.render()
        frame += 1

        if frame in wanted:
            img = viewer.get_frame()
            name = f"{args.example}_f{frame:05d}.png"
            dest = os.path.join(args.out, name)
            iio.imwrite(dest, img.numpy())
            saved.append(dest)

        if frame >= args.frames:
            break

    viewer.close()

    elapsed = time.time() - t0
    print(f"[capture] {args.example}: {frame} frames in {elapsed:.1f}s, {len(saved)} shots")
    for s in saved:
        print(f"[capture]   {s}")
    return 0 if saved else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)
