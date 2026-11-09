"""Bộ kiểm thử cấu hình Container hoá cho Module 2 (Dockerfile, Compose, Nginx, .dockerignore)."""

import re
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_dockerignore_excludes_models_and_venv() -> None:
    """Đảm bảo .dockerignore chặn việc nhúng cứng model.joblib và .venv vào image."""
    content = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert re.search(r"^\.venv/", content, flags=re.MULTILINE)
    assert re.search(r"^models/", content, flags=re.MULTILINE)
    assert re.search(r"^\*\.joblib", content, flags=re.MULTILINE)
    assert re.search(r"^frontend/node_modules/", content, flags=re.MULTILINE)


def test_dockerfile_api_multistage_nonroot_and_healthcheck() -> None:
    """Kiểm tra Dockerfile.api tuân thủ multi-stage, chạy non-root user và có HEALTHCHECK."""
    content = (PROJECT_ROOT / "Dockerfile.api").read_text(encoding="utf-8")
    assert re.search(r"FROM\s+python:3\.12-slim\s+AS\s+builder", content)
    assert re.search(r"FROM\s+python:3\.12-slim\s+AS\s+runtime", content)
    assert re.search(r"^USER\s+appuser", content, flags=re.MULTILINE)
    assert re.search(r"^HEALTHCHECK\s+", content, flags=re.MULTILINE)
    assert re.search(r"backend\.api\.main:app", content)


def test_dockerfile_web_multistage_and_layer_cache_order() -> None:
    """Kiểm tra Dockerfile.web copy package.json trước khi copy toàn bộ source để giữ layer cache."""
    content = (PROJECT_ROOT / "Dockerfile.web").read_text(encoding="utf-8")
    pos_pkg = content.find("COPY frontend/package.json")
    pos_install = content.find("RUN npm install")
    pos_source = content.find("COPY frontend/ ./")

    assert pos_pkg != -1 and pos_install != -1 and pos_source != -1
    assert pos_pkg < pos_install < pos_source
    assert re.search(r"FROM\s+nginxinc/nginx-unprivileged", content)
    assert re.search(r"^HEALTHCHECK\s+", content, flags=re.MULTILINE)


def test_docker_compose_app_no_latest_tag_and_volume_mount() -> None:
    """Kiểm tra docker-compose.app.yml không dùng tag :latest, mount volume read-only và có depends_on healthy."""
    compose_path = PROJECT_ROOT / "docker-compose.app.yml"
    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    services = data.get("services", {})
    assert "api" in services
    assert "web" in services

    api_svc = services["api"]
    web_svc = services["web"]

    assert not str(api_svc.get("image", "")).endswith(":latest")
    assert not str(web_svc.get("image", "")).endswith(":latest")
    assert "./models:/app/models:ro" in api_svc.get("volumes", [])
    assert (
        web_svc.get("depends_on", {}).get("api", {}).get("condition")
        == "service_healthy"
    )
