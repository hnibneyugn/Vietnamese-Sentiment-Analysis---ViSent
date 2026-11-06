"""Script kiểm tra môi trường hệ thống cho Module 0 (make doctor).

Kiểm tra sự tồn tại và phiên bản của:
- Git, Python, uv, Node.js
- WSL2 & bản phân phối Ubuntu
- Docker CLI & Docker Daemon
- GPU NVIDIA trên máy host và bên trong container CUDA
"""

import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Kết quả kiểm tra từng thành phần hệ thống."""

    name: str
    passed: bool
    detail: str
    hint: str = ""


def run_cmd(cmd: list[str], timeout: int = 15) -> tuple[bool, str]:
    """Chạy lệnh hệ thống và trả về trạng thái thành công cùng chuỗi kết quả."""
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        output = (proc.stdout or proc.stderr).strip()
        # Loại bỏ ký tự null thường xuất hiện từ đầu ra UTF-16 của lệnh wsl.exe
        output = output.replace("\x00", "").strip()
        first_line = output.splitlines()[0] if output else ""
        return proc.returncode == 0, first_line
    except FileNotFoundError:
        return False, "Không tìm thấy lệnh"
    except subprocess.TimeoutExpired:
        return False, "Quá thời gian chờ (timeout)"
    except OSError as exc:
        return False, f"Lỗi: {exc}"


def check_binary(name: str, cmd: list[str], hint: str) -> CheckResult:
    """Kiểm tra một công cụ dòng lệnh cơ bản."""
    ok, out = run_cmd(cmd)
    return CheckResult(
        name=name,
        passed=ok,
        detail=out if ok else "Chưa cài đặt / Không có trong PATH",
        hint=hint,
    )


def check_python() -> CheckResult:
    """Kiểm tra phiên bản Python đang thực thi."""
    ver = sys.version.split()[0]
    return CheckResult(
        name="Python",
        passed=True,
        detail=f"Python {ver} ({sys.executable})",
    )


def check_docker_daemon() -> CheckResult:
    """Kiểm tra Docker Daemon có đang chạy hay không."""
    ok, out = run_cmd(["docker", "info", "--format", "{{.ServerVersion}}"])
    if ok and out:
        return CheckResult(
            name="Docker Daemon",
            passed=True,
            detail=f"Server Engine v{out} (Đang chạy)",
        )
    return CheckResult(
        name="Docker Daemon",
        passed=False,
        detail="Docker Engine đang tắt hoặc không phản hồi",
        hint="Hãy mở ứng dụng Docker Desktop và đợi biểu tượng cá voi chuyển sang trạng thái Running.",
    )


def check_container_gpu(docker_running: bool) -> CheckResult:
    """Kiểm tra container Docker có nhận diện được GPU NVIDIA không."""
    if not docker_running:
        return CheckResult(
            name="GPU trong Container",
            passed=False,
            detail="Bỏ qua vì Docker Daemon chưa chạy",
            hint="Khởi động Docker Desktop trước, sau đó chạy: docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi",
        )
    ok, out = run_cmd(
        [
            "docker",
            "run",
            "--rm",
            "--gpus",
            "all",
            "nvidia/cuda:12.4.1-base-ubuntu22.04",
            "nvidia-smi",
            "--query-gpu=name,memory.total",
            "--format=csv,noheader",
        ],
        timeout=60,
    )
    if ok and out:
        return CheckResult(
            name="GPU trong Container", passed=True, detail=f"Container thấy GPU: {out}"
        )
    return CheckResult(
        name="GPU trong Container",
        passed=False,
        detail=out or "Không truy cập được GPU từ container",
        hint="Kiểm tra Docker Desktop -> Settings -> Resources -> WSL Integration và đảm bảo driver NVIDIA đã cài trên Windows.",
    )


def main() -> int:
    """Chạy toàn bộ bài kiểm tra Module 0 và in bảng tổng hợp."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 72)
    print("  VISENT MLOPS DOCTOR — KIỂM TRA MÔI TRƯỜNG (MODULE 0)")
    print("=" * 72)

    results: list[CheckResult] = [
        check_python(),
        check_binary(
            "uv (Package Manager)",
            ["uv", "--version"],
            "Cài đặt uv để quản lý package Python cực nhanh.",
        ),
        check_binary(
            "Git", ["git", "--version"], "Cài đặt Git từ https://git-scm.com/"
        ),
        check_binary(
            "Node.js",
            ["node", "--version"],
            "Cài đặt Node.js LTS cho phần Frontend ở Module 2.",
        ),
        check_binary(
            "GPU Host (nvidia-smi)",
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
            "Cài đặt NVIDIA Game Ready hoặc Studio Driver mới nhất trên Windows.",
        ),
        check_binary(
            "Docker CLI",
            ["docker", "--version"],
            "Cài đặt Docker Desktop với WSL2 backend.",
        ),
    ]

    docker_daemon = check_docker_daemon()
    results.append(docker_daemon)
    results.append(check_container_gpu(docker_daemon.passed))

    # Kiểm tra thêm make
    has_make = shutil.which("make") is not None
    results.append(
        CheckResult(
            name="GNU Make",
            passed=has_make,
            detail="Đã cài đặt"
            if has_make
            else "Chưa có trên Windows PATH (khuyên dùng trong WSL2 Ubuntu)",
            hint="Chạy `wsl --install -d Ubuntu-22.04` và cài `sudo apt install make build-essential` trong Ubuntu.",
        )
    )

    all_critical_passed = True
    for r in results:
        status = "[OK]  " if r.passed else "[FAIL]"
        print(f"{status} {r.name:<24} : {r.detail}")
        if not r.passed:
            if r.name != "GNU Make":
                all_critical_passed = False
            if r.hint:
                print(f"       -> Gợi ý: {r.hint}")

    print("=" * 72)
    if all_critical_passed:
        print("🎉 CHÚC MỪNG! Môi trường của bạn đã đạt chuẩn Module 0 (`m0-done`).")
        return 0

    print(
        "⚠️  Một số thành phần chưa sẵn sàng. Hãy xem gợi ý bên trên để hoàn tất Module 0."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
