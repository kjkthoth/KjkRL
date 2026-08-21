"""Isaac Lab 3.0 / Isaac Sim 6.0.1 사전 점검.

Isaac Sim을 부팅하지 않습니다. 설치 전에 이 머신이 전제를 만족하는지만 봅니다.
torch가 아직 없어도 돌아갑니다 — 없는 항목은 SKIP으로 표시합니다.

이 머신이 소형 검증용인지 대형 학습용인지도 판정하고, 왕복 흐름에서 주의할 점을
같이 출력합니다 — 특히 bf16 비대칭(개발 머신에는 있고 학습 머신에는 없는 경우).

필수 항목이 하나라도 실패하면 non-zero로 끝납니다 (check_scene.py와 같은 규약).

    python check_env.py
    python check_env.py --save                  # env_profile_<호스트명>.md 로 저장
    python check_env.py --save titan.md         # 경로 지정

--save로 두 머신에서 각각 남겨 커밋하면, 소형과 대형의 차이를 git diff로 봅니다.
"""

import re
import subprocess
import sys

# 한국어 Windows 콘솔은 기본 cp949입니다. em-dash 같은 문자가 인코딩 불가로
# UnicodeEncodeError를 내며 점검 도중 죽습니다 — 출력을 UTF-8로 고정합니다.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# Isaac Sim 6.0 최소 사양 (docs.isaacsim.omniverse.nvidia.com/6.0.0)
MIN_DRIVER_WINDOWS = (581, 42)
MIN_DRIVER_LINUX = (580, 95, 5)
MIN_VRAM_MB = 16 * 1024
REQUIRED_PYTHON = (3, 12)

# bf16은 Ampere(sm_80) 이상. Turing(sm_75)에는 없습니다.
BF16_MIN_CAPABILITY = (8, 0)

# 소형 검증 머신과 대형 학습 머신을 가르는 VRAM 경계.
# 대형 학습은 env를 많이 띄우는 것이 목적이므로 최소사양(16GB)을 기준으로 삼습니다.
LARGE_SCALE_VRAM_MB = MIN_VRAM_MB

failures = []
warnings = []
gpus = []


def report(status, label, detail):
    print(f"  [{status:4}] {label:28} {detail}")


def check_python():
    print("\n== Python ==")
    v = sys.version_info
    actual = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) == REQUIRED_PYTHON:
        report("OK", "version", actual)
    else:
        want = f"{REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}"
        report("FAIL", "version", f"{actual} — Isaac Sim 6.0은 {want} 필요")
        failures.append(f"Python {actual} (필요: {want})")


def parse_version(text):
    parts = re.findall(r"\d+", text.strip())
    return tuple(int(p) for p in parts) if parts else None


def query_smi():
    fields = "name,memory.total,driver_version,compute_cap"
    try:
        out = subprocess.run(
            ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return None, f"nvidia-smi 실행 불가 ({type(exc).__name__})"
    if out.returncode != 0:
        return None, f"nvidia-smi 실패: {out.stderr.strip()[:120]}"
    rows = [line for line in out.stdout.splitlines() if line.strip()]
    if not rows:
        return None, "nvidia-smi가 GPU를 보고하지 않음"
    return [[c.strip() for c in row.split(",")] for row in rows], None


def check_gpu():
    print("\n== GPU / 드라이버 ==")
    rows, err = query_smi()
    if err:
        report("FAIL", "nvidia-smi", err)
        failures.append(err)
        return

    for idx, row in enumerate(rows):
        name = row[0]
        mem_raw = row[1] if len(row) > 1 else ""
        driver_raw = row[2] if len(row) > 2 else ""
        cap_raw = row[3] if len(row) > 3 else ""

        print(f"\n  GPU {idx}: {name}")

        # VRAM
        mem = parse_version(mem_raw)
        if mem:
            mb = mem[0]
            if mb >= MIN_VRAM_MB:
                report("OK", "VRAM", f"{mb} MiB (최소 {MIN_VRAM_MB})")
            else:
                report("WARN", "VRAM", f"{mb} MiB — 최소 {MIN_VRAM_MB} 미달")
                warnings.append(f"GPU{idx} VRAM {mb} MiB < {MIN_VRAM_MB}")
        else:
            report("SKIP", "VRAM", f"파싱 실패: {mem_raw!r}")

        # 드라이버 — 유일한 하드 게이트
        want = MIN_DRIVER_WINDOWS if sys.platform == "win32" else MIN_DRIVER_LINUX
        want_str = ".".join(str(n) for n in want)
        got = parse_version(driver_raw)
        if not got:
            report("SKIP", "driver", f"파싱 실패: {driver_raw!r}")
        elif got[: len(want)] >= want:
            report("OK", "driver", f"{driver_raw} (최소 {want_str})")
        else:
            report("FAIL", "driver", f"{driver_raw} — 최소 {want_str} 미달")
            failures.append(f"GPU{idx} 드라이버 {driver_raw} < {want_str}")

        # compute capability → bf16 판정
        cap = parse_version(cap_raw)
        if not cap:
            report("SKIP", "compute cap", f"파싱 실패: {cap_raw!r}")
        else:
            cap_str = ".".join(str(n) for n in cap)
            if cap >= BF16_MIN_CAPABILITY:
                report("OK", "bf16", f"sm_{cap[0]}{cap[1]} — 지원")
            else:
                report("WARN", "bf16", f"sm_{cap[0]}{cap[1]} (cap {cap_str}) — 미지원")
                warnings.append(
                    f"GPU{idx} sm_{cap[0]}{cap[1]}: bf16 없음. 학습 config에서 "
                    "bf16/bfloat16을 fp32 또는 fp16으로 바꿔야 합니다"
                )

        gpus.append(
            {
                "name": name,
                "vram_mb": mem[0] if mem else None,
                "driver": driver_raw or None,
                "cap": cap,
            }
        )


def check_torch():
    print("\n== torch ==")
    try:
        import torch
    except ImportError:
        report("SKIP", "import", "미설치 — 설치 후 다시 돌리십시오")
        return

    report("OK", "version", torch.__version__)

    if not torch.cuda.is_available():
        report("FAIL", "cuda.is_available", "False")
        failures.append("torch에서 CUDA를 못 봅니다 (CPU 빌드이거나 드라이버 문제)")
        return
    report("OK", "cuda.is_available", "True")

    for idx in range(torch.cuda.device_count()):
        cap = torch.cuda.get_device_capability(idx)
        report("OK", f"device {idx}", f"{torch.cuda.get_device_name(idx)} sm_{cap[0]}{cap[1]}")

    # 이 torch 빌드가 이 GPU의 arch를 실제로 담고 있는지.
    # 커널이 없으면 여기서 터집니다 — 학습 도중에 터지는 것보다 낫습니다.
    try:
        (torch.zeros(8, device="cuda") + 1).sum().item()
        report("OK", "커널 실행", "sm 아치 호환 확인")
    except Exception as exc:  # noqa: BLE001 — 무엇이 터지든 원인 표시가 목적
        msg = str(exc).strip().splitlines()[0][:160]
        report("FAIL", "커널 실행", msg)
        failures.append(
            "torch가 이 GPU arch용 커널을 갖고 있지 않습니다. "
            f"다른 CUDA 빌드의 torch가 필요합니다 — {msg}"
        )
        return

    if hasattr(torch.cuda, "is_bf16_supported"):
        supported = torch.cuda.is_bf16_supported()
        report("OK" if supported else "WARN", "is_bf16_supported", str(supported))


def machine_role():
    """이 머신이 소형 검증용인지 대형 학습용인지 판정합니다.

    반환: (역할, bf16 지원 여부, 주 GPU dict) — GPU를 못 읽으면 (None, None, None).
    """
    if not gpus:
        return None, None, None
    primary = gpus[0]
    vram = primary["vram_mb"]
    cap = primary["cap"]
    role = None
    if vram is not None:
        role = "대형 학습" if vram >= LARGE_SCALE_VRAM_MB else "소형 검증"
    has_bf16 = None if cap is None else cap >= BF16_MIN_CAPABILITY
    return role, has_bf16, primary


def summarize_workflow():
    """소형 → 대형 왕복 흐름에서 이 머신의 위치와 주의점을 출력합니다."""
    role, has_bf16, primary = machine_role()
    if role is None:
        return

    print("\n== 왕복 흐름에서의 위치 ==")
    cap = primary["cap"]
    cap_str = f"sm_{cap[0]}{cap[1]}" if cap else "sm 미확인"
    report("INFO", "역할", f"{role} 머신 ({primary['name']}, {cap_str})")

    if role == "소형 검증":
        report("INFO", "다음", "코드 로직·보상·종료조건·저장까지를 여기서 봅니다")
        print(
            "\n  주의: 여기서 통과한 것이 대형 머신에서도 통과한다는 보장은 없습니다.\n"
            "  두 머신의 아키텍처가 다르면 소형이 대형의 부분집합이 아닙니다."
        )
        if has_bf16:
            print(
                "  이 머신은 bf16을 지원합니다. 학습 머신이 Turing(sm_75) 이하라면\n"
                "  bf16 config가 여기서는 통과하고 거기서 죽습니다 — fp32/fp16으로 두십시오."
            )
    else:
        report("INFO", "다음", "아키텍처 의존 항목(bf16, Warp 커널, torch arch)을 여기서 먼저 확인")
        if has_bf16 is False:
            print(
                "\n  이 머신에는 bf16이 없습니다. 개발 머신이 Ampere 이상이면\n"
                "  거기서 통과한 bf16 config가 여기서 죽습니다 — config를 이 머신 기준으로 맞추십시오."
            )


def save_profile(path):
    """다른 머신과 비교할 수 있도록 프로파일을 파일로 남깁니다."""
    import platform
    from datetime import date

    role, has_bf16, primary = machine_role()
    lines = [
        f"# 환경 프로파일 — {platform.node()}",
        "",
        f"- 확인 날짜: {date.today().isoformat()}",
        f"- 역할: {role or '판정 불가'}",
        f"- platform: {sys.platform}",
        f"- Python: {sys.version.split()[0]}",
    ]
    if primary:
        cap = primary["cap"]
        lines += [
            f"- GPU: {primary['name']}",
            f"- VRAM: {primary['vram_mb']} MiB",
            f"- 드라이버: {primary['driver']}",
            f"- compute capability: {'.'.join(str(n) for n in cap) if cap else '미확인'}",
            f"- bf16: {'지원' if has_bf16 else '미지원' if has_bf16 is False else '미확인'}",
        ]
    lines += [
        "",
        f"- 실패 {len(failures)}건, 경고 {len(warnings)}건",
    ]
    lines += [f"  - 실패: {f}" for f in failures]
    lines += [f"  - 경고: {w}" for w in warnings]
    lines.append("")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"\n프로파일 저장: {path}")
    print("  두 머신에서 각각 저장해 커밋하면 차이를 git으로 볼 수 있습니다.")


def parse_args(argv):
    """--save [경로] 만 봅니다. argparse를 쓰지 않는 이유는 의존성 0을 유지하려는 것."""
    if "--save" not in argv:
        return None
    idx = argv.index("--save")
    if idx + 1 < len(argv) and not argv[idx + 1].startswith("-"):
        return argv[idx + 1]
    import platform

    return f"env_profile_{platform.node()}.md"


def main():
    save_path = parse_args(sys.argv[1:])

    print("Isaac Lab 3.0 / Isaac Sim 6.0.1 사전 점검")
    print(f"platform: {sys.platform}")

    check_python()
    check_gpu()
    check_torch()
    summarize_workflow()

    print("\n" + "=" * 60)
    if warnings:
        print(f"경고 {len(warnings)}건 — 돌 수는 있지만 알고 있어야 합니다:")
        for w in warnings:
            print(f"  - {w}")
    if failures:
        print(f"\n실패 {len(failures)}건 — 설치를 진행하기 전에 해결하십시오:")
        for f in failures:
            print(f"  - {f}")
    else:
        print("필수 항목 통과. README.md 3절로 진행하십시오.")

    if save_path:
        save_profile(save_path)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
