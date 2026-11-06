# Makefile cho dự án ViSent MLOps
# Hỗ trợ chạy trên WSL2 Ubuntu, Linux, hoặc Git Bash trên Windows

PYTHON ?= python3

.PHONY: help doctor setup lint test train run-api clean

help:
	@echo "================================================================="
	@echo "  ViSent MLOps - Danh sách lệnh hỗ trợ"
	@echo "================================================================="
	@echo "  make doctor    : Kiểm tra môi trường (Docker, GPU, Python, Git, Node)"
	@echo "  make setup     : Tạo môi trường ảo và cài đặt thư viện (Module 1)"
	@echo "  make train     : Huấn luyện model baseline TF-IDF + LR (Module 1)"
	@echo "  make run-api   : Chạy FastAPI server tại cổng 8000 (Module 1)"
	@echo "  make test      : Chạy pytest kèm kiểm tra coverage (Module 1+)"
	@echo "  make lint      : Kiểm tra code style với ruff (Module 3+)"
	@echo "================================================================="

doctor:
	@echo "[ViSent] Đang kiểm tra môi trường hệ thống..."
	@uv run python scripts/doctor.py || python3 scripts/doctor.py 2>/dev/null || py scripts/doctor.py || python scripts/doctor.py

setup:
	uv venv .venv || $(PYTHON) -m venv .venv
	uv pip install -r requirements.txt

train:
	uv run python ml/src/models/train.py

run-api:
	uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest -v --cov=app --cov=ml --cov-report=term-missing

lint:
	uv run ruff check .
	uv run ruff format --check .
