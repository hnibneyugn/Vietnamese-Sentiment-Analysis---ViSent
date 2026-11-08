"""Mô-đun tiền xử lý văn bản tiếng Việt cho bài toán phân tích cảm xúc."""

import re
import unicodedata

# Biểu thức chính quy giữ lại chữ cái (bao gồm tiếng Việt có dấu), chữ số và khoảng trắng
_SPECIAL_CHARS_PATTERN = re.compile(r"[^\w\s]", flags=re.UNICODE)
_MULTI_SPACE_PATTERN = re.compile(r"\s+")


def preprocess_text(text: str | None) -> str:
    """Chuẩn hoá văn bản tiếng Việt trước khi đưa vào mô hình TF-IDF.

    Các bước thực hiện:
    1. Kiểm tra đầu vào hợp lệ (không phải None, phải là kiểu chuỗi).
    2. Chuẩn hoá bảng mã Unicode về dạng dựng sẵn NFC (tránh lệch dấu tổ hợp/dựng sẵn).
    3. Chuyển về chữ thường (lowercase).
    4. Loại bỏ dấu câu/ký tự đặc biệt, thay bằng khoảng trắng.
    5. Gộp nhiều khoảng trắng liên tiếp thành một khoảng trắng duy nhất.
    """
    if text is None or not isinstance(text, str):
        raise ValueError(
            "Văn bản đầu vào phải là một chuỗi ký tự hợp lệ (không được là None)."
        )

    normalized = unicodedata.normalize("NFC", text).strip().lower()
    if not normalized:
        return ""

    cleaned = _SPECIAL_CHARS_PATTERN.sub(" ", normalized)
    cleaned = cleaned.replace("_", " ")
    return _MULTI_SPACE_PATTERN.sub(" ", cleaned).strip()
