"""Bộ kiểm thử toàn diện cho Module 1: tiền xử lý, huấn luyện mô hình và FastAPI."""

import re
import unicodedata
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.main import (
    app,
    get_model_path,
    health_check,
    initialize_app_state,
    lifespan,
    load_model_if_exists,
    predict_sentiment,
)
from app.api.schemas import PredictRequest
from ml.src.models.train import load_dataset, train_and_save
from ml.src.models.train import main as train_main
from ml.src.preprocess import preprocess_text


# =====================================================================
# 1. KIỂM THỬ HÀM TIỀN XỬ LÝ (preprocess_text)
# =====================================================================
def test_preprocess_happy_path_and_unicode() -> None:
    """Kiểm tra chuẩn hoá Unicode tổ hợp sang dựng sẵn, chữ thường và xoá dấu câu."""
    nfd_text = unicodedata.normalize("NFD", "  Sản_phẩm   RẤT   tốt!!! @#$  ")
    result = preprocess_text(nfd_text)
    assert result == "sản phẩm rất tốt"
    assert unicodedata.is_normalized("NFC", result)


def test_preprocess_empty_and_special_chars_only() -> None:
    """Kiểm tra chuỗi rỗng, chỉ có khoảng trắng hoặc chỉ có ký tự đặc biệt."""
    assert preprocess_text("") == ""
    assert preprocess_text("     \t\n  ") == ""
    assert preprocess_text("!!! ??? ___ @@@") == ""


def test_preprocess_invalid_none_or_non_string() -> None:
    """Kiểm tra truyền None hoặc kiểu không phải chuỗi phải ném ValueError."""
    with pytest.raises(ValueError, match=r"Văn bản đầu vào phải là một chuỗi"):
        preprocess_text(None)

    with pytest.raises(ValueError, match=r"Văn bản đầu vào phải là một chuỗi"):
        preprocess_text(12345)  # type: ignore[arg-type]


# =====================================================================
# 2. KIỂM THỬ PIPELINE HUẤN LUYỆN (load_dataset & train_and_save)
# =====================================================================
def test_load_dataset_errors(tmp_path: Path) -> None:
    """Kiểm tra các trường hợp lỗi dữ liệu: file không tồn tại, thiếu cột, nhãn sai, quá ít mẫu."""
    missing_file = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError, match=r"Không tìm thấy file dữ liệu"):
        load_dataset(missing_file)

    bad_cols = tmp_path / "bad_cols.csv"
    bad_cols.write_text("review,sentiment\nTot,positive\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"bắt buộc phải có hai cột"):
        load_dataset(bad_cols)

    invalid_label = tmp_path / "invalid_label.csv"
    invalid_label.write_text(
        "text,label\nSản phẩm tốt,positive\nHàng tệ,unknown_label\nBình thường,neutral\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"Nhãn không hợp lệ"):
        load_dataset(invalid_label)

    too_few = tmp_path / "too_few.csv"
    too_few.write_text(
        'text,label\n"","positive"\n"!!!","negative"\n"Tốt","positive"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=r"Tập dữ liệu quá ít"):
        load_dataset(too_few)


def test_train_and_save_and_cli_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kiểm tra huấn luyện, lưu file model.joblib và hàm main CLI."""
    model_file = tmp_path / "model.joblib"
    result = train_and_save(model_path=model_file)

    assert model_file.exists()
    assert result.num_samples >= 15
    assert result.accuracy >= 0.8
    assert result.macro_f1 >= 0.8

    monkeypatch.setattr("ml.src.models.train.DEFAULT_MODEL_PATH", model_file)
    assert train_main() == 0


# =====================================================================
# 3. KIỂM THỬ FASTAPI (/health & /predict) VÀ KỊCH BẢN "PHÁ THỬ"
# =====================================================================
def _make_request(state_model: object, state_path: Path) -> MagicMock:
    """Tạo đối tượng Request giả lập mang state của ứng dụng FastAPI."""
    req = MagicMock()
    req.app.state.model = state_model
    req.app.state.model_path = state_path
    return req


def test_lifespan_and_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kiểm tra khởi tạo state, lifespan, /health và /predict trả kết quả chính xác."""
    model_file = tmp_path / "model.joblib"
    train_and_save(model_path=model_file)
    monkeypatch.setenv("MODEL_PATH", str(model_file))

    assert get_model_path() == model_file

    initialize_app_state(app)
    req = _make_request(app.state.model, app.state.model_path)

    health_data = health_check(req)
    assert health_data.status == "ok"
    assert health_data.model_loaded is True

    pos_res = predict_sentiment(
        PredictRequest(
            text="Sản phẩm đóng gói cẩn thận, giao hàng siêu nhanh, rất hài lòng!"
        ),
        req,
    )
    assert pos_res.label == "positive"
    assert 0.0 < pos_res.confidence <= 1.0

    neg_res = predict_sentiment(
        PredictRequest(
            text="Hàng lỗi không dùng được, chất lượng quá kém và thất vọng."
        ),
        req,
    )
    assert neg_res.label == "negative"

    # Kiểm tra trực tiếp coroutine lifespan mà không mở socket của asyncio trên Windows sandbox
    ctx = lifespan(app)
    coro_enter = ctx.__aenter__()
    with pytest.raises(StopIteration):
        coro_enter.send(None)
    coro_exit = ctx.__aexit__(None, None, None)
    with pytest.raises(StopIteration):
        coro_exit.send(None)
    assert app.state.model is None


def test_api_when_model_not_loaded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kiểm tra hành vi degraded của /health và lỗi 503 của /predict khi chưa có file model."""
    non_existent_model = tmp_path / "no_model.joblib"
    monkeypatch.setenv("MODEL_PATH", str(non_existent_model))

    loaded = load_model_if_exists(non_existent_model)
    assert loaded is None

    req = _make_request(None, non_existent_model)
    health_data = health_check(req)
    assert health_data.status == "degraded"
    assert health_data.model_loaded is False

    with pytest.raises(HTTPException) as exc_info:
        predict_sentiment(PredictRequest(text="Sản phẩm tốt"), req)
    assert exc_info.value.status_code == 503
    assert re.search(r"Mô hình chưa được nạp", str(exc_info.value.detail))


def test_api_destructive_inputs() -> None:
    """Kiểm tra các kịch bản 'Phá thử': chuỗi rỗng, chỉ ký tự đặc biệt, chuỗi 1 triệu ký tự, trường lạ."""
    # 1. Chuỗi rỗng ""
    with pytest.raises(ValidationError):
        PredictRequest(text="")

    # 2. Chuỗi chỉ chứa khoảng trắng hoặc ký tự đặc biệt
    with pytest.raises(ValidationError, match=r"không được rỗng"):
        PredictRequest(text="     !!! @@@   ")

    # 3. Chuỗi 1.000.000 ký tự (vượt ngưỡng max_length=2000)
    with pytest.raises(ValidationError):
        PredictRequest(text="a" * 1_000_000)

    # 4. Truyền trường lạ (extra='forbid') hoặc thiếu trường text
    with pytest.raises(ValidationError):
        PredictRequest.model_validate({"text": "Tốt", "hack": 123})

    with pytest.raises(ValidationError):
        PredictRequest.model_validate({})
