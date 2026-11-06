"""Kiểm thử toàn diện cho scripts/doctor.py."""

import subprocess
from unittest.mock import patch

from scripts.doctor import (
    CheckResult,
    check_binary,
    check_container_gpu,
    check_docker_daemon,
    check_python,
    main,
    run_cmd,
)


def test_run_cmd_success() -> None:
    """Kiểm tra run_cmd khi lệnh thực thi thành công và có ký tự null."""
    with patch("scripts.doctor.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "v\x001.0.0\ndòng 2"
        mock_run.return_value.stderr = ""
        ok, out = run_cmd(["dummy"])
        assert ok is True
        assert out == "v1.0.0"


def test_run_cmd_stderr_fallback() -> None:
    """Kiểm tra run_cmd khi stdout rỗng và phải lấy từ stderr."""
    with patch("scripts.doctor.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Lỗi thực thi"
        ok, out = run_cmd(["dummy"])
        assert ok is False
        assert out == "Lỗi thực thi"


def test_run_cmd_empty_output() -> None:
    """Kiểm tra run_cmd khi cả stdout và stderr đều rỗng."""
    with patch("scripts.doctor.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        ok, out = run_cmd(["dummy"])
        assert ok is True
        assert out == ""


def test_run_cmd_exceptions() -> None:
    """Kiểm tra các nhánh ngoại lệ FileNotFoundError, TimeoutExpired và Exception chung."""
    with patch("scripts.doctor.subprocess.run", side_effect=FileNotFoundError()):
        ok, out = run_cmd(["missing"])
        assert ok is False
        assert out == "Không tìm thấy lệnh"

    with patch(
        "scripts.doctor.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="slow", timeout=1),
    ):
        ok, out = run_cmd(["slow"], timeout=1)
        assert ok is False
        assert out == "Quá thời gian chờ (timeout)"

    with patch("scripts.doctor.subprocess.run", side_effect=OSError("Boom")):
        ok, out = run_cmd(["err"])
        assert ok is False
        assert out == "Lỗi: Boom"


def test_check_binary_and_python() -> None:
    """Kiểm tra check_binary ở cả 2 nhánh thành công/thất bại và check_python."""
    py_res = check_python()
    assert py_res.passed is True
    assert "Python" in py_res.detail

    with patch("scripts.doctor.run_cmd", return_value=(True, "git version 2.55")):
        res_ok = check_binary("Git", ["git", "--version"], "Cài Git")
        assert res_ok.passed is True
        assert res_ok.detail == "git version 2.55"

    with patch("scripts.doctor.run_cmd", return_value=(False, "")):
        res_fail = check_binary("Git", ["git", "--version"], "Cài Git")
        assert res_fail.passed is False
        assert res_fail.detail == "Chưa cài đặt / Không có trong PATH"


def test_check_docker_daemon_and_gpu() -> None:
    """Kiểm tra các nhánh của check_docker_daemon và check_container_gpu."""
    with patch("scripts.doctor.run_cmd", return_value=(True, "29.8.2")):
        d_ok = check_docker_daemon()
        assert d_ok.passed is True
        assert "29.8.2" in d_ok.detail

    with patch("scripts.doctor.run_cmd", return_value=(False, "")):
        d_fail = check_docker_daemon()
        assert d_fail.passed is False

    # Nhánh Docker chưa chạy
    gpu_skip = check_container_gpu(docker_running=False)
    assert gpu_skip.passed is False
    assert "Bỏ qua" in gpu_skip.detail

    # Nhánh Docker đang chạy và thấy GPU
    with patch("scripts.doctor.run_cmd", return_value=(True, "RTX 4060, 8188 MiB")):
        gpu_ok = check_container_gpu(docker_running=True)
        assert gpu_ok.passed is True
        assert "RTX 4060" in gpu_ok.detail

    # Nhánh Docker đang chạy nhưng lỗi GPU
    with patch("scripts.doctor.run_cmd", return_value=(False, "")):
        gpu_fail = check_container_gpu(docker_running=True)
        assert gpu_fail.passed is False
        assert "Không truy cập được GPU" in gpu_fail.detail


def test_main_all_passed_and_failed() -> None:
    """Kiểm tra hàm main() khi tất cả pass và khi có thành phần fail."""
    with (
        patch(
            "scripts.doctor.check_python",
            return_value=CheckResult("Python", True, "3.14"),
        ),
        patch(
            "scripts.doctor.check_binary", return_value=CheckResult("Tool", True, "1.0")
        ),
        patch(
            "scripts.doctor.check_docker_daemon",
            return_value=CheckResult("Docker Daemon", True, "Running"),
        ),
        patch(
            "scripts.doctor.check_container_gpu",
            return_value=CheckResult("GPU trong Container", True, "RTX 4060"),
        ),
        patch("scripts.doctor.shutil.which", return_value="/usr/bin/make"),
    ):
        assert main() == 0

    with (
        patch(
            "scripts.doctor.check_python",
            return_value=CheckResult("Python", True, "3.14"),
        ),
        patch(
            "scripts.doctor.check_binary",
            return_value=CheckResult("Tool", False, "Missing", "Hint"),
        ),
        patch(
            "scripts.doctor.check_docker_daemon",
            return_value=CheckResult("Docker Daemon", False, "Stopped", ""),
        ),
        patch(
            "scripts.doctor.check_container_gpu",
            return_value=CheckResult("GPU trong Container", False, "Skip", ""),
        ),
        patch("scripts.doctor.shutil.which", return_value=None),
    ):
        assert main() == 1
