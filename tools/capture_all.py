"""Capture screenshots from many Newton examples, one subprocess each.

Each example runs in its own process so a crash, a hang, or an out-of-memory
kill takes down only that example. Results land in one folder plus an INDEX.md
you can browse or paste into Notion.

Usage:
    il.bat -p tools\\capture_all.py --out out\\shots
    il.bat -p tools\\capture_all.py --out out\\shots --only cable,cloth
    il.bat -p tools\\capture_all.py --out out\\shots --skip kamino,mpm --frames 200

Priority: cable and cloth run first, then everything else.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

# Run these first — they are the point of the exercise.
PRIORITY_PREFIXES = ("cable_", "cloth_")

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVER = os.path.join(HERE, "capture_example.py")


def ordered_examples(only: list[str], skip: list[str]) -> list[str]:
    import newton.examples

    names = sorted(newton.examples.get_examples())

    if only:
        names = [n for n in names if any(n.startswith(o) or n == o for o in only)]
    if skip:
        names = [n for n in names if not any(n.startswith(s) or n == s for s in skip)]

    priority = [n for n in names if n.startswith(PRIORITY_PREFIXES)]
    rest = [n for n in names if not n.startswith(PRIORITY_PREFIXES)]
    return priority + rest


def main() -> int:
    p = argparse.ArgumentParser(description="Capture screenshots from Newton examples.")
    p.add_argument("--out", default="out/shots", help="Output directory.")
    p.add_argument("--frames", type=int, default=150, help="Frames per example.")
    p.add_argument("--shots", type=int, default=3, help="Screenshots per example.")
    p.add_argument("--timeout", type=int, default=420, help="Per-example timeout in seconds.")
    p.add_argument("--only", default="", help="Comma-separated name prefixes to include.")
    p.add_argument("--skip", default="", help="Comma-separated name prefixes to exclude.")
    args = p.parse_args()

    only = [s.strip() for s in args.only.split(",") if s.strip()]
    skip = [s.strip() for s in args.skip.split(",") if s.strip()]

    names = ordered_examples(only, skip)
    os.makedirs(args.out, exist_ok=True)

    print(f"[all] {len(names)} examples -> {args.out}")
    print(f"[all] order: cable/cloth first, then the rest")

    results: list[tuple[str, str, float, int]] = []
    t_start = time.time()

    for i, name in enumerate(names, 1):
        cmd = [
            sys.executable,
            DRIVER,
            name,
            "--out", args.out,
            "--frames", str(args.frames),
            "--shots", str(args.shots),
        ]
        t0 = time.time()
        print(f"[all] ({i}/{len(names)}) {name} ...", flush=True)
        # PYTHONUTF8 is the one that matters: Warp writes its generated CUDA
        # source with open() and no explicit encoding, so on a cp949 locale any
        # kernel source with a non-ASCII character dies with UnicodeEncodeError
        # before it compiles (the kamino solvers do). PYTHONIOENCODING only
        # covers stdio, which is not where this breaks.
        child_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
                cwd=os.path.dirname(HERE),
                env=child_env,
            )
            dt = time.time() - t0
            shots = sum(1 for line in proc.stdout.splitlines() if line.startswith("[capture]   "))
            if proc.returncode == 0 and shots:
                status = "ok"
            else:
                status = "fail"
                tail = (proc.stderr or proc.stdout).strip().splitlines()
                reason = tail[-1][:160] if tail else f"exit {proc.returncode}"
                print(f"[all]     -> FAIL: {reason}", flush=True)
            results.append((name, status, dt, shots))
        except subprocess.TimeoutExpired:
            dt = time.time() - t0
            print(f"[all]     -> TIMEOUT after {dt:.0f}s", flush=True)
            results.append((name, "timeout", dt, 0))

        print(f"[all]     {results[-1][1]} in {results[-1][2]:.0f}s, {results[-1][3]} shots", flush=True)

    total = time.time() - t_start
    ok = [r for r in results if r[1] == "ok"]

    write_index(args.out, results, args)

    print()
    print(f"[all] done: {len(ok)}/{len(results)} ok in {total / 60:.1f} min")
    for name, status, dt, shots in results:
        if status != "ok":
            print(f"[all]   {status:8s} {name}")
    return 0


def write_index(out: str, results, args) -> None:
    """Merge this run's results into results.json, then render INDEX.md.

    Results accumulate across runs on purpose: a retry pass that covers only the
    examples that failed must not erase the index for everything else.
    """
    store = os.path.join(out, "results.json")
    merged: dict[str, dict] = {}
    if os.path.exists(store):
        try:
            with open(store, encoding="utf-8") as fh:
                merged = json.load(fh)
        except (OSError, ValueError):
            merged = {}

    for name, status, dt, shots in results:
        merged[name] = {"status": status, "seconds": round(dt, 1), "shots": shots}

    with open(store, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2, sort_keys=True)

    ok = sum(1 for v in merged.values() if v["status"] == "ok")
    pngs = sorted(f for f in os.listdir(out) if f.endswith(".png"))

    lines = [
        "# Newton 예제 스크린샷",
        "",
        f"예제 {ok}/{len(merged)} 성공 · 이미지 {len(pngs)}장 · 헤드리스 ViewerGL 1280x720",
        f"예제당 {args.shots}장, {args.frames} 프레임 기준",
        "",
        "| 예제 | 결과 | 시간 | 장수 |",
        "| --- | --- | --- | --- |",
    ]
    for name in sorted(merged):
        v = merged[name]
        mark = {"ok": "ok", "fail": "**실패**", "timeout": "**타임아웃**"}.get(v["status"], v["status"])
        lines.append(f"| `{name}` | {mark} | {v['seconds']:.0f}s | {v['shots']} |")

    lines += ["", "## 이미지", ""]
    for name in sorted(merged):
        shots_for = [f for f in pngs if f.startswith(name + "_f")]
        if not shots_for:
            continue
        lines.append(f"### {name}")
        lines.append("")
        for f in shots_for:
            lines.append(f"![{f}]({f})")
        lines.append("")

    with open(os.path.join(out, "INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
