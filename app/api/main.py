"""Ứng dụng FastAPI phục vụ dự đoán cảm xúc tiếng Việt (Module 1)."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Protocol, cast

import joblib
from fastapi import FastAPI, HTTPException, Request, status

from app.api.schemas import (
    HealthResponse,
    PredictRequest,
    PredictResponse,
    SentimentLabel,
)
from ml.src.models.train import DEFAULT_MODEL_PATH
from ml.src.preprocess import preprocess_text


class ProbabilisticClassifier(Protocol):
    """Giao diện kiểu cho mô hình phân loại có hỗ trợ predict_proba."""

    @property
    def classes_(self) -> list[str]:
        """Danh sách tên các lớp phân loại."""
        ...

    def predict_proba(self, raw_documents: list[str]) -> list[list[float]]:
        """Trả về ma trận xác suất của từng lớp cho mỗi văn bản."""
        ...


def get_model_path() -> Path:
    """Lấy đường dẫn file mô hình từ biến môi trường MODEL_PATH hoặc dùng mặc định."""
    env_path = os.getenv("MODEL_PATH", "").strip()
    return Path(env_path) if env_path else DEFAULT_MODEL_PATH


def load_model_if_exists(model_path: Path) -> ProbabilisticClassifier | None:
    """Nạp mô hình từ đĩa nếu tồn tại, trả về None nếu chưa có file."""
    if not model_path.exists():
        return None
    loaded = joblib.load(model_path)
    return cast(ProbabilisticClassifier, loaded)


def initialize_app_state(application: FastAPI) -> None:
    """Khởi tạo trạng thái ứng dụng: nạp đường dẫn và mô hình vào bộ nhớ."""
    model_path = get_model_path()
    application.state.model_path = model_path
    application.state.model = load_model_if_exists(model_path)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Quản lý vòng đời ứng dụng: nạp mô hình vào bộ nhớ khi khởi động server."""
    initialize_app_state(application)
    yield
    application.state.model = None


app = FastAPI(
    title="ViSent MLOps API",
    description="API phân tích cảm xúc bình luận tiếng Việt (Module 1: TF-IDF + Logistic Regression).",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(request: Request) -> HealthResponse:
    """Kiểm tra trạng thái hoạt động của API và tình trạng nạp mô hình."""
    model: ProbabilisticClassifier | None = getattr(request.app.state, "model", None)
    model_path: Path = getattr(request.app.state, "model_path", get_model_path())
    is_loaded = model is not None
    return HealthResponse(
        status="ok" if is_loaded else "degraded",
        model_loaded=is_loaded,
        model_path=str(model_path),
    )


@app.post("/predict", response_model=PredictResponse, tags=["Inference"])
def predict_sentiment(payload: PredictRequest, request: Request) -> PredictResponse:
    """Nhận văn bản tiếng Việt, tiền xử lý và trả về nhãn cảm xúc kèm độ tin cậy."""
    model: ProbabilisticClassifier | None = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mô hình chưa được nạp. Vui lòng huấn luyện mô hình trước (`make train`).",
        )

    cleaned_text = preprocess_text(payload.text)
    probabilities = model.predict_proba([cleaned_text])[0]
    classes = list(model.classes_)

    best_idx = max(range(len(probabilities)), key=lambda idx: float(probabilities[idx]))
    best_label = cast(SentimentLabel, str(classes[best_idx]))
    best_confidence = round(float(probabilities[best_idx]), 4)

    return PredictResponse(label=best_label, confidence=best_confidence)
