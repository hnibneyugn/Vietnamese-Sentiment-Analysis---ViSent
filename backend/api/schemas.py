"""Định nghĩa các Pydantic schema kiểm tra dữ liệu đầu vào và đầu ra cho FastAPI."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ml.src.preprocess import preprocess_text

SentimentLabel = Literal["positive", "negative", "neutral"]


class PredictRequest(BaseModel):
    """Schema yêu cầu dự đoán cảm xúc văn bản."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Câu bình luận hoặc đánh giá tiếng Việt cần phân loại cảm xúc (tối đa 2000 ký tự).",
        examples=["Sản phẩm đóng gói cẩn thận, giao hàng siêu nhanh!"],
    )

    @field_validator("text")
    @classmethod
    def validate_meaningful_text(cls, value: str) -> str:
        """Đảm bảo văn bản sau khi tiền xử lý vẫn còn nội dung có nghĩa (không chỉ chứa khoảng trắng hoặc ký tự đặc biệt)."""
        cleaned = preprocess_text(value)
        if not cleaned:
            raise ValueError(
                "Văn bản đầu vào không được rỗng hoặc chỉ chứa khoảng trắng / ký tự đặc biệt."
            )
        return value.strip()


class PredictResponse(BaseModel):
    """Schema phản hồi kết quả dự đoán cảm xúc."""

    label: SentimentLabel = Field(
        ..., description="Nhãn cảm xúc dự đoán: positive, negative, hoặc neutral."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Độ tin cậy (xác suất cao nhất) của dự đoán trong khoảng [0.0, 1.0].",
    )


class HealthResponse(BaseModel):
    """Schema phản hồi trạng thái sức khoẻ của dịch vụ API."""

    status: Literal["ok", "degraded"]
    model_loaded: bool
    model_path: str
